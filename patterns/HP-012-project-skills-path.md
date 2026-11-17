---
id: HP-012
title: Register project skills under .kilo/skills
status: proven
applies_when: A repo has project-specific skills.
does_not_apply_when: The repo only uses global skills.
evidence:
  projects: [FOT_system, NSP, Proc_library, HHRU]
  measured: "FOT_system and NSP register .kilo/skills; Proc_library/HHRU discover project skills; linear-tech and linear-tech-bi still use the singular .kilo/skill"
requires: [HP-002]
files: [kilo.json, .kilo/skills/<name>/SKILL.md]
verification: "python -X utf8 harness-playbook/scripts/harness_lint.py -> no skills-path findings"
sources: [https://kilocode.ai/docs/features/skills, https://agentskills.io/specification]
enforcement: deterministic
token_cost: neutral
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Two spellings (`.kilo/skills`, `.kilo/skill`) coexist, and some repos do not declare a path at
all. The drift is silent because `check_harness.py` accepts both.

## Solution

```json
"skills": { "paths": [".kilo/skills"] }
```

Each skill is a directory with `SKILL.md` and a non-empty `description` used as the trigger.
Keep the body focused; split large skills per HP-006. Standard: ADR 0002.

## Trade-offs

- Renaming a directory touches `kilo.json` and any docs that cite the path.
- Auto-discovery may already work; the explicit path makes the contract visible and lintable.

## Migration notes

1. Rename `.kilo/skill` → `.kilo/skills` (git mv).
2. Update `kilo.json` and path references in `AGENTS.md`/docs.
3. Run `check_harness.py` for the repo and `/check-harness` for counts.

## Deprecated by

none
