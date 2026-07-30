#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from eval_lib import (
    RunSpec,
    atomic_write_json,
    atomic_write_text,
    build_prompt,
    case_by_id,
    clean_worktrees,
    hash_tree,
    load_suite,
    local_root,
    prepare_run_repository,
    prepare_skill_variants,
    reconstruct_final_repository,
    repository_root,
    run_git_diff,
    checked_remove_tree,
    worktree_root,
)
from grading import grade_run
from providers import execute_provider, preflight_versions
from reporting import (
    build_combined_report,
    materialize_review_workspaces,
    run_skill_creator_reports,
)


def _selection(
    requested: list[str] | None,
    available: list[str],
    label: str,
) -> list[str]:
    if not requested:
        return available
    unknown = sorted(set(requested) - set(available))
    if unknown:
        raise SystemExit(f"unknown {label}: {', '.join(unknown)}")
    return requested


def _specs(args: argparse.Namespace, suite: dict[str, Any]) -> list[RunSpec]:
    providers = _selection(
        args.provider,
        list(suite["providers"]),
        "provider",
    )
    variants = _selection(args.variant, suite["variants"], "variant")
    cases = _selection(
        args.case,
        [case["id"] for case in suite["cases"]],
        "case",
    )
    runs = args.runs or suite["runs_per_cell"]
    specs = [
        RunSpec(provider, variant, case_id, run_number)
        for provider in providers
        for variant in variants
        for case_id in cases
        for run_number in range(1, runs + 1)
    ]
    random.Random(suite["seed"]).shuffle(specs)
    return specs


def _provider_queues(specs: list[RunSpec]) -> dict[str, list[RunSpec]]:
    queues: dict[str, list[RunSpec]] = {}
    for spec in specs:
        queues.setdefault(spec.provider, []).append(spec)
    return queues


def _redacted_command(command: list[str], prompt: str) -> list[str]:
    return ["<PROMPT>" if argument == prompt else argument for argument in command]


def _extract_response(provider: str, stdout: str) -> str:
    documents: list[Any] = []
    for line in stdout.splitlines():
        try:
            documents.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not documents:
        try:
            documents.append(json.loads(stdout))
        except json.JSONDecodeError:
            return stdout

    preferred_keys = (
        "result",
        "text",
        "final_output",
        "message",
        "content",
    )
    for document in reversed(documents):
        if not isinstance(document, dict):
            continue
        for key in preferred_keys:
            value = document.get(key)
            if isinstance(value, str) and value.strip():
                return value
            if isinstance(value, dict):
                text = value.get("text") or value.get("content")
                if isinstance(text, str) and text.strip():
                    return text
    return stdout


def _run_one(
    spec: RunSpec,
    repo_root: Path,
    eval_root: Path,
    suite: dict[str, Any],
    skills: dict[str, Path],
    provider_locks: dict[str, threading.Lock],
    force: bool,
) -> dict[str, Any]:
    result_dir = eval_root / "results" / spec.slug
    result_path = result_dir / "result.json"
    if result_path.exists() and not force:
        existing = json.loads(result_path.read_text())
        if existing.get("complete"):
            return existing

    case = case_by_id(suite, spec.case_id)
    attempts: list[dict[str, Any]] = []
    final = None
    run_repo = None
    initial_patch = ""
    initial_hashes: dict[str, str] = {}
    skill_hash = ""
    prompt = ""
    for attempt_number in range(1, len(suite["retry_delays_seconds"]) + 2):
        run_repo, initial_patch, initial_hashes, skill_hash = prepare_run_repository(
            repo_root,
            eval_root,
            suite,
            skills[spec.variant],
            spec,
        )
        prompt = build_prompt(initial_patch)
        with provider_locks[spec.provider]:
            provider_result = execute_provider(
                spec.provider,
                run_repo,
                prompt,
                suite["providers"][spec.provider],
                suite["timeout_seconds"],
            )
        infrastructure_error = provider_result.infrastructure_error
        attempts.append(
            {
                "attempt": attempt_number,
                "exit_code": provider_result.exit_code,
                "timed_out": provider_result.timed_out,
                "duration_seconds": round(
                    provider_result.duration_seconds,
                    3,
                ),
                "infrastructure_error": infrastructure_error,
            }
        )
        final = provider_result
        if infrastructure_error is None:
            break
        if not provider_result.retryable:
            break
        if attempt_number <= len(suite["retry_delays_seconds"]):
            time.sleep(suite["retry_delays_seconds"][attempt_number - 1])

    assert final is not None
    assert run_repo is not None
    response = _extract_response(spec.provider, final.stdout)
    skill_unchanged = hash_tree(run_repo / ".eval" / "skill") == skill_hash
    provider_ok = final.infrastructure_error is None
    grading, facts = grade_run(
        case,
        run_repo,
        initial_hashes,
        skill_unchanged,
        provider_ok,
        eval_root / "cargo-target",
        response,
        final.tool_calls,
        final.duration_seconds,
    )
    final_patch = run_git_diff(run_repo)
    timing = {
        "total_tokens": final.total_tokens,
        "duration_ms": round(final.duration_seconds * 1000),
        "total_duration_seconds": round(final.duration_seconds, 3),
        "executor_duration_seconds": round(final.duration_seconds, 3),
    }

    result_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_text(result_dir / "response.md", response)
    atomic_write_text(result_dir / "stdout.log", final.stdout)
    atomic_write_text(result_dir / "stderr.log", final.stderr)
    atomic_write_text(result_dir / "initial.diff", initial_patch)
    atomic_write_text(result_dir / "patch.diff", final_patch)
    atomic_write_json(result_dir / "grading.json", grading)
    atomic_write_json(result_dir / "timing.json", timing)
    atomic_write_json(result_dir / "facts.json", facts)

    record = {
        "complete": True,
        "valid": provider_ok,
        "provider": spec.provider,
        "variant": spec.variant,
        "case_id": spec.case_id,
        "run_number": spec.run_number,
        "model": final.model,
        "pass_rate": grading["summary"]["pass_rate"],
        "case_success": facts["case_success"],
        "agent_changed_paths": facts["agent_changed_paths"],
        "attempts": attempts,
        "command": _redacted_command(final.command, prompt),
        "infrastructure_error": final.infrastructure_error,
    }
    atomic_write_json(result_path, record)
    checked_remove_tree(run_repo, worktree_root(repo_root))
    return record


