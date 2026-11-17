# Project brief — <name>

> Single source of truth for goals, stack, architecture and constraints. May be larger than the
> other memory files; still autoloaded, so keep it under ~4 KB.

## Goal

<Observable outcome the project exists to produce.>

## Users and constraints

- <Who uses it; what they must be able to do.>
- <Non-functional constraints: offline, privacy, performance, deployment target.>

## Stack

| Layer | Choice | Why |
|---|---|---|
| Language | <e.g. Python 3.14> | |
| Data | <e.g. SQLite> | |
| UI | <e.g. Dash/pywebview> | |
| Deploy | <e.g. PyInstaller onedir> | |

## Architecture

<3–8 bullets; name the seams. Detail belongs in docs/architecture.md.>

## Non-goals

- <What this project deliberately does not do.>

## Source of truth

- Rules: `AGENTS.md`
- Stack/config detail: `.memory/tech_context.md`
- Patterns/conventions: `.memory/system_patterns.md`
- Status: `.memory/progress.md`
