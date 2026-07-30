from __future__ import annotations

import json
import shutil
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eval_lib import atomic_write_json, atomic_write_text


def _skill_creator_root() -> Path:
    candidates = [
        Path.home()
        / ".codex/plugins/cache/claude-plugins-official/skill-creator/local/skills/skill-creator",
        Path.home()
        / ".claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator",
    ]
    for candidate in candidates:
        if (candidate / "scripts" / "aggregate_benchmark.py").exists():
            return candidate
    raise FileNotFoundError(
        "skill-creator benchmark scripts were not found; set up the skill-creator plugin"
    )


def _copy_run_to_review(
    result_dir: Path,
    target: Path,
) -> None:
    target.mkdir(parents=True, exist_ok=True)
    outputs = target / "outputs"
    outputs.mkdir(exist_ok=True)
    for name in ("grading.json", "timing.json"):
        shutil.copy2(result_dir / name, target / name)
    for name in ("response.md", "patch.diff", "initial.diff", "facts.json"):
        source = result_dir / name
        if source.exists():
            shutil.copy2(source, outputs / name)


def materialize_review_workspaces(
    eval_root: Path,
    suite: dict[str, Any],
) -> list[Path]:
    review_root = eval_root / "review"
    if review_root.exists():
        shutil.rmtree(review_root)
    review_root.mkdir(parents=True)

    workspaces: list[Path] = []
    providers = list(suite["providers"])
    case_order = {case["id"]: index + 1 for index, case in enumerate(suite["cases"])}
    for provider_index, provider in enumerate(providers):
        workspace = review_root / provider / "iteration-1"
        workspace.mkdir(parents=True)
        workspaces.append(workspace)
        for case in suite["cases"]:
            eval_id = case_order[case["id"]]
            eval_dir = workspace / f"eval-{eval_id:02d}-{case['id']}"
            atomic_write_json(
                eval_dir / "eval_metadata.json",
                {
                    "eval_id": eval_id,
                    "eval_name": case["title"],
                    "prompt": (
                        "Use the supplied unslop skill in apply mode to review and "
                        "clean the current fixture patch."
                    ),
                    "assertions": [],
                    "provider": provider,
                },
            )
            for variant, configuration in (
                ("candidate", "new_skill"),
                ("current", "old_skill"),
            ):
                for run_number in range(1, suite["runs_per_cell"] + 1):
                    slug = f"{provider}__{variant}__{case['id']}__run-{run_number}"
                    source = eval_root / "results" / slug
                    if source.exists():
                        _copy_run_to_review(
                            source,
                            eval_dir / configuration / f"run-{run_number}",
                        )

    combined = review_root / "combined" / "iteration-1"
    combined.mkdir(parents=True)
    workspaces.append(combined)
    for provider_index, provider in enumerate(providers):
        provider_workspace = review_root / provider / "iteration-1"
        for source_eval in sorted(provider_workspace.glob("eval-*")):
            local_id = json.loads((source_eval / "eval_metadata.json").read_text())[
                "eval_id"
            ]
            combined_id = provider_index * 100 + local_id
            target_eval = (
                combined
                / f"eval-{combined_id:03d}-{provider}-{source_eval.name.split('-', 2)[2]}"
            )
            shutil.copytree(source_eval, target_eval)
            metadata_path = target_eval / "eval_metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["eval_id"] = combined_id
            metadata["eval_name"] = f"{provider}: {metadata['eval_name']}"
            atomic_write_json(metadata_path, metadata)
    return workspaces


