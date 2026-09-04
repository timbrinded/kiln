# ADR Threshold

Use this reference before recommending or creating a separate architecture
decision record. An ADR records a significant architectural fork and its durable
rationale. It is not a synonym for a design note, implementation task, or
important feature.

## The Four Gates

A separate ADR is justified only when every gate passes.

### 1. A real fork exists

At least two credible approaches are available under the stated constraints. A
reasonable engineer can advocate each. `Implement` versus `do not implement`
is not a design fork when the feature is already required.

Ask:

- What are the approaches?
- What concrete case supports each?
- Is either option invented only to complete a template?

### 2. The choice is architecturally significant

The choice affects structure, quality attributes, dependencies, interfaces,
trust or data boundaries, construction technique, or costly future change.

Ask whether different choices materially change:

- service or data ownership;
- security authority or trust;
- consistency, ordering, or interoperability;
- pervasive technology constraints;
- system-wide reliability, latency, or operability; or
- the cost and risk of reversal.

Local replaceable details do not pass this gate merely because code is changed.

### 3. The rationale has durable value

Future engineers may reasonably revisit the rejected option, and the reason for
the choice is not evident from the resulting code.

Ask:

- Could the rejected approach look attractive after current context fades?
- Which decision-driving constraints would code fail to preserve?
- Will the rationale matter beyond the delivery plan?

### 4. A separate record adds value

Independent discoverability or longevity outweighs duplication with the feature
specification.

Ask:

- Is the feature spec already durable, canonical, and discoverable?
- Does repository convention give ADRs a longer lifecycle or wider scope?
- Would two records create competing authorities?

If gates 1–3 pass but the feature spec already preserves the decision in the
right durable home, keep it there. Architectural significance does not
automatically require duplication.

## Classification and Treatment

| Classification | Treatment |
|---|---|
| Routine implementation choice | Leave to code or ordinary review. No ADR and usually no spec discussion. |
| Feature-level design decision | Explain briefly in the feature spec when rationale helps review. No separate ADR by default. |
| Architectural decision already durably captured | Keep it in the canonical spec. Do not duplicate it to satisfy a convention. |
| Architectural decision whose rationale must outlive the feature spec | Recommend or create an ADR only after all four gates pass. |
| No actual choice | Treat it as a requirement, task, or consequence, not a decision. |

## Decisions That Normally Meet Gates 1 and 2

These may justify durable reasoning, subject to gates 3 and 4:

- build-time static search instead of a server-side search service;
- a search-index partitioning and ownership model;
- shared or separate media-extraction and metadata-indexing workers;
- cross-service consistency, ordering, or data-ownership semantics;
- archive ownership and retention architecture; or
- a persistence technology whose constraints shape many future features.

Example assessment:

> The team can ship a versioned search bundle with each static documentation
> release or operate a server-side search service. Both are credible. The choice
> changes deployment topology, availability dependencies, freshness, and client
> cost, so gates 1 and 2 pass. The rationale will matter when adding other
> documentation sites, so gate 3 passes. The canonical feature spec is retained
> with architecture documents and already records the forces, so a separate ADR
> adds no value; gate 4 fails.

The correct result is no separate ADR.

## Decisions That Normally Do Not Meet the Threshold

- adding the route, table, handler, or tests required by an approved feature;
- following an existing repository pattern;
- naming a method or endpoint;
- adding routine telemetry to a new background job;
- choosing a minor locally replaceable helper library; or
- implementing the only approach allowed by a prior architectural decision.

Example assessment:

> The sitemap endpoint follows the repository's existing route, content query,
> and renderer pattern. There is no credible architectural fork. Gate 1 fails,
> so no ADR is warranted.

Stop at the first failed gate. Do not manufacture alternatives or significance
to continue the test.

## When a Separate ADR Adds Value

A transient project plan selects one shared search index instead of separate
indexes owned by each data source. The repository keeps durable architecture
decisions in indexed ADRs, and the plan will be deleted after launch. Both
partitioning models are credible; the choice changes data ownership, query
routing, and recovery; those constraints will remain relevant; and the project
plan is not a lasting record. All four gates pass. Recommend an ADR and state
that reasoning explicitly.

Create the ADR only when the user asks for it. Review mode recommends; it does
not edit or create files.

## False-Positive Controls

- Do not equate “we chose to do this” with an architectural decision.
- Do not use importance, risk, or document length as a substitute for a fork.
- Do not demand an Alternatives heading before recognizing a concise real
  choice.
- Do not require a separate ADR when the canonical feature spec is the durable
  source of truth.
- Do not call an imposed external standard a choice unless adoption of that
  standard was the live architectural fork under review.
