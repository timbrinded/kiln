from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT))

from eval_lib import (  # noqa: E402
    LIVE_CODESAVER_PATH,
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

    def test_codesaver_move_preserves_directives_gotchas_and_fixtures(self) -> None:
        live = self.repo_root / LIVE_CODESAVER_PATH
        historical = self.skills["current"]

        self.assertEqual(
            hash_tree(historical / "references"),
            hash_tree(live / "references"),
        )
        historical_fixtures = tree_hashes(historical / "evals" / "files")
        live_fixtures = tree_hashes(live / "evals" / "files")
        self.assertEqual(
            historical_fixtures,
            {path: live_fixtures[path] for path in historical_fixtures},
        )
        skill_text = (live / "SKILL.md").read_text()
        for directive_number in range(1, 16):
            self.assertIn(f"| {directive_number} |", skill_text)
        self.assertNotIn("| 16 |", skill_text)

    def test_codesaver_retains_original_eval_scenarios_and_routing(self) -> None:
        historical = json.loads(
            (self.skills["current"] / "evals" / "evals.json").read_text()
        )
        live = json.loads(
            (self.repo_root / LIVE_CODESAVER_PATH / "evals" / "evals.json").read_text()
        )
        historical_by_id = {case["id"]: case for case in historical["evals"]}
        live_by_id = {case["id"]: case for case in live["evals"]}

        self.assertEqual(set(historical_by_id), set(range(1, 9)))
        self.assertEqual(set(live_by_id), set(range(1, 11)))

        overrides = {
            1: {
                "prompt": "Use Codesavers to review the attached app.js for unnecessary complexity.",
                "expected_output": "A report-only Codesavers review that does not modify the working tree.",
            },
            2: {
                "prompt": "Use Codesavers with --apply to simplify the attached app.js and validate the result.",
                "expected_output": "A Codesavers report followed by explicitly authorized fixes and project validation.",
            },
            3: {
                "prompt": "Run the attached setup-layered-diff.sh with sh and an unused directory inside the evaluation workspace, enter the repository it creates, then use Codesavers with --check to review every current change relative to main, including new files.",
            },
            7: {
                "expected_output": "The generic review is not replaced by a Codesavers-only review.",
                "expectations": [
                    "The response does not present Codesavers as a complete answer to the request.",
                    "Any Codesavers pass is clearly scoped as optional or supplementary.",
                ],
            },
            8: {
                "expected_output": "A report-only Codesavers review using all relevant directives.",
                "expectations": [
                    "The Codesavers skill is used.",
                    "The report follows the canonical Summary, file findings, Recommendations order.",
                    "No edits are made without separate authorization.",
                    "The response does not apply specification-quality directives.",
                ],
            },
        }
        for case_id, historical_case in historical_by_id.items():
            expected_case = {**historical_case, **overrides.get(case_id, {})}
            self.assertEqual(live_by_id[case_id], expected_case)

        prompts = [case["prompt"] for case in live["evals"]]
        self.assertIn("Unslop this branch.", prompts)
        self.assertTrue(any("Use Codesavers" in prompt for prompt in prompts))
        self.assertTrue(any("Specsavers" in prompt for prompt in prompts))
        self.assertIn("--apply", live_by_id[2]["prompt"])
        self.assertIn("No repository file is modified.", live_by_id[1]["expectations"])
        self.assertIn("Directive #15", live_by_id[4]["expected_output"])
        self.assertIn("No Directive #15", live_by_id[5]["expected_output"])

    def test_live_skill_eval_manifests_are_well_formed(self) -> None:
        manifests = {
            "codesaver": (
                self.repo_root
                / LIVE_CODESAVER_PATH
                / "evals"
                / "evals.json",
                10,
            ),
            "specsaver": (
                self.repo_root
                / "plugins"
                / "unslop"
                / "skills"
                / "specsaver"
                / "evals"
                / "evals.json",
                18,
            ),
        }

        for skill_name, (manifest_path, expected_count) in manifests.items():
            with self.subTest(skill_name=skill_name):
                self.assertTrue(manifest_path.is_file())
                manifest = json.loads(manifest_path.read_text())
                self.assertEqual(manifest["skill_name"], skill_name)
                cases = manifest["evals"]
                self.assertEqual(len(cases), expected_count)
                ids = [case["id"] for case in cases]
                self.assertTrue(all(isinstance(case_id, int) for case_id in ids))
                self.assertEqual(len(ids), len(set(ids)))

                for case in cases:
                    self.assertTrue(
                        {
                            "id",
                            "prompt",
                            "expected_output",
                            "files",
                            "expectations",
                        }.issubset(case)
                    )
                    self.assertIsInstance(case["prompt"], str)
                    self.assertTrue(case["prompt"].strip())
                    self.assertIsInstance(case["expected_output"], str)
                    self.assertTrue(case["expected_output"].strip())
                    self.assertIsInstance(case["files"], list)
                    self.assertIsInstance(case["expectations"], list)
                    self.assertTrue(case["expectations"])
                    self.assertTrue(
                        all(
                            isinstance(expectation, str) and expectation.strip()
                            for expectation in case["expectations"]
                        )
                    )
                    skill_root = manifest_path.parents[1]
                    for fixture in case["files"]:
                        self.assertTrue((skill_root / fixture).is_file(), fixture)

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
