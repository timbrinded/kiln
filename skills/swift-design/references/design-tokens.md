# SwiftUI Design Tokens

Standard iOS design tokens for spacing, typography, color, and corner radii. Use these when generating SwiftUI code to ensure consistency and HIG compliance.

---

## Spacing (8-point grid)

Apple uses an 8-point grid. SwiftUI's `.padding()` defaults to ~16pt on all edges.

```swift
enum Spacing {
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 16   // System default padding
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
    static let xxl: CGFloat = 48
}
```

### Standard measurements

| Context | Value | Notes |
|---------|-------|-------|
| Screen-edge margin (iPhone) | 16pt | Standard horizontal inset |
| Screen-edge margin (iPad) | 20pt | Wider for larger screens |
| Element-to-element (tight) | 4pt | Icon-to-text in labels |
| Element-to-element (standard) | 8pt | VStack default text spacing |
| Section spacing | 24pt | Between logical groups |
| Large section spacing | 32–48pt | Between major sections |
| List row default height | 44pt | Minimum for accessibility |
| Navigation bar height | 44pt | Standard nav bar |
| Tab bar height | 49pt | Standard tab bar |
| Status bar (Dynamic Island) | 59pt | iPhone 14 Pro+ |
| Home indicator area | 34pt | Bottom safe area |

### VStack/HStack default spacing

When `spacing` is omitted, SwiftUI applies **adaptive spacing** (~8pt for text-to-text in VStack). Explicit `spacing: 0` is required for zero spacing.

```swift
// Adaptive spacing (system decides)
VStack {
    Text("Title")
    Text("Subtitle")  // ~8pt gap
}

// Zero spacing (must be explicit)
VStack(spacing: 0) {
    Text("Title")
    Text("Subtitle")  // 0pt gap
}

// Custom grid-aligned spacing
VStack(spacing: Spacing.md) {
    Text("Title")
    Text("Subtitle")  // 16pt gap
}
```

---

## Typography

### Dynamic Type scale (default "Large" size category)

| Text Style | Size | Weight | Leading | Usage |
|------------|------|--------|---------|-------|
| `.largeTitle` | 34pt | Regular | 41pt | Screen titles (collapsing nav bar) |
| `.title` | 28pt | Regular | 34pt | Section headers |
| `.title2` | 22pt | Regular | 28pt | Subsection headers |
| `.title3` | 20pt | Regular | 25pt | Card titles |
| `.headline` | 17pt | **Semibold** | 22pt | Emphasized body text, row titles |
| `.body` | 17pt | Regular | 22pt | Primary content |
| `.callout` | 16pt | Regular | 21pt | Secondary descriptions |
| `.subheadline` | 15pt | Regular | 20pt | List subtitles |
| `.footnote` | 13pt | Regular | 18pt | Timestamps, metadata |
| `.caption` | 12pt | Regular | 16pt | Labels, badges |
| `.caption2` | 11pt | Regular | 13pt | **Absolute minimum readable size** |

### Font design variants

```swift
// Default — SF Pro Text/Display
Text("Standard").font(.body)

// Rounded — friendly, metric-heavy contexts (fitness, counters)
Text("Steps: 10,432").font(.title).fontDesign(.rounded)

// Monospaced — code and tabular data only
Text("func hello()").font(.body).fontDesign(.monospaced)

// Serif — editorial, long-form reading
Text("Article body").font(.body).fontDesign(.serif)
```

SF Pro Text is used for sizes ≤19pt. SF Pro Display auto-activates at ≥20pt.

### Hierarchy guideline

Use **2–3 levels** per screen, maximum 4:
- **Level 1**: Title (`.title` or `.largeTitle`)
- **Level 2**: Body (`.body` or `.headline`)
- **Level 3**: Secondary (`.subheadline`, `.footnote`, or `.caption`)
- **Level 4** (sparingly): Metadata (`.caption2`)

### ScaledMetric for custom dimensions

