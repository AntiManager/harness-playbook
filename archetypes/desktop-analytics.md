---
name: desktop-analytics
status: proven
applies_when: A local-first analytics tool for one team; data fits SQLite; Windows EXE is acceptable.
source_projects: [FOT_system, NSP]
patterns: [HP-001, HP-002, HP-003, HP-012, HP-007]
last_reviewed: 2026-11-05
---

# Archetype — Desktop analytics (PyInstaller + Dash/pywebview + SQLite)

## Decision tree

1. Single-user or small-team analysis, no server → this archetype.
2. Shared data, multi-user, API needed → `web-platform`.
3. Rich typed desktop UI with a React team → `desktop-migration`.

## Minimal composition

| Layer | Files | Pattern |
|---|---|---|
| Instructions | `AGENTS.md` ≤60 lines + boot trio | HP-001, HP-002 |
| Config | `kilo.json` permissions; skills path if project skills exist | HP-003, HP-012 |
| Skills | one per job: `*-build`, `*-desktop`, `*-parser`, `*-analysis`, `*-testing` | HP-006 if large |
| Data | SQLite under a local app-data path; no raw files in git | HP-003 |
| Verification | `pytest`, packaged EXE smoke, `verify_repo.ps1` | HP-007 |

## Required commands and skills

- Build: PyInstaller `build.spec`, onedir, package data (`FOT_system/.kilo/skills/fot-build`).
- Parse/import: one importer per source format (`fot-importer`, `nsp-parser`).
- Test: unit + integration + Playwright E2E against the packaged app (`nsp-testing`).
- Domain analyst skill when the user asks business questions (`fot-analyst`, `nsp-analyst`).

## Anti-patterns

- Autoloading `tech_context`/`system_patterns` (ADR 0003).
- A single 200-line `AGENTS.md` listing every Excel column.
- Committing the SQLite DB or raw Excel exports.
- Mixing several source formats in one parser skill.

## Verification

```powershell
python -m pytest -q
powershell -NoProfile -File "$env:USERPROFILE\.config\kilo\scripts\verify_repo.ps1" .
# expected: tests green; verify_repo STATUS: OK
```

## Sources

`FOT_system/AGENTS.md`, `FOT_system/.kilo/skills/*`, `NSP/AGENTS.md`,
`NSP/.kilo/skills/{nsp-build,nsp-desktop,nsp-parser,nsp-testing}`.
