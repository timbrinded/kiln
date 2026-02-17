# SwiftUI Accessibility Guide

Accessibility is a first-class requirement, not an afterthought. Apple Design Award winners universally share deep accessibility support. This guide covers VoiceOver, Dynamic Type, contrast, and motor accessibility.

---

## VoiceOver

### Labels

Every interactive element needs an accessibility label unless its visible text is self-describing.

```swift
// Self-describing — no label needed
Button("Add to Cart") { }

// Icon-only — label required
Button(action: addToCart) {
    Image(systemName: "cart.badge.plus")
}
.accessibilityLabel("Add to cart")

// Complex content — combine or provide label
HStack {
    Image(systemName: "star.fill")
    Text("4.8")
    Text("(2,341 reviews)")
}
.accessibilityElement(children: .combine)
// VoiceOver reads: "star fill, 4.8, 2,341 reviews"
// Better:
.accessibilityElement(children: .ignore)
.accessibilityLabel("Rating: 4.8 out of 5, 2,341 reviews")
```

### Traits

```swift
// Mark headers for navigation
Text("Settings")
    .accessibilityAddTraits(.isHeader)

// Mark images
Image("hero-banner")
    .accessibilityLabel("Mountain landscape at sunset")
    .accessibilityAddTraits(.isImage)

// Decorative elements — hide from VoiceOver
Image("decorative-divider")
    .accessibilityHidden(true)

// Buttons that toggle
Toggle("Dark Mode", isOn: $isDarkMode)
// Toggle automatically handles its trait
```

### Grouping

```swift
// Group related elements into single VoiceOver focus
VStack {
    Text("John Doe")
    Text("Senior Engineer")
    Text("San Francisco, CA")
}
.accessibilityElement(children: .combine)

// Custom reading order
VStack {
    priceView
    titleView
}
.accessibilityElement(children: .contain)
.accessibilitySortPriority(1) // Read first
```

### Actions

```swift
// Custom actions (swipe up/down in VoiceOver)
Text(message.body)
    .accessibilityAction(named: "Reply") { reply(to: message) }
    .accessibilityAction(named: "Forward") { forward(message) }
    .accessibilityAction(named: "Delete") { delete(message) }
```

### Values

```swift
// Adjustable controls
Slider(value: $brightness, in: 0...100)
    .accessibilityValue("\(Int(brightness)) percent")
    .accessibilityLabel("Screen brightness")
```

---

## Dynamic Type

### Semantic Font Styles

Always use semantic styles — they scale automatically across all 12 size categories:

```swift
// Correct — scales with Dynamic Type
Text("Title").font(.title)
Text("Body text").font(.body)
Text("Small print").font(.caption)

// Incorrect — fixed size, doesn't scale
Text("Title").font(.system(size: 28))
```

### Adaptive Layouts

Horizontal layouts must collapse at large type sizes:

```swift
// Using ViewThatFits (iOS 16+)
ViewThatFits(in: .horizontal) {
    HStack {
        icon
        VStack(alignment: .leading) {
            title
            subtitle
        }
        Spacer()
        actionButton
    }
    // Fallback for when horizontal doesn't fit
    VStack(alignment: .leading) {
        HStack {
            icon
            title
        }
        subtitle
        actionButton
    }
}
```

```swift
// Using AnyLayout
struct AdaptiveStack: View {
    @Environment(\.dynamicTypeSize) var typeSize

    var body: some View {
        let layout = typeSize.isAccessibilitySize
            ? AnyLayout(VStackLayout(alignment: .leading))
            : AnyLayout(HStackLayout())

        layout {
            Text("Name")
            Text("Value")
        }
    }
}
```

### ScaledMetric

Custom dimensions that should scale with Dynamic Type:

```swift
struct ProfileRow: View {
    @ScaledMetric(relativeTo: .headline) private var avatarSize: CGFloat = 40
    @ScaledMetric(relativeTo: .body) private var spacing: CGFloat = 12

    var body: some View {
        HStack(spacing: spacing) {
            Avatar(size: avatarSize)
            VStack(alignment: .leading) {
                Text(name).font(.headline)
                Text(role).font(.subheadline)
            }
        }
    }
}
```

### ScrollView for Overflow

