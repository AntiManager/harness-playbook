# Archetypes — one decision tree

Start here, then open the chosen archetype. Each archetype states a **minimum set** and a
**not now** list: adopt the smallest change that works (HP-016, ADR 0004).

## Decision tree

```
What is the primary deliverable?
├─ Content (Markdown/site posts)             → content-site
├─ A dataset, report or scored list          → data-etl
└─ An application
   ├─ Single user, local data, Windows EXE   → desktop-analytics
   ├─ Rebuilding an existing BI/desktop tool → desktop-migration
   └─ Several users, shared DB, VPS deploy   → web-platform
```

Counter-signals:
- Local app that must later become multi-user → start `desktop-analytics`, plan a `web-platform`
  extraction; do not mix both in the first harness.
- ETL whose output is a UI → `data-etl` + the UI archetype, but keep one verification recipe.
- Content site with an app-like calculator → `content-site`; add only the commands the site uses.

## Composition matrix

| Pattern | desktop-analytics | desktop-migration | web-platform | content-site | data-etl |
|---|---|---|---|---|---|
| HP-001 minimal AGENTS.md | required | required | required | required | required |
| HP-002 boot trio | required | required | required | required | required |
| HP-003 permissions | required | required | required | required | required |
| HP-004 memory write-last | required | required | required | required | required |
| HP-005 closeout | optional | optional | optional | required | optional |
| HP-006 router skill | when >20 KB | required | when >20 KB | when >20 KB | when >20 KB |
| HP-007 read-only checks | required | required | required | required | required |
| HP-008 scratch + ignore | required | required | required | required | required |
| HP-009 project commands | build/test | dev/e2e/migrate | dev/status/logs | publish/park | parse/build |
| HP-010 delegation | optional | optional | optional | optional | optional |
| HP-011 plan lifecycle | required | required | required | required | required |
| HP-012 skills path | when skills | required | when skills | required | required |
| HP-013 SPEC | ambiguous work | ambiguous work | ambiguous work | optional | optional |
| HP-014 nested AGENTS | monorepo | monorepo | monorepo | vault + site | pipeline + UI |
| HP-015 verify recipe | required | required | required | required | required |
| HP-016 deterministic split | required | required | required | required | required |

## Minimum sets

| Archetype | Minimum |
|---|---|
| desktop-analytics | HP-001, 002, 003, 007, 008, 015, 016 + build/test commands |
| desktop-migration | above + HP-009 (`dev`, `e2e`, `migrate`), HP-012 |
| web-platform | above + HP-009 (`dev`, `status`, `logs`), HP-012, shared-DB safety note |
| content-site | above + HP-005 (`park`), publish skill, encoding check |
| data-etl | above + one skill per stage, `.env.example`, parity/golden check |

## Not now (all archetypes)

- Full skill deduplication across repos.
- Custom primary agents (ADR 0005).
- Hooks or a toolkit install (Spec Kit, MCP servers) before a demonstrated need.
- More than 4 autoloaded instruction files (ADR 0003).

## Verification for any composition

```powershell
python -X utf8 harness-playbook\scripts\harness_lint.py --repo <name>
python -X utf8 "$env:USERPROFILE\.config\kilo\scripts\check_harness.py" <repo>
powershell -NoProfile -File "$env:USERPROFILE\.config\kilo\scripts\verify_repo.ps1" <repo>
```

Expected: no findings / `problems: 0` / `STATUS: OK` (WARN only for no upstream or skipped tests).
