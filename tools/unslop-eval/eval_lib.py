from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parent
SUITE_PATH = TOOL_ROOT / "suite.json"
# The benchmark is a historical Directive 16 experiment. Keep extracting the
# pre-rename skill from its path at the pinned baseline instead of turning the
# migration into a third benchmark variant.
HISTORICAL_SKILL_PATH = Path("plugins/unslop/skills/unslop")
LIVE_CODESAVER_PATH = Path("plugins/unslop/skills/codesaver")


@dataclass(frozen=True)
class RunSpec:
    provider: str
    variant: str
    case_id: str
    run_number: int

    @property
    def slug(self) -> str:
        return f"{self.provider}__{self.variant}__{self.case_id}__run-{self.run_number}"


def load_suite() -> dict[str, Any]:
    return json.loads(SUITE_PATH.read_text())


def repository_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=TOOL_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip()).resolve()


def local_root(repo_root: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    git_dir = Path(result.stdout.strip())
    if not git_dir.is_absolute():
        git_dir = repo_root / git_dir
    return git_dir.resolve() / "unslop-eval"


def worktree_root(repo_root: Path) -> Path:
    root = repo_root / ".unslop-eval-worktrees"
    root.mkdir(exist_ok=True)
    exclude_path = Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "info/exclude"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    if not exclude_path.is_absolute():
        exclude_path = repo_root / exclude_path
    pattern = "/.unslop-eval-worktrees/"
    existing = exclude_path.read_text() if exclude_path.exists() else ""
    lines = existing.splitlines()
    if pattern not in lines:
        separator = "" if not existing or existing.endswith("\n") else "\n"
        atomic_write_text(
            exclude_path,
            f"{existing}{separator}{pattern}\n",
        )
    return root


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def checked_remove_tree(path: Path, root: Path) -> None:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    if resolved_path == resolved_root or not resolved_path.is_relative_to(
        resolved_root
    ):
        raise ValueError(f"refusing to remove path outside evaluation root: {path}")
    if path.exists():
        shutil.rmtree(path)


def clean_worktrees(repo_root: Path) -> None:
    root = worktree_root(repo_root)
    for child in root.iterdir():
        checked_remove_tree(child, root)
    root.rmdir()


def copy_overlay(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(os.readlink(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def tree_hashes(root: Path, *, exclude_eval: bool = False) -> dict[str, str]:
    hashes: dict[str, str] = {}
    generated_directories = {
        "node_modules",
        "target",
        "__pycache__",
        ".pytest_cache",
    }
    generated_files = {
        "Cargo.lock",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
    }
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if generated_directories.intersection(relative.parts):
            continue
        if relative.name in generated_files:
            continue
        if exclude_eval and relative.parts[:1] == (".eval",):
            continue
        hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for relative, file_hash in tree_hashes(root).items():
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(file_hash.encode())
        digest.update(b"\0")
    return digest.hexdigest()


def extract_skill(repo_root: Path, baseline_ref: str, destination: Path) -> None:
    archive = subprocess.run(
        ["git", "archive", baseline_ref, HISTORICAL_SKILL_PATH.as_posix()],
        cwd=repo_root,
        check=True,
        capture_output=True,
    ).stdout
    with tarfile.open(fileobj=BytesIO(archive), mode="r:") as bundle:
        bundle.extractall(destination, filter="data")


def prepare_skill_variants(
    repo_root: Path,
    eval_root: Path,
    suite: dict[str, Any],
) -> dict[str, Path]:
    skills_root = eval_root / "skills"
    checked_remove_tree(skills_root, eval_root)
    extracted = skills_root / "extracted"
    extracted.mkdir(parents=True)
    extract_skill(repo_root, suite["baseline_ref"], extracted)
    baseline_source = extracted / HISTORICAL_SKILL_PATH

    current = skills_root / "current"
    candidate = skills_root / "candidate"
    shutil.copytree(baseline_source, current)
    shutil.copytree(baseline_source, candidate)

    patch_path = TOOL_ROOT / "candidate" / "directive-16.patch"
    subprocess.run(
        ["git", "apply", "--check", str(patch_path)],
        cwd=candidate,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "apply", str(patch_path)],
        cwd=candidate,
        check=True,
        capture_output=True,
        text=True,
    )
    shutil.rmtree(extracted)

    manifest = {
        "baseline_ref": suite["baseline_ref"],
        "current_sha256": hash_tree(current),
        "candidate_sha256": hash_tree(candidate),
        "candidate_patch_sha256": hashlib.sha256(patch_path.read_bytes()).hexdigest(),
    }
    atomic_write_json(skills_root / "manifest.json", manifest)
    return {"current": current, "candidate": candidate}


def case_by_id(suite: dict[str, Any], case_id: str) -> dict[str, Any]:
    for case in suite["cases"]:
        if case["id"] == case_id:
            return case
    raise KeyError(case_id)


def prepare_run_repository(
    repo_root: Path,
    eval_root: Path,
    suite: dict[str, Any],
    skill_path: Path,
    spec: RunSpec,
) -> tuple[Path, str, dict[str, str], str]:
    case = case_by_id(suite, spec.case_id)
    fixture = TOOL_ROOT / case["fixture"]
    mutable_root = worktree_root(repo_root)
    run_repo = mutable_root / spec.slug
    checked_remove_tree(run_repo, mutable_root)
    run_repo.mkdir(parents=True)

    copy_overlay(fixture / "base", run_repo)
    shutil.copytree(skill_path, run_repo / ".eval" / "skill")

    git_env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Unslop Eval",
        "GIT_AUTHOR_EMAIL": "unslop-eval@example.invalid",
        "GIT_COMMITTER_NAME": "Unslop Eval",
        "GIT_COMMITTER_EMAIL": "unslop-eval@example.invalid",
    }
    for command in (
        ["git", "init", "--quiet"],
        ["git", "add", "--force", "."],
        ["git", "commit", "--quiet", "-m", "baseline fixture"],
    ):
        subprocess.run(
            command, cwd=run_repo, env=git_env, check=True, capture_output=True
        )

    copy_overlay(fixture / "change", run_repo)
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=run_repo,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    untracked_paths = [path.decode() for path in untracked if path]
    if untracked_paths:
        subprocess.run(
            ["git", "add", "--intent-to-add", "--", *untracked_paths],
            cwd=run_repo,
            check=True,
            capture_output=True,
        )
    initial_patch = subprocess.run(
        ["git", "diff", "--binary", "--no-ext-diff"],
        cwd=run_repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if not initial_patch:
        raise RuntimeError(f"fixture {spec.case_id} produced no current patch")

    initial_hashes = tree_hashes(run_repo, exclude_eval=True)
    skill_hash = hash_tree(run_repo / ".eval" / "skill")
    return run_repo, initial_patch, initial_hashes, skill_hash


def reconstruct_final_repository(
    repo_root: Path,
    eval_root: Path,
    suite: dict[str, Any],
    skill_path: Path,
    spec: RunSpec,
    final_patch: Path,
) -> tuple[Path, dict[str, str], str]:
    run_repo, _, initial_hashes, skill_hash = prepare_run_repository(
        repo_root,
        eval_root,
        suite,
        skill_path,
        spec,
    )
    subprocess.run(
        ["git", "reset", "--quiet", "HEAD", "--", "."],
        cwd=run_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "restore", "--worktree", "--", "."],
        cwd=run_repo,
        check=True,
        capture_output=True,
    )

    case = case_by_id(suite, spec.case_id)
    fixture = TOOL_ROOT / case["fixture"]
    for changed in sorted((fixture / "change").rglob("*"), reverse=True):
        relative = changed.relative_to(fixture / "change")
        target = run_repo / relative
        if changed.is_file() and not (fixture / "base" / relative).exists():
            if target.exists():
                target.unlink()
        elif changed.is_dir() and target.exists():
            try:
                target.rmdir()
            except OSError:
                pass

    patch = final_patch.read_text()
    sections: list[list[str]] = []
    current: list[str] = []
    for line in patch.splitlines(keepends=True):
        if line.startswith("diff --git ") and current:
            sections.append(current)
            current = []
        current.append(line)
    if current:
        sections.append(current)

    applicable_sections: list[str] = []
    for section in sections:
        header = section[0].split()
        target = header[3].removeprefix("b/") if len(header) >= 4 else ""
        deletes_untracked_addition = (
            any(line.startswith("deleted file mode ") for line in section)
            and target
            and not (fixture / "base" / target).exists()
        )
        if not deletes_untracked_addition:
            applicable_sections.append("".join(section))
    applicable_patch = "".join(applicable_sections)

    if applicable_patch.strip():
        subprocess.run(
            ["git", "apply", "-"],
            cwd=run_repo,
            check=True,
            capture_output=True,
            text=True,
            input=applicable_patch,
        )
    return run_repo, initial_hashes, skill_hash


def build_prompt(initial_patch: str) -> str:
    return f"""Read and follow the unslop skill at `.eval/skill/SKILL.md`.
This is an explicit `--apply` request. Review only the current fixture changes,
apply evidence-backed fixes, preserve unrelated behavior, and return the
skill's report. Do not use installed skills, external web access, or expected
benchmark results. Do not modify `.eval/skill`.
Use the available file-editing tool when a fix is justified. Do not claim that
an edit or validation occurred unless its tool call succeeded.

The complete current patch is included below. Inspect the repository files and
manifest as required by the skill.

```diff
{initial_patch}
```
"""


def changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(
        path for path in set(before) | set(after) if before.get(path) != after.get(path)
    )


def run_git_diff(run_repo: Path) -> str:
    return subprocess.run(
        ["git", "diff", "--binary", "--no-ext-diff"],
        cwd=run_repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
