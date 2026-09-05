# Architecture documentation convention

Feature specifications live under `docs/specs/` while a feature is designed,
delivered, and maintained. Temporary delivery plans are removed after delivery.

Accepted decisions that change cross-service data ownership, durable storage,
public interfaces, or other costly-to-reverse architecture are recorded under
`docs/adr/`. The ADR is the durable, independently discoverable record after
its delivery plan is removed. It links to the feature specification or project
issue instead of copying task detail.
