# swift-design

A Claude Code plugin that encodes Apple's Human Interface Guidelines as 40 machine-enforceable rules for SwiftUI. Reviews code, generates HIG-compliant views, evaluates screenshots, and catches the deprecated APIs and accessibility gaps that AI-generated SwiftUI consistently gets wrong.

## What it does

| Mode | Input | Output |
|------|-------|--------|
| **Review** | SwiftUI file(s) | Severity-graded findings + letter grade (A–F) |
| **Visual Review** | Screenshot / mockup | 5-dimension design score + top 3 fixes |
| **Generate** | Natural language description | HIG-compliant SwiftUI code + design spec |
| **Iterate** | Code + feedback | Targeted fixes + updated grade |

The plugin checks 40 rules across 6 categories:

| Category | Rules | Catches |
|----------|-------|---------|
| **Modern API** (M1–M6) | `NavigationView` → `NavigationStack`, `ObservableObject` → `@Observable`, `.foregroundColor` → `.foregroundStyle`, and more | The #1 failure mode in AI-generated SwiftUI |
| **Accessibility** (A1–A7) | Missing labels, small tap targets, `.onTapGesture` misuse, no reduce-motion check | Real user impact |
| **Platform Idioms** (P1–P6) | NavigationStack wrapping TabView, hamburger menus, broken swipe-back | Non-native feel |
| **Spacing & Layout** (S1–S7) | Off-grid spacing, deep nesting, GeometryReader misuse, nested ScrollViews | Layout bugs |
| **Typography** (T1–T5) | Hardcoded font sizes, text below 11pt, too many type levels | Dynamic Type breakage |
| **Color & Contrast** (C1–C4) | `Color.black`/`.white`, inline colors, color-only state, low contrast | Dark mode & a11y failures |

---

## Installation

### Option 1: Plugin directory (recommended)

Clone the repo and point Claude Code at it:

```bash
git clone https://github.com/timbrinded/kiln.git ~/.claude/plugins/kiln
```

Then add it to your Claude Code settings at `~/.claude/settings.json`:

```json
{
  "plugins": [
    "~/.claude/plugins/kiln/plugins/swift-design"
  ]
}
```

Restart Claude Code. The plugin loads automatically on next session.

### Option 2: Test without installing

Run Claude Code with the `--plugin-dir` flag:

```bash
claude --plugin-dir /path/to/kiln/plugins/swift-design
```

### Option 3: Project-level installation

Copy or symlink into a project's `.claude/plugins/` directory to share with your team via git:

```bash
ln -s /path/to/kiln/plugins/swift-design .claude/plugins/swift-design
```

### Verify installation

After installing, run `/help` in Claude Code. You should see:

```
/swift-review   (swift-design)  Review SwiftUI code for design quality...
/swift-generate (swift-design)  Generate HIG-compliant SwiftUI views...
```

The `swift-design-reviewer` agent and the `swift-design` skill activate automatically when relevant — no manual setup required.

---

## Usage

### Slash commands

#### `/swift-review`

Review SwiftUI code against all 40 rules:

```
/swift-review ContentView.swift
```

Review a screenshot for iOS design quality:

```
/swift-review screenshot.png
```

Review and iterate with feedback:

```
/swift-review ContentView.swift "fix the deprecated APIs and add accessibility labels"
```

Review all SwiftUI views in the project (no arguments):

```
/swift-review
```

**Output format:**

```
## SwiftUI Design Review — Grade: B

### 🔴 Critical (must fix)
- [M1] NavigationView is deprecated → NavigationStack — ContentView.swift:12
  Fix: Replace `NavigationView { ... }` with `NavigationStack { ... }`
- [P2] NavigationStack wraps TabView — ContentView.swift:10
  Fix: Move NavigationStack inside each Tab { }

### 🟡 Warning (should fix)
- [S1] Non-standard spacing value 13 — CardView.swift:45
  Fix: Use 12 or 16 (nearest 4pt-grid values)

### 🔵 Suggestion (consider)
- [P4] Missing large title on root screen — HomeView.swift:8

### 🟢 Praise
- Correct @Observable usage throughout
- Semantic colors — dark mode safe
- All buttons have accessibility labels
```

#### `/swift-generate`

Generate a HIG-compliant SwiftUI view from a description:

```
/swift-generate a settings screen with dark mode toggle, notification preferences, and account section
```

```
/swift-generate a photo grid with pull-to-refresh and detail view navigation
```

```
/swift-generate a fitness dashboard showing steps, calories, and heart rate with tab navigation
```

The output includes the SwiftUI code plus a **Design Specification** explaining the type hierarchy, spacing tokens, color choices, and accessibility measures applied.

### Automatic skill activation

The `swift-design` skill activates automatically when you're working with SwiftUI and mention anything related to design quality, HIG compliance, accessibility, or modern APIs. No slash command needed — just talk naturally:

- "Review this SwiftUI view for me"
- "Is this code accessible?"
- "Check for deprecated APIs"
- "Generate a login screen"
- "How should I add haptics to this view?"

### Agent: swift-design-reviewer

The `swift-design-reviewer` agent triggers proactively when Claude detects you're reviewing or discussing SwiftUI code quality. It runs as an autonomous subprocess with read-only access (`Read`, `Grep`, `Glob`) and returns a structured review.

You can also invoke it explicitly by asking Claude to use the reviewer agent.

---

## Configuration

Create a settings file at `.claude/swift-design.local.md` in your project root (or `~/.claude/swift-design.local.md` globally) to customize behavior:

```yaml
---
ios-target: 17
strictness: standard
---
```

### ios-target

Controls which rules apply and at what severity.

| Value | Effect |
|-------|--------|
| `16` | `@Observable` (M2) and Tab API (M3) become suggestions. NavigationStack (M1) still critical. |
| `17` | **(default)** Tab API (M3) is a suggestion. All other rules at listed severity. |
| `18` | All 40 rules at their full listed severity. |

### strictness

Controls how much gets reported.

| Value | Effect |
|-------|--------|
| `relaxed` | Only 🔴 Critical findings reported |
| `standard` | **(default)** 🔴 Critical + 🟡 Warning reported. 🔵 Suggestions listed at the end. |
| `strict` | Everything reported. Grade calculation penalizes suggestions. |

---

## The 40 Rules

### Spacing & Layout (S1–S7)

| ID | Rule | Severity |
|----|------|----------|
| S1 | Spacing values must be multiples of 4pt. Allowed: {4, 8, 12, 16, 20, 24, 32, 40, 48} | 🟡 |
| S2 | No magic-number padding — use `.padding()` or allowed values | 🟡 |
| S3 | VStack/HStack nesting ≤ 4 levels | 🟡 |
| S4 | No same-axis nested ScrollViews | 🔴 |
| S5 | GeometryReader in ScrollView must have `.frame()` | 🔴 |
| S6 | Prefer `containerRelativeFrame` over GeometryReader (17+) | 🔵 |
| S7 | Use Lazy stacks in ScrollView for 20+ items | 🟡 |

### Typography (T1–T5)

| ID | Rule | Severity |
|----|------|----------|
| T1 | Semantic font styles only — no `.system(size:)` | 🔴 |
| T2 | No font size below 11pt | 🔴 |
| T3 | Max 3–4 text styles per screen | 🟡 |
| T4 | Use `@ScaledMetric` for scalable custom dimensions | 🔵 |
| T5 | Horizontal layouts must collapse at accessibility sizes | 🟡 |

### Color & Contrast (C1–C4)

| ID | Rule | Severity |
|----|------|----------|
| C1 | No `Color.black` / `Color.white` — use semantic colors | 🔴 |
| C2 | No inline `Color(red:green:blue:)` — use Asset Catalog | 🟡 |
| C3 | Text contrast ≥ 4.5:1 (<18pt) or ≥ 3:1 (≥18pt) | 🔴 |
| C4 | Color must not be the sole state indicator | 🔴 |

### Accessibility (A1–A7)

| ID | Rule | Severity |
|----|------|----------|
| A1 | Interactive elements need `accessibilityLabel` | 🔴 |
| A2 | Tap targets ≥ 44×44pt | 🔴 |
| A3 | ≥ 8pt spacing between adjacent interactive elements | 🟡 |
| A4 | `Button` not `.onTapGesture` for tappable elements | 🔴 |
| A5 | Decorative images: `.accessibilityHidden(true)` | 🟡 |
| A6 | Animations must check `accessibilityReduceMotion` | 🟡 |
| A7 | Content in ScrollView for accessibility type sizes | 🔵 |

