# infographic

A Claude Code plugin for writing copy-paste-ready image generation prompts from repository documentation. It turns Markdown docs, ADRs, specs, diagrams, research summaries, runbooks, or inline context into structured visual briefs, using repo style references when available and a neutral technical-documentation style when they are not. If the user explicitly asks for an actual generated image and an image generation tool is attached, the skill uses the generated prompt with that tool.

## What it does

| Situation | Behavior |
|-----------|----------|
| Architecture docs or ADRs | Extracts the main visual message, canonical labels, relationships, and source status |
| Draft or proposed material | Preserves uncertainty instead of making unresolved decisions look settled |
| Dense technical sources | Selects an appropriate information density and canvas size |
| Repos without style docs | Uses a neutral technical-documentation style instead of assuming a brand guide exists |
| Reference images | Names each image by role and separates allowed changes from invariants |
| Prompt handoff | Returns a parameter summary plus a copy-paste-ready prompt |
| Explicit image generation | Calls an attached image generation tool when the user asks for the actual image |

---

## Installation

### From the Kiln marketplace

In the Claude Code interactive terminal:

```
/plugin marketplace add https://github.com/timbrinded/kiln.git
/plugin install infographic@kiln
```

### Test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/infographic
```

### Verify installation

The `infographic` skill activates automatically when relevant. Ask naturally:

- "Generate an infographic prompt from @docs/architecture.md."
- "Generate an actual infographic image from @docs/architecture.md."
- "Turn this ADR into a landscape design-system infographic prompt."
- "Make a heavy 16:9 architecture visual prompt from this spec."
- "Create a generic repo-docs infographic prompt from this runbook."
- "Use this screenshot as a reference image and preserve the layout."

---

## Usage

The skill accepts:

- `context`: a repo Markdown path/link, `@file:` reference, or inline text block
- `orientation`: `landscape`, `portrait`, or `square`
- `level`: `lite`, `medium`, or `heavy`
- `format`: `markdown` or `json`
- `mode`: inferred as `prompt` by default, or `generate` when the user asks for the actual image
- `style_reference`: optional design system, brand guide, screenshot, or prior visual
- `reference_images`: optional prior explainers, screenshots, mockups, or style references

It returns only the generated prompt and a short parameter summary in prompt mode. In generate mode, it passes the generated prompt to an attached image generation tool, then returns a concise result note with the key parameters used. If no image tool is available, it falls back to the prompt handoff.

---

## Plugin structure

```
infographic/
|-- .claude-plugin/
|   `-- plugin.json
|-- skills/
|   `-- infographic/
|       |-- SKILL.md
|       `-- references/
|           |-- output-formats.md
|           `-- prompt-patterns.md
`-- README.md
```

## Requirements

No build dependencies. Actual image generation requires an attached image generation tool; otherwise the plugin works as a prompt-handoff skill.

## License

MIT
