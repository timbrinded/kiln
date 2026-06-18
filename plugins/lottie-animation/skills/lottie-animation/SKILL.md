---
name: lottie-animation
description: This skill should be used when the user asks to "create a Lottie", "generate a Lottie animation", "make a Bodymovin JSON", "fix a Lottie", "make a seamless loop", "make a large Lottie", "make a 30 MB Lottie", or mentions lottie-web, Bodymovin, Skottie, dotLottie, .lottie, or Lottie JSON.
---

# Lottie Animation Authoring

Create production-ready Lottie animations as renderable Bodymovin JSON, not just syntactically valid JSON. Prioritize the user's target player, visible motion quality, loop correctness, and runtime stability.

## Target Surface First

Before authoring or editing an animation:

1. Inspect the target app or viewer.
2. Read the dependency manifest to identify the package manager and Lottie player.
3. Locate the actual asset path, route, component, and fetch behavior.
4. Use the existing player when one exists.
5. Create a standalone viewer only when no target app or viewer is present.

When no target app exists, read `references/standalone-player.md` and use the
official standalone player workflow.

Prefer a procedural generator script for nontrivial animations. Keep the generator beside the generated asset so the animation can be regenerated, reviewed, and extended.

Before generating or substantially editing Bodymovin JSON, read
`references/bodymovin-authoring.md`. It contains the concrete layer, shape,
keyframe, slot, helper, and generator patterns needed to build a valid Lottie
file rather than only describing the workflow around one.

## Motion Design Workflow

Define the animation in named visual systems before writing JSON. Use semantic systems such as:

- `centralSubject`
- `atmosphericWash`
- `orbitRing`
- `currentTrace`
- `refractionWavelet`
- `particleBead`
- `causticGlint`
- `surfacePulse`

Layer motion at different scales:

1. Background atmosphere and anchoring washes.
2. Midground structure or flow field.
3. A clear primary subject.
4. Secondary rings, traces, ribbons, or arcs.
5. Micro-particles, glints, and texture.

Keep the first frame intentional. It often appears during loading, reduced-motion states, thumbnails, and paused previews.

## Large But Renderable Lotties

Treat raw JSON size and render complexity as separate constraints. Do not satisfy a size target by blindly adding thousands of visible SVG layers.

When the user asks for a large raw JSON file, such as "30 MB":

1. Build the visible animation first.
2. Keep visible layer and shape counts within the target renderer's practical limits.
3. Measure raw, gzip, and Brotli sizes.
4. If the visible animation is below the requested raw-size floor, add deterministic top-level metadata only when the user explicitly requires raw JSON size.
5. Verify the target renderer ignores that metadata.

For SVG-rendered `lottie-web`, prefer hundreds to low thousands of rendered shapes. Treat 10k+ visible layers as high risk unless the actual target renderer has been tested with that density.

For the Luminous tide-prism style and detailed large-file strategy, read `references/luminous-tide-prism.md`.

## Loop Closure

Treat seamless loops as a hard requirement unless the user says otherwise.

1. Use `op - 1` as the final visible frame.
2. Close every animated property on `op - 1` to the same visible value it has at frame `0`.
3. Add generator-level post-processing that closes animated properties automatically.
4. Render frame `0` and frame `op - 1`.
5. Byte-compare or pixel-compare the screenshots.

Do not assume cyclic math proves a rendered loop. Verify the rendered frames.

## Validation

Validate in this order:

1. Parse the JSON.
2. Audit layer counts, animated property counts, keyframe monotonicity, and keyframe ranges.
3. Render at frame `0`, midpoint, and `op - 1`.
4. Inspect screenshots for blank regions, muddy density, accidental clutter, cropped subjects, and weak hierarchy.
5. Verify loop closure when looping.
6. Verify in the actual app route or viewer.
7. Run the app's typecheck, build, lint, or equivalent project gate.

For user-facing app integrations, capture desktop and mobile screenshots. Report the exact asset path, file size, rendered frame checks, compressed sizes when relevant, and build/typecheck result.

## Delivery Rules

Keep edits narrow:

- Add or update a generator script when the animation is generated.
- Write generated JSON to the existing asset location.
- Wire the animation into the app only when the user asked for integration or the existing workflow requires it.
- Avoid replacing unrelated animations unless explicitly requested.
- Do not use unsupported Lottie constructs without verifying the target player supports them.

When a file-size target is satisfied through metadata padding, say so plainly. Raw-size padding is acceptable only when it is deterministic, ignored by the renderer, and the visible animation has already been made as rich as the renderer can reasonably handle.
