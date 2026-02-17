# Spacing and Layout

## Mental Model Shifts

**Wrong:** "Add spacing until it doesn't look cramped."
**Right:** Start with way too much whitespace, then remove it until you're happy. What seems like "a little too much" in isolation is usually "just right" in the context of a complete UI. The default should be generous, not minimal.

**Wrong:** "Everything should be sized using a 12-column grid with percentage widths."
**Right:** Grids are a tool, not a religion. Sidebars should have fixed widths optimized for their content. The main content area flexes to fill remaining space. Percentage-based sidebars become too wide on large screens and too narrow on small ones.

**Wrong:** "If I have the space, I should use it."
**Right:** If you only need 600px, use 600px. Stretching content to fill a wide viewport makes interfaces harder to read. Use `max-width` to constrain elements to their optimal size, and only let them shrink when the viewport demands it.

## The Spacing Scale

Use a non-linear scale based on 16px. Smaller values are packed tightly; larger values have bigger jumps. Each step should be at least 25% different from its neighbor.

| Token | Value | Common Use |
|-------|-------|------------|
| `space-1` | 4px | Icon-to-text gap, tight badge padding |
| `space-2` | 8px | Inline padding, compact list items |
| `space-3` | 12px | Button vertical padding, form input padding |
| `space-4` | 16px | Button horizontal padding, card inner padding start |
| `space-5` | 24px | Card padding, gap between related elements |
| `space-6` | 32px | Section inner padding, gap between form groups |
| `space-7` | 48px | Section vertical padding |
| `space-8` | 64px | Large section spacing |
| `space-9` | 96px | Hero vertical padding |
| `space-10` | 128px | Major page section gaps |
| `space-11` | 192px | Landing page section spacing |
| `space-12` | 256px+ | Hero sections, above-the-fold spacing |

## Principles

### Start with Too Much Whitespace
- WHEN laying out a new component → DO add generous padding/margins first, then reduce selectively
- WHEN a dense UI is needed (dashboards) → DO make density a deliberate decision, not the accidental default
- BECAUSE removing whitespace is obvious; knowing when to add more is not

### Use the Spacing Scale
- WHEN choosing any margin, padding, gap, or sizing value → DO pick from the scale above
- WHEN a value feels wrong → DO try the adjacent values (one up, one down) — one will be obviously right
- BECAUSE arbitrary pixel values (13px, 17px, 22px) create subtle inconsistency; the scale makes decisions mechanical

### Don't Fill the Screen
- WHEN content has an optimal width → DO constrain it with `max-width` and center it
- WHEN a form works best at 500px → DO NOT stretch it to match a full-width navigation bar
- WHEN you have extra horizontal space → DO consider splitting into columns rather than stretching

### Fixed Widths Beat Percentage Columns
- WHEN laying out a sidebar + main content → DO give the sidebar a fixed width (e.g., 240px, 280px); let the main area flex
- WHEN a sidebar is percentage-based (e.g., 25%) → DO replace with fixed width — it wastes space on wide screens and breaks on narrow ones
- WHEN sizing elements within components (avatars, icons) → DO use fixed sizes, not percentages

### Max-Width Over Grid Breakpoints
- WHEN a component has an ideal size (e.g., login card at 500px) → DO set `max-width: 500px` and let it fill available space below that
- DO NOT use grid column breakpoints that make the element paradoxically wider at medium than large viewports
- BECAUSE max-width preserves optimal size and only yields when truly necessary

### Proximity Signals Relationship
- WHEN elements form a group (label + input, heading + paragraph) → DO use tighter spacing within the group than between groups
- WHEN label-to-input spacing equals between-group spacing → DO tighten label-to-input (e.g., 8-12px) and widen between-groups (e.g., 24-32px)
- WHEN section headings float ambiguously → DO use more space above the heading than below it

### Relative Sizing Doesn't Scale
- WHEN sizing elements across breakpoints → DO adjust values independently, not proportionally
- WHEN body text shrinks from 18px to 14px on mobile → DO NOT keep headlines at 2.5em (35px is too big for mobile); re-pick headline size independently (20-24px)
- WHEN creating button size variants → DO scale padding non-linearly (large buttons get disproportionately more padding; small buttons get disproportionately less)

## Anti-Patterns

### Ambiguous Spacing
- **Detection:** The gap between a label and its input is the same as the gap between form groups; headings float equidistant from paragraphs above and below; bullet spacing matches line-height
- **Fix:** Tighten within-group spacing, widen between-group spacing. Use asymmetric heading margins (more above, less below).

### Full-Width Everything
- **Detection:** Content stretches edge-to-edge on a 1400px viewport; forms, cards, or text blocks span the full container
- **Fix:** Add `max-width` constraints. Forms: 500-600px. Text blocks: 65ch / 34em. Cards: size to content. Center with auto margins.

### Percentage Sidebars
- **Detection:** Sidebar width defined as `width: 25%` or grid columns like `3 / 12`
- **Fix:** Replace with `width: 240px` (or similar fixed value) and let the main content `flex: 1`.

### Spacing by Feel
- **Detection:** Arbitrary values like `margin-bottom: 13px`, `padding: 17px 22px` that don't come from a system
- **Fix:** Round to the nearest value on the spacing scale. If between two values, try both — one will be clearly better.
