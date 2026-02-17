# Building a Claude Code skill for SwiftUI design excellence

**A Claude Code skill that reliably produces and evaluates high-quality iOS screens must encode Apple's Human Interface Guidelines as machine-enforceable rules, pair them with quantifiable design heuristics, and wrap everything in a composable skill architecture that supports review, generation, and iteration modes.** This report distills hundreds of HIG principles, design metrics, and SwiftUI best practices into the concrete rule set and skill blueprint needed to build it. The existing open-source landscape — particularly AvdLee's SwiftUI-Agent-Skill (230 GitHub stars) and Axiom for Claude Code — provides proven structural patterns to build on, while academic work like UICrit (CHI 2024) demonstrates that LLM vision models can already achieve meaningful design critique when given explicit rubrics.

---

## Apple's HIG distilled into enforceable SwiftUI rules

The HIG is vast, but a skill needs a finite set of checkable rules. The following represents the most impactful HIG principles translated into code-level checks.

**Layout fundamentals.** Apple uses an **8-point grid** for all spacing. SwiftUI's `.padding()` defaults to approximately **16pt** on all edges. Standard screen-edge margins are **16pt on iPhone**, **20pt on iPad**. Safe areas must be respected — the status bar is **59pt** tall on Dynamic Island devices, the home indicator area is **34pt**, and no fixed elements should overlap either zone. When `spacing` is omitted from VStack/HStack, SwiftUI applies adaptive spacing (roughly **8pt** for text-to-text in VStack) rather than zero — explicit `spacing: 0` is required for zero spacing.

**Typography hierarchy.** The complete Dynamic Type scale at the default "Large" size category:

| Text Style | Size | Weight | Leading |
|---|---|---|---|
| `.largeTitle` | 34pt | Regular | 41pt |
| `.title` | 28pt | Regular | 34pt |
| `.title2` | 22pt | Regular | 28pt |
| `.title3` | 20pt | Regular | 25pt |
| `.headline` | 17pt | **Semibold** | 22pt |
| `.body` | 17pt | Regular | 22pt |
| `.callout` | 16pt | Regular | 21pt |
| `.subheadline` | 15pt | Regular | 20pt |
| `.footnote` | 13pt | Regular | 18pt |
| `.caption` | 12pt | Regular | 16pt |
| `.caption2` | 11pt | Regular | 13pt |

SF Pro Text is used for sizes ≤19pt; SF Pro Display auto-activates at ≥20pt. **Caption2 at 11pt is Apple's absolute minimum readable size.** A screen should use **2–3 levels of type hierarchy**, maximum 4. SF Rounded (`.fontDesign(.rounded)`) suits friendly, metric-heavy contexts like fitness apps; SF Mono (`.fontDesign(.monospaced)`) is reserved for code and tabular data.

**Color system.** Semantic colors — `Color.primary`, `.secondary`, `Color(.systemBackground)`, `.background.secondary` (iOS 17+) — auto-adapt to light mode, dark mode, and Increase Contrast. Custom colors must be defined in Asset Catalogs with "Any Appearance" and "Dark" variants, with optional "High Contrast" variants for accessibility. Hardcoded `Color.white` or `Color.black` is a critical violation. Apple's own system blue (`#007AFF`) on white background actually fails WCAG AA for normal text at **~3.75:1** contrast — reinforcing that custom color choices need explicit verification against the **4.5:1 minimum** for text under 18pt and **3:1** for large text.

**Component correctness is non-negotiable.** The single most common structural mistake is wrapping `NavigationStack` around `TabView` instead of placing a `NavigationStack` inside each tab. This causes the tab bar to disappear during navigation. The correct pattern:

```swift
TabView {
    Tab("Home", systemImage: "house") {
        NavigationStack { HomeView().navigationTitle("Home") }
    }
    Tab("Settings", systemImage: "gear") {
        NavigationStack { SettingsView().navigationTitle("Settings") }
    }
}
```

Other frequently violated rules: using deprecated `NavigationView` instead of `NavigationStack`, hamburger menus instead of bottom tab bars (iOS uses tabs for primary navigation), alerts when confirmation dialogs are appropriate, and custom tab bars that don't remember per-tab navigation state.

---

## Forty enforceable rules an LLM can check against code

The skill needs a concrete, enumerable checklist. Based on cross-referencing HIG documentation, accessibility standards, and observed anti-patterns in AI-generated SwiftUI, the following rules can be verified through static code analysis:

