# HIG Rules Summary for Generation Mode

Key Apple Human Interface Guidelines distilled for SwiftUI code generation. Consult when generating new views to ensure HIG compliance from the start.

---

## Layout Fundamentals

### 8-Point Grid
All spacing, padding, and margins must be multiples of 4pt (preferably 8pt). SwiftUI's `.padding()` defaults to ~16pt.

### Safe Areas
- Always respect safe areas — never place fixed content behind status bar or home indicator
- Status bar: 59pt on Dynamic Island devices
- Home indicator area: 34pt
- Use `.safeAreaInset()` for floating elements, not `.ignoresSafeArea()`

### Screen-Edge Margins
- iPhone: 16pt horizontal inset
- iPad: 20pt horizontal inset
- Use `.padding(.horizontal)` for standard margins (system applies 16pt)

### Content Width
- Readable content width: use `.frame(maxWidth: .readableContentGuide)` or limit to ~672pt
- Full-bleed images/maps: extend to edges
- Text content: respect readable width, especially on iPad

---

## Navigation Patterns

### Primary Navigation
- **iPhone**: Bottom tab bar (2–5 tabs) for top-level destinations
- **iPad**: Tab bar or sidebar (`NavigationSplitView`)
- **Never**: Hamburger menus as primary navigation on iOS

### Tab Bar Rules
- 2–5 tabs maximum
- Use SF Symbols for tab icons
- Each tab maintains its own navigation state
- `NavigationStack` inside each tab, never wrapping `TabView`

### Hierarchical Navigation
- Push/pop via `NavigationStack` within tabs
- Large title (`.large`) on root screens, inline on pushed screens
- Back button always shows previous screen's title
- Never break swipe-to-go-back gesture

### Modal Presentation
- Use `.sheet()` for focused tasks
- Use `.fullScreenCover()` for immersive experiences
- Use `.confirmationDialog()` for action lists (not custom action sheets)
- Dismiss button: "Cancel" (top-left) or "Done"/"Save" (top-right)

---

## Typography Rules

### Hierarchy
- Maximum 2–3 type levels per screen (4 absolute max)
- Use semantic text styles: `.largeTitle`, `.title`, `.headline`, `.body`, `.caption`
- Never go below `.caption2` (11pt) — Apple's absolute minimum
- Use weight to create hierarchy within same size: Regular vs Semibold

### Dynamic Type
- Always use semantic font styles — they scale automatically
- Test at largest accessibility size category
- Use `@ScaledMetric` for custom dimensions that should scale
- Horizontal layouts must collapse to vertical at large type sizes

---

## Color Rules

### Semantic Colors
- Use `Color.primary`, `.secondary` for text
- Use `Color(.systemBackground)` for backgrounds
- Use `Color.accentColor` for interactive elements
- Never use `Color.black` or `Color.white`

### Dark Mode
- Define all custom colors with light AND dark variants
- Use Asset Catalog for custom colors
- Test in both modes — semantic colors handle this automatically

### Contrast
- Text <18pt: minimum 4.5:1 contrast ratio (WCAG AA)
- Text ≥18pt: minimum 3:1 contrast ratio
- Color must never be the sole indicator of state

---

## Component Usage

### Lists
- Use `List` for scrollable collections with standard row styling
- Use `Form` for settings/input screens
- Add `.searchable()` for filterable lists
- Add `.refreshable()` for pull-to-refresh
- Swipe actions via `.swipeActions()`

### Buttons
- Use `Button` for all interactive elements (not `.onTapGesture`)
- Apply `.buttonStyle(.borderedProminent)` for primary CTAs
- Apply `.buttonStyle(.bordered)` for secondary actions
- Use `.role(.destructive)` for destructive actions
- Minimum 44×44pt tap target

### Alerts & Dialogs
- `.alert()` for informational messages with simple actions
- `.confirmationDialog()` for action lists with destructive options
- Button order: Cancel + destructive actions use roles for correct platform ordering

### Text Fields
- Use `TextField` with `.textFieldStyle(.roundedBorder)` for standard inputs
- Use `SecureField` for passwords
- Apply `.textContentType()` for autofill: `.emailAddress`, `.password`, `.name`
- Use `.keyboardType()` for appropriate keyboard: `.emailAddress`, `.phonePad`, `.URL`

---

## Accessibility Requirements

### VoiceOver
- Every interactive element needs an `accessibilityLabel`
- Buttons with icon-only content: explicit label required
- Decorative images: `.accessibilityHidden(true)`
- Group related elements: `.accessibilityElement(children: .combine)`

### Tap Targets
- Minimum 44×44pt for all interactive elements
- 8pt minimum spacing between adjacent targets
- Use `.contentShape(Rectangle())` to expand hit area when needed

### Dynamic Type
- All text must use semantic font styles
- Layouts must adapt to accessibility sizes
- `ViewThatFits` for horizontal-to-vertical collapse
- `ScrollView` wrapper for content that may overflow

### Motion
- Check `@Environment(\.accessibilityReduceMotion)` for animations
- Provide static alternative when motion is reduced
- Never use animation as the sole way to convey information

---

## Interaction Patterns

### Haptics
- `.sensoryFeedback(.success, trigger:)` — task completion
- `.sensoryFeedback(.selection, trigger:)` — selection changes
- `.sensoryFeedback(.impact, trigger:)` — collisions, snapping
- `.sensoryFeedback(.warning, trigger:)` — approaching limits
- `.sensoryFeedback(.error, trigger:)` — failures
- Match haptic to semantic meaning — success haptic on error confuses VoiceOver users

### Animation
- iOS 17+ default animation is spring-based
- Use `.spring()` or `.snappy` for most transitions
- Use `.matchedGeometryEffect` for shared element transitions
- Phase animator for multi-step animations
- Keyframe animator for complex custom motion

### Gestures
- Prefer system gestures over custom ones
- Never override left-edge swipe (system back navigation)
- Use `.sensoryFeedback()` to acknowledge gesture recognition
- Long press: 0.5s default duration, use `.contextMenu()` when appropriate

---

## View States

Every data-driven view should handle these states:

### Loading
- Use `ProgressView()` for indeterminate loading
- Skeleton/shimmer views for known layout shapes
- Place loading state where content will appear

### Empty
- Icon + title + description + CTA pattern
- Explain what will appear and how to populate
- Example: "No Messages" + "Start a conversation" button

### Error
- Clear error description (not technical jargon)
- Retry action when recoverable
- Navigation to help/support for unrecoverable errors

### Content
- The normal state with data displayed
- Handle single item vs. many items
- Handle overflow/truncation gracefully
