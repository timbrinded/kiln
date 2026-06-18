# Luminous Tide Prism Reference

Use this reference when the user wants an animation similar to "Luminous - tide prism", asks for a visually impressive abstract Lottie, or asks for a large raw JSON asset that still needs to render reliably.

## Visual Recipe

Use one clear central subject and a layered field around it.

Core composition:

- central faceted prism or geometric object
- pale atmospheric background
- soft aqua, coral, gold, white, and mist palette
- translucent elliptical halos behind the subject
- orbiting refraction rings around the center
- curved wavelets near the subject
- directional current traces across the whole canvas
- small refracted beads and sparse cross-shaped glints

Avoid a one-hue palette. The Luminous style works because aqua, coral, gold, white, and pale mist share the canvas without one color dominating every element.

## Motion Systems

Name systems by visual role, not by generic particle count:

- `central-tide-prism`: the primary subject, with small position, scale, and rotation changes.
- `breathing-halo`: soft background ellipses that pulse without competing with the subject.
- `orbital-refraction-ring`: thin elliptical rings that rotate in alternating directions.
- `current-trace`: short line dashes drifting across the canvas.
- `refracted-bead`: small dots orbiting and pulsing around the subject.
- `refraction-wavelet`: thin elliptical arcs placed along radial paths.
- `prism-glint`: brief cross glints with delayed opacity spikes.

Use different phases, speeds, opacity ranges, and sizes so the motion feels authored rather than random.

## Renderability Strategy

For SVG-rendered `lottie-web`, keep the visible animation around hundreds to low thousands of shapes. The Luminous implementation that rendered reliably used approximately:

- 940 visible Lottie layers
- 1,063 rendered SVG shapes
- 3,033 animated properties
- 240 frames at 60 fps

A first attempt with about 14,784 visible layers crashed the browser. Treat that as the failure mode to avoid: raw file size must not be achieved by unbounded visible layers.

## Large Raw JSON Strategy

When a user explicitly asks for a large JSON file, such as "make it 30 MB":

1. Generate the visible animation normally.
2. Verify it renders.
3. Measure the raw byte size.
4. If the requested raw size is still not met, add deterministic top-level metadata:

```json
{
  "metadata": {
    "note": "Deterministic raw-size payload. Ignored by Lottie renderers.",
    "visualSystems": ["tide prism", "orbital refractions", "current traces"],
    "payload": "..."
  }
}
```

The metadata should be top-level and outside `layers` and `assets`. It should not introduce hidden shapes, offscreen layers, masks, expressions, or other render work.

Verify the target renderer ignores the metadata by loading and rendering the animation in the real player.

## Verification Checklist

Use concrete evidence:

- exact raw byte size
- decimal MB and MiB
- gzip and Brotli size when large delivery matters
- layer count
- rendered shape count when using SVG
- frame `0`, midpoint, and `op - 1` screenshots
- frame `0` versus `op - 1` loop comparison
- app route screenshot on desktop
- app route screenshot on mobile for user-facing integrations
- build/typecheck result

Do not stop at "valid JSON". A Lottie is complete only when it renders in the user's target surface and the requested motion and size constraints are verified.
