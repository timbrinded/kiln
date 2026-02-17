---
description: Generate HIG-compliant SwiftUI views from a natural language description or screenshot reference
argument-hint: "[description-or-screenshot-path]"
allowed-tools: Read, Write, Edit, Grep, Glob
---

Generate a SwiftUI view using the swift-design skill's generation mode.

**Input:** `$ARGUMENTS` contains either:
- A natural language description of the desired screen/component (e.g., "a settings screen with dark mode toggle and account section")
- A screenshot path to use as a visual reference for the generated code

**Process:**
1. Check `.claude/swift-design.local.md` for iOS target version (default: 17)
2. Load the swift-design skill's design tokens, HIG rules, component patterns, and deprecated API guide
3. Parse the description to identify:
   - Screen type (list, detail, form, dashboard, onboarding, etc.)
   - Required components (navigation, tabs, buttons, inputs, etc.)
   - Data model needs
   - View states needed (loading, empty, error, content)
4. Generate SwiftUI code that:
   - Uses design tokens for all spacing (8pt grid)
   - Uses semantic font styles (`.body`, `.headline`, `.title`, etc.)
   - Uses semantic colors (`Color.primary`, `Color(.systemBackground)`, etc.)
   - Uses `@Observable` for view models
   - Uses `NavigationStack` (not `NavigationView`)
   - Uses `Tab` API for tab views (iOS 18) or `.tabItem` (iOS 17)
   - Includes proper accessibility labels on interactive elements
   - Handles all view states (loading, empty, error, content)
   - Applies spring animations for state transitions
   - Adds haptic feedback on key interactions
   - Uses `Button` (not `.onTapGesture`) for all interactive elements
   - Applies `ViewThatFits` or `AnyLayout` for Dynamic Type adaptation
5. Self-verify the output against the review checklist before presenting
6. Output the code followed by a **Design Specification** explaining:
   - Type hierarchy chosen (which text styles and why)
   - Spacing decisions (which tokens and why)
   - Color choices (which semantic colors and why)
   - Accessibility measures applied
   - Animation and haptic choices

If the description is ambiguous about layout or behavior, ask clarifying questions before generating. Prefer asking 1–2 focused questions over guessing wrong.
