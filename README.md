# Kiln

**Raw code refined into polished design.**

![Kiln](kiln.png)

Kiln is a marketplace of Codex and Claude Code plugins for code quality and
intelligent tooling. Design plugins encode platform-specific guidelines as
machine-enforceable rules. Performance plugins distill expert optimization
knowledge into actionable guidance. Developer workflow plugins make complex
repository operations safer and repeatable. Learning plugins guide users
through concepts, exercises, and debugging with a tutoring-first style.

---

## Available Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [swift-design](./plugins/swift-design/) | Design | 40 HIG rules for SwiftUI — letter grading, visual review, accessibility checks, modern API enforcement |
| [ui-refactor](./plugins/ui-refactor/) | Design | Refactoring UI principles — review screenshots, CSS, and Tailwind for hierarchy, spacing, typography, color, depth, and polish |
| [performance-optimization](./plugins/performance-optimization/) | Performance | Abseil-derived optimization guidance — measurement methodology, cross-language patterns for C++, Rust, and TypeScript |
| [unslop](./plugins/unslop/) | Code quality | Post-generation cleanup for avoidable state, defensive code, verbosity, and complexity |
| [teach-me](./plugins/teach-me/) | Education | Tutoring mode for hints, guided questions, mental models, and learning from local project context |
| [infographic](./plugins/infographic/) | Design | Image-generation prompt writer for repo docs, with optional tool-backed image generation when explicitly requested |
| [lottie-animation](./plugins/lottie-animation/) | Design | Lottie authoring workflow for renderable Bodymovin JSON, seamless loops, and large-but-stable animation assets |
| [stacked-prs](./plugins/stacked-prs/) | Developer tools | Design and operate safe GitHub stacked PR workflows from decomposition through merge and recovery |

---

## Installation

### Codex

Add the Git marketplace:

```bash
codex plugin marketplace add timbrinded/kiln
```

Install a plugin:

```bash
codex plugin add swift-design@kiln
codex plugin add ui-refactor@kiln
codex plugin add performance-optimization@kiln
codex plugin add unslop@kiln
codex plugin add teach-me@kiln
codex plugin add infographic@kiln
codex plugin add lottie-animation@kiln
codex plugin add stacked-prs@kiln
```

For a local clone, replace the marketplace command with:

```bash
codex plugin marketplace add ./path/to/kiln
```

Start a new Codex thread after installation so that the new skills are loaded.

### Claude Code

Add the Kiln marketplace in the Claude Code interactive terminal:

```
/plugin marketplace add https://github.com/timbrinded/kiln.git
```

Browse available plugins:

```
/plugin
```

Navigate to the **Discover** tab, select a plugin, and choose a scope (User, Project, or Local).

Or install directly:

```
/plugin install swift-design@kiln
/plugin install ui-refactor@kiln
/plugin install performance-optimization@kiln
/plugin install unslop@kiln
/plugin install teach-me@kiln
/plugin install infographic@kiln
/plugin install lottie-animation@kiln
/plugin install stacked-prs@kiln
```

### Alternative: test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/swift-design
claude --plugin-dir /path/to/kiln/plugins/ui-refactor
claude --plugin-dir /path/to/kiln/plugins/performance-optimization
claude --plugin-dir /path/to/kiln/plugins/unslop
claude --plugin-dir /path/to/kiln/plugins/teach-me
claude --plugin-dir /path/to/kiln/plugins/infographic
claude --plugin-dir /path/to/kiln/plugins/lottie-animation
claude --plugin-dir /path/to/kiln/plugins/stacked-prs
```

### Alternative: local marketplace

If you've cloned the repo locally:

```
/plugin marketplace add ./path/to/kiln
```

---

## Adding a New Plugin

Each plugin lives in `plugins/<name>/` as a self-contained Codex and Claude Code plugin:

```
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json          # Claude Code manifest
├── .codex-plugin/
│   └── plugin.json          # Codex manifest and interface metadata
├── agents/                  # Claude Code review agents, when needed
├── commands/                # Claude Code slash commands, when needed
├── skills/                  # Shared skills with progressive disclosure
│   └── <name>/
│       ├── SKILL.md
│       └── references/
└── README.md
```

Register it in both `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` at the repo root. A Codex marketplace entry has this form:

```json
{
  "name": "<name>",
  "source": {
    "source": "local",
    "path": "./plugins/<name>"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Design"
}
```

---

## License

MIT
