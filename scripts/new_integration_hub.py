#!/usr/bin/env python3
"""Generate or refresh integration hub repositories from the registry.

Usage:
    python -X utf8 new_integration_hub.py [--root DIR] [--registry FILE] [--only KEY,KEY] [--force]

Behaviour:
  * reads harness-playbook/inventory/integrations.json;
  * creates <root>/<dir> for every hub entry that has a dir;
  * writes missing files only (existing files are kept unless --force);
  * never writes secrets, never touches git.

Exit codes: 0 = all requested hubs are present, 1 = a hub is missing files after generation.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

DATE = "2026-11-17"

README = """# Integration hub — {title}

> Status: **{status}** · mode: {mode} · updated: {date}
> Source of truth: `harness-playbook/inventory/integrations.json`. This repository is generated from it.

## What this is

{summary}

## Consumers

{consumers}

## Entry points

| Need | File |
|---|---|
| Auth, endpoints, limits, change policy | `CONTRACT.md` |
| Symptom → cause → action | `FAILURES.md` |
| Agent procedure | `.kilo/skills/{slug}/SKILL.md` |
| Gate | `scripts/verify.ps1 -Offline` (structure + env state), `-Live` (smoke) |

## How another repo uses this hub

1. Run `scripts/verify.ps1 -Offline`; on exit 2 the integration is not configured here.
2. On an error read the matching row in `FAILURES.md` — do not explore this repo file by file.
3. Never copy this text into a consumer repo: link the hub and pin a commit.

## Status meaning

| status | meaning |
|---|---|
| live | the contract is exercised by production code |
| partial | part works in production, part is blocked or planned |
| blocked | no access yet; the contract comes from official docs and cannot be exercised |
| deferred | registered but intentionally not a hub |

## Rules

- No secrets, tokens or webhook URLs in this repository — environment variable names only.
- A contract change (env name, endpoint, write permission) requires a version bump in `CONTRACT.md`.
"""

CONTRACT = """# Contract — {title}

Version: 1 · {date} · status: **{status}** · mode: {mode}

## Service

{service}

## Summary

{summary}

## Authentication (env names only)

{auth_list}

{auth_notes}

## Endpoints and methods

{endpoints}

## Limits and quotas

{limits}

## Gotchas that are not in the official docs

{gotchas}

## Consumers and evidence

{consumers}

## Verify

```powershell
pwsh -NoProfile -File scripts/verify.ps1 -Offline   # structure + env state, no network
pwsh -NoProfile -File scripts/verify.ps1 -Live      # live smoke, needs configured env
```

Exit codes: `0` ready, `2` not configured (blocked), `1` broken.

## Change policy

- Read-only by default. Any write operation needs an explicit user decision and a confirmation argument in the calling code.
- Changing an env name requires: bump `Version`, update every consumer, add a row to `FAILURES.md` for the old name.
- Status moves `blocked → partial → live` only after `verify.ps1 -Live` succeeds against the real service.
"""

FAILURES = """# Failure matrix — {title}

> Read the matching row before exploring the code. One row per observed or documented failure.

| Symptom | Likely cause | Action | Evidence |
|---|---|---|---|
{rows}

## Not yet observed

{unknown}

If a new failure appears, add a row here in the same change that fixes it.
"""

AGENTS = """# {title} — integration hub

> Auto-loaded by Kilo. Keep ≤60 lines. This repo owns the contract, not the consumers' business logic.

## What this repo is

Single source of truth for the **{service}** integration: auth contract, endpoints, limits, failure
matrix and the verify gate. Consumers link this repo and pin a commit; they never copy its text.

## Status

**{status}** — {mode}. Read `CONTRACT.md` before any call; read `FAILURES.md` before debugging.

## Commands

| Job | Command | Success looks like |
|---|---|---|
| structure + env | `pwsh -NoProfile -File scripts/verify.ps1 -Offline` | `STATUS: OK (offline)` |
| live smoke | `pwsh -NoProfile -File scripts/verify.ps1 -Live` | `STATUS: OK (live)` and one evidence line |
| repo check | `pwsh -NoProfile -File $env:USERPROFILE\\.config\\kilo\\scripts\\verify_repo.ps1 -Repo .` | `STATUS: OK` |
| harness lint | `python -X utf8 C:\\Work\\Python\\harness-playbook\\scripts\\harness_lint.py --repo {dir}` | `0 findings` |

## Rules that always hold

