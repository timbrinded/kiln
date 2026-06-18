# Bodymovin Authoring Mechanics

Use this reference before creating or substantially editing a Lottie JSON file.
The goal is to produce simple Bodymovin shape data that renders in strict
players, not just in permissive local previews.

## Document Skeleton

Start from a complete document:

```json
{
  "v": "5.7.0",
  "fr": 60,
  "ip": 0,
  "op": 240,
  "w": 512,
  "h": 512,
  "nm": "Animation name",
  "ddd": 0,
  "assets": [],
  "layers": []
}
```

Use `op` as the exclusive end frame. The final visible frame is usually
`op - 1`.

## Shape Layer Pattern

Most generated vector animations should use `ty: 4` shape layers:

```json
{
  "ddd": 0,
  "ind": 1,
  "ty": 4,
  "nm": "layer-name",
  "sr": 1,
  "ks": {
    "o": { "a": 0, "k": 100 },
    "r": { "a": 0, "k": 0 },
    "p": { "a": 0, "k": [256, 256, 0] },
    "a": { "a": 0, "k": [0, 0, 0] },
    "s": { "a": 0, "k": [100, 100, 100] }
  },
  "ao": 0,
  "shapes": [],
  "ip": 0,
  "op": 240,
  "st": 0,
  "bm": 0
}
```

Keep transform values three-dimensional in layer `ks.p`, `ks.a`, and `ks.s`.
Use two-dimensional values inside shape groups.

## Shape Group Pattern

Wrap visible shapes in a group and end each group with a transform:

```json
{
  "ty": "gr",
  "nm": "group-name",
  "it": [
    { "ty": "el", "p": { "a": 0, "k": [0, 0] }, "s": { "a": 0, "k": [80, 80] } },
    { "ty": "fl", "c": { "a": 0, "k": [0.02, 0.66, 0.74, 1] }, "o": { "a": 0, "k": 100 }, "r": 1 },
    {
      "ty": "tr",
      "p": { "a": 0, "k": [0, 0] },
      "a": { "a": 0, "k": [0, 0] },
      "s": { "a": 0, "k": [100, 100] },
      "r": { "a": 0, "k": 0 },
      "o": { "a": 0, "k": 100 },
      "sk": { "a": 0, "k": 0 },
      "sa": { "a": 0, "k": 0 },
      "nm": "Transform"
    }
  ],
  "np": 3,
  "cix": 2,
  "bm": 0
}
```

Use these shape primitives first:

- `el` for ellipses and circles
- `rc` for rectangles and rounded rectangles
- `sh` for custom paths
- `fl` for fills
- `st` for strokes
- `tr` for group transforms

Avoid effects, expressions, masks, precomps, and trim paths until the target
player has been verified with those constructs.

## Keyframes

Static property:

```json
{ "a": 0, "k": 100 }
```

Animated scalar:

```json
{
  "a": 1,
  "k": [
    { "t": 0, "s": [20], "i": { "x": [0.55], "y": [1] }, "o": { "x": [0.45], "y": [0] } },
    { "t": 120, "s": [80], "i": { "x": [0.55], "y": [1] }, "o": { "x": [0.45], "y": [0] } },
    { "t": 239, "s": [20] }
  ]
}
```

Animated vector:

```json
{
  "a": 1,
  "k": [
    { "t": 0, "s": [256, 180, 0], "i": { "x": [0.55], "y": [1] }, "o": { "x": [0.45], "y": [0] } },
    { "t": 120, "s": [256, 332, 0], "i": { "x": [0.55], "y": [1] }, "o": { "x": [0.45], "y": [0] } },
    { "t": 239, "s": [256, 180, 0] }
  ]
}
```

Keep keyframe times monotonic and inside `[ip, op]`. For exact loops, close on
`op - 1`, not `op`.

## Generator Helpers

For anything beyond a small icon, write a generator. Use helpers like these:

```js
let ind = 1
const nextInd = () => ind++
const num = (k) => ({ a: 0, k })
const vec2 = (k) => ({ a: 0, k })
const vec3 = (k) => ({ a: 0, k })
const color = (k) => ({ a: 0, k })
const anim = (k) => ({ a: 1, k })
const keyValue = (value) => (typeof value === 'number' ? [value] : value)
const ease = (t, value) => ({
  t,
  s: keyValue(value),
  i: { x: [0.55], y: [1] },
  o: { x: [0.45], y: [0] },
})
const hold = (t, value) => ({ t, s: keyValue(value), h: 1 })
```

Build small helpers for `layer`, `group`, `ellipse`, `rect`, `pathShape`, and
`tr`. Then create named motion systems that return layers.

## Loop Closure Helper

Add a post-processing pass so every animated property closes:

```js
function closeLoopProperty(property, lastFrame) {
  if (!property || property.a !== 1 || !Array.isArray(property.k) || property.k.length === 0) return
  const first = property.k[0]
  if (!first || typeof first !== 'object' || !('s' in first)) return
  property.k = [
    ...property.k.filter((keyframe) => !keyframe || typeof keyframe.t !== 'number' || keyframe.t < lastFrame),
    { ...first, t: lastFrame, s: Array.isArray(first.s) ? [...first.s] : first.s },
  ]
}
```

Walk the full Lottie object recursively and apply this to every animated
property. Then render frame `0` and frame `op - 1` and compare pixels.

## Slots And Controls

Use slots only when the target player supports them. For standalone editable
scenes, expose at least a background color slot:

```json
{
  "slots": {
    "bgColor": { "p": { "a": 0, "k": [0.955, 0.975, 0.988, 1] } }
  }
}
```

Reference the slot from a property:

```json
{ "ty": "fl", "c": { "sid": "bgColor" }, "o": { "a": 0, "k": 100 }, "r": 1 }
```

Optional `controls.json` lives next to `lottie.json`:

```json
{
  "controls": [
    { "sid": "bgColor", "label": "Background color" }
  ]
}
```

## Asset Images

Prefer vector shapes for portability. When image assets are needed:

- Put image files beside the Lottie file when using a scene-folder player.
- Use bare filenames in `assets[].p`.
- Use data URLs only when the target app already accepts embedded assets and
  the extra JSON size is acceptable.

## Structural Audit

Before visual review, run a script that checks:

- JSON parses
- top-level `fr`, `ip`, `op`, `w`, `h`, `layers` exist
- layer `ind` values are unique
- keyframe times are monotonic
- keyframe times are inside the timeline
- shape groups end with transforms
- no unsupported effects, expressions, masks, or precomps were introduced

Structural validity is not completion. It only proves the file is ready to
render-test.
