---
id: HP-010
title: State the delegation boundary in AGENTS.md
status: candidate
applies_when: The repo has mechanical, high-volume tasks that a cheap subagent can do.
does_not_apply_when: The work needs architecture judgment, visual validation or secrets handling.
evidence:
  projects: [exhomebird]
  measured: "44-line AGENTS.md names delegate/do-not-delegate examples (token saving)"
requires: [HP-001]
files: [AGENTS.md]
verification: "grep -n 'Delegation' AGENTS.md -> a delegate list and a do-not-delegate list"
sources: [https://code.claude.com/docs/en/best-practices, https://kilocode.ai/docs/customize/custom-subagents]
enforcement: advisory
token_cost: lowers
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Without a boundary, an agent either does everything in the primary context or delegates
judgment-heavy work to a cheap subagent, which produces plausible but wrong results.

## Solution

Source: `exhomebird/AGENTS.md` §Delegation (token saving).

- **Delegate:** find/replace across files, simple CSS edits, dead-code removal, `.gitignore`
  entries, read-and-summarize files.
- **Do not delegate:** architecture decisions, visual validation, unclear bugs,
  CSP/security/secrets/deploy.
- Name the subagent type and require a compact summary back.

## Trade-offs

- The list ages; review it when a delegation produces a bad result.
- One project uses the explicit form; most use the global model-routing rule.

## Migration notes

1. Add the section to `AGENTS.md` with repo-specific examples.
2. Keep the global routing rule (`deepseek-flash` for mechanical) as the model default.

## Deprecated by

none
