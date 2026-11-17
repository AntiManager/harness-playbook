# ADR 0005 — Agent vs skill

- Status: accepted (global layer); project agents queued for cleanup
- Date: 2026-11-05
- Evidence: `inventory/2026-11-05-agents.md`, Kilo session DB (21 sessions, all `debug`/`code`)

## Context

The machine carries 7 global agents and 16 project agents across 6 repos. The user reports using
only the built-in modes (Ask, Debug, Plan, Code). The session store confirms it: 20 sessions in
`debug`, 1 in `code`, **0 sessions in any custom agent**. Global `kilo.jsonc` also overrides every
custom agent's model to `deepseek/deepseek-flash`, so the custom primary modes do not even keep
their advertised model advantage.

A custom **primary** agent is a visible mode in the UI and a full parallel instruction surface
that must be maintained, counted, and verified. A skill is loaded on demand inside a built-in mode,
costs nothing until triggered, and keeps the same tools/permissions as the mode.

## Decision

1. **Custom primary agents are removed.** Their content becomes a skill when it is a procedure,
   or is folded into an existing skill/command when it duplicates one.
2. **Subagents stay agents.** `cheap-worker` and `reviewer` are invisible in the mode picker and
   exist because they need a different model/permission profile and an isolated context. That is a
   real reason to keep an agent.
3. A new custom agent is justified only when **all** hold:
   - it must be selected **before** tools run (a mode, not a procedure);
   - it needs a materially different model or permission set;
   - the same effect cannot be achieved by a skill in Code/Plan/Debug.
4. Project agents follow the same rule during per-repo cleanup (ADR 0004). Commands that bind
   `agent:` must be rewritten in the same change.
5. Deleting an agent is reversible: move the file to `.run/kilo/agents-backup-<date>/`, never
   hard-delete history.

## Consequences

Global layer: agents 7 → 2, skills 10 → 12. `planner`, `utf8-documenter` and `code-guardian` are
folded into existing skills; `requirements-architect` and `security-architect` become skills and
their commands load the skill instead of setting `agent:`.

Project layer (16 agents): HHRU 5, linear-tech 6, factory-ui-template 2, FOT_system 1, NSP 1,
Zakup 1. All become skills or are deleted in the repo's cleanup session; their bound commands
(`HHRU/*`, `linear-tech/audit|scrape`, `factory-ui-template/test-auth`) must be rewritten then.

## Classification

| Artifact | Kind | Action | Reason |
|---|---|---|---|
| `planner` | primary | delete → `plan-lifecycle` skill | Duplicates built-in Plan; skill explicitly says no dedicated agent needed |
| `utf8-documenter` | primary | delete → `shell-hygiene` | 2-line rule already covered; `/check-encoding` command exists |
| `code-guardian` | primary | delete → `security-audit` skill | `/scan` already reuses its report; slop pass already in the skill |
| `requirements-architect` | primary | **skill** | Long procedure, no special permissions; `/requirements` loads it |
| `security-architect` | primary | **skill** | Long procedure; `/security-design` loads it |
| `reviewer` | subagent | keep | Read-only + v4-pro isolation for `/review` |
| `cheap-worker` | subagent | keep | Flash routing + scoped edits for delegation |

## Verification

```powershell
python -X utf8 "$env:USERPROFILE\.config\kilo\scripts\check_harness.py" "$env:USERPROFILE\.config\kilo"
# expected: skills 12 / agents 2 / commands 18; problems: 0
```
