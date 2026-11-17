---
id: HP-002
title: Autoload the AGENTS.md plus the memory boot trio
status: proven
applies_when: A repo uses the Memory Bank (`.memory/`) and a project `kilo.json`.
does_not_apply_when: The repo has no `.memory/` yet; create it first.
evidence:
  projects: [AntiManager, Proc_library, Zakup, PowerBI_architecture, Zagruzka_personala]
  measured: "5 repos use AGENTS.md + 3 memory files; 5 more use the trio without AGENTS.md"
requires: [HP-001]
files: [kilo.json, .memory/project_brief.md, .memory/active_context.md, .memory/progress.md]
verification: "python -X utf8 harness-playbook/scripts/harness_lint.py -> no autoload findings"
sources: [https://kilocode.ai/docs/customize/custom-rules, https://kilocode.ai/docs/customize/agents-md]
enforcement: deterministic
token_cost: lowers
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Reference material (`tech_context`, `system_patterns`) is useful but not needed before the first
tool call. Loading everything inflates fixed prompt overhead and makes cache invalidation
frequent.

## Solution

```json
"instructions": [
  "AGENTS.md",
  ".memory/project_brief.md",
  ".memory/active_context.md",
  ".memory/progress.md"
]
```

`tech_context.md` and `system_patterns.md` stay on demand. Caps: `active_context` ≤3 KB,
`progress` ≤8 KB. Rationale: ADR 0003.

## Trade-offs

- The agent must know when to read `tech_context`; name that trigger in `AGENTS.md`.
- Four files is a convention, not a Kilo hard limit.

## Migration notes

1. Compare the current `instructions` list with this four-file set.
2. For each extra entry, add a pointer line in `AGENTS.md` and remove it from `instructions`.
3. Verify the project still has the information it needs: run one representative task.

## Deprecated by

none
