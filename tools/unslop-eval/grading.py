from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from eval_lib import changed_paths, tree_hashes


def _expectation(text: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"text": text, "passed": passed, "evidence": evidence}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text()
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def _validation(
    run_repo: Path,
    commands: list[list[str]],
    cargo_target: Path,
) -> tuple[bool, str]:
    evidence: list[str] = []
    success = True
    env = {
        **os.environ,
        "CARGO_TARGET_DIR": str(cargo_target),
        "CARGO_TERM_COLOR": "never",
        "NO_COLOR": "1",
    }
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=run_repo,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        success = success and completed.returncode == 0
        output = (completed.stdout + completed.stderr).strip()
        evidence.append(
            f"{' '.join(command)} exited {completed.returncode}"
            + (f": {output[-500:]}" if output else "")
        )
    return success, "\n".join(evidence)


def grade_run(
    case: dict[str, Any],
    run_repo: Path,
    initial_hashes: dict[str, str],
    skill_unchanged: bool,
    provider_ok: bool,
    cargo_target: Path,
    response: str,
    tool_calls: int,
    duration_seconds: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    final_hashes = tree_hashes(run_repo, exclude_eval=True)
    agent_changes = changed_paths(initial_hashes, final_hashes)
    validation_ok, validation_evidence = _validation(
        run_repo,
        case["validation"],
        cargo_target,
    )
    expectations = [
        _expectation(
            "The provider completed without an infrastructure error.",
            provider_ok,
            "Provider process completed."
            if provider_ok
            else "Provider process failed.",
        ),
        _expectation(
            "The protected skill snapshot was not modified.",
            skill_unchanged,
            "Skill hash is unchanged." if skill_unchanged else "Skill hash changed.",
        ),
        _expectation(
            "The fixture validation command passes.",
            validation_ok,
            validation_evidence,
        ),
    ]
    false_positive = False

    grader = case["grader"]
    if grader == "dependency_only_tests":
        manifest = _load_json(run_repo / "package.json")
        dependencies = {
            **manifest.get("dependencies", {}),
            **manifest.get("devDependencies", {}),
        }
        test_removed = not (run_repo / "slugify.test.js").exists()
        expectations.extend(
            [
                _expectation(
                    "The dependency-only slugify test is deleted.",
                    test_removed,
                    "slugify.test.js is absent."
                    if test_removed
                    else "slugify.test.js still exists.",
                ),
                _expectation(
                    "The now-unused slugify dependency is removed.",
                    "slugify" not in dependencies,
                    f"Declared dependency keys: {sorted(dependencies)}",
                ),
                _expectation(
                    "The application-owned article test remains.",
                    (run_repo / "article.test.js").exists(),
                    "article.test.js presence checked.",
                ),
            ]
        )
    elif grader == "owned_retry_integration":
        expectations.extend(
            [
                _expectation(
                    "The owned retry integration test remains.",
                    (run_repo / "retry.test.js").exists(),
                    "retry.test.js presence checked.",
                ),
                _expectation(
                    "No false-positive source or manifest change is applied.",
                    not agent_changes,
                    f"Agent-changed paths: {agent_changes}",
                ),
            ]
        )
    elif grader == "alloy_keccak_duplication":
        source = _read_text(run_repo / "src" / "lib.rs")
        manifest = _read_text(run_repo / "Cargo.toml")
        exact_api = "keccak256" in source
        manual_removed = "Keccak256" not in source and "sha3" not in source
        dependency_removed = not any(
            line.lstrip().startswith("sha3") for line in manifest.splitlines()
        )
        expectations.extend(
            [
                _expectation(
                    "The exact Alloy keccak256 API replaces the manual hash.",
                    exact_api,
                    "Searched src/lib.rs for keccak256.",
                ),
                _expectation(
                    "The local Keccak256 implementation imports are removed.",
                    manual_removed,
                    "Searched src/lib.rs for Keccak256 and sha3.",
                ),
                _expectation(
                    "The now-unused sha3 dependency is removed.",
                    dependency_removed,
                    "Checked Cargo.toml dependency declarations.",
                ),
            ]
        )
    elif grader == "alloy_address_storage":
        source = _read_text(run_repo / "src" / "lib.rs")
        manifest = _read_text(run_repo / "Cargo.toml")
        checksum_substituted = "to_checksum" in source.split("#[cfg(test)]", 1)[0]
        manifest_unchanged = (
            manifest
            == (
                Path(__file__).parent
                / "cases"
                / "alloy-address-storage"
                / "base"
                / "Cargo.toml"
            ).read_text()
        )
        false_positive = checksum_substituted or not manifest_unchanged
        expectations.extend(
            [
                _expectation(
                    "The checksum formatter is not substituted for lowercase storage semantics.",
                    not checksum_substituted,
                    "Checked production source before the test module for to_checksum.",
                ),
                _expectation(
                    "No new dependency is added for the storage formatter.",
                    manifest_unchanged,
                    "Compared Cargo.toml with the fixture manifest.",
                ),
            ]
        )
    elif grader == "workspace_only_dependency":
        source = _read_text(run_repo / "storage-key" / "src" / "lib.rs")
        member_manifest = _read_text(run_repo / "storage-key" / "Cargo.toml")
        dependency_added = "alloy" in member_manifest.lower()
        dependency_imported = "alloy" in source.lower()
        false_positive = dependency_added or dependency_imported
        expectations.extend(
            [
                _expectation(
                    "The workspace-only Alloy dependency is not added to the member.",
                    not dependency_added,
                    "Checked storage-key/Cargo.toml.",
                ),
                _expectation(
                    "The member source does not import the unavailable dependency.",
                    not dependency_imported,
                    "Checked storage-key/src/lib.rs.",
                ),
            ]
        )
    elif grader == "verbose_boolean_control":
        source = _read_text(run_repo / "feature.js")
        production_lines = [line for line in source.splitlines() if line.strip()]
        expectations.extend(
            [
                _expectation(
                    "The temporary enabled variable is removed.",
                    "let enabled" not in source,
                    "Checked feature.js for the temporary variable.",
                ),
                _expectation(
                    "The redundant boolean branch is removed.",
                    "if (" not in source and "} else {" not in source,
                    "Checked feature.js for the redundant branch.",
                ),
                _expectation(
                    "The resulting function stays concise.",
                    len(production_lines) <= 4,
                    f"Non-empty line count: {len(production_lines)}",
                ),
            ]
        )
    else:
        raise KeyError(grader)

    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 4),
        },
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": tool_calls,
            "total_steps": 0,
            "errors_encountered": 0 if provider_ok else 1,
            "output_chars": len(response),
            "transcript_chars": len(response),
        },
        "timing": {
            "executor_duration_seconds": round(duration_seconds, 3),
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": round(duration_seconds, 3),
        },
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
    }
    facts = {
        "agent_changed_paths": agent_changes,
        "provider_ok": provider_ok,
        "skill_unchanged": skill_unchanged,
        "validation_ok": validation_ok,
        "case_success": passed == total,
        "false_positive": false_positive,
    }
    return grading, facts
