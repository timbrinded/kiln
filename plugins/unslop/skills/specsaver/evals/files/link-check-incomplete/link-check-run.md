# Documentation link-check run

**Status:** Implementation-ready

## Problem

A documentation release can contain links that no longer resolve. Link checks
must finish even when a worker restarts, and a release report must show which
links passed or failed.

## Proposed design

The documentation builder asks the Link Checker to start a run for a release.
The Link Checker loads the release's link manifest and adds one item per URL to
an at-least-once queue. Worker replicas probe those URLs and record whether each
one is valid or broken.

Workers use the existing public-web egress client. It sends no cookies or
application credentials and rejects URL credentials and any literal, resolved,
or redirected destination outside public unicast address space.

A worker retries a transient network or server error later. When no work
remains, the Link Checker marks the run complete and makes the report available
to the documentation builder. Multiple workers can process one run so that a
large release does not wait on one worker.

## Verification

Tests will cover a valid link, a broken link, a transient network error, and a
worker restart.
