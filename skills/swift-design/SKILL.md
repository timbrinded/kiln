---
name: swift-design
description: >
  This skill should be used when the user asks to "review SwiftUI code",
  "check HIG compliance", "audit iOS design quality", "generate SwiftUI views",
  "create an iOS screen", "improve SwiftUI design", "iterate on SwiftUI feedback",
  "fix accessibility in SwiftUI", "modernize SwiftUI code", "check deprecated APIs",
  "review this screenshot for iOS design", "add animations to SwiftUI",
  "add haptics to SwiftUI", or is working with SwiftUI views where design quality,
  accessibility, or Apple HIG compliance matters. Provides 40 enforceable rules,
  design token references, modern API guidance, animation/haptics patterns,
  and visual review rubrics for iOS design excellence.
version: 0.1.0
---

# SwiftUI Design Excellence

Encode Apple's Human Interface Guidelines as machine-enforceable rules for SwiftUI code review, generation, and iteration. Target: iOS 17+ by default (configurable via settings).

## Operational Modes

### Review Mode

Accept SwiftUI code (files or inline) and evaluate against 40 enforceable rules.

**Process:**
1. Read the target SwiftUI file(s)
2. Check settings for iOS target version and strictness — read `.claude/swift-design.local.md` if it exists (see Settings section below)
3. Load `references/review-checklist.md` for the complete rule set
4. Evaluate code against each applicable rule category in priority order:
   - Modern API compliance (M1–M6) — load `references/deprecated-apis.md` for replacement patterns
   - Accessibility (A1–A7) — load `references/accessibility-guide.md` for detailed checks
   - Platform idioms (P1–P6) — load `references/component-patterns.md` for correct patterns
   - Spacing & layout (S1–S7)
   - Typography (T1–T5)
   - Color & contrast (C1–C4)
5. Calculate letter grade per the rubric in `references/review-checklist.md`
6. Output findings grouped by severity: 🔴 Critical → 🟡 Warning → 🔵 Suggestion → 🟢 Praise
7. Each finding: rule ID, file:line, description, concrete fix

**When iterating on existing code** (review + feedback argument):
- Focus analysis on the areas mentioned in feedback
- Load the relevant reference file for that area
- Apply targeted improvements as a minimal diff
- Re-run the checklist on modified code
- Report what changed and the new grade

### Visual Review Mode

Accept a screenshot or mockup of an iOS screen.

**Process:**
1. Load `references/visual-review-rubric.md`
2. Evaluate the screenshot across 5 dimensions:
   - Platform nativeness (30% weight)
   - Visual hierarchy (25%)
   - Spacing consistency (20%)
   - Color coherence (15%)
   - Typography discipline (10%)
3. Score each dimension 1–5 with specific observations
4. Calculate weighted average and map to letter grade
5. Provide top 3 actionable improvements

### Generation Mode

Accept a natural language description (or screenshot as reference) and produce HIG-compliant SwiftUI code.

**Process:**
1. Load `references/design-tokens.md` for spacing, typography, color tokens
2. Load `references/hig-rules.md` for generation guidelines
3. Load `references/component-patterns.md` for structural patterns
4. Load `references/deprecated-apis.md` to ensure modern API usage
5. Generate SwiftUI code that:
   - Uses semantic font styles and colors
   - Follows 8pt spacing grid via design tokens
   - Handles all view states (loading, empty, error, content)
   - Includes accessibility labels and proper tap targets
   - Uses `@Observable`, `NavigationStack`, `Tab` API
   - Applies spring animations and appropriate haptics
6. Self-verify output against `references/review-checklist.md`
7. Output the code plus a design specification noting:
   - Type hierarchy used (which text styles, why)
   - Spacing choices (which tokens, why)
   - Color decisions (which semantic colors, why)
   - Accessibility considerations applied

## Settings

Read settings from `.claude/swift-design.local.md` if present:

```yaml
---
ios-target: 17
strictness: standard
---
```

**ios-target** (16 | 17 | 18, default: 17):
- iOS 16: M2 (@Observable) becomes suggestion, M3 (Tab API) becomes suggestion
- iOS 17: M3 (Tab API) becomes suggestion, all others at listed severity
- iOS 18: All 40 rules at their listed severity

**strictness** (relaxed | standard | strict, default: standard):
- relaxed: Only 🔴 Critical rules reported
- standard: 🔴 Critical + 🟡 Warning reported, 🔵 Suggestions at end
- strict: All findings reported, grade penalizes suggestions

## Key Anti-Patterns

The most common failures in AI-generated SwiftUI — check these first:

1. **NavigationStack wrapping TabView** (P2) — tab bar disappears during navigation
2. **NavigationView instead of NavigationStack** (M1) — deprecated since iOS 16
3. **ObservableObject instead of @Observable** (M2) — causes unnecessary re-renders
4. **Color.black/Color.white** (C1) — invisible in dark mode
5. **Hardcoded font sizes** (T1) — breaks Dynamic Type
6. **.onTapGesture instead of Button** (A4) — invisible to VoiceOver

See `references/anti-patterns.md` for the complete anti-pattern catalog with examples.

## Reference Files

Consult these for detailed guidance:

| File | Contents | When to Load |
|------|----------|-------------|
| `references/review-checklist.md` | 40 rules, severity, grade rubric | Every review |
| `references/deprecated-apis.md` | Before/after for every deprecated API | Reviews with modern API violations, generation |
| `references/design-tokens.md` | Spacing, typography, color, radius tokens | Generation mode |
| `references/hig-rules.md` | HIG fundamentals for generation | Generation mode |
| `references/accessibility-guide.md` | VoiceOver, Dynamic Type, contrast, motor | Reviews with accessibility issues |
| `references/component-patterns.md` | TabView, NavigationStack, List, Form, states | Reviews with structural issues, generation |
| `references/animation-guide.md` | Spring animations, haptics, micro-interactions | Generation, animation reviews |
| `references/visual-review-rubric.md` | 5-dimension screenshot evaluation | Visual review mode |
| `references/anti-patterns.md` | AI-generated code smells and fixes | Quick checks, all reviews |
