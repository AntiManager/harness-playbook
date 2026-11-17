---
id: HP-003
title: Declare an explicit permission model
status: proven
applies_when: The repo contains secrets, raw data, generated core, node_modules or a deploy path.
does_not_apply_when: A throwaway scratch repo with no secrets and no destructive flows.
evidence:
  projects: [linear-tech-bi, factory-system, Proc_library]
  measured: "18/18 project kilo.json files declare a permission block; 15 deny .env; linear-tech-bi is the reference model"
requires: [HP-002]
files: [kilo.json]
verification: "python -m json.tool kilo.json -> valid JSON; confirm deny on .env* and data/raw"
sources: [https://code.claude.com/docs/en/best-practices, https://kilocode.ai/docs/customize/custom-modes]
enforcement: deterministic
token_cost: neutral
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Broad allow rules let an agent read secrets or overwrite raw data during a routine task. A
single `deny` on `.env*` prevents most accidental leaks; an `ask` on destructive git/shell
prevents irreversible mistakes.

## Solution

Reference implementation: `linear-tech-bi/kilo.json` §permission.

- `read`: deny `.env*`, `_private/**`, `data/raw/**`; allow the rest.
- `edit`: deny `.env*`, `.git/**`, `node_modules/**`, core/raw paths; allow `docs/**`,
  `.memory/**`, `.kilo/**`, module dirs; `"*": "ask"`.
- `bash`: allow `*`; ask on `git commit/push/reset/clean/checkout --`, `rm/del/Remove-Item`,
  `sed -i`; deny redirection into core/raw.

## Trade-offs

- `"*": "ask"` on edit is noisy for active development; scope allow rules to the working dirs.
- Permission rules are path-globs; verify them against a real attempted write.

## Migration notes

1. Copy the block, then narrow the allow list to the repo's actual directories.
2. Keep `edit` broad enough that routine work is not blocked (global `HARNESS.md` §Config patterns).
3. Test one denied read and one asked edit.

## Deprecated by

none
