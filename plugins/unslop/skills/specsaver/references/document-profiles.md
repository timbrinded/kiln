# Document Profiles and Maturity

Use profiles and maturity as internal review lenses. They select applicable
questions; they are not mandatory templates, section lists, or document types
that an author must declare.

## Classify by the Document's Primary Question

### Technical design or feature specification

**Primary question:** What system will be built, and why this design?

Inspect the problem, positive system model, responsibilities, state and
contracts, material choices, verification, and only delivery concerns activated
by the design.

Applicability questions:

- Is the desired outcome clear enough to judge the mechanism?
- Are component responsibilities and sources of truth explicit?
- Are material design choices decided and their real trade-offs explained?
- Can required behavior and activated operational concerns be verified?

Minimal useful shape: for a local change, a problem paragraph, proposed design,
and focused verification can be enough. Add contract, decision, state, or
delivery sections only when they compress relevant detail.

### Requirements specification

**Primary question:** What observable behavior and constraints must hold?

Inspect actors, triggers, responses, state, invariants, measurable quality
attributes, and verification. Separate a required outcome from one possible
implementation.

Applicability questions:

- Does each material obligation identify an actor and observable response?
- Are conditional and temporal rules unambiguous?
- Can each requirement be verified independently?
- Are assumptions, examples, and optional behavior distinguishable from the
  contract?

Minimal useful shape: group requirements by behavior or lifecycle, not by a
universal taxonomy. A short list of precise clauses may be the complete
document.

### API or protocol specification

**Primary question:** What exact contract permits correct use or independent
implementation?

Inspect authoritative schemas, units, required and optional fields, null
semantics, validation, errors, authentication, authorization, identity,
ordering, delivery, atomicity, versioning, compatibility, and boundary examples
only where applicable.

Applicability questions:

- Can each side implement the interaction without private assumptions?
- Are identities, errors, and retry or duplicate semantics stable?
- Does the text point to one canonical schema instead of copying it?
- Can clients evolve through the expected version-skew window?

Minimal useful shape: link the authoritative schema, define local semantics and
state, and include only examples that expose a boundary case. Protocol detail
required for interoperability is not excess prose.

### Migration or rollout specification

**Primary question:** How does the system move safely from one state to another?

Inspect preconditions, phases, compatibility window, data transition, backfill,
observability, abort criteria, reversal limits, operator actions, and completion
proof as activated by the change.

Applicability questions:

- What old and new versions coexist, and what must remain compatible?
- Which step first makes reversal costly or impossible?
- What evidence permits advance, abort, or completion?
- Who owns data repair and partial progress?

Minimal useful shape: a small ordered sequence with entry, advance, abort, and
completion conditions is often clearer than many generic operations headings.

### Architecture decision record

**Primary question:** Which architectural fork was chosen, and why?

First load `adr-threshold.md`. Inspect the context, credible options, selected
decision, decision-driving forces, and consequences. An ADR is not a synonym
for a feature note or task.

Applicability questions:

- Did a real architectural fork exist?
- Could a reasonable engineer advocate each recorded option?
- Will the rationale remain valuable when the feature work is no longer
  current?
- Does a separate record add value beyond the canonical feature spec?

Minimal useful shape: context, decision, live alternatives or forces, and
consequences. Do not require an ADR for routine implementation.

### Composite document

**Primary question:** Which combination of the other questions must one
coherent model answer?

Use only applicable elements. For example, a cross-service feature spec may
include a protocol contract and rollout sequence without becoming three
documents or filling three templates.

Applicability questions:

- Which parts share terms, state, or authority and should remain together?
- Would separation cause duplication or make an invariant harder to review?
- Does each section serve the primary design rather than a process category?

Minimal useful shape: order information for reader comprehension—usually
problem, positive model, then activated contracts, decisions, verification, and
delivery—not for template completion.

## Infer Maturity

Use explicit status first, then the document's language, repository context,
and requested review purpose.

### Exploratory

Alternatives and open questions are expected. Check that the problem and
unknowns are honest, live options are credible, and blocking questions are
distinguished from later refinements. Do not report a finding merely because a
decision remains open.

Flag an assumption presented as fact, a fake chosen design, contradictions, or
an open question whose effect on the exploration is hidden.

### Decision-ready

The problem, constraints, and live choices should be clear enough for an owner
to select a design. Material forces and consequences must be visible, but the
choice may still be open.

Flag missing decision criteria, straw alternatives, unknowns that prevent the
options from being evaluated, or a proposal that looks selected while leaving
its central behavior undecided.

### Implementation-ready

No material product or architectural choice remains for the implementer.
Externally observable behavior, boundaries, state, activated failure semantics,
and acceptance evidence must be fixed or explicitly grant immaterial freedom.

Flag material `TBD` values and choices. Do not over-specify local helper names,
algorithms, or libraries merely because implementation is next.

### As-built

The document claims to describe deployed behavior. Its contracts, state, and
ownership must agree with authoritative implementation artifacts and current
decisions.

Flag drift that changes the reader's model. Do not turn the task into a general
code audit; inspect code only to verify the document's material claims.

## Mixed Maturity and Document Sets

A document can be exploratory in one bounded area and implementation-ready in
another. State that interpretation only when it changes findings. Do not lower
the whole review standard because one explicit question remains open.

Keep semantically dependent documents together. A feature spec, linked schema,
ADR, and rollout note may jointly define one contract. Reconcile their
authority; do not demand duplicate content in every file.

These profiles remain internal lenses. Do not create empty headings, `N/A`
sections, or longer documents to demonstrate that every lens was considered.
