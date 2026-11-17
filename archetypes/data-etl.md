---
name: data-etl
status: proven
applies_when: The core work is ingestion, parsing, scoring or ETL into SQLite/Postgres.
source_projects: [HHRU, Proc_library, Zagruzka_personala]
patterns: [HP-001, HP-002, HP-003, HP-006, HP-009, HP-012]
last_reviewed: 2026-11-05
---

# Archetype — Data / ETL

## Decision tree

1. The deliverable is a dataset, report or scored entity list → this archetype.
2. The deliverable is a UI over the data → add `web-platform` or `desktop-analytics`.
3. The deliverable is prose → `content-site`.

## Minimal composition

| Layer | Files | Pattern |
|---|---|---|
| Instructions | `AGENTS.md` with stack + API gotchas + test commands | HP-001, HP-002 |
| Config | permissions deny `.env*`, `data/raw/**`; project skills | HP-003, HP-012 |
| Code layout | `src/<pkg>/{api,analysis,models,storage}` | — |
| Commands | parse/import/build/rebuild per stage | HP-009 |
| Verification | `pytest`, `ruff`, `mypy`, parity/golden check | HP-007 |

## Required commands and skills

- One skill per stage: API client, parser, scoring, analysis (`hhru-api`, `data-pipeline`,
  `resume-scoring`, `vacancy-analysis`).
- One client seam for every external API; rate limits documented in `AGENTS.md` (HHRU:
  10 req/s, DDoS-Guard 403 on `GET /vacancies`).
- Secrets only via `.env` + `.env.example`; raw data git-ignored.
- `uv` + `.venv` for Python; `ruff` + `mypy` strict.

## Anti-patterns

- Calling an API directly from a command instead of the service layer.
- Committing raw exports, DB files or PII.
- One skill covering API + scoring + analysis (use HP-006 to split).
- Silent schema changes without a migration.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m mypy src
powershell -NoProfile -File "$env:USERPROFILE\.config\kilo\scripts\verify_repo.ps1" .
# expected: tests/lint/type green; STATUS: OK
```

## Sources

`HHRU/AGENTS.md`, `HHRU/.kilo/skills/{hhru-api,data-pipeline,resume-scoring,vacancy-analysis}`,
`Proc_library/.kilo/skills/{app-pipeline,library-pipeline,ocr-pipeline,remote-db-ops}`,
`Zagruzka_personala/.kilo/skills/*`.
