---
name: web-platform
status: proven
applies_when: Multi-user web app with a database, Docker/VPS deploy and browser E2E.
source_projects: [factory-system, factory-ui-template]
patterns: [HP-001, HP-002, HP-003, HP-009, HP-012]
last_reviewed: 2026-11-05
---

# Archetype — Web platform (Supabase + Docker/VPS + Playwright)

## Decision tree

1. Shared data, several users, deploy to a VPS → this archetype.
2. Single-user local analysis → `desktop-analytics`.
3. Public content without app state → `content-site`.

## Minimal composition

| Layer | Files | Pattern |
|---|---|---|
| Instructions | `AGENTS.md` + boot trio; split if >60 lines | HP-001, HP-002 |
| Config | permissions: deny `.env*`, raw, generated; ask destructive | HP-003 |
| Stack | Supabase (Postgres/Auth), Vanilla + React apps, Caddy, n8n | — |
| Commands | `dev`, `stop`, `status`, `logs`, `restart`, `backup`, `seed`, `cleanup` | HP-009 |
| Verification | `pytest`, build, Playwright E2E, `verify_repo.ps1` | HP-007 |

## Required commands and skills

- `dev.ps1` Windows stack; document ports in `AGENTS.md`.
- `seed`/`cleanup` for fixture and artifact hygiene.
- `status`/`logs`/`restart` for the Docker stack.
- Playwright E2E against the built app, not the dev server.

## Anti-patterns

- `docker compose down -v`, deleting `supabase_db_data`, rotating shared keys — the DB is shared
  with `Proc_library` (global `HARNESS.md` §Known machine-specifics).
- Autoloading deploy/architecture files (7–8-file lists exist today; trim per ADR 0003).
- MCP servers left enabled by default (removed invalid `docker`, Chrome-dependent `playwright`).
- Project-specific `check-encoding` copies — the global command is authoritative.

## Verification

```powershell
.\dev.ps1            # stack comes up on documented ports
npx playwright test  # built app
powershell -NoProfile -File "$env:USERPROFILE\.config\kilo\scripts\verify_repo.ps1" .
# expected: E2E green; STATUS: OK
```

## Sources

`factory-system/kilo.json`, `factory-system/.kilo/command/*`, `factory-ui-template/kilo.json`,
`factory-system/AGENTS.md` (579 lines — do not copy; split first).
