---
id: HP-011
title: Run non-trivial work through plan, execution log and retro
status: proven
applies_when: Work spans multiple steps, files or sessions, or changes the harness.
does_not_apply_when: A single-file, single-command task.
evidence:
  projects: [linear-tech-bi, factory-system, workspace]
  measured: "plan + execution log under .kilo/plans/; /retro folds >=1 lesson back into the harness"
requires: [HP-007]
files: [.kilo/plans/<name>.md, audit/execution log]
verification: "ls .kilo/plans/<name>.md -> plan has atomic steps, acceptance command per step, log, retro"
sources: [https://github.com/github/spec-kit, ~/.config/kilo/skills/plan-lifecycle/SKILL.md]
enforcement: advisory
token_cost: neutral
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Long work without a checkpoint loses decisions, re-litigates settled questions and cannot be
resumed.

## Solution

Source: `~/.config/kilo/skills/plan-lifecycle`, `linear-tech-bi/AGENTS.md` §Plan lifecycle.

1. Plan: atomic steps, one approach per step, acceptance + exact command per step.
2. Execute: append to the execution log; amendments go to an `## Amendments` section.
3. Checkpoint at phase/context boundaries; write a resume pointer in `active_context.md`.
4. Retro: at least one lesson folded into the harness (`/retro`).

## Trade-offs

- The plan file must not become an edit target: target ≤3 edits per plan (measured drift was
  526 plan edits across 56 sessions).
- Small tasks do not need the full format.

## Migration notes

1. Create `.kilo/plans/` if absent.
2. Use the plan format from `plan-lifecycle`; keep the log in the same file.
3. On completion, archive the plan and write the retro.

## Deprecated by

none
