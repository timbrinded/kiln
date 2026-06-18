# Compatibility And Renderers

Use this reference when choosing a target renderer, diagnosing an unsupported
Lottie feature, packaging a `.lottie` file, or deciding whether an animation is
portable enough for production.

## Compatibility Contract

Start every task with these facts:

- target player package and version
- renderer mode: SVG, canvas, HTML, Skottie, native, or dotLottie-web
- required platforms: web, iOS, Android, desktop, or embedded player
- allowed file format: `.json`, `.lottie`, or either
- whether expressions, masks, images, text, slots, or themes are required

Do not assume feature parity across renderers. Schema-valid JSON can still fail
or degrade in the target player.

## Validation Order

Use layered validation:

1. Parse JSON.
2. Validate against the Lottie schema when a schema validator is available.
3. Run a structural audit for layers, keyframes, transforms, and unsupported
   constructs.
4. Render in the actual target player.
5. Render in a second engine, such as Skottie, when portability matters.

Useful sources:

- Lottie format spec: <https://lottie.github.io/lottie-spec/1.0/>
- Lottie schema: <https://lottie.github.io/lottie-spec/latest/specs/schema/>
- `lottie-specs-js`: <https://github.com/lottie/lottie-specs-js>
- Skottie: <https://skia.org/docs/user/modules/skottie/>

## Stable Authoring Subset

Prefer this subset for generated JSON:

- shape layers
- transforms
- fills and strokes
- rectangles, ellipses, and paths
- simple trim paths when verified
- static images only when needed
- baked keyframes instead of expressions
- top-level slots only when the target player supports them

Avoid by default:

- expressions
- unsupported After Effects effects
- 3D layers
- camera/light features
- complex masks and mattes
- glyph-heavy text exports
- renderer-specific settings that are not verified

When text is needed, prefer app-rendered text outside the Lottie if the target
UI can support it. Text converted to shapes is portable but increases file size
and makes localization harder.

## Renderer Notes

For `lottie-web`:

- SVG usually has the broadest feature coverage.
- Canvas can reduce DOM pressure but has feature gaps.
- `progressiveLoad` can reduce initial SVG load but may not work with all
  matte/ordering scenarios.
- Disable expressions when possible.
- Measure actual rendered SVG node count for complex files.

Useful sources:

- lottie-web feature matrix: <https://github.com/airbnb/lottie-web/wiki/Features>
- load options: <https://github.com/airbnb/lottie-web/wiki/loadAnimation-options>
- renderer settings: <https://github.com/airbnb/lottie-web/wiki/Renderer-Settings>
- shapes: <https://github.com/airbnb/lottie-web/wiki/Shapes>
- expressions: <https://github.com/airbnb/lottie-web/wiki/Expressions>
- effects: <https://github.com/airbnb/lottie-web/wiki/Effects>

For dotLottie:

- Use only after confirming the project has a dotLottie-capable player.
- Treat `.lottie` as packaging, not a fix for unsupported animation features.
- Remember that `.lottie` packages animations, images, themes, fonts, and state
  machines inside a compressed archive.

Useful sources:

- dotLottie v2 spec: <https://dotlottie.io/spec/2.0/>
- dotLottie web docs: <https://developers.lottiefiles.com/docs/dotlottie-player/dotlottie-web/>

For Skottie:

- Use as a second-renderer smoke test for generated JSON.
- Treat warnings and low-power-profile warnings as evidence to simplify.
- Do not assume Skottie behavior exactly matches `lottie-web`.

## Performance Checks

Measure the real costs:

- raw bytes
- gzip bytes
- Brotli bytes
- layer count
- rendered SVG node count
- parse and first-frame time
- frame screenshots at `0`, midpoint, and `op - 1`
- mobile viewport behavior

For large files, test slow CPU or mobile emulation when possible. A beautiful
desktop animation that stalls the target page is not production-ready.

## Compatibility Rules

- Let the target renderer choose the allowed feature set.
- Prefer boring primitives over clever unsupported constructs.
- Bake procedural motion into keyframes instead of relying on expressions.
- Use `.lottie` for packaging only when the player supports it.
- Keep image assets explicit and local to the scene or app asset path.
- Validate schema first, render second, inspect screenshots third.
