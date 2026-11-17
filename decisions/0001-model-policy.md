# ADR 0001 — Model policy

- Status: accepted (default), project overrides need a recorded reason
- Date: 2026-11-05
- Source of truth: `~/.config/kilo/AGENTS.md` §8, `~/.config/kilo/HARNESS.md`

## Context

The 2026-11-05 inventory found six different model strings across 18 `kilo.json` files,
including `deepseek/deepseek-v4-flash` (7×), `deepseek/deepseek-chat` (1×) and two Anthropic
strings. Only `deepseek/deepseek-flash` and `deepseek/deepseek-v4-pro` are declared available on
this machine. Invalid or unlisted model strings cause silent provider fallback and unpredictable
cost.

## Decision

1. Default project model: `deepseek/deepseek-flash` (routine code, ask, small tasks, subagents).
2. Reasoning-heavy work: `deepseek/deepseek-v4-pro` (plan, debug, review, security).
3. Do not pin a model in a project `kilo.json` unless the project has a recorded reason.
   Inheritance from the global/session choice is preferred.
4. Anthropic strings stay only where deliberately chosen (`linear-tech`,
   `factory-ui-template`) and must be rewritten to a currently available model when the
   project is next touched; otherwise migrate to the deepseek default.
5. Any new model string must appear in `HARNESS.md` §Known machine-specifics before use.

## Consequences

- Removes 7 invalid `deepseek-v4-flash` pins and 1 `deepseek-chat` pin during cleanup.
- Keeps the option of a deliberate Anthropic project without making it the default.
- Model drift becomes a `harness_lint.py` finding instead of a silent runtime behavior.

## Verification

```powershell
python -X utf8 harness-playbook\scripts\harness_lint.py
# expected: no "model" findings for the standardized repos
```