- No secrets in the repo: environment variable names only (`CONTRACT.md` lists them).
- No write operation without an explicit user decision and a confirmation argument.
- Every new failure gets a `FAILURES.md` row in the same change as the fix.
- Contract changes bump `Version` and are announced to consumers by commit message prefix `contract:`.

## Where to look

- Auth and endpoints: `CONTRACT.md`
- Failures: `FAILURES.md`
- Procedure for an agent: `.kilo/skills/{slug}/SKILL.md`
- State and next step: `.memory/active_context.md`
- Provenance and exceptions: `.kilo/harness.md`
"""

SKILL = """---
name: {slug}
description: Use when a task touches {service} through this hub — lists the contract, the verify gate and the failure matrix so a consumer repo does not explore the hub.
---

# {title} — integration procedure

## When to use

- A task needs {service}.
- A call to this service failed and the cause is not obvious.
- A new project has to be wired to this integration.

## Procedure

1. Read `CONTRACT.md` in `C:\\Work\\Python\\{dir}` (auth names, endpoints, limits).
2. Run the gate:
   `pwsh -NoProfile -File C:\\Work\\Python\\{dir}\\scripts\\verify.ps1 -Offline`
   - exit `0` — configured; continue;
   - exit `2` — not configured (status `{status}`); report the missing env names and stop;
   - exit `1` — broken repository; fix before calling the service.
3. On a service error, read the matching row in `FAILURES.md` and apply the action there.
4. For a live check use `-Live`; report the exact evidence line, not a summary.

## Rules

- Never paste this procedure into a consumer repo — link the hub.
- No writes without an explicit user decision and a confirmation argument.
- Do not store tokens in any repo; names come from `CONTRACT.md`, values from User env.

## References

- `C:\\Work\\Python\\{dir}\\CONTRACT.md`
- `C:\\Work\\Python\\{dir}\\FAILURES.md`
- `C:\\Work\\Python\\harness-playbook\\inventory\\integrations.json`
"""

HARNESS = """# Harness provenance — {dir}

> Written by the integration-hub generator. Not autoloaded.

## Composition

- Archetype: `integration-hub` (custom; generated from `harness-playbook/inventory/integrations.json`)
- Patterns: `HP-001, HP-002, HP-003, HP-007, HP-012, HP-015`
- Initialized: {date}

## Verify

- Command: `pwsh -NoProfile -File scripts/verify.ps1 -Offline`
- Success: exit 0 and `STATUS: OK (offline)`
- Scope: required files present, env names known, skill resolvable
- Not covered: service availability and credentials (use `-Live` with real env)
- Full gate: `verify.ps1 -Live` plus the consumer project's own tests

## Known exceptions

| Finding | Why accepted | Review by |
|---|---|---|
| live smoke not run in CI | real credentials are never stored in this repo | 2027-02-01 |
"""

PROGRESS = """# Progress — {dir}

## Status

- **{status}** — {mode}
- Contract version: 1 ({date})

## Done

- Hub created from the integration registry.
- Contract, failure matrix and local agent harness in place.

## Open

{open_items}
"""

ACTIVE = """# Active context — {dir}

## Now

The hub is on status **{status}**. Nothing is in flight.

## Next task

{next_step}

## Do not redo

- Do not copy the contract into consumer repos; link the hub and pin a commit.
- Do not add secrets or webhook URLs anywhere in this repository.

## First three commands

```powershell
pwsh -NoProfile -File scripts/verify.ps1 -Offline
Get-Content CONTRACT.md -TotalCount 40
Get-Content FAILURES.md -TotalCount 40
```
"""

BRIEF = """# Project brief — {dir}

## Purpose

Single source of truth for the {service} integration: contract, limits, failure matrix, verify gate.

## Boundaries

- Owns: auth contract (env names), endpoints, quotas, failure matrix, smoke check.
- Does not own: consumer business logic, credentials, data exports.

## Consumers

{consumers}

## Status

{status} — {mode}
"""

VERIFY = """<#
Integration hub gate. Read-only unless -Live is passed.
Usage:
  pwsh -NoProfile -File scripts/verify.ps1 -Offline
  pwsh -NoProfile -File scripts/verify.ps1 -Live
