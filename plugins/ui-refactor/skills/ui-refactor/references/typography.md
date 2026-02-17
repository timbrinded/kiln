# Typography

## Mental Model Shifts

**Wrong:** "I'll calculate my type scale using a mathematical ratio (golden ratio, major third, etc.)."
**Right:** Modular scales produce fractional pixel values (31.25px, 39.06px) that render inconsistently across browsers, and the jumps are either too large or too small for interface work. Hand-craft a scale with whole-number values that gives you enough options for UI design.

**Wrong:** "Line-height should be 1.5 everywhere."
**Right:** Line-height is inversely proportional to font size and directly proportional to line width. Body text at 1.5 is a starting point. Headlines need 1.0-1.2 (tighter). Wide paragraphs need up to 2.0 (looser). A single line-height value across all text is always wrong.

**Wrong:** "I'll use `em` units for my type scale so everything scales together."
**Right:** `em` units compound when elements nest. If a `1.25em` element contains a `.875em` child, the computed size is 17.5px — not a value from your scale. Use `px` or `rem` to guarantee you're sticking to the system.

## The Type Scale

A practical hand-crafted scale for interface design:

| Step | Size | Typical Use |
|------|------|-------------|
| `text-xs` | 12px | Fine print, badges, captions |
| `text-sm` | 14px | Secondary text, labels, metadata |
| `text-base` | 16px | Body text (browser default) |
| `text-md` | 18px | Emphasized body, lead paragraphs |
| `text-lg` | 20px | Card titles, section labels |
| `text-xl` | 24px | Section headings |
| `text-2xl` | 30px | Page headings |
| `text-3xl` | 36px | Feature headings |
| `text-4xl` | 48px | Hero headlines |
| `text-5xl` | 60px | Display text |
| `text-6xl` | 72px | Large display text |

## Principles

### Use the Type Scale
- WHEN choosing a font size → DO pick from the scale above; never type an arbitrary value
- WHEN you need something "between" two values → DO pick the closer one and adjust weight or color instead
- BECAUSE more than ~10 distinct sizes in a UI creates visual noise without adding meaningful hierarchy

### Line-Height Is Inversely Proportional to Font Size
- WHEN setting line-height for body text (14-18px) → DO use `line-height: 1.5` to `1.75`
- WHEN setting line-height for sub-headings (20-30px) → DO use `line-height: 1.25` to `1.4`
- WHEN setting line-height for headlines (36px+) → DO use `line-height: 1.0` to `1.2`
- BECAUSE large text with 1.5 line-height creates awkward gaps that make headlines feel disconnected

### Line-Height Is Proportional to Line Width
- WHEN paragraph width is narrow (~45 chars) → DO use shorter line-height (1.5)
- WHEN paragraph width is wide (~75 chars) → DO use taller line-height (1.75-2.0)
- BECAUSE wider lines require more vertical spacing to help eyes track back to the left edge

### Constrain Line Length
- WHEN styling paragraph text → DO set `max-width: 65ch` (or 20-35em) to keep lines at 45-75 characters
- WHEN content area is wider than the optimal reading width → DO constrain paragraphs independently; images and other elements can use the full width
- BECAUSE lines over 75 characters cause readers to lose their place when tracking to the next line

### Font Weight: Keep It Simple
- WHEN building UI → DO use only two weights: normal (400-500) and bold (600-700)
- DO NOT use weights under 400 (light/thin) for body text — they're hard to read at small sizes
- WHEN tempted to use a light weight to de-emphasize → DO use a lighter color or smaller size instead

### Choose Fonts Pragmatically
- WHEN selecting a UI typeface → DO start with the system font stack or a neutral sans-serif (Inter, Roboto, Helvetica Neue)
- WHEN evaluating font quality → DO filter for families with 10+ styles (5+ weights with italics) — more weights generally means more careful craftsmanship
- WHEN unsure → DO sort by popularity on font directories and pick from the top results
- WHEN choosing a display/personality font → DO inspect sites you admire and check what they use

### Baseline Alignment
- WHEN mixing font sizes on the same line (e.g., title + action links) → DO use `align-items: baseline` not `center`
- BECAUSE baseline alignment uses the natural reference line our eyes perceive; vertical centering creates subtle misalignment that looks off

### Letter-Spacing
- WHEN using a body-text font for headlines → DO tighten letter-spacing slightly: `letter-spacing: -0.02em` to `-0.05em`
- WHEN using ALL CAPS text → DO increase letter-spacing: `letter-spacing: 0.05em` to `0.1em`
- WHEN using text at its intended size → DO leave letter-spacing at default; trust the type designer

### Right-Align Numbers in Tables
- WHEN displaying numeric data in columns → DO right-align numbers so decimal points line up vertically
- BECAUSE right-aligned numbers are dramatically easier to compare at a glance

### Link Styling in Context
- WHEN links appear in body text → DO use color + underline to make them pop
- WHEN almost everything is a link (nav, card grid) → DO use subtle emphasis (heavier weight, darker color) not bright blue on every element
- WHEN links are ancillary (footer, metadata) → DO reveal interactive affordance only on hover

## Anti-Patterns

### Font Size Soup
- **Detection:** More than 8-10 distinct font sizes in a single view, often with values like 13px, 15px, 17px, 19px that don't come from a scale
- **Fix:** Map all text to the type scale above. Adjacent sizes in the scale are perceptually different enough that you won't miss the in-between values.

### Single Line-Height
- **Detection:** `line-height: 1.5` applied globally; headlines have awkward gaps, dense UIs feel too airy
- **Fix:** Set line-height per text-size tier: body 1.5-1.75, sub-heading 1.25-1.4, headline 1.0-1.2.

### Em-Based Type Scale
- **Detection:** Font sizes defined in `em` units with nested elements computing unexpected sizes
- **Fix:** Switch to `px` or `rem`. With rem, `1rem = 16px` by default, so the scale maps cleanly.

### Center-Aligned Paragraphs
- **Detection:** Body text longer than 2-3 lines is center-aligned, creating ragged edges that are hard to read
- **Fix:** Left-align anything longer than 2-3 lines. Reserve center alignment for short headings and 1-2 line blocks.
