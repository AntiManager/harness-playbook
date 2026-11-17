---
name: content-site
status: proven
applies_when: The repo's main output is Markdown/content, a static site, and a publish pipeline.
source_projects: [exhomebird, AntiManager, linear-tech]
patterns: [HP-001, HP-002, HP-005, HP-009, HP-012]
last_reviewed: 2026-11-05
---

# Archetype — Content site (Astro/Next/Obsidian)

## Decision tree

1. Publishing pipeline dominates; code changes are secondary → this archetype.
2. App state and users → `web-platform`.
3. Local data analysis → `desktop-analytics`.

## Minimal composition

| Layer | Files | Pattern |
|---|---|---|
| Instructions | minimal `AGENTS.md` (exhomebird: 44 lines) + `active_context` | HP-001, HP-002 |
| Config | permissions deny `.env*`; project skills | HP-003, HP-012 |
| Content | single source of truth for categories; drafts dir (`New_posts/`, `Книга/`) | — |
| Commands | `new-post`/`new-article`, `park`/`closeout`, `check-site` | HP-009, HP-005 |
| Verification | `npm run build`, `astro check`, Playwright, encoding check | HP-007 |

## Required commands and skills

- A migration/publish skill (`post-migration`, `content-publisher`) with the draft → publish flow.
- An encoding/vault audit command (`fix-encoding`, `/check-encoding`).
- `park` — docs, archive plans, clean artifacts, check deploy, commit/push.

## Anti-patterns

- Editing generated site output by hand instead of the source content.
- Multiple category/tag sources.
- Storing the vault or raw drafts in a repo that should only carry site sources.
- One giant article skill; split editorial rules from the mechanical migration.

## Verification

```powershell
npm run build
npx astro check
npx playwright test
powershell -NoProfile -File "$env:USERPROFILE\.config\kilo\scripts\verify_repo.ps1" .
# expected: build/check green; STATUS: OK
```

## Sources

`exhomebird/AGENTS.md`, `exhomebird/.kilo/skills/post-migration`,
`exhomebird/.kilo/command/park.md`, `AntiManager/.kilo/skills/*`, `linear-tech/.kilo/skills/*`.
