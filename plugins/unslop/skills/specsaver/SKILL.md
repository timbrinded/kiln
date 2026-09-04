---
name: specsaver
description: >-
  This skill should be used when the user asks to "review this technical spec",
  "check this design document", "tighten this RFC", "find ambiguity",
  "make this implementation-ready", "remove documentation slop", "write a
  technical specification", "review these requirements", "check this API or
  protocol spec", "review this migration plan", "decide whether this needs an
  ADR", or improve a software engineering design document. It reviews and
  authors precise, concise specifications; finds missing material decisions,
  vague requirements, negative-definition prose, fake alternatives, gratuitous
  non-goals, and unnecessary ADRs. It performs a broad internal applicability
  review but reports only material concerns. Existing documents are report-only
  by default and are edited only when the user explicitly requests changes. It
  must not invent requirements or require a universal template. It must not
  replace a general code, security, performance, or architecture review merely
  because a Markdown document is present.
---

# Specsavers — Technical Specification Quality

Transfer a precise software design from one engineer's head into another's with
the minimum cognitive load needed to implement and review it correctly. Detect
both missing design and documentation slop.

Use two governing questions:

1. **If this sentence were removed, could a reasonable implementer form a
   materially different interpretation of the required system?**
2. **Does the specification force a competent implementer to make a material
   product or architectural decision that the author should have made?**

Keep nothing that does not constrain or explain the implementation. Omit no
constraint whose absence forces the implementer to invent the design.

## Modes

Determine the mode before reviewing any document:

- **Review** is the default for an existing document. Accept `--check` as an
  explicit report-only convention. Report findings, then stop.
- **Apply** requires an explicit request to edit, rewrite, fix, apply findings,
  or use `--apply`. Report findings first, then make the smallest coherent edit.
- **Author** requires an explicit request to write, draft, or create a technical
  specification. Build the leanest structure that transfers the known design.

Treat `--check`, `--apply`, `--files path1 path2 ...`, `--profile
<auto|design|requirements|api|migration|adr>`, and an explicitly requested
positional diff base ref as prompt conventions. Do not add a parser or runtime.
Do not implement the system described by the specification.

## Resolve the Target

Use this precedence:

1. Explicit file paths, attachments, quoted documents, or inline content.
2. Files named by the user in the current request.
3. For a repository-wide request to review current specification changes,
   changed specification candidates.
4. If no candidate is established, report that no target specification was
   found and stop.

Likely candidates are Markdown, MDX, reStructuredText, or plain-text files with
paths or names containing `spec`, `design`, `proposal`, `architecture`,
`requirements`, `rfc`, `adr`, `migration`, or `rollout`. Do not classify every
README, changelog, or ordinary documentation file as a specification.

For every target:

- Read the complete document, even in diff mode.
- Follow local links to authoritative schemas, decisions, and related
  specifications only when needed to understand a claim.
- Inspect code or conventions only when they establish context or reveal a
  contradiction.
- Use related material as evidence without widening into a general codebase
  audit.
- In diff mode, use unchanged text for context, but report only issues
  introduced by or materially related to the changed proposal. A missing
  requirement is in scope when the proposal creates the need for it.

## Classify Profile and Maturity

Classify the document privately. Profiles and maturity are applicability lenses,
not required headings or templates. Load
`references/document-profiles.md` when classification affects the review.

Profiles:

- **Design:** what system will be built, and why this design?
- **Requirements:** what observable behavior and constraints must hold?
- **API:** what exact contract permits correct use or independent
  implementation?
- **Migration:** how does the system move safely between states?
- **ADR:** which architectural fork was selected, and why?
- **Composite:** which applicable parts of those profiles form one coherent
  model?

Maturity:

- **Exploratory:** alternatives and managed open questions are expected.
- **Decision-ready:** the problem, constraints, and live choices permit a
  design decision.
- **Implementation-ready:** no material product or architectural choice is left
  to the implementer.
- **As-built:** claims about deployed behavior must agree with authoritative
  implementation artifacts.

Do not fail an exploratory document because choices remain open. Flag unknowns
disguised as decisions and approved implementation documents that still defer
material behavior.

## Silent Applicability Pass

Form a private two-to-five sentence model of the proposed system. Then inspect
only concerns activated by its mechanisms:

| Design trigger | Inspect silently |
|---|---|
| Network or service call | Timeout, retry class and identity, partial failure, authentication, observability |
| Queue or asynchronous worker | Delivery, ordering, deduplication, leases, concurrency, terminal states, cancellation |
| Persisted schema or data ownership change | Source of truth, migration, backfill, compatibility, retention, reversal limits |
| Public API or protocol | Schema, errors, authentication, authorization, idempotency, pagination, versioning, interoperability |
| Key, secret, signature, or trust-boundary change | Authority, integrity, custody, rotation, recovery, replay, audit |
| Concurrent or distributed writers | Atomicity, isolation, race resolution, consistency, clocks, leader failure |
| User or regulated data | Collection purpose, access, retention, deletion, disclosure |
| Availability- or latency-critical path | Load model, threshold, capacity, degradation, recovery |
| Deployment behavior change | Rollout, version skew, gating, abort criteria, reversal, monitoring |