```swift
struct CardView: View {
    @ScaledMetric(relativeTo: .body) private var iconSize: CGFloat = 24
    @ScaledMetric(relativeTo: .body) private var cardPadding: CGFloat = 16

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "star")
                .font(.system(size: iconSize))
            Text("Content")
        }
        .padding(cardPadding)
    }
}
```

---

## Color

### Semantic colors (auto-adapt to light/dark/high-contrast)

```swift
// Text
Color.primary          // Label text (black/white)
Color.secondary        // Secondary label text (gray)

// Backgrounds
Color(.systemBackground)           // Primary background
Color(.secondarySystemBackground)  // Grouped/card background
Color(.tertiarySystemBackground)   // Nested background

// Grouped backgrounds (for grouped-style lists)
Color(.systemGroupedBackground)
Color(.secondarySystemGroupedBackground)
Color(.tertiarySystemGroupedBackground)

// Fills (for interactive elements)
Color(.systemFill)
Color(.secondarySystemFill)
Color(.tertiarySystemFill)
Color(.quaternarySystemFill)

// Separators
Color(.separator)       // Standard separator
Color(.opaqueSeparator) // Non-translucent separator
```

### System accent colors

```swift
Color.accentColor   // App-wide accent (set in Asset Catalog)
Color.blue          // #007AFF — links, actions
Color.green         // #34C759 — success, positive
Color.red           // #FF3B30 — destructive, errors
Color.orange        // #FF9500 — warnings
Color.yellow        // #FFCC00 — highlights
Color.indigo        // #5856D6 — secondary accent
Color.teal          // #5AC8FA — informational
```

### Custom color definition (Asset Catalog pattern)

Name colors semantically, not visually:

| Good Name | Bad Name | Why |
|-----------|----------|-----|
| `TextPrimary` | `Grey900` | Semantic names survive theme changes |
| `Surface` | `White` | Works in dark mode |
| `AccentBrand` | `Blue` | Maintains meaning if brand color changes |
| `DestructiveAction` | `Red` | Intent-driven |

Every custom color must have **Any Appearance** and **Dark** variants in the Asset Catalog. Optional **High Contrast** variants for accessibility.

---

## Corner Radii

```swift
enum Radius {
    static let sm: CGFloat = 6    // Small chips, tags
    static let md: CGFloat = 12   // Cards, buttons
    static let lg: CGFloat = 20   // Large cards, sheets
    static let xl: CGFloat = 28   // Bottom sheets, modals
}
```

### System reference radii

| Element | Radius | Notes |
|---------|--------|-------|
| Small button | ~6pt | Compact interactive elements |
| Standard card | ~12pt | Most common container radius |
| App icon (display) | Continuous superellipse | Not a simple cornerRadius |
| Bottom sheet | ~20pt | System `.sheet()` presentation |
| Search bar | ~10pt | Standard search field |
| Text field | ~8pt | Input field border |

Use `.clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))` for Apple's smooth "squircle" corners.

---

## Environment-Based Token Injection

### iOS 17+ with @Observable

```swift
@Observable
class DesignTokens {
    var spacing = Spacing.self
    var radius = Radius.self
}
```

### iOS 18+ with @Entry macro

```swift
extension EnvironmentValues {
    @Entry var compactSpacing: Bool = false
}

// Usage
struct AdaptiveCard: View {
    @Environment(\.compactSpacing) var compactSpacing

    var body: some View {
        VStack(spacing: compactSpacing ? Spacing.sm : Spacing.md) {
            // ...
        }
    }
}
```

---

## Generation Checklist

When generating new SwiftUI views, verify:

- [ ] All spacing values from the 8pt grid set
- [ ] Font styles are semantic (`.body`, `.headline`, etc.)
- [ ] No font size below 11pt
- [ ] 2–3 type levels per screen
- [ ] Colors are semantic or from Asset Catalog
- [ ] No `Color.black` or `Color.white`
- [ ] Corner radii from the standard set
- [ ] `@ScaledMetric` for custom dimensions that should scale