def run_skill_creator_reports(
    workspaces: list[Path],
    suite: dict[str, Any],
    combined_report: dict[str, Any],
) -> None:
    skill_creator = _skill_creator_root()
    aggregate = skill_creator / "scripts" / "aggregate_benchmark.py"
    viewer = skill_creator / "eval-viewer" / "generate_review.py"
    for workspace in workspaces:
        subprocess.run(
            [
                "python",
                str(aggregate),
                str(workspace),
                "--skill-name",
                "unslop",
                "--skill-path",
                ".eval/skill",
            ],
            check=True,
        )
        benchmark_path = workspace / "benchmark.json"
        benchmark = json.loads(benchmark_path.read_text())
        benchmark["metadata"]["runs_per_configuration"] = suite["runs_per_cell"]
        if workspace.parent.name != "combined":
            provider = workspace.parent.name
            benchmark["metadata"]["executor_model"] = str(
                suite["providers"][provider]["model"]
            )
        else:
            benchmark["metadata"]["executor_model"] = "multiple providers"
        benchmark["metadata"]["analyzer_model"] = "deterministic"
        if workspace.parent.name == "combined":
            benchmark["notes"] = combined_report["analysis"]["observations"]
        atomic_write_json(benchmark_path, benchmark)
        subprocess.run(
            [
                "python",
                str(viewer),
                str(workspace),
                "--skill-name",
                "unslop",
                "--benchmark",
                str(benchmark_path),
                "--static",
                str(workspace / "review.html"),
            ],
            check=True,
        )


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _sample_stddev(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def build_combined_report(
    eval_root: Path,
    suite: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    missing: list[str] = []
    for provider in suite["providers"]:
        for variant in suite["variants"]:
            for case in suite["cases"]:
                for run_number in range(1, suite["runs_per_cell"] + 1):
                    slug = f"{provider}__{variant}__{case['id']}__run-{run_number}"
                    result_path = eval_root / "results" / slug / "result.json"
                    if not result_path.exists():
                        missing.append(slug)
                        continue
                    result = json.loads(result_path.read_text())
                    timing_path = result_path.parent / "timing.json"
                    timing = (
                        json.loads(timing_path.read_text())
                        if timing_path.exists()
                        else {}
                    )
                    result["duration_seconds"] = timing.get(
                        "total_duration_seconds",
                        0.0,
                    )
                    result["total_tokens"] = timing.get("total_tokens", 0)
                    if result.get("model") in ("default", "auto", ""):
                        stdout_path = result_path.parent / "stdout.log"
                        if stdout_path.exists():
                            try:
                                stdout = json.loads(stdout_path.read_text())
                            except json.JSONDecodeError:
                                stdout = {}
                            model_usage = stdout.get("modelUsage", {})
                            if isinstance(model_usage, dict) and model_usage:
                                result["model"] = next(iter(model_usage))
                    result["dimension"] = case["dimension"]
                    records.append(result)

    by_variant: dict[str, Any] = {}
    for variant in suite["variants"]:
        values = [
            record["pass_rate"]
            for record in records
            if record["variant"] == variant and record["valid"]
        ]
        by_variant[variant] = {
            "valid_runs": len(values),
            "mean_pass_rate": round(_mean(values), 4),
            "stddev": round(_sample_stddev(values), 4),
            "mean_duration_seconds": round(
                _mean(
                    [
                        record["duration_seconds"]
                        for record in records
                        if record["variant"] == variant and record["valid"]
                    ]
                ),
                3,
            ),
            "mean_total_tokens": round(
                _mean(
                    [
                        record["total_tokens"]
                        for record in records
                        if record["variant"] == variant and record["valid"]
                    ]
                )
            ),
        }

    by_provider: dict[str, Any] = {}
    provider_deltas: list[float] = []
    providers_improve_or_tie = 0
    for provider in suite["providers"]:
        current = [
            record["pass_rate"]
            for record in records
            if record["provider"] == provider
            and record["variant"] == "current"
            and record["valid"]
        ]
        candidate = [
            record["pass_rate"]
            for record in records
            if record["provider"] == provider
            and record["variant"] == "candidate"
            and record["valid"]
        ]
        delta = _mean(candidate) - _mean(current)
        provider_deltas.append(delta)
        if delta >= 0:
            providers_improve_or_tie += 1
        by_provider[provider] = {
            "current": round(_mean(current), 4),
            "candidate": round(_mean(candidate), 4),
            "delta": round(delta, 4),
            "valid_current_runs": len(current),
            "valid_candidate_runs": len(candidate),
            "observed_models": sorted(
                {
                    record["model"]
                    for record in records
                    if record["provider"] == provider and record.get("model")
                }
            ),
        }

    positive_candidate = [
        record
        for record in records
        if record["variant"] == "candidate"
        and record["dimension"] == "directive16_positive"
        and record["valid"]
    ]
    negative_candidate = [
        record
        for record in records
        if record["variant"] == "candidate"
        and record["dimension"] == "directive16_negative"
        and record["valid"]
    ]
    false_positive_changes = sum(
        bool(record.get("false_positive")) for record in negative_candidate
    )

    legacy_rates: dict[str, float] = {}
    for variant in suite["variants"]:
        legacy_rates[variant] = _mean(
            [
                record["pass_rate"]
                for record in records
                if record["variant"] == variant
                and record["dimension"] == "legacy"
                and record["valid"]
            ]
        )

    overall_delta = (
        by_variant["candidate"]["mean_pass_rate"]
        - by_variant["current"]["mean_pass_rate"]
    )
    maximum_possible_overall_delta = 1.0 - by_variant["current"]["mean_pass_rate"]
    legacy_delta = legacy_rates["candidate"] - legacy_rates["current"]
    expected_runs = (
        len(suite["providers"])
        * len(suite["variants"])
        * len(suite["cases"])
        * suite["runs_per_cell"]
    )
    valid_runs = sum(record["valid"] for record in records)
    positive_successes = sum(
        bool(record["case_success"]) for record in positive_candidate
    )

    cell_counts: dict[str, int] = {}
    for provider in suite["providers"]:
        for variant in suite["variants"]:
            for case in suite["cases"]:
                key = f"{provider}/{variant}/{case['id']}"
                cell_counts[key] = sum(
                    1
                    for record in records
                    if record["provider"] == provider
                    and record["variant"] == variant
                    and record["case_id"] == case["id"]
                    and record["valid"]
                )
    invalid_cells = {
        key: count
        for key, count in cell_counts.items()
        if count != suite["runs_per_cell"]
    }
    worst_provider_delta = min(provider_deltas, default=0.0)

    case_metrics: dict[str, Any] = {}
    for case in suite["cases"]:
        variants: dict[str, Any] = {}
        for variant in suite["variants"]:
            selected = [
                record
                for record in records
                if record["case_id"] == case["id"]
                and record["variant"] == variant
                and record["valid"]
            ]
            variants[variant] = {
                "valid_runs": len(selected),
                "mean_pass_rate": round(
                    _mean([record["pass_rate"] for record in selected]),
                    4,
                ),
                "case_successes": sum(
                    bool(record["case_success"]) for record in selected
                ),
                "agent_change_runs": sum(
                    bool(record["agent_changed_paths"]) for record in selected
                ),
                "by_provider": {
                    provider: {
                        "mean_pass_rate": round(
                            _mean(
                                [
                                    record["pass_rate"]
                                    for record in selected
                                    if record["provider"] == provider
                                ]
                            ),
                            4,
                        ),
                        "case_successes": sum(
                            bool(record["case_success"])
                            for record in selected
                            if record["provider"] == provider
                        ),
                        "agent_change_runs": sum(
                            bool(record["agent_changed_paths"])
                            for record in selected
                            if record["provider"] == provider
                        ),
                    }
                    for provider in suite["providers"]
                },
            }
        case_metrics[case["id"]] = {
            "title": case["title"],
            "dimension": case["dimension"],
            "variants": variants,
        }

    false_positive_breakdown = {
        f"{provider}/{case['id']}": sum(
            bool(record.get("false_positive"))
            for record in negative_candidate
            if record["provider"] == provider and record["case_id"] == case["id"]
        )
        for provider in suite["providers"]
        for case in suite["cases"]
        if case["dimension"] == "directive16_negative"
    }

    acceptance = {
        "three_valid_runs_per_cell": {
            "passed": not missing and not invalid_cells,
            "actual": valid_runs,
            "required": expected_runs,
            "invalid_cells": invalid_cells,
        },
        "alloy_positive_successes": {
            "passed": positive_successes >= 9,
            "actual": positive_successes,
            "required": 9,
            "possible": 12,
        },
        "directive16_negative_false_positive_changes": {
            "passed": false_positive_changes <= 1,
            "actual": false_positive_changes,
            "maximum": 1,
            "possible": 24,
        },
        "legacy_pass_rate_regression": {
            "passed": legacy_delta >= -0.05,
            "actual_delta": round(legacy_delta, 4),
            "minimum_delta": -0.05,
        },
        "overall_candidate_uplift": {
            "passed": overall_delta >= 0.10,
            "actual_delta": round(overall_delta, 4),
            "required_delta": 0.10,
            "maximum_possible_delta": round(
                maximum_possible_overall_delta,
                4,
            ),
            "attainable": maximum_possible_overall_delta >= 0.10,
        },
        "provider_consistency": {
            "passed": (providers_improve_or_tie >= 3 and worst_provider_delta >= -0.10),
            "providers_improve_or_tie": providers_improve_or_tie,
            "required_providers": 3,
            "worst_provider_delta": round(worst_provider_delta, 4),
            "minimum_provider_delta": -0.10,
        },
    }
    duration_delta = (
        by_variant["candidate"]["mean_duration_seconds"]
        / by_variant["current"]["mean_duration_seconds"]
        - 1
    )
    token_delta = (
        by_variant["candidate"]["mean_total_tokens"]
        / by_variant["current"]["mean_total_tokens"]
        - 1
    )
    failed_gates = [
        name.replace("_", " ")
        for name, gate in acceptance.items()
        if not gate["passed"]
    ]
    observations = [
        (
            f"The candidate passed {positive_successes}/12 Alloy-positive runs, "
            "meeting the gate exactly."
        ),
        (
            f"The candidate caused {false_positive_changes}/24 semantic false "
            "positives in Directive 16 negative runs; the maximum allowed was 1."
        ),
        (
            f"Overall pass rate improved by {overall_delta:+.1%}, below the "
            "required +10.0%."
        ),
        (
            f"Legacy pass rate changed by {legacy_delta:+.1%}; the new wording "
            "did not regress the existing directives."
        ),
        (
            f"Candidate runs used {duration_delta:+.1%} mean wall time and "
            f"{token_delta:+.1%} mean reported tokens."
        ),
        (
            "The planned +10.0% overall uplift gate is unattainable with the "
            f"{by_variant['current']['mean_pass_rate']:.1%} corrected baseline; "
            f"its mathematical maximum is {maximum_possible_overall_delta:.1%}."
        ),
        (
            "The candidate is not accepted because it failed: "
            + ", ".join(failed_gates)
            + "."
            if failed_gates
            else "The candidate passed every acceptance gate."
        ),
    ]
    report = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "seed": suite["seed"],
            "expected_runs": expected_runs,
            "valid_runs": valid_runs,
            "missing_runs": missing,
        },
        "variants": by_variant,
        "providers": by_provider,
        "cases": case_metrics,
        "directive16_negative_false_positive_breakdown": (false_positive_breakdown),
        "legacy": {
            "current": round(legacy_rates["current"], 4),
            "candidate": round(legacy_rates["candidate"], 4),
            "delta": round(legacy_delta, 4),
        },
        "acceptance": acceptance,
        "analysis": {"observations": observations},
        "accepted": all(item["passed"] for item in acceptance.values()),
    }
    atomic_write_json(eval_root / "combined-benchmark.json", report)
    atomic_write_text(
        eval_root / "combined-benchmark.md",
        _combined_markdown(report),
    )
    return report


