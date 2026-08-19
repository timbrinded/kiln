# stacked-prs

A Codex and Claude Code plugin for designing and operating GitHub stacked pull
requests. It uses the official `github/gh-stack` CLI and covers stack selection,
layer design, creation, review, handoff, merge, cleanup, and recovery.

## What it does

- Keeps one change in one ordinary PR.
- Keeps independent changes in independent PRs.
- Designs required merge order as a linear stack with valid prefixes.
- Creates deliberate branches and submits draft or ready PRs.
- Moves lower-layer fixes to their owning branch and rebases upper layers.
- Verifies every PR and the combined diff before a stack merge.
- Recovers from conflicts without discarding branches, PRs, or unrelated work.

## Installation

### Codex

```bash
codex plugin marketplace add timbrinded/kiln
codex plugin add stacked-prs@kiln
```

Start a new Codex thread after installation so that the skill is loaded.

### Claude Code

In the Claude Code interactive terminal:

```text
/plugin marketplace add https://github.com/timbrinded/kiln.git
/plugin install stacked-prs@kiln
```

### Test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/stacked-prs
```

## Verify installation

Ask naturally:

- "Should this change be one PR, independent PRs, or a stack?"
- "Split this feature into a safe three-layer PR stack."
- "Update the API layer in this stack and rebase the layers above it."
- "Review and merge the ready prefix of this stack."
- "Recover this stack after a rebase conflict."

## Plugin structure

```text
stacked-prs/
|-- .claude-plugin/
|   `-- plugin.json
|-- .codex-plugin/
|   `-- plugin.json
|-- skills/
|   `-- stacked-prs/
|       |-- SKILL.md
|       `-- references/
|           |-- lifecycle.md
|           |-- recovery.md
|           `-- stack-design.md
`-- README.md
```

## Requirements

- GitHub CLI (`gh`) version 2.0 or later, authenticated for the target
  repository.
- The official `github/gh-stack` extension version 0.1.0 or later.
- Same-repository branches for native GitHub stacks.

With `gh-stack` 0.1.0, agents prepare and verify merges, but a human confirms
the exact PR set in the interactive merge picker. The version has no safe typed
target for a headless merge.

The plugin has no bundled runtime dependencies and does not install or upgrade
the CLI extension without permission.

## Sources

Command behavior follows the official
[`github/gh-stack`](https://github.com/github/gh-stack) documentation. The skill
keeps command flags secondary to `gh stack <command> --help`, which reflects the
installed version.

## License

MIT
