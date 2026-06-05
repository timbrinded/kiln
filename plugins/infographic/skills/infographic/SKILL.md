---
name: infographic
description: This skill should be used when the user asks to create an infographic from repository documentation, Markdown docs, ADRs, specs, diagrams, research summaries, runbooks, or inline context. It writes copy-paste-ready image prompts by default, and if the user explicitly asks to generate, render, make, or create the actual image and an image generation tool is available, it should pass the generated prompt to that tool.
---

# Infographic Prompt Writer And Generator

Create a structured image-generation prompt from repo documentation or inline
context. Return the prompt for handoff by default. If the user explicitly asks
for an actual generated image and an image generation tool is available, call
that tool with the structured prompt after building it.

## Inputs

- `context` (required): A repo Markdown path/link, `@file:` reference, or inline
  text block. If it is a path or link, read the source before writing the prompt.
  If it is missing or unreadable, ask for it.
- `orientation` (optional): `landscape` by default. Also accept `portrait` or
  `square`.
- `level` (optional): `lite` by default. Also accept `medium` or `heavy`.
- `format` (optional): `markdown` by default. Also accept `json`.
- `mode` (optional): infer from the request. Use `prompt` by default. Use
  `generate` only when the user explicitly asks for an image to be generated,
  rendered, created, or made.
- `style_reference` (optional): a design system, brand guide, style guide,
  product screenshot, prior visual, or other repo artifact that should influence
  the visual treatment.
- `reference_images` (optional): one or more prior explainers, screenshots,
  mockups, or style references to preserve, remix, or edit. If provided,
  identify each image by index and role in the prompt.

Normalize common aliases:

- `wide`, `16:9`, `deck`, `slide` -> `landscape`
- `vertical`, `9:16`, `poster`, `mobile` -> `portrait`
- `1:1` -> `square`
- `md`, `sections`, `structured` -> `markdown`
- `object`, `schema`, `strict-json` -> `json`
- `render`, `make image`, `create image`, `actual image`, `generate image` ->
  `generate`
- `prompt only`, `handoff`, `copy-paste`, `do not generate` -> `prompt`

## Mode Selection

Default to prompt handoff. This keeps the skill useful in environments without
image tools and avoids surprising generation when the user only asked for a
brief.

Use `mode=generate` only when all of these are true:

1. The user asks for an actual generated image, not just an image prompt.
2. An image generation tool is available in the current tool set.
3. The tool can accept a text prompt, or a text prompt plus the provided
   reference images.

When `mode=generate`:

1. Build the same structured prompt that would be returned in prompt mode.
2. Include the selected `model`, `quality`, and `size` inside the prompt or tool
   call when the tool supports those parameters.
3. Pass the prompt to the image generation tool.
4. After tool completion, return a short note identifying the generated image
   result and the key parameters used. Do not include a long duplicate prompt
   unless the user asked to see it.

When `mode=prompt`, no image tool is called. Return the prompt and parameter
summary exactly as a handoff artifact.

If the user asks to generate an image but no image generation tool is available,
return the handoff prompt and say that generation requires an attached image
generation tool.

If the user explicitly asks not to generate, do not call an image generation
tool even if one is available.

## Style Handling

Use explicit style references when provided. If none are provided, inspect only
nearby, obvious repo artifacts when available, such as:

- `DESIGN.md`
- `STYLEGUIDE.md`
- `BRAND.md`
- `docs/design/`
- `docs/brand/`
- screenshots, mockups, or prior explainers mentioned by the user

If no style reference exists, use a neutral technical-documentation style:

- clean structured surfaces
- legible sans-serif typography
- restrained accent color chosen from the repo or source material when possible
- compact panels with crisp borders
- clear hierarchy and high contrast for labels
- no decorative clutter, generic stock-photo treatment, or unsupported logos

Treat style references as visual guidance only. Do not use them as evidence for
product behavior, architecture, maturity, security, privacy, timelines, or
implementation details.

## Source Handling

When `context` points to repo documentation:

1. Read the source and use its front matter status when present.
2. Treat `accepted`, `approved`, or equivalent final-status docs as
   authoritative for their stated scope.
3. Preserve `proposed`, `draft`, `experimental`, and `research` uncertainty. Do
   not make unresolved design choices look settled.
4. If the source is under `research/`, frame it as exploratory unless the prompt
   context explicitly asks for a research infographic.
5. Use canonical project terms from the source. If a glossary exists, check it
   when labels or component names are ambiguous.
6. Do not invent implementation details, production readiness, security or
   privacy guarantees, timelines, metrics, owners, or dependencies.

When `context` is inline text:

1. Use only the supplied claims unless the user explicitly asks you to inspect
   repo files.
2. Keep unknowns out of the image or label them as open questions.

## Density Levels

Use the `level` parameter to choose how much information the image should carry.

| Level | Use For | Content Budget | Layout Guidance | Quality Guidance |
| --- | --- | --- | --- | --- |
| `lite` | quick explainers, meeting recaps, social/deck visuals | 1 headline, 3-5 key points, 3-6 labels | one dominant flow or hub-and-spoke, generous spacing | `quality=medium` by default; use `high` when text accuracy matters |
| `medium` | architecture explainers, decision summaries, runbook overviews | 1 headline, 5-8 key points, 6-10 labels | 2-4 sections, clear arrows, compact callouts | `quality=high` for diagrams, slides, small labels, or stakeholder-facing output |
| `heavy` | dense technical posters, review artifacts, system maps | 1 headline, 8-12 key points, 10-18 labels | multi-panel poster, swimlanes, layered system map, or timeline | `quality=high` because dense labels and layout precision need maximum fidelity |