def _combined_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Unslop multi-provider benchmark",
        "",
        f"- Valid runs: {report['metadata']['valid_runs']}/{report['metadata']['expected_runs']}",
        f"- Current mean pass rate: {report['variants']['current']['mean_pass_rate']:.1%}",
        f"- Candidate mean pass rate: {report['variants']['candidate']['mean_pass_rate']:.1%}",
        f"- Candidate accepted: {'yes' if report['accepted'] else 'no'}",
        "",
        "## Provider results",
        "",
        "| Provider | Current | Candidate | Delta |",
        "|---|---:|---:|---:|",
    ]
    for provider, values in report["providers"].items():
        lines.append(
            f"| {provider} | {values['current']:.1%} | "
            f"{values['candidate']:.1%} | {values['delta']:+.1%} |"
        )
    lines.extend(
        [
            "",
            "## Acceptance gates",
            "",
            "| Gate | Result | Evidence |",
            "|---|---|---|",
        ]
    )
    for name, gate in report["acceptance"].items():
        evidence = ", ".join(
            f"{key}={value}" for key, value in gate.items() if key != "passed"
        )
        lines.append(
            f"| {name.replace('_', ' ')} | "
            f"{'pass' if gate['passed'] else 'fail'} | {evidence} |"
        )
    lines.extend(["", "## Analyst observations", ""])
    lines.extend(
        f"- {observation}" for observation in report["analysis"]["observations"]
    )
    lines.extend(
        [
            "",
            "## Case results",
            "",
            "| Case | Current | Candidate | Current successes | Candidate successes |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for case_id, case in report["cases"].items():
        current = case["variants"]["current"]
        candidate = case["variants"]["candidate"]
        lines.append(
            f"| {case_id} | {current['mean_pass_rate']:.1%} | "
            f"{candidate['mean_pass_rate']:.1%} | "
            f"{current['case_successes']}/{current['valid_runs']} | "
            f"{candidate['case_successes']}/{candidate['valid_runs']} |"
        )
    return "\n".join(lines) + "\n"
