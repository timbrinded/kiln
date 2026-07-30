from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT))

from eval_lib import (  # noqa: E402
    RunSpec,
    atomic_write_text,
    build_prompt,
    checked_remove_tree,
    clean_worktrees,
    hash_tree,
    load_suite,
    local_root,
    prepare_run_repository,
    prepare_skill_variants,
    reconstruct_final_repository,
    repository_root,
    tree_hashes,
    worktree_root,
)
from grading import grade_run  # noqa: E402
from providers import provider_command  # noqa: E402
from run import _provider_queues  # noqa: E402


class HarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.suite = load_suite()
        cls.repo_root = repository_root()
        cls.eval_root = local_root(cls.repo_root)
        cls.eval_root.mkdir(parents=True, exist_ok=True)
        cls.skills = prepare_skill_variants(
            cls.repo_root,
            cls.eval_root,
            cls.suite,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        clean_worktrees(cls.repo_root)

    def test_candidate_is_separate_and_adds_directive_16(self) -> None:
        current = (self.skills["current"] / "SKILL.md").read_text()
        candidate = (self.skills["candidate"] / "SKILL.md").read_text()

        self.assertNotEqual(
            hash_tree(self.skills["current"]), hash_tree(self.skills["candidate"])
        )
        self.assertNotIn("Use existing APIs before hand-rolling", current)
        self.assertIn("Use existing APIs before hand-rolling", candidate)
        self.assertIn(
            "Directive #16: Use Existing APIs Before Hand-Rolling",
            (
                self.skills["candidate"] / "references" / "code-quality-directives.md"
            ).read_text(),
        )

    def test_prompt_embeds_skill_usage_without_grader_answers(self) -> None:
        prompt = build_prompt("diff --git a/a.js b/a.js\n+sloppy\n")

        self.assertIn("Read and follow the unslop skill", prompt)
        self.assertIn("explicit `--apply` request", prompt)
        self.assertIn("Do not use installed skills", prompt)
        self.assertNotIn("Directive #16", prompt)
        self.assertNotIn("keccak256", prompt)

    def test_provider_commands_keep_external_context_disabled(self) -> None:
        repo = self.repo_root
        prompt = "test prompt"
        commands = {
            provider: provider_command(
                provider,
                repo,
                prompt,
                config,
            )[0]
            for provider, config in self.suite["providers"].items()
        }

        self.assertIn("--ignore-user-config", commands["codex"])
        self.assertIn("--ignore-rules", commands["codex"])
        self.assertIn("--safe-mode", commands["claude"])
        self.assertIn("--disable-slash-commands", commands["claude"])
        self.assertIn('{"mcpServers":{}}', commands["claude"])
        self.assertIn("--no-custom-instructions", commands["copilot"])
        self.assertIn("--disable-builtin-mcps", commands["copilot"])
        self.assertIn("--deny-tool=shell", commands["copilot"])
        self.assertIn("--disable-web-search", commands["grok"])
        self.assertIn("--no-memory", commands["grok"])
        self.assertIn("--no-subagents", commands["grok"])
        self.assertIn("workspace", commands["grok"])
        self.assertIn("Execute,WebSearch,WebFetch", commands["grok"])

    def test_scheduler_uses_one_queue_per_provider(self) -> None:
        specs = [
            RunSpec("codex", "current", "one", 1),
            RunSpec("grok", "current", "one", 1),
            RunSpec("codex", "candidate", "two", 1),
            RunSpec("claude", "current", "one", 1),
        ]

        queues = _provider_queues(specs)

        self.assertEqual(set(queues), {"codex", "grok", "claude"})
        self.assertEqual(
            [spec.variant for spec in queues["codex"]],
            ["current", "candidate"],
        )
        self.assertTrue(
            all(
                spec.provider == provider
                for provider, provider_specs in queues.items()
                for spec in provider_specs
            )
        )

    def test_dependency_fixture_grader_detects_and_accepts_cleanup(self) -> None:
        case = next(
            case
            for case in self.suite["cases"]
            if case["id"] == "dependency-only-tests"
        )
        spec = RunSpec("fixture-test", "current", case["id"], 1)
        run_repo, _, initial_hashes, skill_hash = prepare_run_repository(
            self.repo_root,
            self.eval_root,
            self.suite,
            self.skills["current"],
            spec,
        )

        before, _ = grade_run(
            case,
            run_repo,
            initial_hashes,
            hash_tree(run_repo / ".eval" / "skill") == skill_hash,
            True,
            self.eval_root / "cargo-target",
            "",
            0,
            0.0,
        )
        self.assertLess(before["summary"]["pass_rate"], 1.0)

        (run_repo / "slugify.test.js").unlink()
        manifest = json.loads((run_repo / "package.json").read_text())
        manifest.pop("dependencies")
        (run_repo / "package.json").write_text(json.dumps(manifest, indent=2) + "\n")
        after, facts = grade_run(
            case,
            run_repo,
            initial_hashes,
            hash_tree(run_repo / ".eval" / "skill") == skill_hash,
            True,
            self.eval_root / "cargo-target",
            "",
            0,
            0.0,
        )

        self.assertEqual(after["summary"]["pass_rate"], 1.0)
        self.assertEqual(
            facts["agent_changed_paths"],
            ["package.json", "slugify.test.js"],
        )

    def test_owned_retry_fixture_rewards_no_change(self) -> None:
        case = next(
            case
            for case in self.suite["cases"]
            if case["id"] == "owned-retry-integration"
        )
        spec = RunSpec("fixture-test", "current", case["id"], 1)
        run_repo, _, initial_hashes, skill_hash = prepare_run_repository(
            self.repo_root,
            self.eval_root,
            self.suite,
            self.skills["current"],
            spec,
        )

        grading, facts = grade_run(
            case,
            run_repo,
            initial_hashes,
            hash_tree(run_repo / ".eval" / "skill") == skill_hash,
            True,
            self.eval_root / "cargo-target",
            "",
            0,
            0.0,
        )

        self.assertEqual(grading["summary"]["pass_rate"], 1.0)
        self.assertEqual(facts["agent_changed_paths"], [])

    def test_generated_build_artifacts_do_not_count_as_agent_changes(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.eval_root) as temporary:
            root = Path(temporary)
            (root / "src").mkdir()
            (root / "src" / "lib.rs").write_text("pub fn owned() {}\n")
            (root / "target" / "debug").mkdir(parents=True)
            (root / "target" / "debug" / "artifact").write_text("generated")
            (root / "Cargo.lock").write_text("generated")

            hashes = tree_hashes(root)

        self.assertEqual(set(hashes), {"src/lib.rs"})

    def test_regrade_reconstructs_deleted_untracked_addition(self) -> None:
        spec = RunSpec(
            "fixture-test",
            "current",
            "dependency-only-tests",
            99,
        )
        with tempfile.TemporaryDirectory(dir=self.eval_root) as temporary:
            patch = Path(temporary) / "final.diff"
            atomic_write_text(
                patch,
                (
                    "diff --git a/slugify.test.js b/slugify.test.js\n"
                    "deleted file mode 100644\n"
                    "index e69de29..0000000\n"
                ),
            )
            run_repo, _, _ = reconstruct_final_repository(
                self.repo_root,
                self.eval_root,
                self.suite,
                self.skills["current"],
                spec,
                patch,
            )

            self.assertFalse((run_repo / "slugify.test.js").exists())
            checked_remove_tree(run_repo, worktree_root(self.repo_root))

    def test_address_negative_allows_semantics_preserving_lower_hex(self) -> None:
        case = next(
            case
            for case in self.suite["cases"]
            if case["id"] == "alloy-address-storage"
        )
        spec = RunSpec("fixture-test", "candidate", case["id"], 1)
        run_repo, _, initial_hashes, skill_hash = prepare_run_repository(
            self.repo_root,
            self.eval_root,
            self.suite,
            self.skills["candidate"],
            spec,
        )
        source_path = run_repo / "src" / "lib.rs"
        source = source_path.read_text()
        start = source.index("pub fn address_storage_key")
        test_module = source.index("#[cfg(test)]")
        source_path.write_text(
            source[:start]
            + (
                "pub fn address_storage_key(address: Address) -> String {\n"
                '    format!("{address:x}")\n'
                "}\n\n"
            )
            + source[test_module:]
        )

        grading, facts = grade_run(
            case,
            run_repo,
            initial_hashes,
            hash_tree(run_repo / ".eval" / "skill") == skill_hash,
            True,
            self.eval_root / "cargo-target",
            "",
            0,
            0.0,
        )

        self.assertEqual(grading["summary"]["pass_rate"], 1.0)
        self.assertFalse(facts["false_positive"])
        checked_remove_tree(run_repo, worktree_root(self.repo_root))


if __name__ == "__main__":
    unittest.main()