def command_preflight(args: argparse.Namespace) -> int:
    suite = load_suite()
    providers = _selection(
        args.provider,
        list(suite["providers"]),
        "provider",
    )
    checks = preflight_versions(providers)
    print(json.dumps(checks, indent=2))
    return 0 if all(check["ok"] for check in checks.values()) else 1


def command_prepare(_: argparse.Namespace) -> int:
    suite = load_suite()
    repo_root = repository_root()
    eval_root = local_root(repo_root)
    eval_root.mkdir(parents=True, exist_ok=True)
    skills = prepare_skill_variants(repo_root, eval_root, suite)
    print(
        json.dumps(
            {name: str(path) for name, path in skills.items()},
            indent=2,
        )
    )
    return 0


def command_validate_fixtures(args: argparse.Namespace) -> int:
    suite = load_suite()
    repo_root = repository_root()
    eval_root = local_root(repo_root)
    eval_root.mkdir(parents=True, exist_ok=True)
    skills = prepare_skill_variants(repo_root, eval_root, suite)
    cases = _selection(
        args.case,
        [case["id"] for case in suite["cases"]],
        "case",
    )
    failures = 0
    for case_id in cases:
        spec = RunSpec("fixture", "current", case_id, 1)
        run_repo, _, initial_hashes, skill_hash = prepare_run_repository(
            repo_root,
            eval_root,
            suite,
            skills["current"],
            spec,
        )
        case = case_by_id(suite, case_id)
        grading, _ = grade_run(
            case,
            run_repo,
            initial_hashes,
            hash_tree(run_repo / ".eval" / "skill") == skill_hash,
            True,
            eval_root / "cargo-target",
            "",
            0,
            0.0,
        )
        validation = next(
            item
            for item in grading["expectations"]
            if item["text"] == "The fixture validation command passes."
        )
        print(f"{case_id}: {'pass' if validation['passed'] else 'fail'}")
        if not validation["passed"]:
            print(validation["evidence"])
            failures += 1
    return 1 if failures else 0


def command_run(args: argparse.Namespace) -> int:
    suite = load_suite()
    repo_root = repository_root()
    eval_root = local_root(repo_root)
    eval_root.mkdir(parents=True, exist_ok=True)
    specs = _specs(args, suite)
    if args.dry_run:
        for spec in specs:
            print(spec.slug)
        print(f"{len(specs)} runs")
        return 0

    providers = sorted({spec.provider for spec in specs})
    checks = preflight_versions(providers)
    failed = [provider for provider, check in checks.items() if not check["ok"]]
    if failed:
        raise SystemExit(f"provider preflight failed: {', '.join(failed)}")

    skills = prepare_skill_variants(repo_root, eval_root, suite)
    provider_locks = {provider: threading.Lock() for provider in suite["providers"]}

    def run_provider_queue(provider_specs: list[RunSpec]) -> int:
        provider_failures = 0
        for spec in provider_specs:
            try:
                result = _run_one(
                    spec,
                    repo_root,
                    eval_root,
                    suite,
                    skills,
                    provider_locks,
                    args.force,
                )
            except Exception as error:
                provider_failures += 1
                print(f"{spec.slug}: harness error: {error}", flush=True)
                continue
            status = "valid" if result["valid"] else "infrastructure failure"
            print(
                f"{spec.slug}: {status}, pass rate {result['pass_rate']:.1%}",
                flush=True,
            )
        return provider_failures

    queues = _provider_queues(specs)
    failures = 0
    with ThreadPoolExecutor(
        max_workers=min(args.max_workers, len(queues), 4)
    ) as executor:
        futures = {
            executor.submit(run_provider_queue, provider_specs): provider
            for provider, provider_specs in queues.items()
        }
        for future in as_completed(futures):
            provider = futures[future]
            try:
                failures += future.result()
            except Exception as error:
                failures += 1
                print(f"{provider}: provider worker failed: {error}", flush=True)

    if not args.no_report:
        report_args = argparse.Namespace()
        command_report(report_args)
    return 1 if failures else 0


