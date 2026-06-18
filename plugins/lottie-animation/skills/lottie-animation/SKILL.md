---
name: lottie-animation
description: This skill should be used when the user asks to "create a Lottie", "generate a Lottie animation", "make a Bodymovin JSON", "fix a Lottie", "make a seamless loop", "make a large Lottie", "make a 30 MB Lottie", or mentions lottie-web, Bodymovin, Skottie, dotLottie, .lottie, or Lottie JSON.
---

# Lottie Animation Authoring

Create production-ready Lottie animations as renderable Bodymovin JSON. Optimize for the real target player, motion intent, loop correctness, and runtime stability.

## Operating Rules

Start with the target surface:

1. Inspect the target app or viewer.
2. Read the dependency manifest to identify the package manager and Lottie player.
3. Locate the actual asset path, route, component, and fetch behavior.
4. Use the existing player when one exists.
5. Create a standalone viewer only when no target app or viewer is present.

Use a procedural generator for nontrivial animation work. Keep the generator beside the generated asset when working in a target repo.

## Reference Router

Load references by task:

| Need | Read |
| --- | --- |
| Build or edit Bodymovin JSON | `references/bodymovin-authoring.md` |
| No app or viewer was provided | `references/standalone-player.md` |
| Choose safe features, renderer settings, or dotLottie/Skottie strategy | `references/compatibility-and-renderers.md` |
| Improve timing, easing, choreography, or accessibility | `references/motion-design-systems.md` |
| Decide how guidance changes for icons, loaders, heroes, explainers, wallpapers, product illustrations, or diagrams | `references/animation-taxonomy.md` |
| Generate a large raw JSON while keeping the visible animation stable | `references/large-stable-lotties.md` |

For open-ended "make it beautiful" requests, read `motion-design-systems.md` and `animation-taxonomy.md` before generating. For large raw-size requests, read `large-stable-lotties.md` and `compatibility-and-renderers.md`.

## Authoring Workflow

1. Classify the animation intent: feedback, transition, progress, attention, orientation, delight, brand, explainer, ambient, or data flow.
2. Define the visible composition before coding: focal subject, supporting systems, palette roles, loop duration, and first-frame poster.
3. Generate simple Bodymovin shape data first: shape layers, transforms, fills, strokes, paths, and baked keyframes.
4. Avoid effects, expressions, masks, precomps, 3D, renderer-specific tricks, and large visible layer counts unless the target player proves support.
5. Close loops on `op - 1`, not `op`, and verify rendered frame `0` against `op - 1`.

## Validation

Validate in this order:

1. Parse the JSON.
2. Audit layer counts, animated property counts, keyframe monotonicity, and keyframe ranges.
3. Render at frame `0`, midpoint, and `op - 1`.
4. Inspect screenshots for blank regions, muddy density, accidental clutter, cropped subjects, and weak hierarchy.
5. Verify loop closure when looping.
6. Verify in the actual app route or viewer.
7. Run the app's typecheck, build, lint, or equivalent project gate.

For user-facing integrations, capture desktop and mobile screenshots. Report the asset path, file size, rendered frame checks, compressed sizes when relevant, and build/typecheck result.

## Delivery Rules

Keep edits narrow:

- Add or update a generator script when the animation is generated.
- Write generated JSON to the existing asset location.
- Wire the animation into the app only when the user asked for integration or the existing workflow requires it.
- Avoid replacing unrelated animations unless explicitly requested.
- Do not use unsupported Lottie constructs without verifying the target player supports them.

When a file-size target is satisfied through metadata padding, say so plainly. Raw-size padding is acceptable only when it is deterministic, ignored by the renderer, and the visible animation has already been made as rich as the renderer can reasonably handle.
