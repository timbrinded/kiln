# teach-me

A Claude Code plugin for tutoring through code, exercises, framework concepts, and debugging. It shifts Claude toward hints, guided questions, mental models, and small checkpoints instead of immediately editing files or handing over complete solutions.

## What it does

| Situation | Behavior |
|-----------|----------|
| Learning a language or framework | Explains the core concept, then gives a small next step |
| Working through an exercise or kata | Reads local docs, tests, and starter code before giving hints |
| Debugging unfamiliar code | Uses the error message and project context to teach the failure mode |
| Asking for review | Explains what is wrong and why before suggesting changes |
| Getting stuck repeatedly | Progressively reveals examples, pseudocode, or a fuller solution only as needed |

---

## Installation

### From the Kiln marketplace

In the Claude Code interactive terminal:

```
/plugin marketplace add https://github.com/timbrinded/kiln.git
/plugin install teach-me@kiln
```

### Test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/teach-me
```

### Verify installation

The `teach-me` skill activates automatically when relevant. Ask naturally:

- "Teach me this React pattern. I want hints, not a patch."
- "Walk me through why this test is failing without fixing it for me."
- "Help me learn Go interfaces on this exercise."
- "Tutor me through this bug. Ask guiding questions and don't edit my code."

---

## Usage

The skill follows a teaching ladder:

1. State the core concept or constraint.
2. Point to the most relevant local artifact.
3. Give one concrete hint or checkpoint.
4. Show a minimal isolated example when useful.
5. Offer pseudocode or a partial outline if still needed.
6. Give a full solution only when explicitly requested.

For exercise repositories, it starts from files such as `README.md`, `HELP.md`, `HINTS.md`, the test file, and the starter implementation so the explanation stays grounded in the task.

---

## Plugin structure

```
teach-me/
|-- .claude-plugin/
|   `-- plugin.json          # Plugin manifest
|-- skills/
|   `-- teach-me/
|       `-- SKILL.md         # Tutoring behavior and teaching ladder
`-- README.md
```

## Requirements

None. Pure knowledge plugin with no external dependencies, API keys, or build steps.

## License

MIT
