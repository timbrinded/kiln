---
description: Review a screenshot, code file, or UI description for design quality using Refactoring UI principles
argument-hint: "[screenshot-or-code-path] [optional-focus-area]"
allowed-tools: Read, Grep, Glob
---

Review the given input for UI design quality using the ui-refactor skill.

**Determine the mode from arguments:**

- If `$ARGUMENTS` contains an image path (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`) → Visual review mode
- If `$ARGUMENTS` contains a code file path (`.css`, `.scss`, `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`) → Code review mode
- If `$ARGUMENTS` contains text description → Advisory mode
- If no arguments → Prompt the user to provide a screenshot, file path, or description

**Optional focus area (second argument):**
If the user specifies a focus area (e.g., "typography", "color", "spacing", "hierarchy", "depth", "polish"), narrow the review to that dimension and load only the relevant reference file.

**For visual review (screenshot):**
1. Read the screenshot
2. Load the ui-refactor skill's SKILL.md for the review framework
3. Run the Quick Anti-Pattern Checklist first
4. Evaluate across all 6 dimensions (or focused dimension if specified)
5. Load specific reference files as issues emerge
6. Output: What Works Well → Issues Found (What/Why/Fix) → Quick Wins

**For code review:**
1. Read the target file(s)
2. Load the ui-refactor skill's SKILL.md
3. Check against specific code-level patterns:
   - Spacing values: Should come from the scale (4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256)
   - Font sizes: Should come from the type scale (12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72)
   - Line-heights: Should vary by font size (not a single global value)
   - Shadows: Should use a defined elevation system (not one shadow for everything)
   - Colors: Should come from a palette with shade variations (not ad-hoc hex values)
   - Borders: Check if spacing or box-shadow would be cleaner alternatives
   - Grey values: Should have saturation > 0% for temperature
4. Load specific reference files as issues emerge
5. Output: What Works Well → Issues Found with file:line references → Quick Wins

**For advisory mode (description):**
1. Identify which dimension(s) the description maps to
2. Load the relevant reference file(s)
3. Provide the specific principles, concrete values, and reasoning
4. If the description is vague ("looks amateur"), run the Quick Anti-Pattern Checklist

Every issue must include a concrete CSS/Tailwind fix and an explanation of WHY — so the user learns the principle, not just the fix.