**Spacing and layout rules:**
- S1: All explicit spacing values must be multiples of 4pt (preferably 8pt)
- S2: No "magic number" padding — use `.padding()` (system default) or explicit values from {4, 8, 12, 16, 20, 24, 32, 40, 48}
- S3: VStack/HStack nesting must not exceed 4 levels — extract subviews beyond this
- S4: No nested `ScrollView` instances with the same scroll axis
- S5: `GeometryReader` inside `ScrollView` must have an explicit `.frame()` constraint
- S6: Prefer `containerRelativeFrame` (iOS 17+) over `GeometryReader` for responsive sizing
- S7: Use `LazyVStack`/`LazyHStack` in `ScrollView` for collections exceeding ~20 items

**Typography rules:**
- T1: Use semantic font styles (`.font(.body)`) not hardcoded sizes (`.font(.system(size: 17))`)
- T2: No font size below 11pt anywhere in the app
- T3: Maximum 3–4 distinct text styles per screen
- T4: Use `@ScaledMetric` for dimensions that should scale with Dynamic Type
- T5: At accessibility type sizes, horizontal layouts must switch to vertical using `AnyLayout` or `ViewThatFits`

**Color and contrast rules:**
- C1: No `Color.black` or `Color.white` for text or backgrounds — use semantic colors
- C2: No inline `Color(red:green:blue:)` — define colors in Asset Catalog with dark mode variants
- C3: Text contrast ratio ≥ **4.5:1** for text under 18pt, ≥ **3:1** for text ≥18pt
- C4: Color must never be the sole indicator of state — pair with icons, text, or shapes

**Accessibility rules:**
- A1: Every interactive element must have an `accessibilityLabel`
- A2: All tap targets ≥ **44×44pt** — check `.frame()` and `.contentShape()`
- A3: Minimum **8pt** spacing between adjacent interactive elements
- A4: Use `Button` instead of `.onTapGesture()` for tappable elements (VoiceOver and eye-tracking compatibility)
- A5: Decorative images must have `.accessibilityHidden(true)`
- A6: Check for `@Environment(\.accessibilityReduceMotion)` when animations are present
- A7: Wrap content in `ScrollView` for accessibility type sizes to prevent clipping

