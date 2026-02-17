# UI Refactor — Refactoring UI Design Review Plugin

Review screenshots, CSS/Tailwind code, and UI descriptions against principles from Refactoring UI. Get concrete, actionable fixes — not vague "make it look better" advice.

## What It Does

| Input | Output |
|-------|--------|
| Screenshot of your UI | Structured review across 6 dimensions with specific CSS fixes |
| CSS / Tailwind code file | Code-level audit for spacing system, type scale, color palette, shadow hierarchy |
| "My page looks amateurish" | Diagnosis via anti-pattern checklist with prioritized fixes |
| "How should I choose colors?" | Specific principles with concrete HSL values and methodology |

## Installation

### From Kiln Marketplace
```bash
claude plugin install kiln/ui-refactor
```

### Direct Install
```bash
claude plugin install github:timbrinded/kiln/plugins/ui-refactor
```

### Local Testing
```bash
claude --plugin-dir /path/to/kiln/plugins/ui-refactor
```

## Usage

### Slash Command
```
/design-review path/to/screenshot.png
/design-review src/components/Card.tsx
/design-review src/styles/main.css typography
/design-review "My dashboard looks flat and boring"
```

### Automatic Activation
The skill activates automatically when you ask to:
- "Review this screenshot", "make this look better", "improve the UI"
- "Fix the spacing", "improve visual hierarchy", "choose colors"
- "Review my CSS", "review my Tailwind", "make this more professional"

### Agent
The `design-reviewer` agent activates when reviewing frontend work, providing structured design feedback with concrete fixes.

## The Six Dimensions

Every review evaluates across these dimensions in priority order:

| # | Dimension | What It Checks |
|---|-----------|----------------|
| 1 | **Hierarchy & Emphasis** | Primary/secondary/tertiary distinction, button hierarchy, label strategy |
| 2 | **Spacing & Layout** | Spacing scale adherence, proximity relationships, max-width constraints |
| 3 | **Typography** | Type scale, line-height proportionality, line length, letter-spacing |
| 4 | **Color** | Palette system, shade variations, grey temperature, WCAG contrast |
| 5 | **Depth & Images** | Shadow elevation system, text-on-image readability, icon sizing |
| 6 | **Polish & Finishing** | Supercharged defaults, accent borders, empty states, border alternatives |

## Quick Anti-Pattern Checklist

The 8 highest-signal problems checked before detailed analysis:

1. **Wall of Content** — Everything at same size/weight/color
2. **Ambiguous Spacing** — Equal gaps obscure element relationships
3. **Font Size Soup** — Too many arbitrary font sizes
4. **Color Without System** — Ad-hoc hex values, no shade palette
5. **One Shadow Fits All** — Same shadow on buttons, cards, and modals
6. **Border Everything** — Borders as default separator everywhere
7. **Full-Width Everything** — Content stretched to fill viewport
8. **Ignored Empty States** — "No items found" with no guidance

## Output Format

```
## Design Review

### What Works Well
- [Specific praise with why it works]

### Issues Found
1. **[Issue Name]** — [Dimension]
   - What: [Observable problem]
   - Why: [Principle being violated]
   - Fix: [Concrete CSS/Tailwind change]

### Quick Wins
- [Highest-impact, lowest-effort changes]
```

## Reference System

The plugin uses progressive disclosure to minimize context window usage:

| Layer | Size | Loaded When |
|-------|------|-------------|
| Skill metadata | ~100 words | Always (in memory) |
| SKILL.md | ~1,000 words | On activation |
| Each reference file | ~1,000-1,400 words | On demand per dimension |
| **Typical review** | **~2,500-3,500 words** | Only relevant references loaded |

### Reference Files

| File | Topic |
|------|-------|
| `design-process.md` | Start with features, work low-fidelity, constrain choices, personality |
| `hierarchy-and-emphasis.md` | De-emphasize to emphasize, weight/color over size, labels strategy |
| `spacing-and-layout.md` | Non-linear spacing scale, fixed sidebars, proximity, max-width |
| `typography.md` | Hand-crafted type scale, proportional line-height, line length |
| `color.md` | HSL workflow, 8-10 shades, hue rotation, warm/cool greys, WCAG |
| `depth-and-images.md` | 5-level shadow system, two-part shadows, text on images |
| `polish-and-finishing.md` | Supercharged defaults, accent borders, fewer borders, empty states |

## Plugin Structure

```
ui-refactor/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── agents/
│   └── design-reviewer.md       # Review agent (screenshot/code/description)
├── commands/
│   └── design-review.md         # /design-review slash command
├── skills/
│   └── ui-refactor/
│       ├── SKILL.md             # Navigation hub + decision tree
│       └── references/
│           ├── design-process.md
│           ├── hierarchy-and-emphasis.md
│           ├── spacing-and-layout.md
│           ├── typography.md
│           ├── color.md
│           ├── depth-and-images.md
│           └── polish-and-finishing.md
└── README.md
```

## Requirements

None. Pure knowledge plugin — no external dependencies, APIs, or scripts.

## License

MIT
