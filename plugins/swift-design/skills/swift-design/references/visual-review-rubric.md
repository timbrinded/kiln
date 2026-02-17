# Visual Review Rubric

Five-dimension rubric for evaluating iOS screenshots. Use when a user provides a screenshot or mockup for design assessment.

Research basis: UICrit (CHI 2024) demonstrates that LLM vision models achieve meaningful design critique when given explicit heuristics and structured evaluation dimensions.

---

## How to Use This Rubric

When evaluating a screenshot:

1. Score each dimension 1–5
2. Note specific observations for each
3. Calculate weighted average for overall score
4. Map to letter grade
5. Provide actionable improvement suggestions

---

## Dimension 1: Platform Nativeness (Weight: 30%)

Does this look and feel like a native iOS app?

| Score | Criteria |
|-------|----------|
| 5 | Indistinguishable from Apple's own apps. Tab bar at bottom, SF font, large titles, frosted glass effects, standard navigation patterns |
| 4 | Clearly iOS-native. Uses most platform conventions. Minor deviations are intentional brand choices |
| 3 | Mostly native but some non-standard elements. Mixed platform signals |
| 2 | Noticeably cross-platform feel. Missing key iOS conventions (wrong navigation, non-SF fonts, Android-style elements) |
| 1 | Could be any platform. No recognizable iOS patterns |

### What to look for

**Native signals:**
- Bottom tab bar for primary navigation
- Large title that collapses on scroll
- SF Pro font (or close equivalent)
- Back chevron with previous screen title
- Frosted glass effect on navigation/tab bars
- Standard list row styling with disclosure indicators
- System-style switches, toggles, segmented controls
- Pull-to-refresh on scrollable content

**Non-native signals:**
- Hamburger menu / side drawer
- Custom tab bar without proper safe area handling
- Android-style floating action button (FAB)
- Material Design-style cards with elevation shadows
- Top app bar instead of iOS navigation bar
- Non-system fonts for UI chrome

---

## Dimension 2: Visual Hierarchy (Weight: 25%)

Can you instantly identify the primary content and action?

| Score | Criteria |
|-------|----------|
| 5 | Immediate clarity. Primary action stands out. Clear heading/body/caption levels. Deliberate emphasis and de-emphasis |
| 4 | Clear hierarchy with minor ambiguity. Easy to scan |
| 3 | Hierarchy present but some elements compete for attention. Moderate scan time |
| 2 | Flat hierarchy — most elements have equal visual weight. Hard to scan |
| 1 | Chaotic. No clear entry point. Competing elements confuse scanning |

### What to look for

**Strong hierarchy indicators:**
- One clear primary CTA (prominent color/size)
- Distinct heading/body/caption size levels
- Strategic use of weight (bold for titles, regular for body)
- Secondary content visually recessed (smaller, lighter color)
- Adequate whitespace to separate sections
- F-pattern or Z-pattern reading flow

**Weak hierarchy indicators:**
- Multiple elements same size/weight/color
- No visual distinction between sections
- CTA blends with surrounding content
- All text same size
- Equal emphasis on everything

---

## Dimension 3: Spacing Consistency (Weight: 20%)

Does the layout follow a consistent spatial rhythm?

| Score | Criteria |
|-------|----------|
| 5 | Pixel-perfect grid alignment. Consistent margins throughout. Rhythmic spacing creates visual comfort |
| 4 | Mostly consistent with minor irregularities. Overall feels aligned |
| 3 | Generally aligned but noticeable inconsistencies. Some margins vary without reason |
| 2 | Inconsistent spacing. Margins appear arbitrary. Elements feel misaligned |
| 1 | No spatial system. Random spacing throughout |

### What to look for

**Consistent spacing indicators:**
- Equal margins on left/right edges (~16pt on iPhone)
- Consistent padding within cards/containers
- Regular vertical rhythm between sections
- Aligned baselines across horizontal elements
- Adequate whitespace (roughly 30–40% of screen area)
- Groups of elements share consistent internal spacing

**Inconsistent spacing indicators:**
- Different left/right margins
- Cards with varying internal padding
- Uneven gaps between same-type elements
- Elements that don't align vertically or horizontally
- Screen feels cramped or unevenly distributed
- Too little whitespace (< 20% of screen)

---

## Dimension 4: Color Coherence (Weight: 15%)

Is the color palette intentional and accessible?

