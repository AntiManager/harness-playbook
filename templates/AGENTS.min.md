# <Project name> — agent instructions

> Auto-loaded by Kilo. Keep ≤60 lines. Write only what the model cannot derive from the repo:
> commands, gotchas, decisions. Detail lives in `.memory/` or `docs/`.

## What this repo is

<2–3 lines: purpose and main output.>

## Commands

| Job | Command | Success looks like |
|---|---|---|
| install | `<cmd>` | `<line or exit 0>` |
| test | `<cmd>` | `<line>` |
| lint/typecheck | `<cmd>` | `0 errors` |
| run/dev | `<cmd>` | `<URL or ready line>` |

Full verification recipe: `.kilo/harness.md`.

## Gotchas

- <Something that looks wrong but is intentional.>
- <A directory that looks unused but is live.>
- <Required env var and where it is documented.>

## Decisions

- <A team choice not visible in the code, e.g. "use the helpers in src/lib/errors.ts".>

## Rules that must always hold

- Never commit `.env*`, raw data or DB files.
- <Other zero-exception rule; the deterministic copy lives in `kilo.json` permissions.>

## Where to look

- Stack/config detail: `.memory/tech_context.md`
- Patterns/conventions: `.memory/system_patterns.md`
- Status: `.memory/progress.md`
- Skills: `.kilo/skills/` (load by trigger)
