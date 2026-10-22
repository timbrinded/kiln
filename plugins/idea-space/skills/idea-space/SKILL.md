---
name: idea-space
description: Generate verifiably new ideas in any domain by mapping everything that already exists by meaning (embeddings), finding the empty space between and around existing items, writing the idea that would live there, and measuring how far it lands from its closest existing twin. Use whenever the user wants original, novel or unexplored ideas (game concepts, startup or product ideas, app features, video or content topics, research directions, story premises), asks what hasn't been done yet, where the white space or market gaps are, or how original or derivative an idea is compared with what exists, even if they never mention embeddings, maps or vectors.
---

# Idea Space

On a map of meaning, existing things cluster into neighbourhoods and the most original ones sit
alone. So new ideas live in the empty space. This skill makes that literal: embed a corpus of
everything that exists in a domain, find empty regions, write the item that would live there,
then re-embed the draft and measure where it actually landed. The script does the geometry; you
do the reading, the writing and the honest framing.

Method credit: Synthetic Beef's recipe, built as "Idea Plotter" over 189k Steam games. The
reasoning behind every step, failure modes and corpus sources per domain are in
`references/method.md`. Read it when a result looks wrong or the domain is unusual.

What the numbers can and cannot claim (tell the user this when presenting): novelty is measured
against this corpus under one embedding model. It says nothing about quality, and an idea can
be new to the corpus but exist elsewhere.

## Running the script