Exit: 0 = OK, 2 = not configured (missing env), 1 = broken.
#>
[CmdletBinding()]
param([switch]$Offline, [switch]$Live)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$required = @('README.md', 'CONTRACT.md', 'FAILURES.md', 'AGENTS.md', 'kilo.json', '.kilo\\skills\\{slug}\\SKILL.md', '.kilo\\harness.md')
$missing = @()
foreach ($f in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $f))) { $missing += $f }
}
if ($missing.Count -gt 0) {
    Write-Output ("STATUS: FAIL (missing: " + ($missing -join ', ') + ")")
    exit 1
}
$names = @({env_array})
$state = @()
$missingEnv = @()
foreach ($n in $names) {
    $value = [Environment]::GetEnvironmentVariable($n, 'Process')
    if (-not $value) { $value = [Environment]::GetEnvironmentVariable($n, 'User') }
    if ($value) { $state += ($n + '=set') } else { $state += ($n + '=missing'); $missingEnv += $n }
}
Write-Output ("ENV: " + ($state -join ' '))
Write-Output ("HUB: {dir} status={status}")
if ($Offline) {
    Write-Output 'STATUS: OK (offline)'
    exit 0
}
if (-not $Live) {
    Write-Output 'STATUS: OK (offline; pass -Live for the smoke)'
    exit 0
}
if ($missingEnv.Count -gt 0) {
    Write-Output ("STATUS: BLOCKED (missing env: " + ($missingEnv -join ', ') + ")")
    exit 2
}
try {
{smoke}
    Write-Output 'STATUS: OK (live)'
    exit 0
} catch {
    Write-Output ("STATUS: FAIL (live smoke: " + $_.Exception.Message + ")")
    exit 1
}
"""

KILO_JSON = """{
  "$schema": "https://app.kilo.ai/config.json",
  "instructions": [
    "AGENTS.md",
    ".memory/project_brief.md",
    ".memory/active_context.md",
    ".memory/progress.md"
  ],
  "snapshot": false,
  "skills": {
    "paths": [".kilo/skills"]
  },
  "permission": {
    "bash": {
      "*": "allow",
      "git commit*": "ask",
      "git push*": "ask",
      "git reset*": "ask",
      "git clean*": "ask",
      "git checkout -- *": "ask",
      "rm *": "ask",
      "Remove-Item*": "ask"
    },
    "read": {
      ".env*": "deny",
      "**/.env*": "deny",
      "_private/**": "deny",
      "**/_private/**": "deny",
      "*": "allow"
    },
    "write": { ".env*": "deny", "**/.env*": "deny", "*": "allow" },
    "edit": { ".env*": "deny", "**/.env*": "deny", ".git/**": "deny", "**/.git/**": "deny", "*": "allow" },
    "glob": "allow",
    "grep": "allow",
    "webfetch": "allow",
    "skill": "allow"
  }
}
"""

GITIGNORE = """# secrets and local state
.env
.env.*
!.env.example
.run/
__pycache__/
*.pyc
*.log
.venv/
node_modules/
.DS_Store
"""

EVALS = """# Evals — {dir}

Runner is not implemented yet; every task below has a deterministic grader command.

| # | Task | Grader | Expected |
|---|---|---|---|
{rows}

