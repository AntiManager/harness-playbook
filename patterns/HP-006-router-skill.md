---
id: HP-006
title: Split a large skill into a router plus on-demand references
status: candidate
applies_when: A skill or rule file exceeds ~20 KB or covers several unrelated areas.
does_not_apply_when: The skill is short and always loaded as one coherent procedure.
evidence:
  projects: [Proc_library]
  measured: "app-pipeline-full.md is 131 KB; the router loads a rule map and range files of 0.4–26 KB"
requires: []
files: [.kilo/skills/<name>/SKILL.md, .kilo/skills/<name>/references/*.md]
verification: "read the SKILL.md -> it names a file/range per rule group; no rule body copied"
sources: [https://agentskills.io/specification, https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents]
enforcement: advisory
token_cost: lowers
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

A single huge skill cannot be loaded without flooding the context, so in practice it is either
ignored or loaded at the wrong time.

## Solution

Source: `Proc_library/.kilo/skills/app-pipeline`.

- `SKILL.md` is a router: trigger description, bootstrap notes, and a rule-map table
  (`rules 12–30 → references/rules-01-30.md`).
- Rule bodies live in `references/`; read by file or by `offset`/`limit`.
- The full concatenation is a fallback only, never the default.
- Keep a single numbering space so cross-references stay stable.

## Trade-offs

- Two-level lookup costs one extra read.
- Splitting must follow natural boundaries; arbitrary chunks make the map useless.

## Migration notes

1. Identify independent rule groups and assign ranges.
2. Write the router with a group → file table.
3. Move bodies verbatim into `references/`; do not rewrite them.
4. Verify one cross-cutting task can find every needed rule from the router.

## Deprecated by

none