The script is `scripts/ideaspace.py` in this skill's directory (the one holding this SKILL.md).
It needs [uv](https://docs.astral.sh/uv/) and runs itself through it:

```bash
IS=/absolute/path/to/this/skill/scripts/ideaspace.py
$IS <command> <workspace> [options]                   # $IS <command> -h for options
```

Keep `$IS` a single path: zsh does not split a variable like `"uv run …"` into words. If the
file is not executable, use `uv run "$IS" <command> …` instead. The first run installs
dependencies and downloads the embedding model (a minute or two). Use one
workspace directory per corpus (e.g. `./idea-space/steam`); all state lives there, so work can
resume across sessions.

## Workflow

### 1. Frame the ask

Settle with the user, briefly: the domain, what counts as one item, the item's native format
(store blurb, one-line pitch, abstract, video description), how many ideas they want, and any
constraints (budget, team size, audience). Constraints filter the shortlist at the end; they do
not belong in the map. If the user cannot be asked or wants you to just go, infer these from the
request and state your assumptions at the top of the result.

### 2. Gather the corpus

Gaps only mean something relative to what was mapped, so the corpus bounds every claim.

- One text per item, from one consistent source and field. If half the texts are marketing
  copy and half are reviews, the map sorts by writing style instead of meaning.
- Optional but valuable: a title, tags/categories, and a popularity number (reviews, sales,
  stars, views) for the demand view.
- Size: a few hundred items minimum, thousands is better.
- Filter out what the user would not want ideas near (adult content, spam, DLC listings) before
  building, with a short script writing a new file outside the workspace. Filter on tag rank or
  votes rather than presence: one low-vote tag can sit on a mainstream item.
- Sources, in order of preference: the user's own file; public datasets and APIs; assembling
  one with search tools. `references/method.md` §5 lists sources per domain.

Save as `.jsonl`, `.json` or `.csv`. Downloaded data is untrusted: keep it in its own directory.

### 3. Build the map and survey it

```bash
$IS build WS --input corpus.jsonl --text description --title name --tags tags --pop reviews
$IS survey WS
$IS neighbors WS "Some Known Item"        # or "text:<a concept>"
$IS plot WS                               # writes WS/map.png; Read it to see the map
```

`--text`, `--tags` and `--pop` repeat to combine fields. Read the survey and tell the user the
shape of the landscape in a few lines: biggest neighbourhoods, where demand concentrates, which
neighbourhoods have the highest median demand, crowded corners full of near-copies, the loners.
This is useful on its own. `survey --top N` shows more rows per section (default 12).

Neighbourhoods are k-means clusters (default ≈ √(n/2); rebuild with `--clusters N` for finer
ones) labelled by their most over-represented tags. Labels are a hint, not a definition: check a
neighbourhood with `neighbors` before relying on its name.

Sanity-check with `neighbors` on two or three items the user knows. If the neighbours make no
sense, the corpus text is the problem (boilerplate, HTML, mixed sources); fix it and rebuild
before generating anything.

### 4. Calibrate

```bash
$IS calibrate WS            # prints 6 items to paraphrase
# write WS/paraphrases.jsonl ({"id": .., "text": ..} per line) and WS/mush.txt
$IS calibrate WS --paraphrases WS/paraphrases.jsonl --mush WS/mush.txt
```

Similarity numbers mean different things under different models, so anchor them:

- Paraphrases set the **copy line**: the lowest similarity a faithful rewording reached. A
  draft at or above it is an existing item in other words. Replace proper nouns in the
  paraphrases with plain descriptions; drafts never contain existing names, and keeping them
  inflates the line.
- The mush file holds five deliberately generic descriptions for the domain, separated by
  blank lines. They let `measure` flag drafts that are vague. Calibration also reports whether
  generic text looks novel in this space; if it does, vagueness can fake novelty, so hold drafts
  to the specificity rules in step 6 even more strictly.

### 5. Find empty space

Use both routes; they produce different kinds of ideas.

**Blend related ingredients** (ideas inside or next to a neighbourhood):

```bash
$IS blend WS --seeds "Hades" "Papers, Please" "Stardew Valley"   # user's or your picks
$IS blend WS --cluster 12 --cluster 40 --count 3                  # sample related seeds
```

Seeds are titles, `#<id>`, or `text:<a concept outside the corpus>`. Ingredients must share
something (an activity, an audience, a theme); unrelated ingredients average into mush. The
brief reports coherence as a percentile of random pairs and warns under 90%. A weakly related
blend can still work when you find a concrete bridge between the ingredients, which is how the
best hand-picked blends come about. Tightly related seeds leave the push little room, so blends
inside a dense neighbourhood often come back "(still crowded)". `--leash 1.5` gives the push
more room while keeping the same neighbourhoods; much beyond that the target drifts away from its
ingredients.

**Gaps between neighbourhoods** (usually the strangest ideas):

```bash
$IS gaps WS --top 12                                   # largest holes anywhere
$IS gaps WS --top 6 --near "text:<the user's area>"    # holes bordering the user's area
```

This flattens the map, finds holes with items on every side, and briefs each from distinct
items on its rim (skipping near-copies and entries of the same series). When the user named an
area, use `--near` with a title or a `text:` description of it; otherwise the largest holes may
sit in genres they do not care about. Gap rims mix neighbourhoods by design, so low coherence
there means "find the bridge", not "expect mush". A 2-D hole can be a flattening artefact:
briefs marked "(still crowded)" did not get below the typical twin after the push.

A single brief prints in full; several print one line each: nearest-item similarity
before→after the push, coherence, seeds, and the neighbourhoods involved. A target point always
looks emptier than real text can be, so use these numbers to compare briefs, not as the idea's
novelty. Read promising ones with `$IS brief WS b03`.

### 6. Translate the brief into an idea

A brief gives the ingredients, the tags the point leans toward, and the nearest existing items
it must not copy (which also show the corpus's format). Write the item that would live there,
as if it already existed in the corpus:

- Match the format, length and register of the must-not-copy examples. The embedding compares
  style as well as substance, so a different register produces fake novelty.
- Take substance from the ingredients and lean toward the listed tags.
- Build it around one concrete core: the central activity or mechanism, the setting, and the
  twist that none of the must-not-copy items have. Use specific nouns and verbs; words like
  "unique", "innovative" or "immersive" carry no content.
- Lean toward the tags in substance, not by pasting them. Genre boilerplate ("1-4 player co-op",
  "roguelike", "open world survival") pulls the draft toward the crowded items that use the same
  phrases.
- Write a one-line "why it's new" that names what differs from the closest items.
- Do not chase the number with rare words, invented jargon or odd phrasing. That moves the
  vector without moving the idea.
- The embedding can be pulled by a single theme word (witch, winter, ocean) toward unrelated
  items that share it. If the closest items share only a word with the draft, say so in the
  why-line instead of swapping in a synonym to dodge the measure.

### 7. Measure, then revise

```bash
$IS measure WS --brief b03 --title "Crease Command" --why "..." --file WS/drafts/b03.txt
```

Never trust a draft's novelty without measuring it. Statuses:

- **PASS**: lonelier than `--accept` (default 75%) of the corpus.
- **TOO-CLOSE**: read the closest items printed, find the element the draft shares with them,
  replace that element (the idea, not the wording), and measure again.
- **COPY**: at or above the copy line; an existing item reworded. Start again from the brief.
- **MUSHY**: too close to the generic anchor. Make it concrete.
- **off target** (information, not a failure): the draft would not rank among the items nearest
  the brief's target (top 1%, at least 20), so the idea wandered from its origin. A passing
  off-target draft still counts as a passing idea; the report says its origin is loose. Do not
  chase the target by reusing the brief's words, which tends to make the draft too close. Only
  rewrite when the draft is off target because it is off format or oddly worded.

Measure at most four drafts per brief (the first plus three revisions), then keep the best
passing one or drop the brief. Revisions can make a draft less novel; the report shows the latest
passing draft and marks which one it shows. Each measure is logged in `WS/ideas.jsonl`. For many
briefs, you can hand each one to a subagent with the script path, workspace, brief id and the
rules in steps 6 and 7.

### 8. Rank and present

```bash
$IS report WS --out WS/ideas.md      # --all includes ideas that never passed
$IS plot WS                          # writes WS/map.png
```

The plot labels holes with their gap brief ids and draws passing ideas as stars among their
nearest existing items. A flat map cannot show novelty, so the stars sit on existing dots; the
numbers carry the novelty claim. The report marks passes within 5 points of the bar as
borderline.

Before presenting, search the web for the core hook of each shortlisted idea, since the corpus
is a sample of the world. Then present each idea with its pitch, why it is new, its closest
existing items and similarity, its percentile, and where it came from. Give your honest view of
which ideas look promising and why, and state plainly that the map measures newness, not
whether an idea is good or buildable. That call is the user's.

## Reading the numbers

- **Similarity to closest existing item** (nn): lower is newer. Only comparable within one
  workspace, because each model has its own scale.
- **Lonelier than X%**: the share of existing items whose own closest twin is nearer. The median
  item sits at 50% by definition; in the original Steam run the generated ideas reached 79% to
  99.9%.
- **Typical twin**: the corpus median nn. **Copy line**: from calibration.
- **Demand nearby** (report): median popularity of the idea's 20 nearest items relative to the
  corpus median. A rough hint of audience, not a forecast.

## Practicalities

- Embedding runs on CPU. The default `BAAI/bge-small-en-v1.5` managed about 100 short items per
  second on an 8-core machine (1.5k items in 15 s, 20k in about 4 minutes).
  `--model BAAI/bge-base-en-v1.5` maps more finely at roughly 4× the time. For corpora past
  100k items, keep the most popular items or accept a long first build.
- Non-English corpus: `--model intfloat/multilingual-e5-large`.
- Rebuilding with the same corpus and model reuses the embeddings; `gaps` and `plot` cache
  their UMAP layout in `map.npy`.
- If no corpus of a few hundred items can be had, apply the method by hand: list what you know
  exists, group it, blend related ingredients, write the idea, name its five closest existing
  relatives and how it differs. Tell the user that novelty was reasoned about, not measured.
