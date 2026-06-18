# Large Stable Lottie JSONs

Use this reference when the user asks for a large raw Lottie JSON file, a
visually impressive abstract animation, or a dense generated animation that must
still render reliably.

The core rule: large JSON size, visual richness, and renderer complexity are
three different budgets. Satisfy each budget deliberately.

## Generation Contract

Before writing code, state the contract in concrete terms:

- target player: `lottie-web`, Skottie, app-specific wrapper, or standalone
  player
- renderer: SVG, canvas, or native
- canvas size and frame rate
- loop duration and final visible frame
- raw-size target, if any
- visible layer and shape budget
- verification route and screenshots

Do not begin by adding particles. Begin by deciding what the viewer should see
first, what should support it, and what can be safely ignored.

## Stable Size Strategy

Use this order:

1. Build the visible animation at a renderer-safe complexity.
2. Verify it renders and loops.
3. Measure raw, gzip, and Brotli sizes.
4. If the user explicitly asked for a raw byte floor and the visible animation
   is smaller, add deterministic top-level metadata padding.
5. Verify the renderer ignores the metadata.

Do not satisfy raw size by creating hidden offscreen layers, invisible shapes,
zero-opacity shape spam, masks, expressions, or precomps. Those still increase
parse, layout, or renderer risk.

For SVG-rendered `lottie-web`, keep visible output roughly in the hundreds to
low thousands of rendered shapes unless the target app has proven it can handle
more. A large JSON that crashes the player is a failed Lottie.

## Visual Design Laws

Apply these rules before increasing density:

- **One focal subject:** Give the animation one dominant object, gesture, or
  field. If the first frame has no obvious subject, the animation will feel like
  noise.
- **Hierarchy before decoration:** Make primary, secondary, and tertiary motion
  readable. De-emphasize support layers before amplifying the subject.
- **Constrained palette:** Use 4-6 named colors with clear roles: background,
  primary accent, secondary accent, highlight, shadow/ink, and optional warmth.
  Avoid one-hue gradients and ad-hoc random colors.
- **Gestalt grouping:** Place related particles, traces, and rings in coherent
  bands, orbits, grids, flows, or fields. Proximity and direction should explain
  why elements belong together.
- **Negative space:** Leave breathing room around the focal subject. Density is
  more impressive when it has contrast against quiet areas.
- **Rhythm over randomness:** Vary phase, scale, opacity, and speed according to
  a pattern. Random-looking motion reads as unfinished.
- **One signature effect:** Spend visual boldness in one place: a prism, bloom,
  vortex, field sweep, portal, wave, map, constellation, or mechanical reveal.
  Keep the rest disciplined.
- **Readable first frame:** Treat frame `0` as a poster. It should look
  intentional before motion begins.

## Motion Architecture

Name motion systems by visual role, not implementation count:

- `primarySubject`: central object or visual thesis
- `backgroundAtmosphere`: low-opacity washes or field gradients made from
  simple shapes
- `structuralRings`: orbits, frames, grids, or paths that organize the scene
- `flowTraces`: short marks that indicate direction and velocity
- `microParticles`: beads, motes, sparks, bubbles, or dust with constrained
  placement
- `highlightGlints`: sparse bright events that punctuate the loop
- `depthShadows`: soft anchors that prevent floating cutouts from feeling flat

Each system needs a reason to exist. If removing a system does not change the
read of the scene, remove it or lower its count.

## Layering Recipe

Build from quiet to loud:

1. Background plane: one full-canvas rectangle plus 2-4 soft organic shapes.
2. Depth anchors: soft shadows or translucent halos behind the subject.
3. Structure: rings, arcs, grid lines, or orbital paths.
4. Primary subject: the clearest shape group, with the strongest contrast.
5. Directional field: traces, wavelets, bands, or current marks.
6. Particles: constrained clusters, orbits, rows, or flow paths.
7. Highlights: a small number of glints or pulses with intentional timing.

Prefer many simple, coherent marks over many complex unique shapes. Complexity
should come from composition and timing, not from unsupported Lottie features.

## Large JSON Padding

Use metadata padding only when the user explicitly asks for raw JSON size:

```json
{
  "metadata": {
    "note": "Deterministic raw-size payload. Ignored by Lottie renderers.",
    "visualSystems": ["primary subject", "flow traces", "glints"],
    "payload": "..."
  }
}
```

Keep padding:

- top-level
- deterministic
- outside `layers` and `assets`
- plainly documented in the final answer
- verified in the target renderer

Never pretend metadata padding is visual complexity. Report both the raw size
and the visible layer/rendered shape count.

## Generator Rules

Use a procedural generator for large animations:

- define constants for `W`, `H`, `FR`, `OP`, and `LAST`
- define a named palette object
- define helpers for static values, animated values, layers, groups, transforms,
  rectangles, ellipses, paths, fills, and strokes
- define one function per motion system
- create deterministic phase offsets from indexes
- close the loop with a recursive post-processing pass
- measure output bytes after serialization

Keep the generator as the source of truth. Do not hand-edit generated JSON
unless the edit is a temporary diagnostic step.

## Failure Modes

Watch for these problems:

- **DOM overload:** too many visible SVG layers or shapes
- **Muddy density:** every region has equal texture and no visual hierarchy
- **Particle soup:** marks exist but do not communicate direction, depth, or
  structure
- **Palette mush:** similar hues with similar saturation and value
- **Dead center:** subject is centered but unsupported by directional motion
- **Loop seam:** frame `0` and `op - 1` do not match
- **JSON-only success:** parse succeeds but the real player is blank, slow, or
  visually weak

Fix hierarchy before adding more elements. Fix palette before adding effects.
Fix the loop before increasing duration.

## Verification Checklist

Collect evidence:

- exact raw byte size, decimal MB, and MiB
- gzip and Brotli size when delivery matters
- visible layer count
- rendered shape count for SVG
- animated property count
- structural audit for keyframe ranges and monotonic times
- rendered screenshots at frame `0`, midpoint, and `op - 1`
- frame `0` versus `op - 1` comparison for loops
- app route screenshot on desktop
- app route screenshot on mobile for user-facing integrations
- build/typecheck result

Completion requires a renderable, intentional animation in the target surface.
Valid JSON and a large byte count are necessary evidence only when they support
that end state.
