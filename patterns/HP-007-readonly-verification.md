---
id: HP-007
title: Use read-only verification scripts as the acceptance gate
status: proven
applies_when: Every repo on this machine; any harness or repo-health change.
does_not_apply_when: Never — these checks do not modify state.
evidence:
  projects: [global harness, all 21 repos]
  measured: "check_harness.py -> problems: 0; verify_repo.ps1 -> ~0.5 KB report, STATUS OK"
requires: []
files: [scripts/check_harness.py, scripts/verify_repo.ps1, scripts/harness_lint.py]
verification: "python -X utf8 ~/.config/kilo/scripts/check_harness.py <root> -> problems: 0"
sources: [https://code.claude.com/docs/en/best-practices, ~/.config/kilo/scripts/check_harness.py]
enforcement: deterministic
token_cost: neutral
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

"Should work" claims are unverifiable. Manual inspection of 21 repos is expensive and
inconsistent between sessions.

## Solution

Use the three deterministic scripts:

| Script | Scope | Output |
|---|---|---|
| `check_harness.py [root]` | skills/agents/commands resolve, frontmatter, manifest counts | problem lines |
| `verify_repo.ps1 <repo>` | branch, remotes, dirty, harness, encoding | compact report |
| `harness_lint.py` | drift across all repos (model, autoload, skills path, AGENTS length) | table + exit code |

A red result is a stop condition, not a note. Keep each output ≤~4 KB; write bulk output to
`.run/kilo/*.log` and grep it.

## Trade-offs

- `check_harness.py` has no notion of project-specific policy; lint covers that.
- Scripts can drift from the manifest; verify the script itself when counts change.

## Migration notes

1. Run both scripts before and after any harness change.
2. Attach command + exit code + key line as evidence.

## Deprecated by

none
