# SwiftUI Design Review Checklist

40 enforceable rules organized by category. Each rule has:
- **ID**: Category prefix + number (e.g., S1, T2, M3)
- **Severity**: 🔴 Critical | 🟡 Warning | 🔵 Suggestion
- **iOS**: Minimum iOS version where rule applies

Severity is calibrated to the default iOS 17+ target. Rules marked with an iOS version higher than the configured target become 🔵 Suggestions instead of their listed severity.

---

## Spacing & Layout (S1–S7)

| ID | Rule | Severity | iOS |
|----|------|----------|-----|
| S1 | All explicit spacing values must be multiples of 4pt (preferably 8pt). Allowed set: {4, 8, 12, 16, 20, 24, 32, 40, 48} | 🟡 Warning | 14+ |
| S2 | No "magic number" padding — use `.padding()` (system default) or values from the allowed set | 🟡 Warning | 14+ |
| S3 | VStack/HStack nesting must not exceed 4 levels — extract subviews beyond this | 🟡 Warning | 14+ |
| S4 | No nested `ScrollView` instances with the same scroll axis | 🔴 Critical | 14+ |
| S5 | `GeometryReader` inside `ScrollView` must have an explicit `.frame()` constraint | 🔴 Critical | 14+ |
| S6 | Prefer `containerRelativeFrame` over `GeometryReader` for responsive sizing | 🔵 Suggestion | 17+ |
| S7 | Use `LazyVStack`/`LazyHStack` in `ScrollView` for collections exceeding ~20 items | 🟡 Warning | 14+ |

### How to check

- **S1/S2**: Search for `.padding(` and `.spacing(` with numeric literals. Flag values not in {4, 8, 12, 16, 20, 24, 32, 40, 48}.
- **S3**: Count nested VStack/HStack/ZStack depth in each `body`. Flag >4 levels.
- **S4**: Search for `ScrollView` inside `ScrollView` with matching axis (both `.vertical` or both `.horizontal`).
- **S5**: Search for `GeometryReader` inside `ScrollView` without a sibling/child `.frame(` modifier.
- **S6**: Search for `GeometryReader` usage; suggest `containerRelativeFrame` when the reader only uses `proxy.size`.
- **S7**: Search for `VStack`/`HStack` inside `ScrollView` containing `ForEach` with >20 items or dynamic data.

---

## Typography (T1–T5)

| ID | Rule | Severity | iOS |
|----|------|----------|-----|
| T1 | Use semantic font styles (`.font(.body)`) not hardcoded sizes (`.font(.system(size: 17))`) | 🔴 Critical | 14+ |
| T2 | No font size below 11pt anywhere in the app | 🔴 Critical | 14+ |
| T3 | Maximum 3–4 distinct text styles per screen/view | 🟡 Warning | 14+ |
| T4 | Use `@ScaledMetric` for custom dimensions that should scale with Dynamic Type | 🔵 Suggestion | 14+ |
| T5 | At accessibility type sizes, horizontal layouts must switch to vertical using `AnyLayout` or `ViewThatFits` | 🟡 Warning | 16+ |

### How to check

- **T1**: Search for `.system(size:` — flag any hardcoded font size. Correct pattern: `.font(.body)`, `.font(.headline)`, etc.
- **T2**: Search for `.system(size:` where size < 11. Also check `.font(.custom(` with size < 11.
- **T3**: Count distinct `.font(` modifiers per View struct. Flag if >4 unique styles.
- **T4**: Search for `CGFloat` constants used for frame sizes/padding that don't use `@ScaledMetric`.
- **T5**: Search for `HStack` containing Text views. Flag if no `ViewThatFits` or `AnyLayout` wrapper exists for Dynamic Type adaptation.

---

## Color & Contrast (C1–C4)

| ID | Rule | Severity | iOS |
|----|------|----------|-----|
| C1 | No `Color.black` or `Color.white` for text or backgrounds — use semantic colors | 🔴 Critical | 14+ |
| C2 | No inline `Color(red:green:blue:)` — define colors in Asset Catalog with dark mode variants | 🟡 Warning | 14+ |
| C3 | Text contrast ratio ≥ 4.5:1 for text <18pt, ≥ 3:1 for text ≥18pt (WCAG AA) | 🔴 Critical | 14+ |
| C4 | Color must never be the sole indicator of state — pair with icons, text, or shapes | 🔴 Critical | 14+ |