| Score | Criteria |
|-------|----------|
| 5 | Cohesive palette. Single accent color. Adequate contrast everywhere. Color used purposefully for meaning |
| 4 | Good palette with minor issues. Mostly consistent accent usage |
| 3 | Acceptable but some color choices feel random. Possible contrast issues |
| 2 | Inconsistent palette. Multiple competing accent colors. Likely contrast violations |
| 1 | No color system. Colors appear arbitrary. Obvious contrast problems |

### What to look for

**Cohesive color indicators:**
- One primary accent color for interactive elements
- Consistent use of accent color across buttons, links, selected states
- Semantic color usage (red for destructive, green for success)
- Sufficient contrast between text and backgrounds
- Dark mode compatibility (no pure black/white)
- Color is never the sole state indicator (always paired with icon/text)

**Incoherent color indicators:**
- Multiple accent colors competing (blue buttons here, green there)
- Low contrast text (light gray on white, dark gray on dark)
- Gratuitous use of color (rainbow-like variety)
- Inconsistent link/button colors
- Hard-to-read text on colored backgrounds
- Gradient overuse (common AI hallmark)

---

## Dimension 5: Typography Discipline (Weight: 10%)

Is the type system controlled and purposeful?

| Score | Criteria |
|-------|----------|
| 5 | 2–3 clear type levels. Consistent font family. Proper weight hierarchy. Comfortable reading size |
| 4 | Good type system with minor inconsistencies. Mostly controlled |
| 3 | Acceptable but more than 4 type levels visible. Some inconsistencies |
| 2 | Many type sizes/weights with no clear system. Hard to identify hierarchy through type alone |
| 1 | Chaotic typography. Random sizes and weights. Unreadable or uncomfortable |

### What to look for

**Disciplined typography indicators:**
- 2–3 visible type sizes per screen (max 4)
- Clear weight hierarchy (semibold headings, regular body)
- System font or a single consistent custom font
- Comfortable reading size (≥ 11pt)
- Consistent alignment (left-aligned text blocks)
- Proper line spacing for readability

**Undisciplined typography indicators:**
- 5+ visible type sizes
- Random weight usage
- Multiple font families on same screen
- Text too small to read comfortably
- Mixed alignments without purpose
- Cramped or excessive line spacing

---

## Scoring & Grading

### Weighted Average Calculation

```
Score = (Nativeness × 0.30) + (Hierarchy × 0.25) + (Spacing × 0.20) + (Color × 0.15) + (Typography × 0.10)
```

### Score to Grade Mapping

| Score | Grade | Assessment |
|-------|-------|------------|
| 4.5–5.0 | **A** | Excellent — Apple Design Award caliber |
| 3.5–4.4 | **B** | Good — professional quality, minor improvements possible |
| 2.5–3.4 | **C** | Acceptable — clear issues but functional |
| 1.5–2.4 | **D** | Poor — significant design problems |
| 1.0–1.4 | **F** | Failing — fundamental redesign needed |

---

## Output Format

```
## Visual Design Review — Grade: [B]

### Dimension Scores
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Platform Nativeness | 4 | 30% | 1.20 |
| Visual Hierarchy | 3 | 25% | 0.75 |
| Spacing Consistency | 4 | 20% | 0.80 |
| Color Coherence | 4 | 15% | 0.60 |
| Typography Discipline | 3 | 10% | 0.30 |
| **Total** | | | **3.65** |

### Observations
**Platform Nativeness (4/5)**:
- Tab bar correctly positioned at bottom
- Using SF font for UI elements
- Missing: large title on root screen, frosted glass nav bar

**Visual Hierarchy (3/5)**:
- Primary CTA is identifiable but doesn't stand out enough
- Body and secondary text are same visual weight
- Suggestion: increase size/weight contrast between title and body

[...continue for each dimension...]

### Top 3 Improvements
1. [Highest impact fix]
2. [Second priority]
3. [Third priority]
```

---

## Limitations

Vision-based review reliably detects:
- Gross layout issues and inconsistent spacing
- Missing platform conventions
- Flat visual hierarchy
- Color contrast problems (approximate)
- Typography confusion

Vision-based review struggles with:
- Exact pixel-level alignment
- Precise contrast ratio calculations
- Interactive behavior across states
- Animation quality
- Haptic feedback presence
- Dark mode compatibility (unless screenshot provided)

For precise checks, supplement with code-based review using the 40-rule checklist.
