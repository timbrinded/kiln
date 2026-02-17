# Design Process

## Mental Model Shifts

**Wrong:** "I need to design the whole app layout first — navigation, sidebar, header — then fill in features."
**Right:** Start with a single feature. Design the flight search form, the invoice table, the comment thread. The app shell emerges from the features, not the other way around. You lack the information to design navigation until you've designed what it navigates to.

**Wrong:** "I should get the design pixel-perfect in Figma before writing any code."
**Right:** Work in short cycles: design a simple version → build it → discover edge cases in the real thing → iterate → move to the next feature. Static mockups can't reveal interaction problems. Build the real thing as early as possible.

**Wrong:** "I need to pick the perfect shade of blue for this button."
**Right:** You shouldn't be choosing from millions of options. Define constrained systems (8-10 color shades, a type scale, a spacing scale) upfront, then pick from the system. The hard work happens once during system definition, not on every individual decision.

## Principles

### Start with Features, Not Layouts
- WHEN starting a new screen → DO design the core feature first (form, list, card), not the shell (nav, sidebar, footer)
- WHEN tempted to design the navigation → DO wait until you have 3+ features designed, then let the navigation structure emerge from what you've built
- BECAUSE you can't make informed layout decisions without content to inform them

### Work Low-Fidelity First
- WHEN exploring layout ideas → DO sketch with pen/paper or use wireframes — avoid pixel-level decisions early
- WHEN refining an idea → DO design in grayscale first, using only spacing, size, and weight to establish hierarchy
- WHEN grayscale hierarchy is solid → DO add color as an enhancement layer, not a structural crutch
- BECAUSE if your design requires color to create hierarchy, the hierarchy is weak

### Ship the Smallest Useful Version
- WHEN a feature has "nice-to-have" additions → DO design and ship the core version first, add extras later
- WHEN estimating scope → DO expect features to be harder than anticipated; design for the pessimistic case
- BECAUSE a comment system without file attachments is better than no comment system at all

### Define Systems, Not Individual Values
- WHEN making a spacing, sizing, color, or typography decision → DO pick from a pre-defined constrained system
- WHEN no system exists yet → DO define one before continuing (see spacing, typography, and color references)
- BECAUSE designing by process of elimination from a constrained set is fast and consistent; designing from infinite options is slow and inconsistent

## Establishing Personality

Four concrete levers control how a design "feels":

| Lever | Formal / Serious | Playful / Casual |
|-------|-----------------|------------------|
| **Font** | Serif or neutral sans-serif (e.g., Inter, Helvetica) | Rounded sans-serif (e.g., Nunito, Poppins) |
| **Color** | Blue, dark tones, muted palettes | Pink, bright tones, saturated palettes |
| **Border radius** | 0–4px (sharp or minimal) | 12–24px or fully rounded |
| **Language** | "Verify your identity" / "We invest in companies" | "Sweet, thanks Steve!" / "Let's get started" |

- WHEN choosing personality → DO pick a consistent position across all four levers
- WHEN unsure → DO study sites used by your target audience and match their tone
- BECAUSE mixing sharp corners with playful language creates incoherence

## Anti-Patterns

### Shell-First Design
- **Detection:** You're sketching navigation structure before any feature is designed
- **Fix:** Close the app shell. Open a blank canvas. Design one feature.

### Designing Everything Upfront
- **Detection:** You have 10+ screens designed in Figma but zero lines of code
- **Fix:** Pick the most important feature, design a simple version, build it, iterate

### No System
- **Detection:** You're manually typing pixel values (13px, 17px, 22px) or picking colors from the color picker each time
- **Fix:** Define your spacing scale, type scale, and color palette before the next decision (see respective reference files)
