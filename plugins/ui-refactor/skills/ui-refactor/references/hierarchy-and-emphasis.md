# Hierarchy and Emphasis

## Mental Model Shifts

**Wrong:** "To make something stand out, make it bigger and bolder."
**Right:** Emphasize by de-emphasizing. When the hero element doesn't pop, the problem is usually that competing elements are too loud. Make them quieter — softer colors, lighter weights, smaller sizes — and the hero stands out without needing to scream.

**Wrong:** "Font size is how you create hierarchy."
**Right:** Size is one of three tools. Weight and color often do a better job. A bold 16px title with grey 14px supporting text creates clearer hierarchy than a 24px title with 14px body — without the size disparity that makes layouts feel unbalanced.

**Wrong:** "Every piece of data needs a label."
**Right:** Labels are a last resort. `janedoe@example.com` is self-evidently an email. `(555) 765-4321` is a phone number. `$19.99` is a price. When format or context makes the meaning clear, eliminate the label entirely. When a label is truly needed, combine it: "12 left in stock" instead of "In stock: 12".

## Principles

### Three-Tier Content Hierarchy
- WHEN styling any content block → DO establish exactly 3 visual tiers:
  - **Primary:** Dark color (e.g., `hsl(210, 20%, 16%)`) + bold weight (600-700) — headlines, names, key values
  - **Secondary:** Medium grey (e.g., `hsl(210, 12%, 45%)`) + normal weight (400-500) — body text, descriptions
  - **Tertiary:** Light grey (e.g., `hsl(210, 10%, 62%)`) + normal weight — timestamps, fine print, metadata
- BECAUSE more than 3 tiers creates confusion; fewer than 3 makes everything compete

### Emphasize by De-Emphasizing
- WHEN a primary element doesn't stand out enough → DO soften the competing elements first (lighter color, reduced weight) before making the hero louder
- WHEN a sidebar competes with main content → DO remove its background color; let it sit directly on the page background
- BECAUSE reducing noise is more effective than increasing signal

### Weight and Color Over Size
- WHEN creating hierarchy → DO use font weight (400 vs 600-700) and color (dark vs grey) as primary tools; reserve size differences for distinct structural levels (heading vs body)
- WHEN de-emphasizing text → DO use a lighter color, not a smaller font or a weight under 400 (light weights are hard to read at body sizes)
- BECAUSE size-only hierarchy leads to oversized primaries and undersized secondaries

### On Colored Backgrounds
- WHEN placing de-emphasized text on a colored background → DO NOT use literal grey or white with reduced opacity
- DO hand-pick a color with the same hue as the background, adjusting saturation and lightness
- BECAUSE grey on colored backgrounds looks muddy; reduced-opacity white looks washed out and lets textures bleed through

### Labels Strategy
- WHEN data format is self-evident (email, phone, price, date) → DO omit the label entirely
- WHEN context makes meaning clear (department name under a person's name) → DO omit the label
- WHEN a label is needed → DO combine it into natural language: "3 bedrooms" not "Bedrooms: 3"
- WHEN labels are truly necessary (dashboard metrics) → DO de-emphasize the label (smaller, lighter, uppercase) and make the value the hero
- WHEN users scan for labels (spec sheets) → DO emphasize the label slightly, but don't de-emphasize data too much

### Separate Visual Hierarchy from Document Hierarchy
- WHEN using semantic HTML headings (h1-h6) → DO style them based on visual importance, not HTML level
- WHEN a page title is supportive context (e.g., "Manage Account") → DO make it small; the actual content below is what matters
- BECAUSE `<h1>` doesn't have to be large — choose elements for semantics, style for hierarchy

### Button Hierarchy
- WHEN a page has multiple actions → DO style them by importance, not semantics:
  - **Primary action:** Solid, high-contrast background
  - **Secondary action:** Outline or lower-contrast background
  - **Tertiary action:** Styled as a link (no background or border)
- WHEN a destructive action is not the primary action → DO give it secondary or tertiary treatment; reserve bold red for the confirmation dialog where it becomes the primary action
- BECAUSE red "Delete" buttons styled as primary create visual noise when deletion isn't the page's main purpose

### Balance Weight and Contrast
- WHEN icons feel too heavy next to text → DO reduce the icon's contrast (use a softer color like `hsl(210, 20%, 68%)` instead of near-black)
- WHEN thin borders (1px) are too subtle in a soft color → DO increase border width to 2px rather than darkening the color
- BECAUSE weight and contrast are counterbalances: reduce contrast to lighten heavy elements, increase weight to emphasize low-contrast elements

## Anti-Patterns

### Wall of Content
- **Detection:** Every text element in a section has the same size, weight, and color
- **Fix:** Apply three-tier hierarchy: darken + bold the primary, soften the secondary, lighten the tertiary

### Naive Label:Value
- **Detection:** Repeated "Label: Value" pairs where format or context already communicates meaning
- **Fix:** Remove labels where possible; combine into natural phrases where needed

### Semantic Button Styling
- **Detection:** Delete button is big, red, and bold on a page where it's not the primary action
- **Fix:** Restyle as tertiary (link); move bold red treatment to confirmation dialog

### Grey on Color
- **Detection:** Literal grey text (`hsl(0, 0%, 75%)`) on a colored background
- **Fix:** Hand-pick a tint of the background hue at higher lightness (e.g., same hue, 70-84% lightness)
