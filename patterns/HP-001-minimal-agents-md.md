---
id: HP-001
title: Keep the autoloaded AGENTS.md minimal
status: proven
applies_when: Any repo with a root AGENTS.md that loads on every request.
does_not_apply_when: The repo has no project-specific rules (skip the file entirely).
evidence:
  projects: [exhomebird, HHRU, AntiManager]
  measured: "exhomebird 44 lines, HHRU 50 lines; drift table flags 10 repos above 60 lines (factory-system 579)"
requires: [HP-002]
files: [AGENTS.md]
verification: "python -X utf8 ~/.config/kilo/scripts/check_harness.py <repo> -> problems: 0"
sources: [https://agents.md/, https://code.claude.com/docs/en/best-practices]
enforcement: deterministic
token_cost: lowers
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

A large `AGENTS.md` is autoloaded on every request. The 2026-11-05 inventory found ten repos
above 60 lines; `factory-system` has 579. Long files crowd the attention budget and are edited
often, which invalidates the prefix cache.

## Solution

Keep only what must be known **before** the first tool call:

1. What the repo is (2–4 lines).
2. The two or three pipelines and where their detail lives.
3. Core rules that are cheap to state and expensive to violate.
4. Commands that are run every session.
5. Pointer to `.memory/` and `docs/` for everything else.

Sources: `exhomebird/AGENTS.md` (44 lines), `HHRU/AGENTS.md` (50 lines).

## Trade-offs

- Requires a real `docs/` or `.memory/tech_context.md` to point at; otherwise detail is lost.
- Splitting a 579-line file is a behavior change and needs a per-repo session (ADR 0004).

## Migration notes

1. Read the file and tag each section `boot` (needed before tools) or `detail`.
2. Move `detail` to `.memory/tech_context.md` or `docs/`.
3. Replace moved blocks with a one-line pointer.
4. Run the repo's tests and `check_harness.py`; review the diff for lost rules.

## Deprecated by

none
