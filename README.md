# Kiln

**Raw code refined into polished design.**

![Kiln](kiln.png)

Kiln is a marketplace of Claude Code plugins for code quality. Design plugins encode platform-specific guidelines as machine-enforceable rules. Performance plugins distill expert optimization knowledge into actionable guidance.

---

## Available Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [swift-design](./plugins/swift-design/) | Design | 40 HIG rules for SwiftUI — letter grading, visual review, accessibility checks, modern API enforcement |
| [ui-refactor](./plugins/ui-refactor/) | Design | Refactoring UI principles — review screenshots, CSS, and Tailwind for hierarchy, spacing, typography, color, depth, and polish |
| [performance-optimization](./plugins/performance-optimization/) | Performance | Abseil-derived optimization guidance — measurement methodology, cross-language patterns for C++, Rust, and TypeScript |

---

## Installation

### 1. Add the Kiln marketplace

In the Claude Code interactive terminal:

```
/plugin marketplace add https://github.com/timbrinded/kiln.git
```

### 2. Install a plugin

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
```

### Alternative: test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/swift-design
claude --plugin-dir /path/to/kiln/plugins/ui-refactor
claude --plugin-dir /path/to/kiln/plugins/performance-optimization
```

### Alternative: local marketplace

If you've cloned the repo locally:

```
/plugin marketplace add ./path/to/kiln
```

---

## Adding a New Plugin

Each plugin lives in `plugins/<name>/` as a self-contained Claude Code plugin:

```
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, description)
├── agents/                  # Autonomous review agents
├── commands/                # Slash commands (/review, /generate, etc.)
├── skills/                  # Skills with progressive disclosure
│   └── <name>/
│       ├── SKILL.md
│       └── references/
└── README.md
```

Then register it in `.claude-plugin/marketplace.json` at the repo root:

```json
{
  "name": "<name>",
  "source": "./plugins/<name>",
  "description": "...",
  "version": "0.1.0",
  "author": { "name": "timbo" },
  "category": "design",
  "license": "MIT",
  "keywords": []
}
```

---

## License

MIT
