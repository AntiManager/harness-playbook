---
name: desktop-migration
status: proven
applies_when: An existing SPBI/Power BI or desktop tool is being rebuilt as a modern local app.
source_projects: [Zakup, PowerBI_architecture]
patterns: [HP-001, HP-002, HP-003, HP-006, HP-009, HP-012]
last_reviewed: 2026-11-05
---

# Archetype — Desktop migration (FastAPI + React 19 + Tauri sidecar)

## Decision tree

1. Existing analytical model must be preserved while the UI is rebuilt → this archetype.
2. Greenfield local analytics without a migration constraint → `desktop-analytics`.
3. Multi-user deployment → `web-platform`.

## Minimal composition

| Layer | Files | Pattern |
|---|---|---|
| Instructions | short `AGENTS.md` + boot trio | HP-001, HP-002 |
| Config | permissions deny raw/golden data; skills path | HP-003, HP-012 |
| Backend | FastAPI plugin per domain (`BackendModule`/`PluginContext`) | HP-006 |
| Frontend | React 19 module per domain (Vite, Tailwind 4, Radix, TanStack Query) | HP-006 |
| Packaging | Tauri v2 + PyInstaller one-dir FastAPI sidecar on localhost | — |
| Commands | `dev`, `e2e`, `migrate` | HP-009 |

## Required commands and skills

- `fastapi-plugin` — plugin contract and schema conventions.
- `react-module` — module + core conventions.
- `tauri-desktop` — sidecar, dynamic port, packaging.
- `dev`, `e2e`, `migrate`, plus per-domain pipeline commands (`classify`, `build-mask`).
- Parity/golden check when a legacy report is the reference.

## Anti-patterns

- Forking the template core per spoke; core changes belong in the hub (`Proc_library/templates`).
- Business logic in Tauri shell commands instead of an endpoint.
- New chart/table libraries outside the single approved stack.
- Letting raw or golden data into git or LLM context.

## Verification

```powershell
# backend + frontend gates, then packaging smoke
npx playwright test
powershell -NoProfile -File "$env:USERPROFILE\.config\kilo\scripts\verify_repo.ps1" .
# expected: E2E green; STATUS: OK
```

## Sources

`Zakup/.kilo/skills/{fastapi-plugin,react-module,tauri-desktop}`, `Zakup/.kilo/command/{dev,e2e,migrate}`,
`PowerBI_architecture/.kilo/skills/*`, `Proc_library/templates/mvp/NORMALIZE-APP.md`.
