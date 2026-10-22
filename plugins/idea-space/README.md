# idea-space

A Codex and Claude Code plugin for generating ideas that are measurably new. It
maps everything that already exists in a domain by meaning, finds the empty
space, writes the idea that would live there, and re-embeds the draft to measure
how far it landed from its closest existing twin.

## What it does

- Builds a map of meaning from any corpus of items (games, products, papers,
  videos, apps) using local embeddings.
- Surveys the landscape: neighbourhoods, demand, crowded corners full of
  near-copies, and the loneliest existing items.
- Calibrates the similarity scale with paraphrases (the copy line) and generic
  "mush" text, so the numbers mean the same thing under any model.
- Finds empty space two ways: blending related ingredients and pushing away from
  every existing item, or finding holes between neighbourhoods, optionally aimed
  at the user's area.
- Writes each idea in the corpus's own format, then measures it. Drafts that are
  too close to something are revised against the items they resemble.
- Ranks the passing ideas by distance from their closest existing item and plots
  them on the map.

Newness is not quality. The plugin measures how far an idea is from everything
in the corpus; whether it is any good stays with the user.

## Installation

### Codex

```bash
codex plugin marketplace add timbrinded/kiln
codex plugin add idea-space@kiln
```

Start a new Codex thread after installation so that the skill is loaded.

### Claude Code

In the Claude Code interactive terminal:

```text
/plugin marketplace add https://github.com/timbrinded/kiln.git
/plugin install idea-space@kiln
```

### Test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/idea-space
```

## Verify installation

Ask naturally:

- "Give me three genuinely new game ideas in the survival-crafting space."
- "Here's a CSV of every app in our category. Where is the white space?"
- "How original is this startup idea compared with the YC directory?"
- "Map these arXiv abstracts and find research directions nobody has taken."

## How it works

| Step | Command | What happens |
|---|---|---|
| Map | `build`, `survey`, `neighbors`, `plot` | Embed the corpus, cluster it into neighbourhoods, report the landscape |
| Calibrate | `calibrate` | Set the copy line from paraphrases and the mush anchor from generic text |
| Find space | `blend`, `gaps` | Push a blend of related seeds into empty space, or brief holes between neighbourhoods |
| Translate | (the agent) | Write the item that would live at the target, in the corpus's format |
| Measure | `measure` | Re-embed the draft; report its nearest items, percentile and status |
| Rank | `report` | Markdown report of passing ideas, closest items, origin and draft history |

`skills/idea-space/references/method.md` explains why each step exists, the
failure modes it guards against, and where to source a corpus for common
domains.

## Plugin structure

```text
idea-space/
|-- .claude-plugin/
|   `-- plugin.json
|-- .codex-plugin/
|   `-- plugin.json
|-- skills/
|   `-- idea-space/
|       |-- SKILL.md
|       |-- references/
|       |   `-- method.md
|       `-- scripts/
|           `-- ideaspace.py
`-- README.md
```

## Requirements

- [uv](https://docs.astral.sh/uv/). The script declares its dependencies inline
  (fastembed, numpy, scikit-learn, scipy, umap-learn, matplotlib) and uv
  installs them, with a Python 3.11 to 3.13 interpreter, on first run.
- A corpus of a few hundred items or more, one text per item from a consistent
  source. Tags and a popularity number are optional.
- Network access on first run to download the embedding model. Everything else
  runs locally on CPU; no API keys.

The default model, `BAAI/bge-small-en-v1.5`, embedded about 100 short items per
second on an 8-core CPU: 1,500 items in 15 seconds, 20,000 in about 4 minutes.

## Sources

The method follows Synthetic Beef's recipe for finding new ideas in embedding
space, demonstrated as "Idea Plotter" over 189,495 Steam games: plot every item
on a map of meaning, find where nothing exists yet, turn the empty places back
into ideas, and rank them by how unlike everything else they are.

## License

MIT
