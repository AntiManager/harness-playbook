# Harness provenance — harness-playbook

> Written 2026-11-17 (S3: verify recipe for every repo); update when the harness changes.
> Not autoloaded.

## Composition

- Archetype: `content-site` (catalog of patterns, archetypes and templates; no build, no site)
- Patterns: `HP-001, HP-002, HP-003, HP-004, HP-010, HP-011, HP-015, HP-016`
- Decisions followed: `ADR 0001` (model policy), `ADR 0003` (4 autoload files)
- Initialized: `2026-11-17`

## Verify

- Command: `python -X utf8 scripts/harness_lint.py --self`
- Success: `self problems: 0` (card schema, registry links, archetypes, decisions, skill spec, links)
- Scope: this repo's own consistency; drift across the 31 workspace repos is a separate scan
- Not covered: prose accuracy of the cards and analysis notes — review only
- Full gate:

```powershell
python -X utf8 "C:\Work\Python\harness-playbook\scripts\harness_lint.py" --repo harness-playbook
python -X utf8 "C:\Work\Python\harness-playbook\scripts\playbook_eval.py"
python -X utf8 "$env:USERPROFILE\.config\kilo\scripts\check_harness.py" harness-playbook
# expected: total findings: 0, 5/5 passed, problems: 0
```

## Known exceptions

| Finding | Why accepted | Review by |
|---|---|---|
| no unit tests for lint helpers | `playbook_eval.py` exercises the checks end to end on synthetic fixtures | 2027-02-01 |
