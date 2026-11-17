---
id: HP-005
title: Encode closeout as an executable command
status: candidate
applies_when: The repo has repeatable gates (tests, lint, build) and a memory bank.
does_not_apply_when: The repo has no automated gates yet.
evidence:
  projects: [linear-tech-bi]
  measured: "closeout.md fixes order gates -> tree -> resume draft -> memory -> stop; one reprefill budget per session"
requires: [HP-004]
files: [.kilo/command/closeout.md]
verification: "run the command on a no-op session -> it refuses to write memory when a gate is red"
sources: [https://code.claude.com/docs/en/best-practices, linear-tech-bi/.kilo/command/closeout.md]
enforcement: deterministic
token_cost: lowers
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Ad-hoc closeouts interleave checks and memory writes, run checks after the memory write, and
commit twice. Each extra turn after a memory write pays a full prefix reprefill.

## Solution

Source: `linear-tech-bi/.kilo/command/closeout.md`. Ordered steps:

1. Narrowest gates that cover the change; a red gate stops closeout.
2. `git status`/`git diff`; stage only intended files; no secrets, raw data or DBs.
3. Draft the resume contract (state, next step, first three commands, unread set).
4. One turn, one `Write` per memory file.
5. One memory commit if needed, then stop.

## Trade-offs

- Project-specific gate names make the command non-portable; keep those in the repo copy.
- A single project uses it today, hence `candidate`.

## Migration notes

1. Copy the command and replace the gate list with the repo's real gates.
2. Add it to `AGENTS.md` commands.
3. Run it once on a trivial change to measure the turn count.

## Deprecated by

none
