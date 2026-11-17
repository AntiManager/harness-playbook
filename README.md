# Harness Playbook

Curated, evidence-based catalog of reusable Kilo harness patterns, project archetypes and
copy-ready templates for the 21 repos under `C:\Work\Python`.

**Not a second constitution.** Global rules stay in `~/.config/kilo/AGENTS.md`; the playbook
catalogs local/reusable patterns and points to their sources. It never forks a rule body.

Use it to answer:
1. **New project** — which proven pieces should this project get, and which should it not?
2. **Existing project** — which local solution is reusable, which is drift, which must stay local?

On-demand only: do not add playbook files to any `instructions` list.

## Status legend

| Status | Meaning |
|---|---|
| `proven` | Used in ≥2 projects and verified by a command (`check_harness.py`, `verify_repo.ps1`, project tests) |
| `candidate` | Used in 1 project or unmeasured; promising but not yet promoted |
| `deprecated` | Superseded; card kept for history and names its successor |

## Patterns

| ID | Title | Status |
|---|---|---|
| [HP-001](patterns/HP-001-minimal-agents-md.md) | Minimal autoloaded `AGENTS.md` (≤60 lines) | proven |
| [HP-002](patterns/HP-002-boot-trio-instructions.md) | Boot trio in `kilo.json` `instructions` | proven |
| [HP-003](patterns/HP-003-explicit-permission-model.md) | Explicit permission model (deny secrets/raw, ask destructive) | proven |
| [HP-004](patterns/HP-004-memory-write-last.md) | Memory write-last, one `Write` per file | proven |
| [HP-005](patterns/HP-005-executable-closeout.md) | Executable closeout command | candidate |
| [HP-006](patterns/HP-006-router-skill.md) | Router skill + on-demand references | candidate |
| [HP-007](patterns/HP-007-readonly-verification.md) | Read-only verification scripts as acceptance | proven |
| [HP-008](patterns/HP-008-scratch-and-ignore.md) | Uncommitted scratch dir (`.run/`) + gitignore | candidate |
| [HP-009](patterns/HP-009-reused-project-commands.md) | Reused project commands (`dev`, `build`, `seed`, `park`) | proven |
| [HP-010](patterns/HP-010-delegation-policy.md) | Delegation policy in `AGENTS.md` | candidate |
| [HP-011](patterns/HP-011-plan-lifecycle.md) | Plan + execution log + retro | proven |
| [HP-012](patterns/HP-012-project-skills-path.md) | Project skills path (`.kilo/skills`, plural) | proven |
| [HP-013](patterns/HP-013-spec-before-plan.md) | SPEC before plan on ambiguous work | candidate |
| [HP-014](patterns/HP-014-nested-agents-md.md) | Nested `AGENTS.md` for a real subproject | candidate |
| [HP-015](patterns/HP-015-runnable-verification.md) | Runnable verification recipe per repo | proven |
| [HP-016](patterns/HP-016-deterministic-vs-advisory.md) | Deterministic rules vs advisory guidance | proven |

## Archetypes

Start with [the decision tree](archetypes/README.md); each archetype then gives the minimum set.

| Archetype | Composition | Source projects |
|---|---|---|
| [desktop-analytics](archetypes/desktop-analytics.md) | PyInstaller + Dash/pywebview + SQLite | FOT_system, NSP |
| [desktop-migration](archetypes/desktop-migration.md) | FastAPI + React 19 + Tauri sidecar | Zakup, PowerBI_architecture |
| [web-platform](archetypes/web-platform.md) | Supabase + Docker/VPS + Playwright | factory-system, factory-ui-template |
| [content-site](archetypes/content-site.md) | Astro/Next/Obsidian content pipelines | exhomebird, AntiManager, linear-tech |
| [data-etl](archetypes/data-etl.md) | Python + SQLite/Postgres + API clients | HHRU, Proc_library, Zagruzka_personala |

## Templates

`templates/` holds minimal copy-ready files: `AGENTS.min.md`, `AGENTS.nested.md`, `SPEC.md`,
`kilo.json.min.jsonc`, `memory/{project_brief,active_context,progress}.md`, `SKILL.md.tmpl`,
`command.md.tmpl`, `command.verify.md`, `harness.md`.
Instantiate, then run `/check-harness` and `verify_repo.ps1`.

## Checks and evals

```powershell
python -X utf8 harness-playbook\scripts\harness_lint.py --self   # schema, links, skills, registry
python -X utf8 harness-playbook\scripts\harness_lint.py          # repo drift (exit 1 on findings)
python -X utf8 harness-playbook\scripts\playbook_eval.py         # 5 deterministic self-evals
```

`playbook_eval.py` asserts self-check, the 21-repo/44-finding baseline, invalid-card rejection,
singular-skills-path detection, and template/registry completeness. No model calls.

## Analysis

Dated review notes; the v2 plan is in `.kilo/plans/harness-playbook-v2-2026-11-05.md`.

| Date | Note | Verdict |
|---|---|---|
| 2026-11-11 | [Community refresh](analysis/2026-11-11-community-refresh.md) | re-read AGENTS.md + Claude Code; applied `/spec`, `.run/` ignore, client pointer; rejected "1M window" and hooks |
| 2026-11-05 | [Community practices](analysis/2026-11-05-community-practices.md) | adopt/adapt/reject table with sources (AGENTS.md, Claude Code, Agent Skills, Kilo, Spec Kit, context engineering) |
| 2026-11-05 | [Gap analysis](analysis/2026-11-05-playbook-gaps.md) | 12 gaps, target v2 structure, acceptance |

## Inventory

Dated read-only snapshots in `inventory/`. Regenerate with `scripts/harness_lint.py`;
never edit snapshots by hand.

## Governance

- **Promotion:** `proven` only when used in ≥2 projects and a command verifies it. One project →
  `candidate`.
- **No duplication / no body copying:** cards reference `~/.config/kilo/AGENTS.md` and source paths;
  they summarize, they do not fork skill or rule bodies.
- **Provenance:** a new project records used pattern IDs in `.kilo/harness.md`.
- **Deprecation:** mark `deprecated` + successor; never delete history.
- **Ownership:** Kilo writes; DSH reads (`AGENT_BRIDGE.md` §2).
- **Token economy:** index ≤1 page, card ≤100 lines, inventory never autoloaded.
- **Scope:** the playbook never modifies a project harness; cleanup is a separate, per-repo task.

## Decisions

| ADR | Decision |
|---|---|
| [0001](decisions/0001-model-policy.md) | Model policy: `deepseek/deepseek-flash` default, `deepseek-v4-pro` for plan/review |
| [0002](decisions/0002-skills-path.md) | Project skills live in `.kilo/skills/` (plural) |
| [0003](decisions/0003-autoload-set.md) | Autoload = `AGENTS.md` + boot trio (4 files) |
| [0004](decisions/0004-cleanup-scope.md) | Cleanup scope: drift first, one repo per session |
| [0005](decisions/0005-agent-vs-skill.md) | Agent vs skill: custom primary agents removed; subagents kept only for model/permission isolation |

## References

- Sources: `.run/kilo/harness-inventory.{md,json}`, `harness-catalog.txt`, `harness_drift.py`
- Plan: `.kilo/plans/harness-playbook-2026-11-05.md`
- Global manifest: `~/.config/kilo/HARNESS.md`
