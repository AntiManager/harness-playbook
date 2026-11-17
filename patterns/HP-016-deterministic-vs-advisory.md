---
id: HP-016
title: Separate deterministic rules from advisory guidance
status: proven
applies_when: A rule must happen every time, or a guideline is being over-enforced.
does_not_apply_when: The rule genuinely has exceptions; keep it advisory and short.
evidence:
  projects: [linear-tech-bi, factory-system, Proc_library]
  measured: "18/18 kilo.json declare permissions; 15 deny .env; 3 repos enforce scratch via gitignore"
sources: [https://code.claude.com/docs/en/best-practices, https://kilocode.ai/docs/customize/custom-modes]
enforcement: deterministic
token_cost: neutral
since: 2026-11-05
requires: [HP-003]
files: [kilo.json, scripts/*, .kilo/command/*.md]
verification: "attempt the forbidden action -> it is denied/asked; run the gate -> it fails on violation"
last_reviewed: 2026-11-05
---

## Problem

A zero-exception rule written in prose is followed "almost always". The gap is invisible until a
secret is read or a protected directory is edited.

## Solution

Classify each rule and place it accordingly:

| Rule kind | Placement | Example |
|---|---|---|
| Must never happen | `permission` deny | read `.env*`, edit `.git/**` |
| Must always happen | script / command / CI gate | run tests before closeout, encoding check |
| Judgment call | prose in `AGENTS.md` or a skill | "prefer the existing error helper" |

A prose line that keeps being missed is a signal to move it down the table, not to add emphasis.
Do not move preferences into denies: every deterministic rule has a maintenance cost and can fire
when it should not.

## Trade-offs

- Deny rules are path/glob based; verify with a real attempt.
- Too many gates slow work; keep the deterministic set small and high-value.

## Migration notes

1. List the rules currently in `AGENTS.md`.
2. Mark each `never` / `always` / `judgment`.
3. Move `never` to permissions, `always` to a script or command, leave the rest.
4. Test one denied action and one failing gate.

## Deprecated by

none