At accessibility sizes, content may overflow. Wrap in ScrollView:

```swift
var body: some View {
    ScrollView {
        VStack(spacing: 16) {
            headerSection
            contentSection
            actionSection
        }
        .padding()
    }
}
```

---

## Tap Targets

### Minimum 44×44pt

Every interactive element must have a minimum 44×44pt touch area:

```swift
// Small icon button — expand hit area
Button(action: dismiss) {
    Image(systemName: "xmark")
        .font(.caption)
}
.frame(minWidth: 44, minHeight: 44)
.contentShape(Rectangle())

// Compact row with tap action
Button(action: selectItem) {
    HStack {
        Text(item.name)
        Spacer()
        Image(systemName: "chevron.right")
    }
}
.frame(minHeight: 44)

// Adjacent buttons need 8pt spacing
HStack(spacing: 8) {
    Button("Cancel") { }
        .frame(minHeight: 44)
    Button("Confirm") { }
        .frame(minHeight: 44)
}
```

### Use Button, Not onTapGesture

```swift
// Incorrect — invisible to VoiceOver, keyboard, eye tracking
Text("Tap me")
    .onTapGesture { action() }

// Correct — full accessibility support
Button("Tap me") { action() }

// If you need custom appearance:
Button(action: action) {
    Text("Tap me")
        .padding()
        .background(.blue, in: RoundedRectangle(cornerRadius: 8))
}
.buttonStyle(.plain)
```

---

## Color & Contrast

### WCAG AA Requirements

| Text Size | Minimum Contrast Ratio |
|-----------|----------------------|
| < 18pt (or < 14pt bold) | **4.5:1** |
| ≥ 18pt (or ≥ 14pt bold) | **3:1** |
| UI components (icons, borders) | **3:1** |

### Never Color-Only State

```swift
// Incorrect — color is sole indicator
Circle()
    .fill(isOnline ? .green : .red)

// Correct — icon + color
HStack(spacing: 4) {
    Image(systemName: isOnline ? "checkmark.circle.fill" : "xmark.circle.fill")
    Text(isOnline ? "Online" : "Offline")
}
.foregroundStyle(isOnline ? .green : .red)
```

### High Contrast Support

```swift
// Detect high contrast mode
@Environment(\.colorSchemeContrast) var contrast

var body: some View {
    Text("Subtle label")
        .foregroundStyle(contrast == .increased ? .primary : .secondary)
}
```

---

## Reduce Motion

```swift
struct AnimatedCard: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var isVisible = false

    var body: some View {
        CardContent()
            .opacity(isVisible ? 1 : 0)
            .offset(y: isVisible ? 0 : (reduceMotion ? 0 : 20))
            .animation(
                reduceMotion ? .none : .spring(),
                value: isVisible
            )
            .onAppear { isVisible = true }
    }
}
```

### What to do when motion is reduced

| Normal | Reduced Motion |
|--------|---------------|
| Slide-in animation | Fade or instant |
| Continuous rotation | Static indicator |
| Parallax scrolling | Flat scrolling |
| Spring bounce | Instant snap |
| Auto-playing animation | Play button / static frame |

---

## Accessibility Testing Checklist

When reviewing code for accessibility:

- [ ] Every `Button`, `Toggle`, `Slider` has a label (explicit or from visible text)
- [ ] Icon-only buttons have `.accessibilityLabel()`
- [ ] Decorative images have `.accessibilityHidden(true)`
- [ ] All tap targets are ≥ 44×44pt
- [ ] 8pt minimum spacing between adjacent interactive elements
- [ ] No `.onTapGesture()` where `Button` should be used
- [ ] Text uses semantic font styles (`.font(.body)`, not `.font(.system(size:))`)
- [ ] Layouts adapt at accessibility type sizes (`ViewThatFits` or `AnyLayout`)
- [ ] Custom dimensions use `@ScaledMetric`
- [ ] Content wrapped in `ScrollView` for overflow at large sizes
- [ ] Color is not the sole state indicator
- [ ] Animations respect `accessibilityReduceMotion`
- [ ] Headers use `.accessibilityAddTraits(.isHeader)`
- [ ] Related elements grouped with `.accessibilityElement(children: .combine)`
