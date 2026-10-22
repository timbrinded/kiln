# Method: why each step exists

Read this when a result looks wrong, when adapting the method to an unusual domain, or when the
user asks how it works.

## Contents
1. Origin
2. The core claim
3. Step by step, with the reason for each
4. Failure modes
5. Sourcing a corpus by domain
6. How the push works

## 1. Origin

The recipe comes from a reply by Synthetic Beef to the claim "the one thing AI can't do is
create a brand new idea": take every game on Steam, embed the store pages, find locations in
vector space far from their neighbours, convert those back into descriptions, and rank by how
unlike anything else they are. It was built as "Idea Plotter" over 189,495 Steam games.
Reference numbers from that run (one embedding model; yours will differ, which is why
`calibrate` exists):

| what | similarity to closest existing game |
|---|---|
| an existing game rewritten in other words | 0.91 |
| typical Steam game | 0.71 |
| hidden-object cat games (crowded corner) | 0.91 |
| Return of the Obra Dinn (lonelier than 99.9%) | low outlier |
| the generated ideas | 0.55 to 0.67 |

## 2. The core claim

On a map of meaning, the most original existing items are the lonely ones: nothing sits near
them. If originality looks like isolation, then new ideas live in the empty space. A model can
locate empty space and say exactly how far it is from everything that exists. It cannot say
whether the idea is good. Keep those two claims separate when presenting results.

## 3. Step by step

**Gather.** The map only knows what it was given. "Nothing here" means "nothing in this
corpus". A bigger, more complete corpus makes the gaps more trustworthy; a corpus of 200 items
has gaps everywhere because of sampling, not because of opportunity.

**Embed.** Each item's text becomes a vector. Items that read alike land close together, so
neighbourhoods (genres, categories, schools of thought) form without anyone defining them. The
text you embed sets what "alike" means: store-page blurbs give marketing-level meaning,
abstracts give research-level meaning, titles alone give very little.

