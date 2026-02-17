# Depth and Images

## Mental Model Shifts

**Wrong:** "Shadows are decorative — I'll add one that looks nice."
**Right:** Shadows communicate elevation on a virtual z-axis. Bigger shadow = higher elevation = more attention. Define a 5-level shadow system like you define spacing and color scales, and assign shadows by intended elevation, not by what "looks nice."

**Wrong:** "Flat design means no depth."
**Right:** Flat design means no realistic lighting effects. You can still create depth through color (lighter = closer), solid shadows (no blur), and overlapping elements. Effective flat designs use all of these.

**Wrong:** "This SVG icon is vector, so I can scale it to any size."
**Right:** Icons are designed for specific sizes. A 16px icon scaled to 48px looks chunky — it lacks the detail designed for larger sizes. A 128px icon scaled to 16px becomes mush. Use icons at their intended size, or enclose small icons in a colored shape to fill larger spaces.

## The 5-Level Shadow System

Define five shadow levels and assign them by element importance:

| Level | CSS `box-shadow` | Use For |
|-------|-----------------|---------|
| **1 — Subtle** | `0 1px 3px hsla(0,0%,0%,.12), 0 1px 2px hsla(0,0%,0%,.24)` | Buttons, form inputs — slightly raised |
| **2 — Low** | `0 3px 6px hsla(0,0%,0%,.1), 0 2px 4px hsla(0,0%,0%,.2)` | Cards, raised panels — resting state |
| **3 — Medium** | `0 10px 20px hsla(0,0%,0%,.1), 0 3px 6px hsla(0,0%,0%,.15)` | Dropdowns, popovers — floating above content |
| **4 — High** | `0 14px 28px hsla(0,0%,0%,.12), 0 10px 10px hsla(0,0%,0%,.12)` | Sticky headers, drawers — prominent elevation |
| **5 — Highest** | `0 19px 38px hsla(0,0%,0%,.15), 0 15px 12px hsla(0,0%,0%,.1)` | Modals, dialogs — demands immediate attention |

### Why Two Shadows?
Each level uses two shadows:
- **First shadow** (larger offset, more blur): Simulates direct light source casting a shadow below
- **Second shadow** (tighter, darker): Simulates the area directly beneath the element where ambient light can't reach

As elevation increases, the tight ambient shadow should fade (lower opacity) — objects far from a surface lose their contact shadow.

## Principles

### Emulate Light from Above
- WHEN making an element feel raised → DO add a subtle light top edge (`box-shadow: inset 0 1px 0 hsl(...)` slightly lighter than the face) and a dark bottom shadow
- WHEN making an element feel inset → DO add a dark top inner shadow (`box-shadow: inset 0 2px 2px hsla(0,0%,0%,.1)`) and a subtle light bottom edge
- WHEN picking the lighter edge color → DO hand-pick it (same hue, higher lightness); don't overlay semi-transparent white, which desaturates

### Shadows for Interaction Feedback
- WHEN a user grabs a draggable item → DO increase its shadow level to make it feel "picked up"
- WHEN a user clicks a button → DO decrease or remove the shadow to make it feel "pressed in"
- BECAUSE elevation changes on interaction provide tactile feedback that reinforces the action

### Flat Depth Without Shadows
- WHEN designing in a flat style → DO use color to create depth: lighter backgrounds advance (feel closer), darker backgrounds recede
- WHEN needing subtle card elevation in flat design → DO use solid shadows: `box-shadow: 0 3px 0 hsl(220, 7%, 83%)` — a solid color offset with zero blur
- WHEN creating layers → DO overlap elements across background boundaries (card crossing a dark-to-light section break)

### Overlapping for Layers
- WHEN a card or element feels trapped inside its container → DO offset it to cross boundaries (e.g., `margin-top: -48px` to overlap into the section above)
- WHEN overlapping images → DO add an "invisible border" matching the background color to prevent visual clashing at the intersection

### Text on Images
Images have dynamic brightness — white text works in dark areas but disappears in light areas. Solutions:

| Technique | How | When |
|-----------|-----|------|
| **Dark overlay** | Semi-transparent black layer over the image | Most reliable; works for any image |
| **Contrast reduction** | Reduce image contrast + increase brightness | When you want more image detail visible |
| **Colorize** | Desaturate image, add solid fill with `multiply` blend mode | When you want brand-color consistency |
| **Text shadow** | `text-shadow: 0 0 50px rgba(0,0,0,.5)` — large blur, no offset | When you want to preserve image dynamics |

Combine contrast reduction with text shadow for the best of both worlds.

### Icons at Intended Size
- WHEN icons need to be larger than their source size → DO enclose them in a colored circle/rounded-square background; keep the icon at its designed size
- WHEN showing full-app screenshots → DO NOT scale a 1400px screenshot into a 400px space; instead capture at a smaller breakpoint, or crop to a focused area, or draw a simplified wireframe illustration
- WHEN a logo needs favicon treatment → DO redraw a simplified version at 16px rather than scaling down the full logo

## Anti-Patterns

### One Shadow Fits All
- **Detection:** The same `box-shadow` value on buttons, cards, dropdowns, and modals
- **Fix:** Implement the 5-level system above. Assign shadows by intended elevation.

### Unreadable Text on Images
- **Detection:** White text on a hero image with variable brightness — some text disappears into bright areas
- **Fix:** Add a semi-transparent dark overlay, reduce image contrast, or add text-shadow with large blur radius

### Scaled-Up Icons
- **Detection:** Simple line icons (designed for 16-24px) displayed at 48-64px, looking chunky and disproportionate
- **Fix:** Use icons at their intended size enclosed in colored background shapes, or source icons designed for the target size

### Missing Contact Shadow
- **Detection:** Elevated elements use only a large, soft shadow with no tight shadow near the edges — elements feel like they're floating untethered
- **Fix:** Add the second (ambient) shadow: tight, darker, minimal blur — anchors the element to the surface