**Modern API compliance (the #1 pain point with AI-generated SwiftUI):**
- M1: `NavigationStack` not `NavigationView` (deprecated since iOS 16)
- M2: `@Observable` not `ObservableObject`/`@Published`/`@StateObject` (iOS 17+)
- M3: New `Tab` API not `.tabItem()` (iOS 18+)
- M4: `async/await` not completion handlers
- M5: `.foregroundStyle()` not deprecated `.foregroundColor()`
- M6: SF Symbols sized with `.font()` not `.resizable()`

**Platform idiom rules:**
- P1: Bottom tab bar for primary navigation (2–5 tabs), not hamburger menus
- P2: `NavigationStack` inside each tab, not wrapping `TabView`
- P3: Swipe-to-go-back gesture must not be broken by custom gestures
- P4: Large title with `.navigationBarTitleDisplayMode(.large)` on primary screens
- P5: Alert buttons must use `.cancel` and `.destructive` roles for correct ordering
- P6: Use system components (`List`, `Form`, `.searchable()`, `.refreshable()`) over custom alternatives

---

## Evaluating design quality through vision and code analysis

**What LLM vision models can reliably assess.** Research from UICrit (3,059 design critiques for 983 mobile UIs) and a UC Berkeley CHI 2024 study demonstrates that multimodal LLMs achieve meaningful design critique when given explicit heuristics. Vision models reliably detect gross layout issues, inconsistent spacing, flat visual hierarchy, color contrast problems, missing platform conventions (hamburger menus on iOS, wrong navigation patterns), and cluttered interfaces. They struggle with subtle pixel-level alignment, exact color contrast ratios, interactive behavior across states, and animation quality. The most effective prompting strategy combines a **structured JSON representation of the UI hierarchy with the visual screenshot** and explicit heuristics to evaluate against, using few-shot examples from experienced designers.

**A practical vision review rubric for the skill should assess these five dimensions** when receiving a screenshot:

1. **Platform nativeness** — Tab bar at bottom? SF font? Back chevron with label? Large title that collapses on scroll? Frosted glass nav/tab bars?
2. **Visual hierarchy** — Clear primary action? Distinct heading/body/caption levels? Consistent spacing rhythm?
3. **Spacing consistency** — Elements appear to follow an 8pt grid? Consistent margins? Adequate whitespace (roughly 30–40% of screen area)?
4. **Color coherence** — Limited palette? Consistent accent color? Adequate contrast between text and backgrounds?
5. **Typography discipline** — No more than 3–4 font sizes visible? Clear weight hierarchy? System font or deliberate custom choice?

**What separates excellent iOS design from mediocre output.** Analysis of Apple Design Award winners (2023–2025) reveals consistent patterns: **reduced cognitive load** with interfaces that don't overwhelm, content-first design where UI defers to content, accessibility built from day one (VoiceOver, Dynamic Type, high contrast), deep platform integration (PencilKit, App Intents, haptics), and "thoughtful touchpoints" where every interaction feels polished. Things 3 exemplifies this — task boundaries materialize only during interaction, a context-aware "Magic Plus" button adapts based on location, and dark mode transitions at sunset.

**AI-generated UI has identifiable hallmarks** that the skill should flag. Erik Kennedy (LearnUI.design) identifies the telltale signs: **Inter font as default**, generic parallel card grids, uniform 8px border-radius on everything, zero brand identity, and designs that feel "safe" and "bland." Technically, AI code generators produce overuse of gradient backgrounds, equal visual weight across all elements (no hierarchy), missing empty/error/loading states, no haptic feedback, static interfaces without animation, and non-adaptive layouts.

The role of animation and haptics in perceived quality cannot be overstated. iOS uses **spring-based animations** as the default — not linear or bezier curves. SwiftUI's default animation became a spring in iOS 17. The skill should encourage `.sensoryFeedback(.success, trigger:)` for task completion, `.sensoryFeedback(.selection, trigger:)` for selection changes, and warn against semantically incorrect haptics (success haptic on error states confuses VoiceOver users). Phase and keyframe animators (iOS 17+) enable sophisticated multi-step animations, while `matchedGeometryEffect` creates smooth transitions between views sharing an identity.

---

## SwiftUI code architecture that enables design consistency

**Design token implementation is the foundation.** A three-tier token hierarchy — global constants → semantic aliases → component-specific values — ensures consistency. The practical Swift implementation:

```swift
enum Spacing {
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 16
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
}

enum Radius {
    static let sm: CGFloat = 6
    static let md: CGFloat = 12
    static let lg: CGFloat = 20
}
```

These tokens inject through the Environment via custom `EnvironmentKey` (or `@Entry` macro on iOS 18+), creating a single source of truth that flows through the entire view hierarchy. Colors must live in Asset Catalogs with semantic names (`TextPrimary`, `Surface`, not `Grey100`) and both light and dark appearance variants.

**View composition follows a clear principle:** containers are views, styling APIs are modifiers. Extract subviews when a `body` exceeds **40–60 lines**. Keep total files under **200–300 lines**. Use `ViewModifier` for reusable styling, `@ViewBuilder` for content-slot components, and `ButtonStyle`/`LabelStyle` for control-specific styling. The MVVM pattern with `@Observable` (iOS 17+) is the pragmatic default, with ViewModels defined as nested types via extensions.

**Essential reusable components** every well-architected app needs: primary/secondary/destructive buttons, info and action cards, section headers, empty states (icon + title + description + CTA), loading states (skeleton/shimmer), error states (retry-able), styled list rows, and input fields. All must respect Dynamic Type via semantic font styles, dark mode via semantic colors, and VoiceOver via proper accessibility traits and labels.

**Advanced layout APIs reduce GeometryReader dependence.** `ViewThatFits` (iOS 16+) automatically selects the first view that fits available space — perfect for layouts that collapse from horizontal to vertical at large type sizes. `containerRelativeFrame` (iOS 17+) sizes views relative to their scroll container, replacing the most common GeometryReader use case. The custom `Layout` protocol (iOS 16+) enables flow layouts, masonry grids, and equal-width stacks. When GeometryReader is unavoidable, place it in `.background()` or `.overlay()` to avoid disrupting layout.

---

## Skill architecture: structure, modes, and composability

**The existing landscape informs the design.** AvdLee's SwiftUI-Agent-Skill uses a `SKILL.md` + `references/` directory structure with topic-specific markdown files (animation, layout, state management, etc.). Axiom for Claude Code adds deep coverage of HIG compliance, VoiceOver, WCAG, and Apple frameworks. Paul Hudson's SwiftAgents provides an aggressive modern-API replacement guide. The proposed skill should synthesize these approaches while adding the design review dimension none of them fully address.

**Recommended file structure:**

```
swiftui-design-skill/
├── SKILL.md                        # Core routing, modes, workflow (< 5,000 words)
├── references/
│   ├── review-checklist.md         # The 40 enforceable rules with pass/fail criteria
│   ├── design-tokens.md            # Standard iOS spacing, typography, color tokens
│   ├── hig-rules.md                # Key HIG rules summary for generation mode
│   ├── deprecated-apis.md          # Modern API replacements (NavigationStack, @Observable, etc.)
│   ├── accessibility-guide.md      # VoiceOver, Dynamic Type, contrast requirements
│   ├── component-patterns.md       # Correct patterns for TabView, NavigationStack, List, Form
│   ├── animation-guide.md          # Spring animations, haptics, micro-interactions
│   ├── visual-review-rubric.md     # Screenshot evaluation criteria for vision mode
│   └── anti-patterns.md            # AI-generated code smells and fixes
```

**Three operational modes:**

- **Review mode** accepts SwiftUI code, runs the full 40-rule checklist, and outputs annotated findings grouped by severity (🔴 Critical → 🟡 Warning → 🔵 Suggestion → 🟢 Praise). Each finding includes the file and line, the violated rule ID, a description, and a concrete code fix. Priority order: Modern API compliance → Accessibility → Layout → Platform idioms → Typography → Color → Animation → Code quality.

- **Generation mode** accepts a natural language description or screenshot, produces HIG-compliant SwiftUI code using design tokens from `references/design-tokens.md`, applies patterns from `references/component-patterns.md`, and self-verifies against the review checklist before output. The output includes both the code and a design specification noting the spacing, typography, and color choices made.

- **Iteration mode** accepts existing code plus feedback, applies targeted improvements, re-runs the checklist, and outputs a minimal diff with explanatory comments.

**The SKILL.md frontmatter:**

```yaml
---
name: swiftui-design-review
description: >
  Review and generate SwiftUI views for design quality, HIG compliance,
  accessibility, and modern API usage. Use when reviewing SwiftUI code,
  auditing iOS design quality, or generating design-compliant views.
  Accepts code for static analysis or screenshots for visual review.
allowed-tools: Read, Write, Edit, Grep, Glob
---
```

**Composability is built-in through progressive disclosure.** Claude Code's skill system loads SKILL.md into context when it determines relevance, then loads reference files on demand. Other skills can't explicitly invoke this skill, but Claude automatically combines relevant skills when context warrants it. The structured output format (rule ID, severity, file reference, fix) creates a machine-readable interface that downstream skills — such as a code-fix skill or a test-generation skill — can consume naturally.

**Key implementation details:** Keep SKILL.md under 5,000 words with clear pointers to reference files. Store in `.claude/skills/` for project-level sharing via git, or `~/.claude/skills/` for personal use. Distribution through the Claude Code plugin marketplace or `npx skills add`. Changes take effect on the next Claude Code session start. For teams, `.claude/settings.json` can enable skills automatically.

---

## Conclusion

The most impactful single investment for this skill is a **comprehensive deprecated-API replacement guide** — this addresses the #1 failure mode of AI-generated SwiftUI code (defaulting to NavigationView, ObservableObject, and other pre-iOS 17 patterns). Combined with the 40 enforceable rules organized by severity, the design token reference, and the visual review rubric, the skill covers both the "don't break things" baseline and the "make it feel native" aspiration.

The gap between AI-generated iOS UI and award-winning design comes down to three things the skill must encode: **platform idiom compliance** (tab bars, swipe-back, spring animations, haptics), **accessibility as a first-class requirement** (Dynamic Type, VoiceOver, 44pt targets, contrast ratios), and **design system discipline** (consistent tokens, semantic colors, type hierarchy). Apple Design Award winners share these qualities universally — and their absence is what makes AI output feel like "cross-platform slop."

Vision-based review adds a valuable second channel. While LLM vision cannot replace precise contrast-ratio calculations, it excels at catching the holistic issues code analysis misses: visual hierarchy problems, spacing rhythm breaks, native-vs-foreign feel, and overall information density. The five-dimension visual rubric (platform nativeness, visual hierarchy, spacing consistency, color coherence, typography discipline) gives the skill structured reasoning over screenshots. As multimodal model capabilities improve, this channel will become increasingly powerful — but even today, the combination of static code analysis against the 40-rule checklist and vision-based holistic assessment creates a review system substantially more thorough than either approach alone.