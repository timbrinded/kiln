# Exploring documentation archive delivery

**Status:** Exploratory; not ready for implementation

## Problem

A large documentation project can contain more generated files than one
request can package and return before the request deadline.

## Settled constraints

- Every archive represents one immutable documentation snapshot.
- Archive creation does not change source pages or generated files.
- A successful build records the snapshot identifier, archive digest, and file
  count used for later verification.

## Candidate model

A background builder could read the selected snapshot, create the archive, and
publish a download location after the build completes. A restarted builder
would continue or restart work according to the selected delivery model while
retaining the same snapshot identifier.

## Open questions

1. Should the builder create one archive in the existing object store or stream
   restartable volumes from the build service? This choice changes the recovery
   and download contracts and **blocks implementation**.
2. Should archives above a selected size become several numbered volumes or
   remain one file? This does not block a prototype, but it must be resolved
   before the production download contract is complete.
