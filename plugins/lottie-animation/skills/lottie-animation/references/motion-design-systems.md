# Motion Design Systems

Use this reference when the task asks for better motion quality, timing,
choreography, expressive polish, interaction feedback, or accessibility.

## Motion Purpose

Assign one primary purpose before generating:

- `feedback`: confirm an action or state change
- `transition`: preserve continuity between states
- `progress`: show waiting, loading, or completion
- `orientation`: explain where an object came from or went
- `attention`: draw the eye to something important
- `delight`: add brand personality after usability is satisfied
- `ambient`: provide quiet atmosphere without demanding attention
- `explanation`: reveal a process, dependency, or sequence

If the purpose is unclear, do not add motion yet. Motion without a job becomes
noise.

## Motion Modes

Choose one mode:

- `productive`: short, useful, restrained; best for UI feedback, loaders, icons,
  and state changes
- `expressive`: more personality and overshoot; best for heroes, brand moments,
  mascots, and celebratory transitions
- `ambient`: slow, soft, and optional; best for backgrounds, wallpapers, and
  supporting atmosphere

Never let expressive or ambient motion block task completion.

## Choreography

Plan motion as staged poses:

1. first frame / poster
2. anticipation or setup
3. primary action
4. secondary action
5. settle pose
6. loop-close pose

Group related layers by shared direction, timing, color, enclosure, or orbit.
Avoid independent random motion unless randomness is the explicit subject.

Use these patterns:

- parent moves before child when revealing structure
- cause moves before effect when explaining a process
- large objects move slower than small details
- secondary action trails primary action
- highlights arrive after structure is readable
- background motion stays lower contrast than foreground motion

## Timing And Easing

Use eased motion by default. Linear motion usually reads as mechanical unless it
is intentionally technical, orbital, or progress-like.

Practical timing ranges:

- 70-120 ms: tiny feedback and button/icon response
- 150-240 ms: small UI state changes
- 250-500 ms: icons, loaders, compact reveals, product illustration beats
- 500-900 ms: hero entrance, explainer chapter, large spatial transition
- 1-6 s: ambient loops, wallpapers, mascots, decorative idle states

Scale duration with distance, size, and importance. Large movements need enough
time to be understood; repeated UI feedback should be brief.

## Selective Animation Principles

Use these principles for Lottie work:

- **Staging:** make the important idea obvious.
- **Anticipation:** prepare the viewer before a large change.
- **Slow in/out:** ease acceleration and deceleration.
- **Arcs:** avoid stiff straight-line paths unless the object is mechanical.
- **Follow-through/overlap:** let secondary elements trail or settle after the
  primary move.
- **Secondary action:** add glints, dust, traces, or ripples only after the main
  action is readable.
- **Appeal:** make the first frame and core silhouette attractive.

Use squash/stretch and exaggeration only for playful icons, mascots, stickers,
or brand moments. Avoid them in serious diagrams or professional UI feedback.

## Accessibility

Motion must not be the only carrier of information. Provide static, shorter, or
fade-only alternatives when the app supports reduced motion.

Avoid:

- rapid zooming through depth
- large parallax tied to scrolling
- endless attention-grabbing motion near task content
- flashing above safe thresholds
- loops that cannot be paused when they persist beside important content

Useful sources:

- Apple HIG Motion: <https://developer.apple.com/design/human-interface-guidelines/motion>
- WCAG animation from interactions: <https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html>
- WCAG pause, stop, hide: <https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html>
- MDN `prefers-reduced-motion`: <https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion>

## Verification

Review the rendered animation with these questions:

- Is the motion's purpose obvious?
- Is there one primary moving idea?
- Are related objects choreographed together?
- Are secondary effects delayed until after the main idea is readable?
- Does the motion still make sense when paused at frame `0`, midpoint, and
  `op - 1`?
- Is there a reduced-motion or static fallback for user-facing contexts?
