# Output Format Examples

Load this reference only when the exact response shape is needed. In prompt
mode, return a short parameter summary followed by one copy-paste-ready image
generation prompt. In generate mode, use the same prompt internally for the image
tool call and return a concise result note after generation.

## Markdown Format

Use when `format=markdown`, `format=md`, `format=sections`, or no format is
provided.

````markdown
Parameters: context=<source>, orientation=<landscape|portrait|square>, level=<lite|medium|heavy>, mode=prompt, format=markdown, model=gpt-image-2, quality=<medium|high>, size=<image-size>, style_reference=<explicit reference or inferred neutral style>

```text
Create a [orientation] [aspect ratio] infographic for [audience/use].
Suggested generation parameters:
- Model: gpt-image-2
- Quality: [medium|high]
- Size: [1536x864|1680x944|1056x1488|1024x1024|1536x1024]

Style direction:
[explicit style reference if provided, or a concise neutral technical-documentation style summary]

Main message:
[one sentence]

Required visible text:
- "[short label]"
- "[short label]"

Required visual structure:
- [layout instruction]
- [relationship or flow instruction]

Reference images, if provided:
- Image 1: [role and preservation rule]
- Image 2: [role and how it should influence the output]

Text rendering rules:
- Render quoted labels verbatim, once, with no extra characters.
- Use large readable sans-serif text with strong contrast.
- Keep labels short; no paragraphs inside the image.

Content constraints:
- Use only the facts and relationships from the supplied context.
- Preserve any draft/proposed/research uncertainty from the source.
- Do not add unstated implementation details, guarantees, or timelines.
- Keep all labels legible and avoid decorative clutter.

Source context to visualize:
[concise extracted context or inline source summary]
```
````

## JSON Format

Use when `format=json`, `format=object`, `format=schema`, or
`format=strict-json`.

Return valid JSON in the code fence: no comments, no trailing commas, and no
Markdown syntax inside string values.

````markdown
Parameters: context=<source>, orientation=<landscape|portrait|square>, level=<lite|medium|heavy>, mode=prompt, format=json, model=gpt-image-2, quality=<medium|high>, size=<image-size>, style_reference=<explicit reference or inferred neutral style>

```json
{
  "generation_parameters": {
    "model": "gpt-image-2",
    "quality": "high",
    "size": "1536x864"
  },
  "style_reference": "Explicit repo style reference if provided; otherwise neutral technical-documentation style inferred from the source.",
  "deliverable": {
    "type": "infographic",
    "orientation": "landscape",
    "aspect_ratio": "16:9",
    "audience": "engineering and product reviewers"
  },
  "style_direction": [
    "clean structured surfaces",
    "legible sans-serif typography",
    "restrained accent color chosen from the repo or source material when possible",
    "compact panels with crisp borders",
    "clear hierarchy and high contrast for labels"
  ],
  "main_message": "[one sentence]",
  "required_visible_text": [
    "[short label]",
    "[short label]"
  ],
  "required_visual_structure": [
    "[layout instruction]",
    "[relationship or flow instruction]"
  ],
  "reference_images": [
    {
      "image": "Image 1",
      "role": "[source artifact, screenshot, prior explainer, or style reference]",
      "preserve": "[layout, style, labels, or geometry to keep]",
      "change": "[specific allowed change]"
    }
  ],
  "text_rendering_rules": [
    "Render quoted labels verbatim, once, with no extra characters.",
    "Use large readable sans-serif text with strong contrast.",
    "Keep labels short; no paragraphs inside the image."
  ],
  "content_constraints": [
    "Use only the facts and relationships from the supplied context.",
    "Preserve any draft/proposed/research uncertainty from the source.",
    "Do not add unstated implementation details, guarantees, or timelines.",
    "Keep all labels legible and avoid decorative clutter."
  ],
  "source_context_to_visualize": "[concise extracted context or inline source summary]"
}
```
````

## Large Source Note

If the source is too large for a single useful image, add one sentence after the
prompt identifying what was excluded:

```markdown
Excluded from the visual prompt: <brief scope omitted because it does not fit
the requested level>.
```

## Generate Mode Result

Use when the user explicitly requested image generation and an image generation
tool was available. The agent should have already called the tool with the
generated prompt.

```markdown
Generated the infographic image.

Parameters: context=<source>, orientation=<landscape|portrait|square>, level=<lite|medium|heavy>, mode=generate, model=gpt-image-2, quality=<medium|high>, size=<image-size>, style_reference=<explicit reference or inferred neutral style>
```

If generation was requested but no image tool was available, return the normal
prompt-mode handoff and add:

```markdown
Image generation was requested, but no image generation tool is available in
this environment. Use the prompt above with an attached image generation tool.
```