### Modern API (M1–M6)

| ID | Rule | Severity |
|----|------|----------|
| M1 | `NavigationStack` not `NavigationView` | 🔴 |
| M2 | `@Observable` not `ObservableObject` / `@Published` | 🔴 |
| M3 | `Tab` API not `.tabItem()` (18+ only) | 🔵 |
| M4 | `async/await` not completion handlers | 🟡 |
| M5 | `.foregroundStyle()` not `.foregroundColor()` | 🟡 |
| M6 | SF Symbols: `.font()` not `.resizable()` | 🟡 |

### Platform Idioms (P1–P6)

| ID | Rule | Severity |
|----|------|----------|
| P1 | Bottom tab bar for primary nav, not hamburger menu | 🔴 |
| P2 | `NavigationStack` inside each tab, not wrapping TabView | 🔴 |
| P3 | Don't break swipe-to-go-back with custom gestures | 🟡 |
| P4 | Large title on primary screens | 🔵 |
| P5 | Alert buttons use `.cancel` and `.destructive` roles | 🟡 |
| P6 | Prefer system components (List, Form, .searchable) | 🔵 |

---

## Grading

### Code Review (40-rule checklist)

Each category starts at 100. Deductions: 15pts per 🔴, 8pts per 🟡, 3pts per 🔵.

Weighted by impact:

| Category | Weight |
|----------|--------|
| Modern API | 25% |
| Accessibility | 25% |
| Platform Idioms | 20% |
| Spacing & Layout | 15% |
| Typography | 10% |
| Color & Contrast | 5% |

### Visual Review (screenshot)

Five dimensions scored 1–5:

| Dimension | Weight |
|-----------|--------|
| Platform Nativeness | 30% |
| Visual Hierarchy | 25% |
| Spacing Consistency | 20% |
| Color Coherence | 15% |
| Typography Discipline | 10% |

### Grade Scale

| Score | Grade | Meaning |
|-------|-------|---------|
| 90–100 | **A** | Excellent — HIG-compliant, accessible, modern |
| 80–89 | **B** | Good — minor issues, mostly compliant |
| 70–79 | **C** | Acceptable — notable issues, functional |
| 60–69 | **D** | Poor — significant violations, needs rework |
| < 60 | **F** | Failing — critical violations, not ship-ready |

---

## Plugin structure

```
kiln/
├── .claude-plugin/
│   └── marketplace.json                     # Kiln marketplace index
├── plugins/
│   └── swift-design/                        # This plugin
│       ├── .claude-plugin/
│       │   └── plugin.json                  # Plugin manifest
│       ├── agents/
│       │   └── swift-design-reviewer.md     # Proactive design review agent
│       ├── commands/
│       │   ├── swift-review.md              # /swift-review command
│       │   └── swift-generate.md            # /swift-generate command
│       ├── skills/
│       │   └── swift-design/
│       │       ├── SKILL.md                 # Core skill — mode routing (819 words)
│       │       └── references/
│       │           ├── review-checklist.md  # 40 rules + grade rubric
│       │           ├── deprecated-apis.md   # Modern API before/after guide
│       │           ├── design-tokens.md     # Spacing, typography, color tokens
│       │           ├── hig-rules.md         # HIG fundamentals for generation
│       │           ├── accessibility-guide.md   # VoiceOver, Dynamic Type, contrast
│       │           ├── component-patterns.md    # TabView, NavigationStack, List, Form
│       │           ├── animation-guide.md       # Spring animations, haptics
│       │           ├── visual-review-rubric.md  # 5-dimension screenshot rubric
│       │           └── anti-patterns.md         # 17 AI code smells + fixes
│       └── README.md
├── shared/                                  # Future cross-plugin resources
├── README.md                                # Kiln marketplace docs
└── LICENSE
```

**How progressive disclosure works:** The skill metadata (~100 words) is always in Claude's context. When triggered, SKILL.md adds ~800 words of mode routing. Only when a specific mode runs does the relevant reference file (~1,000 words each) get loaded. Maximum context cost for a full review is ~2,800 words — not 11,000.

---

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- No external dependencies, API keys, or build steps

---

## License

MIT