def command_regrade(args: argparse.Namespace) -> int:
    suite = load_suite()
    repo_root = repository_root()
    eval_root = local_root(repo_root)
    skills = prepare_skill_variants(repo_root, eval_root, suite)
    missing = 0
    for spec in _specs(args, suite):
        result_dir = eval_root / "results" / spec.slug
        result_path = result_dir / "result.json"
        if not result_path.exists():
            missing += 1
            print(f"{spec.slug}: missing result", flush=True)
            continue

        record = json.loads(result_path.read_text())
        old_facts = json.loads((result_dir / "facts.json").read_text())
        old_grading = json.loads((result_dir / "grading.json").read_text())
        timing = json.loads((result_dir / "timing.json").read_text())
        response = (result_dir / "response.md").read_text()
        run_repo, initial_hashes, _ = reconstruct_final_repository(
            repo_root,
            eval_root,
            suite,
            skills[spec.variant],
            spec,
            result_dir / "patch.diff",
        )
        case = case_by_id(suite, spec.case_id)
        grading, facts = grade_run(
            case,
            run_repo,
            initial_hashes,
            bool(old_facts["skill_unchanged"]),
            bool(record["valid"]),
            eval_root / "cargo-target",
            response,
            old_grading["execution_metrics"]["total_tool_calls"],
            float(timing["total_duration_seconds"]),
        )
        atomic_write_json(result_dir / "grading.json", grading)
        atomic_write_json(result_dir / "facts.json", facts)
        record["pass_rate"] = grading["summary"]["pass_rate"]
        record["case_success"] = facts["case_success"]
        record["agent_changed_paths"] = facts["agent_changed_paths"]
        record["false_positive"] = facts["false_positive"]
        atomic_write_json(result_path, record)
        checked_remove_tree(run_repo, worktree_root(repo_root))
        print(
            f"{spec.slug}: regraded at {record['pass_rate']:.1%}",
            flush=True,
        )
    clean_worktrees(repo_root)
    return 1 if missing else 0


def command_report(_: argparse.Namespace) -> int:
    suite = load_suite()
    repo_root = repository_root()
    eval_root = local_root(repo_root)
    clean_worktrees(repo_root)
    report = build_combined_report(eval_root, suite)
    workspaces = materialize_review_workspaces(eval_root, suite)
    run_skill_creator_reports(workspaces, suite, report)
    print(json.dumps(report, indent=2))
    print(f"Review: {eval_root / 'review/combined/iteration-1/review.html'}")
    return 0 if not report["metadata"]["missing_runs"] else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description=(
            "Benchmark the current unslop skill against the candidate "
            "Directive 16 patch across local coding CLIs."
        )
    )
    subparsers = root.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser(
        "preflight",
        help="check provider executables, versions, and available auth status",
    )
    preflight.add_argument("--provider", action="append")
    preflight.set_defaults(handler=command_preflight)

    prepare = subparsers.add_parser(
        "prepare",
        help="create immutable current and candidate skill snapshots under .git",
    )
    prepare.set_defaults(handler=command_prepare)

    validate = subparsers.add_parser(
        "validate-fixtures",
        help="build each changed fixture and run its deterministic validation",
    )
    validate.add_argument("--case", action="append")
    validate.set_defaults(handler=command_validate_fixtures)

    run = subparsers.add_parser(
        "run",
        help="run the benchmark, resume completed cells, and generate reports",
    )
    run.add_argument("--provider", action="append")
    run.add_argument("--variant", action="append")
    run.add_argument("--case", action="append")
    run.add_argument("--runs", type=int)
    run.add_argument("--max-workers", type=int, default=4)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--force", action="store_true")
    run.add_argument("--no-report", action="store_true")
    run.set_defaults(handler=command_run)

    report = subparsers.add_parser(
        "report",
        help="rebuild benchmark JSON, Markdown, and static review HTML",
    )
    report.set_defaults(handler=command_report)

    regrade = subparsers.add_parser(
        "regrade",
        help="rebuild deterministic grades from saved provider patches",
    )
    regrade.add_argument("--provider", action="append")
    regrade.add_argument("--variant", action="append")
    regrade.add_argument("--case", action="append")
    regrade.add_argument("--runs", type=int)
    regrade.set_defaults(handler=command_regrade)
    return root


def main() -> int:
    args = parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
