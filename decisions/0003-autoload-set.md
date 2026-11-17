# ADR 0003 — Autoload set

- Status: accepted
- Date: 2026-11-05
- Source: `HARNESS.md` §Token budget, `~/.config/kilo/AGENTS.md` §2

## Context

Ten repos autoload 5–8 files; `factory-ui-template` loads 8 and `factory-system` 7. Every
autoloaded token is paid on every request, and editing an autoloaded file invalidates the
provider prefix cache (measured 21% of spend in one slice).

## Decision

Autoload exactly four files in a project `kilo.json`:

```json
"instructions": [
  "AGENTS.md",
  ".memory/project_brief.md",
  ".memory/active_context.md",
  ".memory/progress.md"
]
```

`tech_context.md` and `system_patterns.md` are read on demand (via a pipeline skill or a direct
`read`). No other file joins the autoload list. Keep `active_context.md` ≤3 KB and
`progress.md` ≤8 KB.

## Consequences

- Predictable fixed prompt overhead; fewer cache-invalidating edits.
- Large `AGENTS.md` files must be split: durable rules stay, project detail moves to
  `.memory/tech_context.md` or `docs/`.
- Ten repos need an `instructions` trim during cleanup.

## Verification

```powershell
python -X utf8 harness-playbook\scripts\harness_lint.py
# expected: no "autoload" findings
```