For `heavy`, explicitly request high quality or maximum fidelity from the image
model because small labels and dense layouts need more precision.

## Model Parameters

When returning a prompt handoff or preparing a tool call, include suggested
generation parameters unless the caller requested prompt text only:

- `model`: default to `gpt-image-2` for new image-generation workflows unless
  the caller specifies another model.
- `quality`: choose from the density table. Prefer `high` whenever the image has
  dense labels, legends, axes, footnotes, small text, or stakeholder-facing
  diagrams.
- `size`: choose for the final display canvas rather than relying on later
  cropping:
  - `landscape`: `1536x864` for deck slides, or `1680x944` for a slightly
    roomier 16:9 explainer canvas.
  - `portrait`: `1056x1488` for poster/deep-dive explainers.
  - `square`: `1024x1024` for compact concept maps.
  - `overview`: `1536x1024` when the user asks for an architecture overview or
    a wider-than-slide reasoning board.

## Prompting Rules

Write the image prompt like an artifact spec, not a vague illustration request.
For examples of good patterns, failure modes, and repairs, read
`references/prompt-patterns.md` only when the request asks for examples, the
source is dense, or the first prompt draft feels underspecified.

Include these parts in a stable order:

1. Deliverable and canvas: infographic, orientation, aspect ratio, intended
   audience.
2. Style reference: explicit source if provided; otherwise a short neutral style
   summary.
3. Main message: the one idea the viewer should understand first.
4. Required content: exact labels, components, relationships, and callouts.
5. Layout: panel structure, flow direction, placement, hierarchy, and spacing.
6. Reference image handling: name each input image by index and role when
   references are provided.
7. Text rules: quote exact in-image text, keep labels short, require verbatim,
   legible typography.
8. Constraints: no invented facts, unsupported arrows, generic stock-photo
   treatment, decorative clutter, illegible tiny text, or logos not present in
   the source/style reference.

Keep the prompt concrete and skimmable with labeled sections. Prefer short lines
over a long paragraph.

If `format=json`, write the prompt as a valid JSON object. Use strings and
arrays, no comments, no trailing commas, and no Markdown inside string values.
Keep the JSON shallow enough for a human to inspect quickly.

For text in the image:

- Put exact visible labels in quotes.
- Ask the model to render quoted labels verbatim, with no extra characters,
  duplicate text, paraphrasing, or spelling changes.
- Specify typography, size, color, and placement when label fidelity matters.
- For uncommon terms or tricky labels, repeat the exact label once and spell out
  difficult parts letter-by-letter, for example `S-S-O Callback`.
- Use title case only when it matches the desired label.
- Avoid paragraphs inside the image. Use short labels and callouts.
- For dense diagrams, ask for large readable labels and strong contrast.

For reference images and edits:

- Identify each input image by index and role, for example `Image 1: prior
  release-process explainer`, `Image 2: product screenshot`.
- State how the images interact, for example `use Image 1's layout structure
  and Image 2's visual treatment`.
- Separate what changes from what must remain invariant. Use `change only...`
  and `keep everything else the same` for surgical edits.
- Restate invariants on every follow-up iteration: canvas, layout, canonical
  labels, source status, colors, typography, and component boundaries.
- For edits to existing artifacts, explicitly preserve saturation, contrast,
  camera/viewpoint, layout, arrows, labels, surrounding objects, and brand/style
  elements unless the requested change depends on modifying them.

For diagrams and architecture flows:

- Use arrows only where the source states a relationship or data/control flow.
- Show open questions as "Open Question" or "Pending Decision" panels rather
  than implying an answer.
- Keep similarly named components distinct when the source distinguishes them.
- Preserve source-stated trust boundaries, lifecycle states, ownership, and
  failure modes without expanding them.

## Orientation Mapping

- `landscape`: 16:9, best for decks, architecture maps, horizontal flows.
- `portrait`: 9:16 or 4:5, best for poster-style summaries and vertical process
  stacks.
- `square`: 1:1, best for compact concept maps.

State both the orientation and aspect ratio in the prompt.

## Iteration Guidance

For multi-step prompt refinement, start with a clean base prompt and make one
small change per follow-up. Re-specify critical invariants each time:

- canonical component names and quoted labels
- source-backed arrows and boundaries only
- source status and open questions
- style reference or neutral style summary
- target canvas and legibility constraints

If a generated image drifts, repair the drift directly instead of expanding the
prompt broadly. Example: `restore the original API Service and Worker Queue
placement; change only the footer wording`.

## Final Checklist

Before returning a prompt, check that it:

- includes suggested `model`, `quality`, and `size` parameters
- uses exact canonical terms and quoted visible text
- preserves `draft`/`proposed`/`accepted` or equivalent status correctly
- avoids invented topology, implementation details, guarantees, and timelines
- fits the requested density and canvas without relying on later cropping
- forbids illegible microtext, generic stock-photo treatment, decorative
  technology art, and unsupported arrows

## Output Format

For `mode=prompt`, return only the generated prompt and a short parameter
summary. Do not include research notes or implementation commentary.

For `mode=generate`, call the available image generation tool with the generated
prompt. After the tool call, return only a concise result note and the key
parameters used.

For copyable `format=markdown` and `format=json` examples, read
`references/output-formats.md` only when you need the exact output shape.

If the source is too large for a single useful image, summarize the most
important theme for the requested `level` and say which parts were excluded from
the prompt.
