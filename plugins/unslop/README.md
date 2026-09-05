# Unslop

Unslop is one post-generation engineering-quality plugin with two skills:

- **Codesavers** reviews changed code for avoidable state, defensive coding,
  verbosity, unnecessary abstractions, dependency-owned tests, and accidental
  complexity.
- **Specsavers** authors and reviews technical software specifications for
  precision, information density, decision completeness, and implementation
  readiness.

Reviews are report-only by default. Codesavers applies fixes, and Specsavers
edits or creates documents, only when you explicitly ask.

## Install

Install the single plugin for Codex:

```bash
codex plugin marketplace add timbrinded/kiln
codex plugin add unslop@kiln
```

Add the Kiln marketplace and install the plugin in Claude Code:

```text
/plugin marketplace add https://github.com/timbrinded/kiln.git
/plugin install unslop@kiln
```

## Use

Natural-language requests select the applicable skill:

```text
Unslop this implementation and report concrete simplifications.
Use Codesavers to review my current changes for avoidable complexity.
Specsavers this technical design before I send it for review.
Use Specsavers to write an implementation-ready spec for this feature.
Does this design actually warrant an ADR?
```

The explicit Claude Code identifiers are `/unslop:codesaver` and
`/unslop:specsaver`. The explicit Codex identifiers are `$unslop:codesaver` and
`$unslop:specsaver`.

## Doctrine

Codesavers preserves the original Unslop code-quality doctrine. Specsavers has
one central instruction:

> Make the specification as easy as possible for a competent engineer to
> understand and implement. Preserve its meaning, not its original wording.

A passage can be necessary and still be badly written. Specsavers rewrites
awkward, dense, repetitive, or badly ordered prose even when its information is
required, deletes prose that conveys no material information, and never deletes
a material constraint, decision, or rationale. It reads the complete document,
identifies missing material decisions without inventing answers, does not
require a universal template, and recommends an ADR only for a genuine
architectural fork.

## Independent specification review

For substantial specifications, Specsavers runs two read-only reviews against
the same unchanged source. The technical reviewer checks contracts, decisions,
and contradictions. The structure and readability reviewer checks how an
engineer learns the design, including organization, sentence connections, and
buried constraints. A technically complete document can still need a substantial
readability rewrite.

The parent checks both reports against the sources and owns all edits. Reviews
remain report-only. Requested rewrites and authored drafts go back to both
specialists for verification against the original documents or brief. Small,
self-contained passages use both perspectives within the parent. Explicit
requests to use or avoid delegation take precedence.

This workflow uses more model work and tokens than one review. Codex uses its
native subagent tools with role instructions packaged inside the skill; no
personal agent setup is required. Claude Code has thin specialist adapters to
the same references. If independent review or verification cannot run, the
parent applies the missing perspective and reports that limitation.

## Structure

```text
plugins/unslop/
├── agents/
│   ├── codesaver-reviewer.md
│   ├── specsaver-technical-reviewer.md
│   └── specsaver-readability-reviewer.md
└── skills/
    ├── codesaver/
    └── specsaver/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/
        └── evals/
```

## Sources

Thanks to George Gopen's *The New Science of Scientific Writing* for the
reader-expectation techniques behind Specsavers' readability guidance:
topic continuity, context before new information, subject–verb proximity,
direct actions, and visible emphasis. These are practical diagnostics, not
a house style or a requirement to comply with ASD-STE100.

Specsavers draws on [Nygard's ADR proposal](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions),
[BCP 14](https://www.rfc-editor.org/rfc/rfc8174), the
[NASA requirements guidance](https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/),
[INCOSE requirements guidance](https://www.incose.org/group/requirements-working-group/),
[EARS](https://alistairmavin.com/ears/),
[Rust RFC practice](https://github.com/rust-lang/rfcs),
[Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/),
the [Kubernetes KEP template](https://github.com/kubernetes/enhancements/blob/master/keps/NNNN-kep-template/README.md),
and Lamport's [Specifying Systems](https://lamport.azurewebsites.net/tla/book.html).
These sources inform the doctrine; none is a mandatory process or template.
