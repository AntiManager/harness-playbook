# ADR 0002 — Project skills path

- Status: accepted
- Date: 2026-11-05

## Context

Four repos register project skills: two use `.kilo/skills` (plural) and two use `.kilo/skill`
(singular): `linear-tech`, `linear-tech-bi` use `.kilo/skill`; global uses `skills/`.
`check_harness.py` accepts both (`skills/*/SKILL.md`, `skill/*/SKILL.md`), so the drift is silent.

## Decision

Standardize on **`.kilo/skills/`** for project skills, matching the global layer.
`kilo.json` registers it explicitly:

```json
"skills": { "paths": [".kilo/skills"] }
```

Migrate the two singular repos in their own cleanup session; do not keep a compatibility alias.

## Consequences

- One path convention in docs, templates, lint and `/harness-init`.
- Two repos need a directory rename + `kilo.json` edit during cleanup.
- The lint script reports `.kilo/skill` as a finding until migrated.

## Verification

```powershell
python -X utf8 harness-playbook\scripts\harness_lint.py
# expected: no "skills path" findings
python -X utf8 "$env:USERPROFILE\.config\kilo\scripts\check_harness.py" <repo>
# expected: problems: 0
```
