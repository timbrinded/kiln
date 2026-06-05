# Infographic Prompt Patterns

Load this reference when an infographic prompt needs examples, repair guidance,
or a stronger structure than the main skill provides. Keep the final user-facing
output concise; do not paste this whole reference into responses.

## Patterns

### Artifact Spec

Use when the output is a slide, poster, architecture map, process flow, or other
structured image.

Bad:

```text
Make an infographic about the release process.
```

Good:

```text
Create a landscape 16:9 process infographic for engineering and product
reviewers. Use the repo's design or brand reference if one exists; otherwise use
a clean technical-documentation style. Show the release path from change
proposal to production rollout with short labels, clear left-to-right flow,
crisp panel borders, and no decorative clutter.
```

Why it works: it names the deliverable, audience, source of style, subject,
layout, and constraints.

### One Main Message

Use when the source contains many facts and needs a single visual hierarchy.

Bad:

```text
Show everything from this document.
```

Good:

```text
Main message: "Requests enter through the API, jobs run asynchronously, and
results return through the dashboard."
Use supporting callouts only for components needed to explain that message.
```

Why it works: the image model gets a clear priority order instead of treating
all facts as visually equal.

### Exact Visible Text

Use when labels must be readable and accurate.

Bad:

```text
Add labels for the important parts.
```

Good:

```text
Required visible text:
- "API Service"
- "Worker Queue"
- "Database"
- "Admin Dashboard"
- "Audit Log"
- "User-visible status"
Render the labels exactly as written, with large readable sans-serif text.
```

Why it works: quoted labels reduce paraphrasing, spelling drift, and accidental
renaming.

### Verbatim Text Control

Use when the image contains project terms, acronyms, or stakeholder-facing
labels.

Bad:

```text
Add the title Login Flow and label the SSO callback.
```

Good:

```text
Required visible text:
- "Login Flow"
- "SSO Callback"
Render each quoted label exactly once, verbatim, with no extra characters,
paraphrasing, repeated words, or spelling changes. Use large sans-serif text,
strong contrast, and enough whitespace around each label.
For the tricky label, preserve the letters: S-S-O Callback.
```

Why it works: exact copy, repetition limits, typography constraints, and
spelling hints reduce the most common text-in-image failures.

### Layout Before Detail

Use when the context describes relationships, not just a topic.

Bad:

```text
Include the API, worker, database, dashboard, and audit log.
```

Good:

```text
Layout:
- Left column: "Users and admins"
- Center stage: "API Service" and "Worker Queue"
- Right column: "Database" and "External Integrations"
- Bottom strip: "Audit and review surfaces"
Use arrows only for relationships described in the source context.
```

Why it works: the model gets placement and flow instructions before it chooses
decorative composition.

### Density Budget

Use when selecting `level`.

Bad:

```text
Create a detailed but simple infographic.
```

Good:

```text
Information density: medium.
Use one headline, three sections, eight visible labels maximum, and two concise
callouts. Do not include paragraphs inside the image.
```

Why it works: the prompt resolves the contradiction between "detailed" and
"simple" with explicit limits.

### Generation Parameters

Use when returning the short parameter summary before the copy-paste prompt.

Bad:

```text
Make a high quality image.
```

Good:

```text
Suggested generation parameters:
- model: gpt-image-2
- quality: high
- size: 1536x864
Reason: landscape deck visual with several labels and a stakeholder-facing
layout.
```

Why it works: the image tool gets an explicit quality and canvas target before
composition starts, which avoids low-fidelity text and post-generation cropping.

### Prompt Handoff Versus Tool Generation

Use when deciding whether to call an image generation tool.

Prompt-only request:

```text
Write an infographic prompt for this runbook.
```

Correct behavior: return a structured prompt and parameter summary. Do not call
an image generation tool.

Generation request:

```text
Generate an actual infographic image from this ADR.
```

Correct behavior when an image generation tool is available: build the same
structured prompt, pass it to the tool, then return a concise result note with
the key parameters used.

Generation request without tool access:

```text
Create the image from this architecture doc.
```

Correct behavior when no image generation tool is available: return the
copy-paste-ready prompt and state that image generation requires an attached
image generation tool.

Why it works: prompt handoff remains portable, while explicit generation
requests get completed end to end in environments that expose an image tool.

### Uncertainty Preservation

Use for draft/proposed docs, open questions, or research.

Bad:

```text
Show the final architecture.
```

Good:

```text
Preserve source status: this is draft/proposed material.
Show unresolved items in a small "Open Questions" panel. Do not depict them as
accepted implementation decisions.
```

Why it works: the image does not overstate design maturity.

### JSON Object Brief

Use when the caller asks for `format=json` or wants a stricter copy-paste prompt.

Bad:

```json
{
  "prompt": "Make a cool detailed infographic about our architecture"
}
```

Good:

```json
{
  "style_reference": "Use the provided repo style guide if present; otherwise use a neutral technical-documentation style.",
  "deliverable": {
    "type": "infographic",
    "orientation": "landscape",
    "aspect_ratio": "16:9",
    "audience": "engineering reviewers"
  },
  "main_message": "The API validates requests before enqueueing background jobs.",
  "required_visible_text": [
    "API Service",
    "Worker Queue",
    "Database"
  ],
  "layout": [
    "landscape 16:9",
    "left-to-right flow",
    "three compact panels"
  ],
  "constraints": [
    "Use only supplied context.",
    "Keep labels legible.",
    "Do not invent implementation details."
  ]
}
```

Why it works: JSON helps make fields inspectable. It is a structure aid, not a
guarantee that the image model will obey every field.

### Negative Constraints

Use when common model tendencies would hurt the artifact.

Bad:

```text
Make it beautiful and futuristic.
```

Good:

```text
Avoid generic stock-photo treatment, glowing network backgrounds, decorative
orbs, illegible microtext, invented logos, vague technology icons, and arrows
that imply flows not present in the source.
```

Why it works: exclusions steer the model away from common cliches and false
architecture claims.

### Reference Image Invariants

Use when editing a prior image or using a screenshot, mockup, or generated
explainer as a reference.

Bad:

```text
Use this image and make the deployment section better.
```

Good:

```text
Reference images:
- Image 1: existing release-process explainer; preserve its canvas, grid,
  typography, color palette, panel borders, and header/footer structure.
- Image 2: source architecture diagram; use it only for component relationships.

Change only the deployment section copy and its two local callouts.
Keep everything else the same: layout, labels, arrows, contrast, saturation,
spacing, status badge, and component boundaries.
```

Why it works: each input has a role, and the prompt separates the allowed change
from the invariants that must not drift.

### Small Iterative Repair

Use after a generated image is close but has one concrete defect.

Bad:

```text
Try again and make it cleaner and more accurate.
```

Good:

```text
Change only the footer wording to "Pending Decision".
Keep the same 1536x864 canvas, style direction, API Service and Worker Queue
placement, arrows, panel grid, colors, and all other labels unchanged.
```

Why it works: one small edit plus a restated preserve list usually fixes drift
without causing unrelated layout or terminology changes.

## Antipatterns

### Overloaded Source Dump

Symptom: the generated image has tiny text, random hierarchy, or merged
concepts.

Avoid:

```text
Turn this whole ADR and all related docs into one infographic with every detail.
```

Repair:

```text
Use level=medium. Extract the single decision, three reasons, two tradeoffs, and
one consequence. Omit procedural history unless it is needed for the decision.
```

### Vague Style Words

Symptom: the image becomes generic marketing art.

Avoid:

```text
Make it modern, clean, sleek, premium, and futuristic.
```

Repair:

```text
Use the explicit repo style reference if one exists. If none exists, use a clean
technical-documentation style with legible sans-serif typography, structured
panels, crisp borders, high contrast, compact information density, and no
stock-photo treatment.
```

### Text-Heavy Poster

Symptom: labels are misspelled, blurry, repeated, or unreadable.

Avoid:

```text
Include the full policy explanation as text in the image.
```

Repair:

```text
Use short visible labels only. Put supporting explanation into visual grouping,
arrows, and callouts. Limit callouts to one sentence of eight words or fewer.
```

### False Certainty

Symptom: draft or proposed architecture appears final.

Avoid:

```text
Depict this as the approved final design.
```

Repair:

```text
Show this as "Proposed Architecture" or "Draft Design" when the source front
matter says proposed or draft. Use an "Open Questions" panel for unsettled
items.
```

### Component Renaming

Symptom: canonical names become generic or wrong.

Avoid:

```text
Show the backend, engine, service, and database layer.
```

Repair:

```text
Use canonical labels exactly as written in the source, for example
"API Service", "Worker Queue", "Rules Engine", and "Event Store". Keep similarly
named components distinct when the source distinguishes them.
```

### Decorative Architecture

Symptom: the image looks impressive but communicates fake topology.

Avoid:

```text
Add many connections, shields, clouds, and data streams to make the system look
sophisticated.
```

Repair:

```text
Use only source-backed relationships. Prefer fewer arrows, labeled boundaries,
and clear trust zones over decorative network effects.
```

### Aspect Ratio Mismatch

Symptom: important content is cropped or squeezed.

Avoid:

```text
Create a portrait poster but make it work as a 16:9 slide later.
```

Repair:

```text
Generate for the final canvas: landscape 16:9 for slides and horizontal
architecture maps; portrait 9:16 or 4:5 for vertical posters; square 1:1 for
compact concept maps.
```

### Missing Parameter Summary

Symptom: the prompt is strong, but the generated result has blurry labels or is
cropped into the wrong shape.

Avoid:

```text
Create a stakeholder-facing architecture explainer with readable labels.
```

Repair:

```text
Parameters: model=gpt-image-2, quality=high, size=1536x864.
Create a landscape 16:9 stakeholder-facing architecture explainer with readable
labels.
```

Dense labels, diagrams, slides, axes, legends, and footnotes should usually use
`quality=high`.

### Generating When Only A Prompt Was Requested

Symptom: the agent surprises the user by spending tool budget or creating an
artifact when they only wanted a prompt.

Avoid:

```text
The user asked for an infographic prompt, so call the image generation tool.
```

Repair:

```text
Use mode=prompt unless the user explicitly asks to generate, render, create, or
make the actual image. Return the prompt handoff without calling image tools.
```

### JSON As Magic Control

Symptom: the prompt looks rigorous but omits the actual visual brief.

Avoid:

```json
{
  "topic": "access control architecture",
  "format": "infographic",
  "quality": "high"
}
```

Repair:

```json
{
  "style_reference": "Repo style guide if provided; otherwise neutral technical-documentation style.",
  "main_message": "Request validation happens before asynchronous job execution.",
  "required_visible_text": ["API Service", "Worker Queue", "Database"],
  "layout": ["landscape 16:9", "left-to-right flow", "three compact panels"],
  "constraints": ["Use only supplied context.", "Keep labels legible."]
}
```

JSON helps when the fields are meaningful. It does not replace specificity.

## Research Basis

These patterns reflect image-prompt guidance from:

- OpenAI GPT Image Generation Models Prompting Guide:
  <https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide>
- Google Imagen prompt and image attribute guide:
  <https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/img-gen-prompt-guide>
- Microsoft Copilot Image Prompting 101:
  <https://www.microsoft.com/en-us/microsoft-copilot/for-individuals/do-more-with-ai/ai-art-prompting-guide/image-prompting-101>
