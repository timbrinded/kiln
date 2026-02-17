# Polish and Finishing Touches

## Mental Model Shifts

**Wrong:** "Borders are the natural way to separate elements."
**Right:** Borders are overused. Before adding a border, try: box-shadow, different background colors, or extra spacing. These alternatives create cleaner separation with less visual noise. When you do use a border, it should be the last resort, not the first instinct.

**Wrong:** "Empty states are just a 'No items found' message — I'll handle them last."
**Right:** Empty states are a user's first interaction with a feature. They're a design opportunity: use illustration, guidance text, and a clear call-to-action. An exciting empty state turns a dead-end into an invitation.

**Wrong:** "A dropdown is a white box with a list of links. A table is rows and columns of text. A radio button is a circle next to a label."
**Right:** Components are just containers — you can put anything in them. Dropdowns can have icons, multiple columns, and supporting text. Tables can combine related data into hierarchical cells with images and badges. Radio buttons can be selectable cards. Don't let conventions limit creativity.

## Principles

### Supercharge the Defaults
- WHEN a design has bulleted lists → DO replace default bullets with icons (checkmarks, arrows, or content-specific icons like padlocks for security features)
- WHEN displaying testimonials → DO "promote" quotation marks into large, colored decorative elements — not just punctuation, but visual anchors
- WHEN styling links → DO go beyond color: try heavier weight, custom thick underlines that partially overlap text, or reveal-on-hover for ancillary links
- WHEN forms use checkboxes/radio buttons → DO replace browser defaults with custom controls using brand colors
- BECAUSE small touches to existing elements create more polish than adding new decorative elements

### Accent Borders for Visual Flair
- WHEN a card, section, or component feels bland → DO add a 3-5px colored accent border:
  - **Top of a card:** `border-top: 4px solid hsl(200, 80%, 50%)`
  - **Left of an alert:** `border-left: 4px solid hsl(200, 80%, 50%)`
  - **Bottom of active nav items:** `border-bottom: 3px solid hsl(200, 80%, 50%)`
  - **Under a headline:** Short decorative line, ~40-50px wide
  - **Top of the entire page:** Full-width colored strip
- BECAUSE a colored rectangle requires zero design talent but significantly elevates perceived quality

### Decorate Backgrounds
- WHEN a section feels monotonous → DO try one of these background treatments:
  - **Color change:** Use a brand color or dark background for feature sections
  - **Subtle gradient:** Two hues no more than 30° apart for energetic feel
  - **Repeating pattern:** Low-contrast geometric pattern (e.g., from Hero Patterns)
  - **Simple shapes:** Dot grids, circles, or geometric elements in specific positions
  - **Illustrations:** Simplified world maps, cityscapes — keep contrast very low
- WHEN using any background decoration → DO keep contrast between pattern and background low enough that text remains easily readable

### Use Fewer Borders
- WHEN creating separation between elements → DO try these alternatives first:
  1. **Box shadow:** `box-shadow: 0 1px 3px hsla(0,0%,0%,.1)` — outlines an element more subtly than a border
  2. **Different background colors:** Adjacent elements with slightly different backgrounds (e.g., alternating row colors `hsl(200, 10%, 94%)`)
  3. **Extra spacing:** Simply increase the gap between elements — no new UI needed
- WHEN a border is the only option → DO use it, but know it was the last resort
- BECAUSE every border adds visual weight and clutter; alternatives create the same separation with less noise

### Design Empty States
- WHEN a feature depends on user-generated content → DO design the empty state as a priority, not an afterthought
- DO include: illustration or icon (grab attention) + explanatory text (provide context) + prominent call-to-action button (guide next step)
- WHEN the empty state has supporting UI (tabs, filters, search) → DO hide those elements — they serve no purpose without data and create clutter
- BECAUSE the empty state is the first impression; a blank screen with "No items found" kills engagement

### Think Outside the Box
- WHEN designing a dropdown → DO consider: multi-column layout, icons, supporting descriptions, grouped sections, featured items with badges
- WHEN designing a table → DO combine related columns with hierarchical typography (name bold + role small underneath), add profile photos, use colored status badges
- WHEN designing radio buttons for important choices → DO consider selectable cards with visual weight, checkmarks, and descriptive text
- BECAUSE components are just containers; the conventional appearance is a starting point, not a constraint

## Concrete Values

### Box-Shadow as Border Alternative
```css
/* Subtle outline effect — replaces border for cards */
box-shadow: 0 1px 3px hsla(0, 0%, 0%, .1);

/* Ring effect — replaces border for form inputs */
box-shadow: 0 0 0 1px hsla(0, 0%, 0%, .1);

/* Alternating row background — replaces border between list items */
background-color: hsl(200, 10%, 94%); /* every other row */
```

### Accent Border Specs
```css
/* Card top accent */
border-top: 4px solid var(--brand-color);

/* Alert left accent */
border-left: 4px solid var(--brand-color);

/* Active nav bottom accent */
border-bottom: 3px solid var(--brand-color);

/* Headline underline accent */
.headline::after {
  content: '';
  display: block;
  width: 48px;
  height: 3px;
  background: var(--brand-color);
  margin-top: 8px;
}
```

## Anti-Patterns

### Border Everything
- **Detection:** Borders between every list item, around every card, inside every form group, around the entire modal
- **Fix:** Remove borders one at a time, replacing with spacing, background color, or box-shadow. You'll find most weren't needed.

### Ignored Empty States
- **Detection:** A feature shows "No [items] found." centered on a blank white page with no illustration, no guidance, and no call-to-action
- **Fix:** Add an illustration/icon, helpful text explaining what goes here, and a prominent button for the first action

### Default Browser Controls
- **Detection:** Checkboxes, radio buttons, and selects use the operating system's default styling — blue squares and circles that don't match the design
- **Fix:** Custom-style with brand colors. Even changing just the selected state color makes a noticeable difference.

### Conventional Component Thinking
- **Detection:** Every dropdown is a plain list, every table is a rigid grid of atomic text values, every radio group is circles-next-to-labels
- **Fix:** Ask "what if this were a [richer component]?" — what if the dropdown had icons and descriptions? What if the table combined related columns? What if the radio buttons were cards?