Do not output checked-but-inapplicable rows. Silence is correct for irrelevant
concerns.

## The 17 Directives

| # | Directive | Core test |
|---|---|---|
| 1 | Establish the problem before the mechanism | Can the reader judge the mechanism against an affected actor and intended outcome? |
| 2 | Specify the system positively | Does the text state what the system owns and does before useful prohibitions? |
| 3 | Bound scope only where ambiguity is plausible | Does each goal, boundary, or non-goal distinguish a credible interpretation? |
| 4 | Keep statement roles distinct | Can the reader distinguish facts, requirements, decisions, rationale, assumptions, examples, tasks, and unknowns? |
| 5 | Decide material behavior; leave local mechanics local | Could compliant implementations behave materially differently, or is local code structure prescribed without cause? |
| 6 | Use one concept, one term, and an explicit actor | Are vocabulary and responsibility stable and unambiguous? |
| 7 | Write atomic, observable behavior | Does each obligation identify its condition or trigger, actor, and observable response? |
| 8 | Define state and material failure behavior | Are ownership, source of truth, legal transitions, invariants, and activated failures clear? |
| 9 | Quantify material quality attributes | Are important quality claims measurable under stated conditions? |
| 10 | Treat boundaries as contracts | Can both sides implement schema and interaction semantics correctly? |
| 11 | Use normative language precisely and sparingly | Does requirement force express a real, verifiable constraint? |
| 12 | Document only live alternatives and trade-offs | Could a reasonable engineer advocate each option under the stated constraints? |
| 13 | Record ADRs only for architectural forks | Do all four ADR gates pass, and does a separate record add value? |
| 14 | Make every sentence and section earn attention | Would deletion change the reader's material model or compress difficult reasoning? |
| 15 | Use examples, tables, and diagrams only to compress complexity | Is the representation clearer than prose and consistent with the contract? |
| 16 | Connect verification and safe evolution to the design | Can material behavior be proved and activated delivery risks be controlled? |
| 17 | Maintain one authoritative model | Do values, terms, ownership, transitions, examples, and references agree? |

Load `references/spec-quality-directives.md` for the full tests, repairs,
examples, and false-positive boundaries. A candidate finding is not final until
the relevant detail and `references/gotchas.md` have been checked.

## ADR Threshold

Recommend a separate ADR only when all four gates pass:

1. A real fork exists between at least two credible approaches.
2. The choice is architecturally significant: it affects structure, quality
   attributes, dependencies, interfaces, trust or data boundaries,
   construction technique, or costly reversibility.
3. The rationale has durable value that future engineers may need and cannot
   infer from the resulting code.
4. A separate record adds discoverability or longevity that outweighs
   duplication.

When gates 1–3 pass but the canonical feature specification already preserves
the decision durably, keep it there. Do not demand duplicate records. Load
`references/adr-threshold.md` before any ADR recommendation or creation.

## Load References Deliberately

- **A possible directive finding:** load the matching section of
  `references/spec-quality-directives.md`, then load
  `references/gotchas.md` before finalizing it.
- **Profile or maturity affects applicability:** load
  `references/document-profiles.md`.
- **Negative prose, requirement force, actor ambiguity, vague qualifiers, or
  atomicity is at issue:** load `references/normative-language.md`.
- **An ADR is discussed or might be recommended:** load
  `references/adr-threshold.md` before reaching a conclusion.
- **A full pattern is needed to understand or author a repair:** load the
  matching case in `references/worked-examples.md`.

Load only references relevant to the task, except that
`references/gotchas.md` is mandatory before finalizing every finding.

## Review Workflow

For a single document or a small coherent set:

1. Resolve target documents and mode.
2. Read every target in full.
3. Read only related local artifacts needed for terms, decisions, schemas, or
   contradictions.
4. Classify profile and maturity.
5. Form the private system model.
6. Run the silent applicability pass.
7. Evaluate the 17 directives.
8. Load the relevant directive detail and gotchas for every candidate finding.
9. Group findings with one root cause.
10. Sort by severity and causal order.
11. Report only material findings.
12. Stop in review mode.
13. In apply mode, edit only the approved scope, validate coherence and local
    links, then report the exact result.

For a large set, assign `specsaver-reviewer` agents by coherent document group.
Keep a feature spec with linked ADRs, schemas, protocols, or migration notes
when their meanings depend on each other. The parent invocation merges
duplicates, reconciles interpretations, applies all four ADR gates, and returns
one concise report.

Before reporting a finding, answer all of these questions:

- What precise text or omission causes it?
- What materially wrong interpretation, decision, or cognitive cost follows?
- Which directive applies?
- What exact repair is available?
- Is the repair derivable, or does it require a human decision?
- Is the concern activated by this design?

If any answer is missing, do not report the finding.

## Severity and Report Contract

- **Blocker:** materially different implementations can claim compliance; a
  security, integrity, state, compatibility, or ownership invariant is missing
  or contradictory; required behavior cannot be verified; an
  implementation-ready document leaves a material decision open; or safe
  introduction cannot be derived where the design requires it.
