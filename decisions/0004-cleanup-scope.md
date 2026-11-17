# ADR 0004 — Cleanup scope

- Status: accepted
- Date: 2026-11-05

## Context

The inventory surfaces five independent kinds of drift: model strings, skills path, autoload
sets, oversized `AGENTS.md`, and empty artifact descriptions. Fixing all of them at once across
21 repos is a high-risk change with no per-repo acceptance.

## Decision

1. **Drift first.** Cleanup in this order: model strings → skills path → autoload → `AGENTS.md`
   split → artifact descriptions.
2. **One repo per session.** Start with the worst offenders: `factory-system`, `FOT_system`,
   `NSP`, `PowerBI_architecture`, `linear-tech-bi`.
3. **Behavior-preserving only.** No rule rewrites, no skill deduplication in the first pass;
   dedup is a separate later task.
4. Every cleanup session: backup to `.run/kilo/cleanup-<date>/`, documented commands, diff
   review, `check_harness.py` → 0, `verify_repo.ps1` green.

## Consequences

- Small, reviewable diffs; a failure is contained to one repo.
- Full deduplication of 60+ skill names is deferred and tracked separately.
- The playbook's inventory flags are the backlog source.

## Verification

Per repo:

```powershell
python -X utf8 "$env:USERPROFILE\.config\kilo\scripts\check_harness.py" <repo>
powershell -NoProfile -File "$env:USERPROFILE\.config\kilo\scripts\verify_repo.ps1" <repo>
# expected: problems: 0 / STATUS: OK
```