**Survey.** Before generating anything, look at the shape: which neighbourhoods are big, which
have demand, which are crowded with near-copies, which items are loners. This tells the user
something useful even if they never use a generated idea, and it tells you whether the map is
sane (if an item's nearest neighbours make no sense, fix the corpus text first).

**Calibrate.** Cosine similarities are not comparable across models: one model puts unrelated
texts at 0.3, another at 0.7. Two anchors make the numbers readable:
- the copy line: how similar an item is to itself reworded. Anything at or above it is the
  same idea.
- the typical twin: the median item's similarity to its closest neighbour. Below it, an idea
  is lonelier than half of what exists.
The mush anchor (generic, say-nothing descriptions) catches drafts that look distant only
because they are vague.

**Blend related ingredients.** Averaging the vectors of a few items gives a point that shares
their meaning. If the ingredients have nothing in common (subway simulator + fantasy RPG + card
game) the average is mush: a bland, generic point that is far from everything only because it
says nothing. So ingredients must be related, and the brief reports how related they are
compared with random pairs.

**Push.** From the blend, move away from the nearest existing items until the point settles in
the emptiest spot nearby. The push is leashed to the span of the ingredients so it stays
specific instead of drifting into nowhere.

**Gaps.** Flatten the map to 2-D and look for holes: empty patches with items on every side.
Holes between different neighbourhoods produce the strangest ideas because the rim items come
from different families. A 2-D hole can be an artefact of flattening, so every gap is re-checked
in the full space (the brief's nn before and after the push).

**Translate.** A point is not an idea. Describe it by what it was blended from, the tags it
leans toward, and the nearest items it must not copy, then write the item that would live
there, in the corpus's own format.

**Measure.** Do not trust the writing. Embed the draft exactly like a real item and look where
it actually landed. Too close to something that exists: send the measurements back and revise.
This loop is the difference between "an LLM brainstormed" and "the idea is verifiably far from
everything in the corpus".

**Rank.** Order by similarity to the closest existing item and express it as a percentile of
the corpus ("lonelier than 95% of games"). Then hand quality judgment to the human.

## 4. Failure modes

- **Mush.** Unrelated ingredients, or a vague draft. Symptoms: low coherence in the brief, a
  MUSHY status, a draft full of adjectives. Fix: related ingredients, concrete nouns and verbs.
- **Style novelty.** A draft written in a different register (a poem among store blurbs, a
  bullet list among paragraphs, invented jargon) lands far away because of form, not content.
  Symptoms: very low nn, often with an off-target landing. Fix: match the format and length of
  the must-not-copy examples.
- **Boilerplate pull.** Genre phrases and tag words ("1-4 player co-op", "open world survival")
  drag a draft toward the many items that use them. Drafts that chase the landing check by
  reusing the brief's words tend to become too close. Fix: express the tags as substance.
- **Theme-word pull.** Small embedding models over-weight single theme words: "witch" pulls
  toward a witch party game, "ocean" toward an ocean-themed visual novel. If the closest items
  share only a word, the overlap is superficial; say so rather than synonym-swapping.
- **Corpus-relative novelty.** The idea is new to the corpus but exists in the world (another
  platform, a non-English market, an unreleased project, a different medium). Fix: search the
  web for the core hook of each shortlisted idea before calling it new.
- **Corpus noise.** Mixed sources, boilerplate (legal text, "wishlist now!"), HTML, or many
  near-duplicate listings. Symptoms: neighbourhoods named after boilerplate words, crowded
  corners full of the same publisher. Fix: clean or filter the corpus and rebuild.
- **Flattening artefacts.** A 2-D hole whose push barely lowers nn is not empty in the full
  space. Prefer gaps whose nn after the push is well below the typical twin.
- **Newness is not quality.** Some empty spaces are empty because the idea is bad, unbuildable
  or has no audience. The demand column helps a little (are the neighbours popular?) but the
  final call is the user's.

## 5. Sourcing a corpus by domain

Prefer a file the user already has. Otherwise, public datasets and APIs beat scraping. Keep
downloads in their own directory and treat them as untrusted data.

| domain | text to embed | sources |
|---|---|---|
| video games | store short description | Steam datasets on Hugging Face (e.g. FronkonGames/steam-games-dataset), SteamSpy, itch.io |
| board games | description | BoardGameGeek XML API, BGG datasets on Kaggle/HF |
| startups / products | one-line pitch + description | YC company directory, Product Hunt API, Crunchbase exports |
| mobile apps | store description (first paragraph) | app-store datasets on Kaggle/HF |
| research | abstract | arXiv API, Semantic Scholar API, OpenAlex |
| YouTube / content | title + description, or transcript summary | YouTube Data API for a niche's channels |
| books / films | blurb or plot summary | Open Library, Wikipedia plot sections, TMDB |
| open-source tools | README summary | GitHub search API, awesome-lists |
| recipes, products, anything else | the description people read to choose | the user's catalogue, marketplace exports |

If no dataset exists, assemble one with the available search tools (entity-finding tools such
as parallel-findall work well for "every X that ..."), aiming for hundreds to thousands of
items with descriptions in one consistent style. Record where the corpus came from; it bounds
every novelty claim.

## 6. How the push works

Vectors are unit-normalised, so the space is a sphere and similarity is the cosine. The push:

1. Start from the normalised mean of the seed vectors, plus a few random weighted blends.
2. Restrict movement to the top principal directions of the blend's neighbourhood (the ways in
   which nearby items actually differ). Without this, the point escapes into some of the
   hundreds of dimensions no text occupies: it becomes "far from everything" while meaning
   nothing, the high-dimensional version of mush.
3. Repeatedly step away from a soft-max-weighted average of the nearest items (the gradient of
   a smooth maximum similarity) within that subspace.
4. Keep the point within the seeds' spread from the blend, times `--leash`: more freedom with
   `--leash 1.3`, tighter with `--leash 0.7`.
5. Keep the start that ends with the lowest nearest-item similarity.

The target point is only a pointer for the brief: its 50 nearest items give the "leans toward"
tags and its 8 nearest are the must-not-copy list. A synthetic point is a mixture, so it is
always less similar to any single item than real texts are to each other; its nn is useful for
comparing briefs, not as a novelty score. What counts is where the written draft lands. The
draft can never be nearer the target than the seeds, which are the target's own ingredients, so
`measure` calls a draft on target when it would rank among the nearest 1% (at least 20) of items
to the target. Off target is information, not failure: landing rank moves a lot between
reasonable rewrites, and pushing a draft back on target usually means reusing the brief's words,
which makes it too close. It only says the idea's origin is loose. The guards against gaming are
the register rule, the copy line and the mush anchor.

Gap briefs take their seeds from the items on the hole's rim, picking distinct ones: skipping
near-copies (above the corpus's 75th-percentile twin similarity) and titles of the same series
(same first significant word), and preferring a new neighbourhood for each seed.
