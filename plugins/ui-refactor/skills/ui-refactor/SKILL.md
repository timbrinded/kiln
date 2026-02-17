---
name: ui-refactor
description: >-
  A design review and UI improvement skill for frontend interfaces.
  This skill should be used when the user asks to "review a design",
  "review a screenshot", "improve the UI", "make this look better",
  "fix the design", "check spacing", "improve visual hierarchy",
  "choose colors", "pick fonts", "review my CSS", "review my Tailwind",
  "make this more professional", "design feedback", "fix the layout",
  "improve typography", "check contrast", "add depth", "polish the UI",
  or is working on frontend code (HTML, CSS, JSX, TSX, Svelte, Vue)
  where design quality matters.
---

# UI Refactor — Design Review Skill

## Core Philosophy

Design quality comes from specific, learnable decisions — not innate talent. Three principles underpin everything:

1. **Hierarchy is the #1 factor.** An interface where every element competes equally for attention feels chaotic. Deliberately de-emphasize secondary elements before amplifying primary ones.
2. **Constrained choices beat infinite options.** Pre-define systems for spacing, type sizes, colors, and shadows. Pick from the system, never from the infinite continuum. Decision fatigue kills quality.
3. **Start functional, add polish last.** Design features not layouts, work in grayscale before adding color, ship the smallest useful version. Details like shadows and icons are finishing touches, not starting points.

## Review Workflow

When reviewing a design (screenshot, code, or description), evaluate across six dimensions in priority order:

1. **Hierarchy & Emphasis** — Can you identify primary, secondary, and tertiary content instantly? Is there a clear visual path?
2. **Spacing & Layout** — Is spacing systematic? Do groups feel cohesive? Is there ambiguous spacing?
3. **Typography** — Is the type scale constrained? Are line-heights proportional? Are line lengths readable?
4. **Color** — Are colors from a defined system? Do greys have temperature? Is contrast accessible?
5. **Depth & Images** — Are shadows from a defined elevation system? Is text readable on images?
6. **Polish & Finishing** — Are defaults supercharged? Are borders overused? Are empty states designed?

**Output format:**
```
## Design Review

### What Works Well
- [Specific praise with why it works]

### Issues Found
1. **[Issue Name]** — [Dimension]
   - What: [Observable problem]
   - Why: [Principle being violated]
   - Fix: [Concrete CSS/code change]

### Quick Wins
- [Highest-impact, lowest-effort changes]
```

## Advisory Workflow

When answering design questions during development (not reviewing existing work):

1. Identify which dimension the question falls under
2. Load the relevant reference file
3. Provide the specific principle, concrete values, and reasoning
4. If the question spans multiple dimensions, address the highest-priority one first

## Decision Tree — Which Reference to Load

Route to the right reference based on the symptom:

| Symptom | Load |
|---------|------|
| "Everything looks the same weight/importance" | `references/hierarchy-and-emphasis.md` |
| "It looks cramped" or "spacing feels off" | `references/spacing-and-layout.md` |
| "The fonts don't feel right" or "text is hard to read" | `references/typography.md` |
| "Colors feel random" or "it looks washed out" | `references/color.md` |
| "It feels flat" or "text on images is unreadable" | `references/depth-and-images.md` |
| "It looks amateur" or "needs more polish" | `references/polish-and-finishing.md` |
| "Where do I even start?" or general design process | `references/design-process.md` |
| Reviewing a full screenshot or page | Load `references/hierarchy-and-emphasis.md` first, then others as issues emerge |

## Quick Anti-Pattern Checklist

Before loading any reference files, check for these 8 high-signal problems:

1. **Wall of Content** — Everything at the same size/weight/color. No primary-secondary-tertiary distinction.
2. **Ambiguous Spacing** — Equal gaps between a label and its input vs. between form groups. Proximity doesn't signal relationship.
3. **Font Size Soup** — More than 8 distinct font sizes visible. No constrained type scale.
4. **Color Without System** — Ad-hoc hex values. No visible shade palette. Grey text on colored backgrounds using literal grey.
5. **One Shadow Fits All** — Same box-shadow on buttons, cards, and modals. No elevation hierarchy.
6. **Border Everything** — Borders used as the default separator when spacing, background color, or box-shadow would be cleaner.
7. **Full-Width Everything** — Content stretched to fill viewport when a max-width constraint would improve readability.
8. **Ignored Empty States** — Blank screens with just "No items found" — no illustration, no guidance, no call-to-action.

If any are detected, load the relevant reference for detailed fixes.

## Reference Files

| File | Contents | Load When |
|------|----------|-----------|
| `references/design-process.md` | Start with features, work low-fidelity, constrain choices, define personality | Starting a new design or asking "where do I begin?" |
| `references/hierarchy-and-emphasis.md` | Emphasize by de-emphasizing, weight + color + size for hierarchy, labels as last resort, semantic vs visual hierarchy | Hierarchy issues detected or reviewing any full interface |
| `references/spacing-and-layout.md` | Non-linear spacing scale, start with too much whitespace, fixed sidebars, avoid ambiguous spacing | Spacing/layout issues or reviewing component/page structure |
| `references/typography.md` | Hand-crafted type scale, proportional line-height, line length, letter-spacing, baseline alignment | Typography issues or text-heavy interfaces |
| `references/color.md` | HSL workflow, 8-10 shades per color, hue rotation, warm/cool greys, accessible contrast | Color issues, palette creation, or contrast problems |
| `references/depth-and-images.md` | 5-level shadow system, two-part shadows, flat depth, text on images, icon sizing | Depth/shadow issues or image-related problems |
| `references/polish-and-finishing.md` | Supercharged defaults, accent borders, fewer borders, empty states, thinking outside the box | "It needs more polish" or finishing a nearly-complete design |
