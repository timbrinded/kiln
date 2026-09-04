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

Codesavers preserves the original Unslop code-quality doctrine. Specsavers uses
two tests:

> If this sentence were removed, could a reasonable implementer form a
> materially different interpretation of the required system?

> Does the specification force a competent implementer to make a material
> product or architectural decision that the author should have made?

**The review checklist may be exhaustive. The specification must not be.** Keep
nothing that does not constrain the system or materially explain a design
decision. Omit no constraint whose absence forces the implementer to invent the
design. Visible section coverage is not evidence of review completeness.

Specsavers reads the complete target specification. It reports only material
concerns activated by the design. It does not require a universal template,
invent missing decisions, or recommend an ADR for routine implementation work.

## Structure

```text
plugins/unslop/
├── agents/
│   ├── codesaver-reviewer.md
│   └── specsaver-reviewer.md
└── skills/
    ├── codesaver/
    └── specsaver/
```

## Sources

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