A task passes only when the grader exits with the expected code and the expected line is present.
Record runs in `.memory/progress.md` with the date and the commit sha.
"""


def bullet_list(items):
    return "\n".join(f"- {item}" for item in items) if items else "- (none recorded)"


def numbered_block(lines, heading):
    if not lines:
        return "_(not documented yet)_"
    body = "\n".join(f"{i}. {line}" for i, line in enumerate(lines, 1))
    return f"{heading}\n\n{body}" if heading else body


def render_verify(hub):
    env = hub.get("auth", [])
    env_array = ", ".join("'" + name + "'" for name in env)
    smoke = hub.get("smoke")
    if smoke:
        smoke_block = "    " + smoke.replace("\n", "\n    ")
    else:
        smoke_block = "    throw 'no live smoke defined for this hub'"
    return (VERIFY
            .replace("{slug}", hub["slug"])
            .replace("{dir}", hub["dir"])
            .replace("{status}", hub["status"])
            .replace("{env_array}", env_array)
            .replace("{smoke}", smoke_block))


def render(hub):
    rows = hub.get("failures", [])
    fail_rows = "\n".join("| {} | {} | {} | {} |".format(*row) for row in rows) if rows else "| - | - | - | - |"
    unknown = "-" if rows else "Nothing observed yet: the integration is not exercised in production."
    consumers = bullet_list(hub.get("consumers", []))
    auth_list = numbered_block(hub.get("auth", []), "")
    endpoints = numbered_block(hub.get("endpoints", []), "")
    limits = numbered_block(hub.get("limits", []), "")
    gotchas = numbered_block(hub.get("gotchas", []), "")
    open_items = "\n".join(
        f"- {item}" for item in hub.get("open_items", [])
    ) or "- None."
    if hub["status"] == "blocked":
        open_items = ("- Obtain access: " + ", ".join(hub.get("auth", [])) + " are not configured.\n"
                      "- Move status to `partial` after the first successful `-Live` run.")
    evals = hub.get("evals", [])
    eval_rows = "\n".join(
        "| {} | {} | `scripts/verify.ps1 {}` | exit 0 |".format(
            i,
            task,
            "-Offline" if "-Offline" in task else ("-Live" if "-Live" in task else "-Offline"),
        )
        for i, task in enumerate(evals, 1)
    ) or "| - | - | - | - |"

    files = {
        "README.md": README.format(
            title=hub["title"], status=hub["status"], mode=hub["mode"], date=DATE,
            summary=hub["summary"], consumers=consumers, slug=hub["slug"]),
        "CONTRACT.md": CONTRACT.format(
            title=hub["title"], date=DATE, status=hub["status"], mode=hub["mode"],
            service=hub["service"], summary=hub["summary"],
            auth_list=auth_list or "_(none)_",
            auth_notes=hub.get("auth_notes", ""),
            endpoints=endpoints, limits=limits, gotchas=gotchas, consumers=consumers),
        "FAILURES.md": FAILURES.format(
            title=hub["title"], rows=fail_rows, unknown=unknown),
        "AGENTS.md": AGENTS.format(
            title=hub["title"], service=hub["service"], status=hub["status"],
            mode=hub["mode"], dir=hub["dir"], slug=hub["slug"]),
        "kilo.json": KILO_JSON,
        ".gitignore": GITIGNORE,
        os.path.join(".kilo", "skills", hub["slug"], "SKILL.md"): SKILL.format(
            slug=hub["slug"], title=hub["title"], service=hub["service"],
            dir=hub["dir"], status=hub["status"]),
        os.path.join(".kilo", "harness.md"): HARNESS.format(dir=hub["dir"], date=DATE),
        os.path.join("scripts", "verify.ps1"): render_verify(hub),
        os.path.join(".memory", "project_brief.md"): BRIEF.format(
            dir=hub["dir"], service=hub["service"], consumers=consumers,
            status=hub["status"], mode=hub["mode"]),
        os.path.join(".memory", "active_context.md"): ACTIVE.format(
            dir=hub["dir"], status=hub["status"],
            next_step=("Получить доступ: " + ", ".join(hub.get("auth", []))) if hub["status"] == "blocked"
            else "Подключить первого потребителя к контракту и прогнать `-Live`."),
        os.path.join(".memory", "progress.md"): PROGRESS.format(
            dir=hub["dir"], status=hub["status"], mode=hub["mode"], date=DATE,
            open_items=open_items),
    }
    if evals:
        files[os.path.join("evals", "tasks.md")] = EVALS.format(dir=hub["dir"], rows=eval_rows)
    return files


def write_if_missing(path, content, force):
    if os.path.exists(path) and not force:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"C:\Work\Python")
    parser.add_argument("--registry", default=None)
    parser.add_argument("--only", default="")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    registry_path = args.registry or os.path.join(os.path.dirname(here), "inventory", "integrations.json")
    with open(registry_path, "r", encoding="utf-8") as handle:
        registry = json.load(handle)

    only = {item.strip() for item in args.only.split(",") if item.strip()}
    hubs = [hub for hub in registry["hubs"] if "dir" in hub and (not only or hub["key"] in only)]
    if only:
        unknown = only - {hub["key"] for hub in hubs}
        if unknown:
            print("unknown hub keys: " + ", ".join(sorted(unknown)))
            return 2

    failures = 0
    for hub in hubs:
        repo_root = os.path.join(args.root, hub["dir"])
        created = 0
        for rel, content in render(hub).items():
            if write_if_missing(os.path.join(repo_root, rel), content, args.force):
                created += 1
        present = os.path.isdir(repo_root)
        print(f"{hub['dir']}: {'created' if created else 'unchanged'} ({created} files) status={hub['status']}")
        if not present:
            failures += 1

    print(f"\nhubs processed: {len(hubs)}")
    print("next: git init each new repo, then run scripts/verify.ps1 -Offline per hub")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
