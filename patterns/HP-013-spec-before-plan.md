---
id: HP-013
title: Write a SPEC before a plan on ambiguous work
status: candidate
applies_when: The request is ambiguous, spans sessions, or a wrong build is expensive.
does_not_apply_when: A one-file fix with an obvious acceptance test.
evidence:
  projects: []
  measured: "unmeasured in this workspace; source-backed by Spec Kit and Claude Code guidance"
sources: [https://github.com/github/spec-kit, https://code.claude.com/docs/en/best-practices]
enforcement: advisory
token_cost: neutral
since: 2026-11-05
requires: [HP-011]
files: [SPEC.md]
verification: "SPEC.md exists with requirements, edge cases and definition of done; the plan links it"
last_reviewed: 2026-11-05
---

## Problem

On ambiguous work the agent starts implementing before the expected outcome is agreed. The plan is
then precise about the wrong thing, and the correction costs a rewrite.

## Solution

One `SPEC.md` (or `.kilo/specs/<id>.md`) before the plan:

1. Problem and users.
2. Requirements (numbered) and non-goals.
3. Edge cases and error paths.
4. Definition of done + the command that proves it.
5. Open questions, each with an owner or an explicit assumption.

Then plan against the spec. On completion, compare the result with the spec (`converge`) and record
gaps instead of silently widening scope.

## Trade-offs

- Ceremony: skip it for small, unambiguous fixes.
- A spec can go stale; update it in the same change as the behavior.

## Migration notes

1. Start with a spec interview: ask the agent to interview the user until it can write the spec.
2. Freeze the spec before planning; later changes go to a revision section.
3. Reference the spec from the plan's acceptance step.

## Deprecated by

none
