# SwiftUI Animation & Haptics Guide

iOS uses spring-based animations as the default. The absence of animation and haptics is what makes AI-generated output feel lifeless. This guide covers springs, transitions, haptics, and micro-interactions.

---

## Spring Animations (Default in iOS 17+)

SwiftUI's default animation became spring-based in iOS 17. Prefer springs over linear or bezier curves.

### Built-in Spring Presets

```swift
// Default spring — good for most transitions
withAnimation(.spring()) { isExpanded.toggle() }

// Snappy — quick response, minimal bounce
withAnimation(.snappy) { showDetail = true }

// Bouncy — playful, more bounce
withAnimation(.bouncy) { isSelected.toggle() }

// Smooth — gentle, no bounce
withAnimation(.smooth) { opacity = 1 }

// Interactive spring — follows finger, good for gestures
withAnimation(.interactiveSpring) { offset = newOffset }
```

### Custom Springs

```swift
// Spring with duration and bounce
withAnimation(.spring(duration: 0.5, bounce: 0.3)) {
    scale = 1.0
}

// Spring with response and damping
withAnimation(.spring(response: 0.4, dampingFraction: 0.7)) {
    position = target
}
```

### When to Use Each

| Animation | Use Case |
|-----------|----------|
| `.spring()` | General transitions, view appearance |
| `.snappy` | Toggles, selections, tab switches |
| `.bouncy` | Success states, playful interactions |
| `.smooth` | Opacity changes, subtle transitions |
| `.interactiveSpring` | Drag gestures, interactive dismissal |
| `.linear` | Progress bars, continuous rotation |

---

## View Transitions

### Appear/Disappear

```swift
if showBanner {
    BannerView()
        .transition(.move(edge: .top).combined(with: .opacity))
}
```

### Common Transitions

```swift
.transition(.opacity)                          // Fade
.transition(.scale)                            // Scale from center
.transition(.slide)                            // Slide from leading edge
.transition(.move(edge: .bottom))              // Slide from bottom
.transition(.asymmetric(                       // Different in/out
    insertion: .move(edge: .trailing),
    removal: .opacity
))
.transition(.push(from: .bottom))              // Push (iOS 16+)
.transition(.blurReplace)                      // Blur morph (iOS 17+)
```

### Matched Geometry Effect

Smooth shared-element transitions between views:

```swift
struct CardToDetailTransition: View {
    @Namespace private var animation
    @State private var selectedCard: Card?

    var body: some View {
        if let card = selectedCard {
            DetailView(card: card)
                .matchedGeometryEffect(id: card.id, in: animation)
                .onTapGesture { withAnimation(.spring()) { selectedCard = nil } }
        } else {
            LazyVGrid(columns: columns) {
                ForEach(cards) { card in
                    CardView(card: card)
                        .matchedGeometryEffect(id: card.id, in: animation)
                        .onTapGesture { withAnimation(.spring()) { selectedCard = card } }
                }
            }
        }
    }
}
```

---

## Phase Animator (iOS 17+)

Multi-step animations that cycle through phases:

```swift
struct PulsingDot: View {
    var body: some View {
        Circle()
            .fill(.blue)
            .frame(width: 12, height: 12)
            .phaseAnimator([false, true]) { content, phase in
                content
                    .scaleEffect(phase ? 1.2 : 1.0)
                    .opacity(phase ? 0.7 : 1.0)
            } animation: { phase in
                phase ? .easeInOut(duration: 0.8) : .easeInOut(duration: 0.8)
            }
    }
}
```

### Triggered Phase Animator

```swift
struct SuccessCheckmark: View {
    @State private var trigger = false

    var body: some View {
        Image(systemName: "checkmark.circle.fill")
            .font(.largeTitle)
            .phaseAnimator([0, 1, 2], trigger: trigger) { content, phase in
                content
                    .scaleEffect(phase == 1 ? 1.3 : 1.0)
                    .foregroundStyle(phase >= 1 ? .green : .secondary)
            } animation: { phase in
                switch phase {
                case 1: .bouncy
                case 2: .smooth
                default: .snappy
                }
            }
    }
}
```

---

## Keyframe Animator (iOS 17+)

Complex custom motion with precise control:

