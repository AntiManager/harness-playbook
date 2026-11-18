---
name: integration-hub
status: proven
applies_when: The repo's deliverable is the contract for a third-party service, not application code.
source_projects: [integration-google, integration-yandex-mail, integration-bitrix24]
patterns: [HP-001, HP-002, HP-003, HP-007, HP-012, HP-015]
last_reviewed: 2026-11-18
---

# Archetype — Integration hub

## Decision tree

1. The repo owns auth/env names, endpoints, limits, a failure matrix and a gate for one external
   service, and other repos consume it → this archetype.
2. The repo calls a service and owns business logic → normal application archetype; it links the hub.
3. The boundary is a file or database export, not a service API → data contract, not a hub.

## Minimal composition

| Layer | Files | Pattern |
|---|---|---|
| Instructions | generated `AGENTS.md` (≤60 lines) + boot trio | HP-001, HP-002 |
| Config | `.kilo/skills/<slug>/`, deny `.env*`/`_private`, `permission.task` allowlist | HP-003, HP-012 |
| Contract | `CONTRACT.md` (auth, endpoints, limits, gotchas, sources, change policy) | — |
| Failure matrix | `FAILURES.md` — one row per observed failure, action, evidence | — |
| Gate | `scripts/verify.ps1 -Offline` (structure + `READY:`), `-Live` (smoke), `scripts/selfcheck.ps1` | HP-007, HP-015 |
| State | `state.json` (status, contract version), `.memory/` trio, `evals/tasks.md` | HP-004 |
| CI | `.github/workflows/gate.yml` — offline gate + selfcheck, no secrets | HP-007 |

## Generation, not hand-editing

Source of truth is `harness-playbook/inventory/integrations.json`; the hub is rendered by
`harness-playbook/scripts/new_integration_hub.py`.

```powershell
python -X utf8 harness-playbook\scripts\new_integration_hub.py --only <key> --force   # render
python -X utf8 harness-playbook\scripts\new_integration_hub.py --only <key> --check   # drift gate
```

- `--force` keeps `.memory/` and preserves `token_expires_on` in `state.json`.
- Any content change (env name, endpoint, quota, failure row) goes to the registry first.
- `--check` is the drift gate: 0 drift is the expected output after every render.

## Status model

| status | meaning |
|---|---|
| `live` | the contract is exercised by production code and `-Live` passes |
| `partial` | part works in production, part is blocked or planned |
| `blocked` | no access yet; the contract comes from official docs |
| `deferred` | registered but intentionally not a hub |

`live` + missing env is a hard failure in `verify.ps1`: status may not outrun configuration.

## Anti-patterns

- Copying hub text or the skill into a consumer repo; link the hub and pin a commit.
- Adding an MCP server to the hub: schemas are paid on every request and credentials belong in env.
- A hub without `FAILURES.md` rows or with empty evidence cells.
- Hand-editing generated files; the next `--force` silently reverts it.
- Testing a live smoke in CI: real credentials never enter CI; `-Live` stays local.

## Verification

```powershell
pwsh -NoProfile -File <hub>\scripts\verify.ps1 -Offline
pwsh -NoProfile -File <hub>\scripts\selfcheck.ps1 -RequireRegistry
pwsh -NoProfile -File <hub>\scripts\verify.ps1 -Live    # local only, needs env
python -X utf8 harness-playbook\scripts\new_integration_hub.py --only <key> --check
python -X utf8 harness-playbook\scripts\harness_lint.py --repo <hub>
# expected: STATUS: OK (offline) / SELFCHECK: OK / 0 drift / total findings: 0
```

## Sources

`harness-playbook/inventory/integrations.json`, `harness-playbook/scripts/new_integration_hub.py`,
`integration-google`, `integration-yandex-mail`, `integration-yandex-disk`, `integration-bitrix24`.
