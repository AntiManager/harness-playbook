---
id: HP-008
title: Keep working notes in an ignored scratch directory
status: candidate
applies_when: A session produces scripts, logs, backups or intermediate reports.
does_not_apply_when: The artifact is a durable deliverable that belongs in `docs/`.
evidence:
  projects: [linear-tech-bi, NSP, Utils]
  measured: "3 repos ignore .run/; global AGENTS.md mandates .run/<agent>/ scratch space"
requires: [HP-004]
files: [.gitignore, .run/]
verification: "git status --short -> .run/ is absent after writing a scratch file"
sources: [.run/kilo/session-audit-2026-11-05.md]
enforcement: deterministic
token_cost: neutral
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Generated inventories, audit scripts and backups end up in the repo root or get committed,
polluting diffs and the file tree.

## Solution

- Write scratch to `.run/<agent>/` (`.run/kilo/`, `.run/dsh/`).
- Add `.run/` to `.gitignore`; keep the directory out of commits.
- Promote only durable findings to `docs/` or `.memory/`, once.

## Trade-offs

- Scratch files are not backed up by git; that is intentional.
- A `.run/` path can be mistaken for config; name it in `AGENTS.md`.

## Migration notes

1. Add `.run/` to `.gitignore`.
2. Move existing scratch files; do not commit the move if they were untracked.
3. Update `AGENTS.md` with the scratch rule.

## Deprecated by

none
