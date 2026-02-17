# Kiln

**Raw code refined into polished design.**

Kiln is a marketplace of Claude Code plugins for front-end design excellence. Each plugin encodes platform-specific design guidelines as machine-enforceable rules — catching the design mistakes that AI-generated UI consistently gets wrong.

---

## Available Plugins

| Plugin | Platform | Description |
|--------|----------|-------------|
| [swift-design](./plugins/swift-design/) | iOS / SwiftUI | 40 HIG rules, letter grading, visual review, accessibility checks, modern API enforcement |

---

## Installation

### 1. Clone the marketplace

```bash
git clone https://github.com/timbrinded/kiln.git ~/.claude/plugins/kiln
```

### 2. Add a plugin to Claude Code settings

Point Claude Code at the specific plugin directory in `~/.claude/settings.json`:

```json
{
  "plugins": [
    "~/.claude/plugins/kiln/plugins/swift-design"
  ]
}
```

### 3. Test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/swift-design
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
