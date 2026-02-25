# Forceful Parallel-Tasks Skill Activation — Design Doc

**Date:** 2026-02-25
**Status:** Implemented

## Problem

The parallel-ai skill only activates when users explicitly ask for web research using specific trigger phrases. Claude defaults to built-in WebSearch/WebFetch tools for web lookups instead of using Parallel.

## Approach: Smart Routing with MANDATORY Override

Uses mgrep-style MANDATORY language in the skill description (always in Claude's context) to force invocation, but unlike a blunt "use Parallel for everything" override, the skill body routes to the optimal Parallel endpoint based on task type.

**Why not unconditional replacement?** Unlike mgrep (which replaces free tools with another free tool), Parallel replaces free built-in tools with a paid API. Unconditional forcing wastes money on trivial lookups. Smart routing ensures the right endpoint is used for the right task.

## Endpoint Routing

| Task Type | Endpoint | Cost | Latency |
|-----------|----------|------|---------|
| Find information (web search, fact lookup) | Search API | $0.005/query | 1-5s |
| Read a URL (fetch, scrape, extract) | Extract API | $0.001/URL | 1-20s |
| Deep research (synthesis, competitive analysis) | Task API (core+) | $0.025+/task | 1min+ |
| Data enrichment (structured output) | Task API (base) | $0.01/task | 15s-100s |
| Batch processing (bulk lookups) | Task API (groups) | varies | varies |

## Changes

**Single file modified:** `plugins/parallel-ai/skills/parallel-ai/SKILL.md`

1. **Frontmatter description** — MANDATORY override language mentioning routing to optimal endpoint
2. **Tool Override section** — WRONG/CORRECT pattern (mgrep-style)
3. **Endpoint Routing section** — Decision tree + cost/latency table + cost-smart defaults
4. **Existing body unchanged** — All operational modes, processor table, settings, references preserved