### How to check

- **C1**: Search for `Color.black`, `Color.white`, `.black`, `.white` used as foreground/background. Acceptable: `Color(.label)`, `Color(.systemBackground)`, `.primary`, `.secondary`.
- **C2**: Search for `Color(red:`, `Color(hue:`, `Color(#`. Flag inline color definitions. Acceptable: `Color("AssetName")`, `Color(.systemColor)`.
- **C3**: Cannot be fully verified via static analysis. Flag combinations of light text on light backgrounds or dark text on dark backgrounds when using non-semantic colors.
- **C4**: Search for conditional color changes (e.g., `.foregroundStyle(isActive ? .green : .red)`) without accompanying icon/text/shape changes.

---

## Accessibility (A1–A7)

| ID | Rule | Severity | iOS |
|----|------|----------|-----|
| A1 | Every interactive element must have an `accessibilityLabel` (unless text content is self-describing) | 🔴 Critical | 14+ |
| A2 | All tap targets ≥ 44×44pt — check `.frame()` and `.contentShape()` | 🔴 Critical | 14+ |
| A3 | Minimum 8pt spacing between adjacent interactive elements | 🟡 Warning | 14+ |
| A4 | Use `Button` instead of `.onTapGesture()` for tappable elements | 🔴 Critical | 14+ |
| A5 | Decorative images must have `.accessibilityHidden(true)` | 🟡 Warning | 14+ |
| A6 | Check for `@Environment(\.accessibilityReduceMotion)` when animations are present | 🟡 Warning | 14+ |
| A7 | Wrap content in `ScrollView` for accessibility type sizes to prevent clipping | 🔵 Suggestion | 14+ |

### How to check

- **A1**: Search for `Button`, `Toggle`, `Slider`, `Stepper` without `.accessibilityLabel(`. Buttons with `Label` or visible text are exempt.
- **A2**: Search for Button/interactive elements with `.frame(width:` or `.frame(height:` < 44. Also flag icon-only buttons without `.frame(minWidth: 44, minHeight: 44)` or `.contentShape(Rectangle())`.
- **A3**: Search for adjacent Button/interactive elements with spacing < 8pt.
- **A4**: Search for `.onTapGesture` on non-Button views. Flag with: "Replace with Button for VoiceOver, keyboard, and eye-tracking compatibility."
- **A5**: Search for `Image(` or `Image(systemName:` that are decorative (no meaningful content) without `.accessibilityHidden(true)`.
- **A6**: Search for `.animation(`, `withAnimation`, `.transition(`, `.matchedGeometryEffect`. If present, check for `@Environment(\.accessibilityReduceMotion)`.
- **A7**: Check if root view body is wrapped in ScrollView. Particularly important for views with multiple text blocks.

---

## Modern API Compliance (M1–M6)

| ID | Rule | Severity | iOS |
|----|------|----------|-----|
| M1 | `NavigationStack` not `NavigationView` | 🔴 Critical | 16+ |
| M2 | `@Observable` not `ObservableObject`/`@Published`/`@StateObject` | 🔴 Critical | 17+ |
| M3 | New `Tab` API not `.tabItem()` | 🔵 Suggestion | 18+ |
| M4 | `async/await` not completion handlers for new code | 🟡 Warning | 15+ |
| M5 | `.foregroundStyle()` not `.foregroundColor()` | 🟡 Warning | 15+ |
| M6 | SF Symbols sized with `.font()` or `.imageScale()` not `.resizable()` | 🟡 Warning | 14+ |

### How to check

- **M1**: Search for `NavigationView`. Replace with `NavigationStack` (or `NavigationSplitView` for multi-column).
- **M2**: Search for `ObservableObject`, `@Published`, `@StateObject`, `@ObservedObject`. Replace with `@Observable` class + `@State`/direct reference.
- **M3**: Search for `.tabItem(`. Replace with `Tab("Title", systemImage:) { }` syntax. Only critical at iOS 18+.
- **M4**: Search for completion handler patterns (`completion:`, `@escaping (Result` etc.) in new code.
- **M5**: Search for `.foregroundColor(`. Replace with `.foregroundStyle()`.
- **M6**: Search for `Image(systemName:` followed by `.resizable()`. SF Symbols should use `.font()` or `.imageScale()`.

