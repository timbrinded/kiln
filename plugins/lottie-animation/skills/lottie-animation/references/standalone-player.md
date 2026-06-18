# Standalone Lottie Player Workflow

Use this reference when no existing app or viewer is named. If the user is
working inside an app, use that app's real Lottie player instead.

## Player Setup

Use the official `diffusionstudio/lottie` player project for standalone work.
Do not hand-roll a custom HTML viewer unless the user explicitly asks for one.

```bash
npx degit diffusionstudio/lottie my-animation
cd my-animation
npm install
npm run dev
```

The development server usually runs at `http://localhost:3030`.

## Scene Layout

Standalone scenes live under `public/projects/`:

```text
public/
|-- canvaskit.wasm
`-- projects/
    `-- <project-slug>/
        `-- scene-<N>/
            |-- lottie.json
            |-- controls.json
            `-- image-assets-if-needed
```

Rules:

- `lottie.json` is required.
- Scene folder names should end in `-N`, such as `scene-1`.
- Project and scene slugs become URL segments.
- Image assets are referenced by bare filename from the Lottie `assets` array.

For a new standalone animation, create:

```text
public/projects/main-project/scene-1/lottie.json
```

Then open:

```text
http://localhost:3030/main-project/scene-1
```

## Inspecting State

Use the context endpoint instead of guessing:

```bash
curl -s http://localhost:3030/__context
```

It reports the project/scene tree, active scene, current frame, and total
frames. Use it to confirm that the file landed and the player sees it.

## Pinning Frames

Use the `frame` query parameter for screenshots:

```text
http://localhost:3030/main-project/scene-1?frame=0
http://localhost:3030/main-project/scene-1?frame=120
http://localhost:3030/main-project/scene-1?frame=239
```

The frame parameter seeks and pauses, which makes screenshots deterministic.

## Verification

For a new standalone scene:

1. Start the dev server.
2. Open the scene route.
3. Capture frame `0`, midpoint, and `op - 1`.
4. For loops, compare frame `0` and `op - 1`.
5. Inspect the canvas for blank output, clipping, muddy density, or unsupported
   constructs.
6. If the scene has slots and controls, confirm the controls appear and edits
   affect the next rendered frame.

Editing an existing `lottie.json` may require reloading or re-navigating the
page. Do not assume hot reload picked up JSON content changes.
