# Kiln release history

Kiln versions each plugin independently. Plugin tags use the form
`<plugin>-v<version>`. Repository-wide marketplace releases use `v<version>`.

Historical GitHub releases were reconstructed from the first commit on
`master` that contained each manifest version. Their annotated tags preserve
that commit's date. GitHub does not permit changing a release's publication
timestamp, so retroactive release notes state the original release date.

## Kiln v0.6.0

<!-- release:v0.6.0 -->
**Release date:** 2026-09-05

Unslop now includes Codesavers for code cleanup and Specsavers for technical
specification review and authoring, available to Codex and Claude Code.

### Included plugin versions

| Plugin | Version |
|---|---:|
| swift-design | 0.2.1 |
| performance-optimization | 0.2.1 |
| ui-refactor | 0.2.1 |
| unslop | 0.4.0 |
| teach-me | 0.1.1 |
| infographic | 0.1.1 |
| lottie-animation | 0.1.1 |
| stacked-prs | 0.1.0 |

See the Unslop v0.4.0 notes below and
[PR #12](https://github.com/timbrinded/kiln/pull/12).

Compare
[`v0.5.0...v0.6.0`](https://github.com/timbrinded/kiln/compare/v0.5.0...v0.6.0).
<!-- /release:v0.6.0 -->

## Kiln v0.4.0

<!-- release:v0.4.0 -->
**Release date:** 2026-07-30

Kiln now supports Codex and Claude Code from the same repository.

### Highlights

- Added a Codex marketplace covering all seven Kiln plugins.
- Added native `.codex-plugin/plugin.json` manifests with Codex interface
  metadata and starter prompts.
- Kept the existing Claude Code manifests and installation flow.
- Added Git and local Codex marketplace installation instructions.
- Synchronized plugin versions across the Claude marketplace and both plugin
  manifest formats.

### Included plugin versions

| Plugin | Version |
|---|---:|
| swift-design | 0.2.1 |
| performance-optimization | 0.2.1 |
| ui-refactor | 0.2.1 |
| unslop | 0.3.1 |
| teach-me | 0.1.1 |
| infographic | 0.1.1 |
| lottie-animation | 0.1.1 |

### Install with Codex

```bash
codex plugin marketplace add timbrinded/kiln
codex plugin add unslop@kiln
```

See [PR #10](https://github.com/timbrinded/kiln/pull/10) and
[commit `54c6ac2`](https://github.com/timbrinded/kiln/commit/54c6ac2cbb391b8790e41774a525cb12290e9062).
<!-- /release:v0.4.0 -->

## swift-design v0.2.1

<!-- release:swift-design-v0.2.1 -->
**Release date:** 2026-07-30

### Added

- Native Codex plugin manifest and interface metadata.
- Codex starter prompts for SwiftUI review, HIG improvement, and accessible
  view generation.
- Installation through the Kiln Codex marketplace.

### Compatibility

- The existing Claude Code plugin remains supported.
- Skill behavior and the 40-rule review system are unchanged.

Compare
[`swift-design-v0.2.0...swift-design-v0.2.1`](https://github.com/timbrinded/kiln/compare/swift-design-v0.2.0...swift-design-v0.2.1).
<!-- /release:swift-design-v0.2.1 -->

## swift-design v0.2.0

<!-- release:swift-design-v0.2.0 -->
**Original release date:** 2026-02-25

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Changed

- Aligned swift-design with Kiln's `0.2.0` marketplace version.
- Updated the multi-plugin marketplace documentation.

This was a version-alignment release. It did not change the SwiftUI review
rules or generation behavior.

Compare
[`swift-design-v0.1.0...swift-design-v0.2.0`](https://github.com/timbrinded/kiln/compare/swift-design-v0.1.0...swift-design-v0.2.0).
<!-- /release:swift-design-v0.2.0 -->

## swift-design v0.1.0

<!-- release:swift-design-v0.1.0 -->
**Original release date:** 2026-02-17

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Initial release

- Added 40 machine-enforceable SwiftUI rules across modern APIs,
  accessibility, platform idioms, layout, typography, and color.
- Added code review with severity-ranked findings and A-F grading.
- Added visual screenshot review across five design dimensions.
- Added HIG-compliant view generation and targeted iteration workflows.
- Added Claude Code commands, automatic skill activation, and a read-only
  reviewer agent.

Source:
[`b24652a`](https://github.com/timbrinded/kiln/commit/b24652ab201c8aa5c9ae598a99bc335f62139878).
<!-- /release:swift-design-v0.1.0 -->

## performance-optimization v0.2.1

<!-- release:performance-optimization-v0.2.1 -->
**Release date:** 2026-07-30

### Added

- Native Codex plugin manifest and interface metadata.
- Codex starter prompts for profiling, hot-path optimization, and regression
  review.
- Installation through the Kiln Codex marketplace.

### Compatibility

- The existing Claude Code plugin remains supported.
- Optimization guidance and cross-language references are unchanged.

Compare
[`performance-optimization-v0.2.0...performance-optimization-v0.2.1`](https://github.com/timbrinded/kiln/compare/performance-optimization-v0.2.0...performance-optimization-v0.2.1).
<!-- /release:performance-optimization-v0.2.1 -->

## performance-optimization v0.2.0

<!-- release:performance-optimization-v0.2.0 -->
**Original release date:** 2026-02-25

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Changed

- Aligned performance-optimization with Kiln's `0.2.0` marketplace version.
- Updated the multi-plugin marketplace documentation.

This was a version-alignment release. It did not change the optimization
workflow or reference guidance.

Compare
[`performance-optimization-v0.1.0...performance-optimization-v0.2.0`](https://github.com/timbrinded/kiln/compare/performance-optimization-v0.1.0...performance-optimization-v0.2.0).
<!-- /release:performance-optimization-v0.2.0 -->

## performance-optimization v0.1.0

<!-- release:performance-optimization-v0.1.0 -->
**Original release date:** 2026-02-17

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Initial release

- Added a measure, identify, optimize, and verify workflow.
- Added guidance for algorithms, memory representation, unnecessary work,
  allocations, profiling, and rollout decisions.
- Added latency references and back-of-envelope estimation techniques.
- Added equivalent patterns and tooling for C++, Rust, and TypeScript.
- Added checklists that require baseline measurement and post-change
  verification.

Source:
[`f4a123a`](https://github.com/timbrinded/kiln/commit/f4a123ab75c476f205362c0b4770e320cd639abc).
<!-- /release:performance-optimization-v0.1.0 -->

## ui-refactor v0.2.1

<!-- release:ui-refactor-v0.2.1 -->
**Release date:** 2026-07-30

### Added

- Native Codex plugin manifest and interface metadata.
- Codex starter prompts for interface review, hierarchy and spacing
  refactoring, and Tailwind improvement.
- Installation through the Kiln Codex marketplace.

### Compatibility

- The existing Claude Code plugin remains supported.
- The six-dimension design review remains unchanged.

Compare
[`ui-refactor-v0.2.0...ui-refactor-v0.2.1`](https://github.com/timbrinded/kiln/compare/ui-refactor-v0.2.0...ui-refactor-v0.2.1).
<!-- /release:ui-refactor-v0.2.1 -->

## ui-refactor v0.2.0

<!-- release:ui-refactor-v0.2.0 -->
**Original release date:** 2026-02-25

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Changed

- Aligned ui-refactor with Kiln's `0.2.0` marketplace version.

This was a version-alignment release. It did not change the design rules or
review output.

Compare
[`ui-refactor-v0.1.0...ui-refactor-v0.2.0`](https://github.com/timbrinded/kiln/compare/ui-refactor-v0.1.0...ui-refactor-v0.2.0).
<!-- /release:ui-refactor-v0.2.0 -->

## ui-refactor v0.1.0

<!-- release:ui-refactor-v0.1.0 -->
**Original release date:** 2026-02-17

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Initial release

- Added screenshot, CSS, Tailwind, and natural-language UI review.
- Added structured checks for hierarchy, spacing, typography, color, depth,
  imagery, and finishing.
- Added concrete CSS fixes and a prioritized quick-win format.
- Added eight high-signal anti-patterns for common interface defects.
- Added a Claude Code command, automatic skill activation, and a reviewer
  agent.

Source:
[`a66fff2`](https://github.com/timbrinded/kiln/commit/a66fff2d9219d2c1d6712c552345e5fddf7647f1).
<!-- /release:ui-refactor-v0.1.0 -->

## unslop v0.4.0

<!-- release:unslop-v0.4.0 -->
**Release date:** 2026-09-05

### Added

- Added Specsavers for concise technical-specification review and authoring.
- Added ten specification-quality directives with per-artifact lenses and
  eighteen outcome-based evals covering review, rewrite, and authoring.
- Added independent technical and readability reviewers for substantial
  specifications, with one parent editor and verification against the original
  sources. Small passages retain a single-agent workflow.
- Added reader-expectation diagnostics for organization, sentence connections,
  emphasis, and direct actions, with safeguards against inventing logical
  relationships while rewriting.
- Packaged shared specialist instructions inside the skill for native Codex
  delegation and thin Claude Code adapters, plus Specsavers interface metadata.
  Independent passes use additional model work and tokens; unavailable checks
  are disclosed.

### Changed

- Renamed the internal `unslop` code-cleanup skill and reviewer to Codesavers.
- Repositioned Unslop as one post-generation engineering-quality plugin with
  sibling Codesavers and Specsavers skills.

### Compatibility

- Legacy natural-language requests such as `Unslop this branch` continue to
  select the same code-cleanup doctrine and report-only default.
- Explicit skill identifiers are now `/unslop:codesaver` in Claude Code and
  `$unslop:codesaver` in Codex.
- Existing code-quality directives, gotchas, fixtures, and Directive #15
  behavior are preserved.

See [PR #12](https://github.com/timbrinded/kiln/pull/12).

Compare
[`unslop-v0.3.1...unslop-v0.4.0`](https://github.com/timbrinded/kiln/compare/unslop-v0.3.1...unslop-v0.4.0).
<!-- /release:unslop-v0.4.0 -->

## unslop v0.3.1

<!-- release:unslop-v0.3.1 -->
**Release date:** 2026-07-30

### Added

- Native Codex plugin manifest and interface metadata.
- Codex starter prompts that preserve report-only behavior.
- Installation through the Kiln Codex marketplace.

### Compatibility

- The existing Claude Code plugin remains supported.
- Directive #15, assertion-level dependency-test review, and explicit apply
  authorization from `0.3.0` are preserved.

Compare
[`unslop-v0.3.0...unslop-v0.3.1`](https://github.com/timbrinded/kiln/compare/unslop-v0.3.0...unslop-v0.3.1).
<!-- /release:unslop-v0.3.1 -->

## unslop v0.3.0

<!-- release:unslop-v0.3.0 -->
**Original release date:** 2026-07-30

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Added

- Added Directive #15: test application-owned behavior, not behavior owned by
  an external dependency.
- Added assertion-level evidence requirements and explicit exemptions for
  configuration, integration, compatibility, regression, and test
  infrastructure coverage.
- Added reproducible fixtures and a four-provider evaluation rig for current
  and candidate skill variants.

### Changed

- Made normal unslop invocation report-only.
- Required explicit apply authorization before editing files.
- Combined committed, staged, unstaged, deleted, and untracked changes into
  one deduplicated review scope.
- Removed the duplicate legacy command contract and made the skill the
  authoritative workflow.

See [PR #8](https://github.com/timbrinded/kiln/pull/8),
[PR #9](https://github.com/timbrinded/kiln/pull/9), and
[commit `db9b06e`](https://github.com/timbrinded/kiln/commit/db9b06e231861a052ed1df993f91f6b0d223fc76).
<!-- /release:unslop-v0.3.0 -->

## unslop v0.2.0

<!-- release:unslop-v0.2.0 -->
**Original release date:** 2026-03-19

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Initial release

- Added 14 directives for reducing accidental complexity in generated code.
- Added diff-scoped review with concrete replacement code for every finding.
- Added guidance for state reduction, type trust, early returns, function
  splitting, assertion use, and argument design.
- Added false-positive guidance for framework conventions and warranted
  complexity.
- Added a reviewer agent for large diffs and post-fix typecheck and lint
  guidance.

See [PR #4](https://github.com/timbrinded/kiln/pull/4) and
[commit `74a9f23`](https://github.com/timbrinded/kiln/commit/74a9f23e13d8a34d76b0a36311bf83e29108e4fe).
<!-- /release:unslop-v0.2.0 -->

## teach-me v0.1.1

<!-- release:teach-me-v0.1.1 -->
**Release date:** 2026-07-30

### Added

- Native Codex plugin manifest and interface metadata.
- Codex starter prompts for codebase learning, guided debugging, and framework
  tutoring.
- Installation through the Kiln Codex marketplace.

### Compatibility

- The existing Claude Code plugin remains supported.
- The tutoring ladder and non-autonomous teaching behavior are unchanged.

Compare
[`teach-me-v0.1.0...teach-me-v0.1.1`](https://github.com/timbrinded/kiln/compare/teach-me-v0.1.0...teach-me-v0.1.1).
<!-- /release:teach-me-v0.1.1 -->

## teach-me v0.1.0

<!-- release:teach-me-v0.1.0 -->
**Original release date:** 2026-05-22

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Initial release

- Added tutoring for languages, frameworks, exercises, code review, and
  debugging.
- Added a progressive teaching ladder from concepts and hints to examples,
  pseudocode, and full solutions only when requested.
- Grounded guidance in local documentation, tests, starter code, and error
  messages.
- Prioritized guiding questions and checkpoints over autonomous file edits.

See [PR #5](https://github.com/timbrinded/kiln/pull/5) and
[commit `0ff1f0b`](https://github.com/timbrinded/kiln/commit/0ff1f0bc126894c8f460897acc0570265de53b91).
<!-- /release:teach-me-v0.1.0 -->

## infographic v0.1.1

<!-- release:infographic-v0.1.1 -->
**Release date:** 2026-07-30

### Added

- Native Codex plugin manifest and interface metadata.
- Codex starter prompts for repository, architecture, and feature
  infographics.
- Installation through the Kiln Codex marketplace.

### Compatibility

- The existing Claude Code plugin remains supported.
- Prompt and optional image-generation behavior are unchanged.

Compare
[`infographic-v0.1.0...infographic-v0.1.1`](https://github.com/timbrinded/kiln/compare/infographic-v0.1.0...infographic-v0.1.1).
<!-- /release:infographic-v0.1.1 -->

## infographic v0.1.0

<!-- release:infographic-v0.1.0 -->
**Original release date:** 2026-06-05

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Initial release

- Added structured infographic prompts from Markdown, ADRs, specifications,
  diagrams, research, and runbooks.
- Preserved uncertainty and source status instead of presenting proposals as
  settled architecture.
- Added orientation, density, format, style-reference, and reference-image
  controls.
- Added optional image generation when a compatible tool is attached and the
  user explicitly requests an image.

See [PR #6](https://github.com/timbrinded/kiln/pull/6) and
[commit `a8d6f8a`](https://github.com/timbrinded/kiln/commit/a8d6f8afcedb93bc6f11b680c956dc45ff70a905).
<!-- /release:infographic-v0.1.0 -->

## lottie-animation v0.1.1

<!-- release:lottie-animation-v0.1.1 -->
**Release date:** 2026-07-30

### Added

- Native Codex plugin manifest and interface metadata.
- Codex starter prompts for Lottie creation, compatibility review, and motion
  refinement.
- Installation through the Kiln Codex marketplace.

### Compatibility

- The existing Claude Code plugin remains supported.
- Player-first authoring, render verification, and loop guidance are
  unchanged.

Compare
[`lottie-animation-v0.1.0...lottie-animation-v0.1.1`](https://github.com/timbrinded/kiln/compare/lottie-animation-v0.1.0...lottie-animation-v0.1.1).
<!-- /release:lottie-animation-v0.1.1 -->

## lottie-animation v0.1.0

<!-- release:lottie-animation-v0.1.0 -->
**Original release date:** 2026-06-18

> Historical release record. The annotated tag points to the original release
> commit and preserves its date.

### Initial release

- Added player-first Lottie and Bodymovin authoring with procedural
  generators.
- Added rendered-frame verification and seamless-loop closure checks.
- Added guidance for large but stable animation assets.
- Added motion-system refinement, app integration, and renderer compatibility
  workflows.
- Restored detailed authoring mechanics and documented upstream provenance and
  reference routing before the release reached `master`.

See [PR #7](https://github.com/timbrinded/kiln/pull/7) and
[commit `9d984ca`](https://github.com/timbrinded/kiln/commit/9d984ca5527b3340a2e4f1d88d9bca14a684b4c3).
<!-- /release:lottie-animation-v0.1.0 -->
