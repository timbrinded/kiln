---
description: Review SwiftUI code for design quality, HIG compliance, accessibility, and modern API usage
argument-hint: "[file-or-screenshot-path] [optional-feedback]"
allowed-tools: Read, Write, Edit, Grep, Glob
---

Review the SwiftUI code or screenshot for design quality using the swift-design skill.

**Determine the mode from arguments:**

- If `$1` is a `.swift` file path → Code review mode
- If `$1` is an image path (`.png`, `.jpg`, `.jpeg`) → Visual review mode
- If `$2` is provided → Iteration mode (review + apply feedback)
- If no arguments → Review all `.swift` files containing `View` in the current project

**For code review:**
1. Read the target file(s)
2. Load the swift-design skill's review checklist
3. Evaluate against all 40 rules, prioritized: Modern API → Accessibility → Platform Idioms → Layout → Typography → Color
4. Calculate letter grade
5. Output findings by severity: 🔴 Critical → 🟡 Warning → 🔵 Suggestion → 🟢 Praise
6. Each finding includes: rule ID, file:line, description, concrete code fix

**For visual review (screenshot):**
1. Read the screenshot
2. Load the visual review rubric
3. Score across 5 dimensions: platform nativeness, visual hierarchy, spacing consistency, color coherence, typography discipline
4. Calculate weighted average → letter grade
5. List top 3 actionable improvements

**For iteration (code + feedback):**
1. Read the target file
2. Focus review on the feedback area
3. Apply targeted improvements as minimal edits
4. Re-run checklist on modified code
5. Report what changed and the updated grade

Always check `.claude/swift-design.local.md` for iOS target version and strictness settings before reviewing.