```swift
struct BouncingBadge: View {
    @State private var trigger = false

    var body: some View {
        Text("New")
            .keyframeAnimator(initialValue: AnimationValues(), trigger: trigger) { content, value in
                content
                    .scaleEffect(value.scale)
                    .rotationEffect(.degrees(value.rotation))
                    .offset(y: value.yOffset)
            } keyframes: { _ in
                KeyframeTrack(\.scale) {
                    SpringKeyframe(1.3, duration: 0.2)
                    SpringKeyframe(0.9, duration: 0.15)
                    SpringKeyframe(1.0, duration: 0.2)
                }
                KeyframeTrack(\.rotation) {
                    SpringKeyframe(-5, duration: 0.1)
                    SpringKeyframe(5, duration: 0.1)
                    SpringKeyframe(0, duration: 0.2)
                }
            }
    }
}

struct AnimationValues {
    var scale: CGFloat = 1.0
    var rotation: Double = 0
    var yOffset: CGFloat = 0
}
```

---

## Haptic Feedback

### Sensory Feedback (iOS 17+)

```swift
// Selection — picker changes, list reordering
Button("Select") { selectedItem = item }
    .sensoryFeedback(.selection, trigger: selectedItem)

// Success — task completion, save confirmed
Button("Save") { save() }
    .sensoryFeedback(.success, trigger: saveCount)

// Warning — approaching limit, undo available
Slider(value: $volume, in: 0...100)
    .sensoryFeedback(.warning, trigger: volume) { old, new in
        new >= 90 && old < 90  // Only trigger at threshold
    }

// Error — failed action, invalid input
Button("Submit") { submit() }
    .sensoryFeedback(.error, trigger: errorCount)

// Impact — collision, snapping to position
DraggableView()
    .sensoryFeedback(.impact(weight: .medium), trigger: snapPoint)
```

### Semantic Matching

| Action | Haptic | Why |
|--------|--------|-----|
| Toggle/selection change | `.selection` | Lightweight, acknowledges choice |
| Task completed | `.success` | Positive confirmation |
| Item deleted | `.success` | Action confirmed (not error!) |
| Save failed | `.error` | Negative outcome |
| Approaching limit | `.warning` | Caution signal |
| Element snapping | `.impact(weight:)` | Physical feedback |
| Pull-to-refresh trigger | `.impact(weight: .medium)` | Threshold crossed |

**Critical**: Never use `.success` for errors or `.error` for successes. VoiceOver announces haptic type — mismatched haptics confuse users.

---

## Micro-Interactions

### Button Press Effect

```swift
struct ScaleButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.snappy, value: configuration.isPressed)
    }
}
```

### Content Appearance

```swift
struct FadeInView<Content: View>: View {
    @ViewBuilder let content: Content
    @State private var isVisible = false

    var body: some View {
        content
            .opacity(isVisible ? 1 : 0)
            .offset(y: isVisible ? 0 : 10)
            .onAppear {
                withAnimation(.spring().delay(0.1)) {
                    isVisible = true
                }
            }
    }
}
```

### List Row Staggered Appearance

```swift
ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
    ItemRow(item: item)
        .opacity(appeared ? 1 : 0)
        .offset(y: appeared ? 0 : 20)
        .animation(.spring().delay(Double(index) * 0.05), value: appeared)
}
.onAppear { appeared = true }
```

### Pull-to-Refresh with Haptic

```swift
List(items) { item in
    ItemRow(item: item)
}
.refreshable {
    await loadItems()
}
// System provides haptic automatically
```

---

## Reduce Motion Compliance

Always provide non-animated alternatives:

```swift
struct AnimatedEntrance: ViewModifier {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var appeared = false

    func body(content: Content) -> some View {
        content
            .opacity(appeared ? 1 : 0)
            .offset(y: appeared ? 0 : (reduceMotion ? 0 : 20))
            .onAppear {
                if reduceMotion {
                    appeared = true
                } else {
                    withAnimation(.spring()) { appeared = true }
                }
            }
    }
}

extension View {
    func animatedEntrance() -> some View {
        modifier(AnimatedEntrance())
    }
}
```

### Animation Decision Tree

1. Is `accessibilityReduceMotion` enabled?
   - Yes → Use instant transitions or simple opacity fades
   - No → Continue
2. Is this a user-initiated action?
   - Yes → Use `.snappy` or `.spring()` (responsive)
   - No → Continue
3. Is this decorative/ambient?
   - Yes → Use `.smooth` with longer duration
   - No → Use `.spring()` default
