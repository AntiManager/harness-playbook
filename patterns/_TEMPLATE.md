---
id: HP-000
title: Pattern title (imperative, short)
status: candidate            # proven | candidate | deprecated
applies_when: One sentence. Use for X when Y.
does_not_apply_when: One sentence. Do not use when Z.
evidence:
  projects: [repo-a, repo-b]
  measured: "command + key output line, or 'unmeasured'"
sources: []                  # URLs or local evidence paths; at least one
enforcement: advisory        # deterministic | advisory
token_cost: neutral          # lowers | neutral | raises
since: 2026-11-05
requires: []                 # [HP-..., ...]
files: []                    # paths that the pattern creates/edits
verification: "exact command; expected result"
last_reviewed: 2026-11-05
---

## Problem

What goes wrong without this pattern. One short paragraph.

## Solution

What the pattern is, minimally. Point to the source path instead of copying the body.

## Trade-offs

Cost, maintenance, failure modes, when it is overkill.

## Migration notes

How to adopt it in an existing repo, in ordered steps.

## Deprecated by

`none` or the successor ID + date.
