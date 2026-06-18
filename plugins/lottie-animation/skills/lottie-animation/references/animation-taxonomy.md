# Animation Taxonomy

Use this reference before designing the animation. Different use cases optimize
for different outcomes; do not apply the same recipe to loaders, hero scenes,
explainers, icons, and abstract loops.

## Type Router

| Type | Optimize For | Avoid |
| --- | --- | --- |
| Explainer diagram | comprehension and sequence | decorative motion that hides causality |
| Abstract wallpaper | atmosphere and seamless texture | attention theft near task content |
| Icon or microinteraction | instant state clarity | long runtimes and dense detail |
| Hero animation | brand thesis and first-viewport impact | load delay and text occlusion |
| Product illustration | object clarity and polish | clutter around the product/metaphor |
| Loading state | instant render and perfect loop | large files and false progress |
| Data or architecture visualization | truth, labels, and relationships | invented flow or ambiguous arrows |
| Sticker or mascot loop | personality and readable silhouette | overacting that breaks the loop |

## Explainer Diagrams

Composition:

- use lanes, numbered phases, or spatial zones
- keep labels short and readable
- reveal one causal step at a time

Motion:

- trace paths, pulse active nodes, or reveal arrows in order
- let each step settle before the next begins
- use finite chapters more often than infinite decorative loops

Verification:

- scrub frame-by-frame
- confirm there is no skipped causal step
- confirm labels remain legible at target size

## Abstract Wallpapers

Composition:

- use full-bleed fields, gradients made from shapes, waves, particles, or
  texture
- keep semantic burden low
- make density intentional: quiet fields plus one signature pattern

Motion:

- slow phase shifts
- opacity waves
- soft parallax
- seamless loop required

Verification:

- pixel-compare frame `0` and `op - 1`
- test reduced motion or pause behavior
- ensure it does not fight foreground UI

## Icons And Microinteractions

Composition:

- single glyph or compact object
- clear before/after state
- readable from 16-64 px

Motion:

- 70-600 ms depending on complexity
- productive easing
- immediate feedback
- no unnecessary loops

Verification:

- inspect at small size
- verify state clarity
- confirm no layout shift
- keep JSON tiny

## Hero Animations

Composition:

- one dominant brand or product metaphor
- strong first frame
- enough negative space for headline and controls

Motion:

- expressive entrance is allowed
- idle loop should be quieter than the intro
- avoid constant motion beside important text

Verification:

- test desktop and mobile crop
- check page-load impact
- verify reduced-motion fallback
- confirm text and controls are not occluded

## Product Illustrations

Composition:

- central product, object, or metaphor
- consistent stroke and shape language
- sparse support marks

Motion:

- reveal, pulse, glint, orbit, or small state change
- keep silhouette stable
- use gentle loops only when they add life

Verification:

- first frame should work as a still illustration
- compare against brand palette
- check subject clarity at target size

## Loading States

Composition:

- centered or locally anchored to the waiting area
- minimal marks
- no misleading progress unless determinate

Motion:

- perfect loop
- constant rhythm
- low annoyance over repeated viewing

Verification:

- test slow network and slow CPU
- confirm instant render
- compare first and final visible frames
- keep asset small

## Data And Architecture Visualizations

Composition:

- nodes, lanes, boundaries, arrows, legends, and labels
- semantic color only where meaning requires it
- group complexity into chunks

Motion:

- highlight active path
- reveal dependency order
- pulse ownership or boundary changes
- avoid decorative infinite motion

Verification:

- check factual accuracy
- verify arrows match source truth
- keep labels readable
- ensure motion does not imply unsupported causality

## Sticker And Mascot Loops

Composition:

- strong silhouette
- face or gesture readable at small size
- bolder palette allowed

Motion:

- blink, wave, bounce, squash, stretch, or secondary prop motion
- 1-3 second seamless loop
- return to a comfortable resting pose

Verification:

- compare frame `0` and `op - 1`
- inspect at small size
- ensure personality does not become chaotic