- **Major:** likely to cause meaningful rework, a wrong design-review
  conclusion, operational failure, or substantial confusion, while the central
  system remains inferable.
- **Minor:** local ambiguity, repetition, weak structure, or excess prose worth
  correcting without changing the main design.

Do not report nits. Use exactly one repair verb per finding:

| Verb | Use when |
|---|---|
| **Rewrite** | Replace ambiguous or negative-definition prose. |
| **Split** | Separate independent obligations or concepts. |
| **Add** | Supply missing text already derivable from authoritative material. |
| **Move** | Put information where its role or authority is clear. |
| **Quantify** | Replace a subjective quality with an established acceptance condition. |
| **Resolve** | Obtain a material decision that cannot be inferred. |
| **Reconcile** | Remove a contradiction and establish one canonical statement. |
| **Delete** | Remove ceremonial, duplicate, or irrelevant content. |
| **Consolidate** | Replace repeated fragments with one authoritative statement. |

Use this output:

```markdown
## Specsavers

**Verdict:** Not implementation-ready — 2 blockers, 1 major.

### Findings

1. **[BLOCKER] Directive 8 — Retry exhaustion has no terminal state**
   - **Evidence:** Section 4 retries transient import failures, but the state
     model defines only `pending` and `indexed`.
   - **Consequence:** An implementation may retry forever, silently stop, or
     invent a failure state; each behavior fits the document.
   - **Fix: Resolve** — choose the terminal state and required import-record
     update after retry exhaustion.
   - **Required decision:** The available material does not determine the state
     name or retry budget.
```

Rules:

- Begin every review result with `## Specsavers`; do not add a preamble.
- Do not add praise or repeat findings as recommendations.
- Do not list concerns that were checked and found irrelevant. When findings
  exist, stop after the final finding; do not add a `No other findings` recap.
- Do not reproduce the complete document.
- Provide replacement prose only when authoritative material determines it.
- State the question for a missing decision. Never invent the answer.
- Include **Required decision** only when the repair cannot be derived. Never
  write `Required decision: None`.
- Before returning, remove every **Required decision** line that gives a
  conditional default or an answer already derivable from the source.
- Group instances when one root cause and repair covers them.
- Include a short interpretation paragraph only when findings depend on it.
- If there are no material findings, return only `## Specsavers` followed by
  one or two sentences; omit the verdict and findings sections.

## Apply Mode

Begin from reported findings. Preserve the user's intent, established voice,
useful structure, and unrelated changes. Prefer deletion and consolidation
before adding sections. Replace negative-definition clusters with a positive
model, but retain precise prohibitions and invariants. Remove fake alternatives,
fanciful non-goals, empty headings, and irrelevant `N/A` sections.

Do not add security, migration, observability, or rollback sections unless the
design activates them. Do not create an ADR unless all four gates pass and the
user explicitly asks for that record. Never invent values, policies,
boundaries, or decisions.

After editing:

1. Re-read the complete document.
2. Reconcile terms, values, ownership, and state transitions.
3. Check examples and diagrams against normative prose.
4. Confirm local links resolve where tools permit.
5. Run available Markdown or documentation checks.
6. Report changed files, resolved findings, unresolved decisions, and commands
   actually run.

## Author Mode

1. Establish the problem and observable outcome.
2. Identify the system boundary and actors.
3. Extract known requirements, constraints, decisions, and real unknowns.
4. Identify material choices the author has actually made.
5. Choose the smallest useful structure for the profile.
6. Describe the positive system model first.
7. Add contracts, state, failure semantics, qualities, verification, and
   delivery detail only where activated.
8. Include alternatives only when they explain a live choice.
9. Keep unresolved material questions explicit.
10. Run the 17-directive self-review before returning the document.

A feature spec may use `Problem`, `Proposed design`, `Behavior and contracts`,
`Decisions and rationale`, `Verification and delivery`, and `Open questions`,
but every heading after `Proposed design` is conditional. Combine, rename, or
omit sections. Never add empty headings or `Not applicable` tombstones.

## Exclusions

Do not:

- impose a universal specification template;
- create ADRs automatically;
- require goals, non-goals, risks, alternatives, security, observability,
  migration, rollback, or other headings in every document;
- assign a numerical grade or synthetic quality score;
- perform generic grammar, punctuation, or Markdown-style linting;
- replace a requested code, security, performance, or architecture review
  merely because the target is Markdown;
- add a runtime, parser, or static-analysis dependency;
- implement the system described by the specification;
- specify helper names, directory layouts, libraries, or algorithms without a
  material reason; or
- expand a specification merely to make it look comprehensive.

## Reference Index

| File | Load when |
|---|---|
| `references/spec-quality-directives.md` | Testing or repairing any of the 17 directives |
| `references/document-profiles.md` | Classifying profile, maturity, applicability, or minimal structure |
| `references/normative-language.md` | Reviewing positive specification, prohibitions, actors, atomic requirements, or requirement force |
| `references/adr-threshold.md` | Classifying a decision or discussing a separate ADR |
| `references/gotchas.md` | Finalizing every candidate finding and controlling false positives |
| `references/worked-examples.md` | Applying complete patterns in author or apply mode |
