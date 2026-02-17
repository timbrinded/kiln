# Color

## Mental Model Shifts

**Wrong:** "I'll pick 5 harmonious colors from a palette generator and build my site with those."
**Right:** You need far more than 5 colors. A real UI needs: 8-10 grey shades, 5-10 shades of your primary color, and 5-10 shades each of several accent colors (success/green, warning/yellow, danger/red, info/blue). That's 30-50+ color values, all defined upfront.

**Wrong:** "I'll use `lighten()` and `darken()` in my CSS preprocessor to create shade variants."
**Right:** CSS preprocessor functions produce muddy, washed-out results. Define a fixed set of 8-10 shades per color by hand, picking each one deliberately. Name them 100-900 (lightest to darkest) and pick from the system.

**Wrong:** "Grey is grey — zero saturation, just vary the lightness."
**Right:** Greys should have 5-15% saturation tinted toward a hue that matches your design's temperature. Saturate with blue (hue ~210) for cool greys, or yellow/orange (hue ~40) for warm greys. "True grey" (0% saturation) looks sterile.

## Working with HSL

Use HSL (Hue, Saturation, Lightness) instead of hex or RGB. HSL makes color relationships visible:

- **Hue** (0-360°): Position on the color wheel. 0°=red, 60°=yellow, 120°=green, 180°=cyan, 240°=blue, 300°=magenta
- **Saturation** (0-100%): How colorful. 0%=grey, 100%=vivid
- **Lightness** (0-100%): How close to black or white. 0%=black, 50%=pure color, 100%=white

Three colors at `hsl(220, 95%, 34%)`, `hsl(220, 65%, 61%)`, `hsl(220, 69%, 80%)` are obviously the same blue family. In hex (`#03369E`, `#587DD7`, `#9FB9ED`) the relationship is invisible.

## Building a Color Palette

### Step 1: Define Base Colors
For each color family (primary, grey, each accent), pick a **base shade** — the one you'd use as a button background. This becomes shade 500.

### Step 2: Define the Edges
- **Shade 900** (darkest): Dark enough for text on light backgrounds
- **Shade 100** (lightest): Subtle enough for tinted backgrounds (e.g., alert backgrounds)

Test both in context: a simple alert component uses the darkest shade for text and lightest for background.

### Step 3: Fill the Gaps
Pick shades 700 and 300 as midpoints, then fill 800, 600, 400, 200 by bisecting remaining gaps. Each step should be perceptually distinct from its neighbors. The result: a 9-shade scale per color.

### Step 4: Greys
Same process, but start from the edges: darkest grey = your body text color (not pure black), lightest = subtle off-white background. Fill inward. Add 5-15% saturation at hue ~210 (cool) or ~40 (warm).

## Principles

### Boost Saturation at Extremes
- WHEN creating lighter or darker shades → DO increase saturation as lightness moves away from 50%
- BECAUSE at extreme lightness values (10%, 90%), perceived colorfulness drops — constant saturation produces washed-out tints and muddy darks

### Rotate Hue to Change Brightness
- WHEN lightening a color → DO rotate hue slightly toward the nearest bright hue (60°/yellow, 180°/cyan, 300°/magenta) — max 20-30°
- WHEN darkening a color → DO rotate hue slightly toward the nearest dark hue (0°/red, 120°/green, 240°/blue)
- BECAUSE hue rotation changes perceived brightness while preserving color intensity, unlike lightness adjustments that wash out toward white/black

This is especially valuable for yellows: rotating toward orange as you darken creates rich, warm dark shades instead of muddy browns.

### Perceived Brightness by Hue
Different hues have inherently different perceived brightness at the same HSL lightness:

| Hue | Perceived Brightness | Role |
|-----|---------------------|------|
| Yellow (60°) | Highest | Naturally bright |
| Cyan (180°) | High | Naturally bright |
| Magenta (300°) | Medium-high | Naturally bright |
| Red (0°) | Low | Naturally dark |
| Green (120°) | Low | Naturally dark |
| Blue (240°) | Lowest | Naturally dark |

### Warm and Cool Greys
- WHEN choosing grey temperature → DO saturate all greys with a consistent hue at 5-15% saturation
- Cool greys: hue 200-215 (blue tint) → crisp, digital, modern
- Warm greys: hue 35-45 (yellow/orange tint) → soft, organic, approachable
- WHEN lightness approaches extremes (very dark, very light) → DO increase saturation slightly to maintain consistent temperature

### Accessible Contrast
- Normal text (under ~18px): minimum 4.5:1 contrast ratio (WCAG AA)
- Large text (18px+ bold or 24px+ regular): minimum 3:1
- WHEN white text on colored backgrounds needs very dark backgrounds to meet 4.5:1 → DO flip the contrast: use dark colored text on a light colored background instead
- BECAUSE dark colored badges/buttons steal attention; light backgrounds with dark text are subtle and meet AAA ratios easily

### Hue Rotation for Accessible Colored Text
- WHEN colored text on a colored background is too close to white → DO rotate the text hue toward a brighter hue (cyan, magenta, yellow) to gain contrast while staying colorful
- BECAUSE lightening alone makes text indistinguishable from white; hue rotation increases perceived brightness without washing out

### Never Rely on Color Alone
- WHEN using color to communicate state (success, error, positive, negative) → DO also use icons, labels, or patterns
- WHEN using color in charts to distinguish categories → DO prefer lightness/contrast variation over hue variation
- BECAUSE ~8% of men have some form of color vision deficiency; red-green distinction is unreliable

## Anti-Patterns

### Palette Generator UI
- **Detection:** Entire interface uses only 5 flat colors with no shade variations; same blue for text, buttons, backgrounds, and links
- **Fix:** Build a full palette: 8-10 shades per color family, greys included

### CSS Lighten/Darken
- **Detection:** Shade variants generated with `lighten($blue, 20%)` or `color-mix()` rather than hand-picked
- **Fix:** Define fixed shade scales (100-900) per color; pick from the scale

### Pure Grey
- **Detection:** Greys use `hsl(0, 0%, X%)` with zero saturation throughout the interface
- **Fix:** Add 5-15% saturation at a consistent hue. Use 210° for cool or 40° for warm.

### Constant Saturation
- **Detection:** All shades in a color family share the same saturation value, with lightest/darkest shades looking washed out
- **Fix:** Increase saturation as lightness moves toward 0% or 100%
