# lottie-animation

A Claude Code plugin for creating, refining, and verifying production-ready Lottie animations. It focuses on real player compatibility, procedural generators, seamless loops, and large-but-renderable JSON assets.

## What it does

The skill activates automatically for Lottie, Bodymovin, Skottie, dotLottie, and Lottie JSON work.

| Situation | Behavior |
|-----------|----------|
| Create a new Lottie | Inspect the target app/player, author a procedural generator, generate JSON, and verify rendered frames |
| Make a seamless loop | Close animated properties on the final visible frame and compare rendered frame `0` with `op - 1` |
| Make a large JSON asset | Separate visible render complexity from raw file-size requirements and verify the renderer survives it |
| Improve animation quality | Add named motion systems, inspect screenshots, and iterate on hierarchy, density, and motion |
| Integrate into an app | Use the app's existing Lottie player, asset paths, package manager, and build/typecheck workflow |

## Installation

### From the Kiln marketplace

In the Claude Code interactive terminal:

```
/plugin marketplace add https://github.com/timbrinded/kiln.git
/plugin install lottie-animation@kiln
```

### Test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/lottie-animation
```

### Verify installation

Ask naturally:

- "Create a Lottie animation for this app."
- "Generate a seamless Bodymovin JSON loop."
- "Make a visually impressive 30 MB Lottie."
- "Fix this lottie-web animation so it renders."
- "Make something like Luminous tide prism."

## Plugin structure

```
lottie-animation/
|-- .claude-plugin/
|   `-- plugin.json
|-- skills/
|   `-- lottie-animation/
|       |-- SKILL.md
|       `-- references/
|           `-- luminous-tide-prism.md
`-- README.md
```

## Requirements

No bundled runtime dependencies. The skill uses whatever Lottie player, package manager, and build tooling the target project already has.

## License

MIT
