---
id: HP-009
title: Reuse project commands for routine loops
status: proven
applies_when: A repo has a repeated dev/build/seed/cleanup/park loop.
does_not_apply_when: The action runs once, or is already a global command.
evidence:
  projects: [Zakup, factory-system, factory-ui-template, Proc_library, HHRU, exhomebird]
  measured: "dev ×3, build ×2, seed ×2, cleanup ×2, park ×2"
requires: [HP-002]
files: [.kilo/command/*.md]
verification: "command frontmatter has a description; the body starts with the exact command; /check-harness -> 0"
sources: [.run/kilo/harness-inventory.md, https://code.claude.com/docs/en/skills]
enforcement: deterministic
token_cost: neutral
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Agents re-derive the same dev/build/cleanup steps each session, with slightly different flags;
mistakes repeat.

## Solution

Keep a small per-repo command set with the same names for the same job:

| Name | Job | Sources |
|---|---|---|
| `dev` | start backend + frontend | Zakup, factory-system, factory-ui-template |
| `build` | production build | Proc_library, factory-ui-template |
| `seed` | load fixture/reference data | factory-system, factory-ui-template |
| `cleanup` | remove scratch/artifacts | HHRU, factory-system |
| `park` | cleanup + docs + commit/push | HHRU, exhomebird |

Command body: the exact command(s), preconditions, and the expected success line. Project
commands live in `<repo>/.kilo/command/`; do not duplicate a global command such as
`check-encoding`.

## Trade-offs

- Command names shared across repos can hide different behavior; document the difference.
- Each command costs a schema/tool entry only when invoked, not per request.

## Migration notes

1. Pick the names from the table that match real loops.
2. Copy the body from the closest source and adapt paths.
3. Verify by running the command in a dry run.

## Deprecated by

none