---

## Platform Idioms (P1–P6)

| ID | Rule | Severity | iOS |
|----|------|----------|-----|
| P1 | Bottom tab bar for primary navigation (2–5 tabs), not hamburger/drawer menus | 🔴 Critical | 14+ |
| P2 | `NavigationStack` inside each tab, not wrapping `TabView` | 🔴 Critical | 14+ |
| P3 | Swipe-to-go-back gesture must not be broken by custom gestures | 🟡 Warning | 14+ |
| P4 | Large title with `.navigationBarTitleDisplayMode(.large)` on primary screens | 🔵 Suggestion | 14+ |
| P5 | Alert buttons must use `.cancel` and `.destructive` roles for correct ordering | 🟡 Warning | 15+ |
| P6 | Use system components (`List`, `Form`, `.searchable()`, `.refreshable()`) over custom alternatives | 🔵 Suggestion | 15+ |

### How to check

- **P1**: Search for drawer/hamburger menu implementations (sidebar toggles, custom slide-out menus). Flag if used as primary navigation on iPhone.
- **P2**: Search for `NavigationStack { TabView` or `NavigationView { TabView`. The correct pattern is `TabView { Tab { NavigationStack { } } }`.
- **P3**: Search for `.gesture(DragGesture()` or `.simultaneousGesture(DragGesture()` that could conflict with the system back gesture (left-edge swipe).
- **P4**: Check primary/root views for `.navigationBarTitleDisplayMode(.large)`. Its absence on root screens is a suggestion.
- **P5**: Search for `.alert(` with `Button("Cancel")` or `Button("Delete")` without `.role(.cancel)` or `.role(.destructive)`.
- **P6**: Search for custom scroll-based lists when `List` or `Form` would be more appropriate. Flag custom pull-to-refresh when `.refreshable()` exists.

---

## Letter Grade Rubric

Calculate the grade from weighted category scores:

| Category | Weight | Score Calculation |
|----------|--------|-------------------|
| Modern API (M) | 25% | Deduct 15pts per 🔴, 8pts per 🟡, 3pts per 🔵 |
| Accessibility (A) | 25% | Deduct 15pts per 🔴, 8pts per 🟡, 3pts per 🔵 |
| Platform Idioms (P) | 20% | Deduct 15pts per 🔴, 8pts per 🟡, 3pts per 🔵 |
| Spacing & Layout (S) | 15% | Deduct 15pts per 🔴, 8pts per 🟡, 3pts per 🔵 |
| Typography (T) | 10% | Deduct 15pts per 🔴, 8pts per 🟡, 3pts per 🔵 |
| Color & Contrast (C) | 5% | Deduct 15pts per 🔴, 8pts per 🟡, 3pts per 🔵 |

Each category starts at 100 and deductions are applied. The weighted sum produces a final score:

| Score | Grade | Meaning |
|-------|-------|---------|
| 90–100 | **A** | Excellent — HIG-compliant, accessible, modern |
| 80–89 | **B** | Good — minor issues, mostly compliant |
| 70–79 | **C** | Acceptable — notable issues but functional |
| 60–69 | **D** | Poor — significant violations, needs rework |
| <60 | **F** | Failing — critical violations, not ship-ready |

---

## Review Output Format

Present findings grouped by severity, then by category:

```
## SwiftUI Design Review — Grade: [B]

### 🔴 Critical (must fix)
- **[M1]** `NavigationView` → `NavigationStack` — file.swift:23
  Fix: Replace `NavigationView { ... }` with `NavigationStack { ... }`
- **[P2]** NavigationStack wraps TabView — file.swift:10
  Fix: Move NavigationStack inside each Tab

### 🟡 Warning (should fix)
- **[S1]** Non-standard spacing value 13 — file.swift:45
  Fix: Use `12` or `16` (nearest 4pt-grid values)

### 🔵 Suggestion (consider)
- **[P4]** Missing large title on root screen — HomeView.swift:8
  Fix: Add `.navigationBarTitleDisplayMode(.large)`

### 🟢 Praise
- Correct use of semantic colors throughout
- Proper `@Observable` usage with `@State`
- Accessible button labels on all interactive elements
```

Priority order when reporting: Modern API → Accessibility → Platform Idioms → Layout → Typography → Color
