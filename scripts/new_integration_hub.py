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

DATE = "2026-11-18"

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
| Gate | `scripts/verify.ps1 -Offline` (structure + `READY:` line), `-Live` (smoke) |

## How another repo uses this hub

1. Run `scripts/verify.ps1 -Offline`; read the `READY:` line. `READY: blocked (...)` means the
   integration is not configured here — stop and report the missing env names. Only `-Live`
   exits 2 for a missing configuration.
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

Version: {version} · {date} · status: **{status}** · mode: {mode}

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

{extra}## Consumers and evidence

{consumers}

## Verify

```powershell
pwsh -NoProfile -File scripts/verify.ps1 -Offline   # structure + READY line, no network
pwsh -NoProfile -File scripts/verify.ps1 -Live      # live smoke, needs configured env
```

Exit codes: `0` structure OK (read `READY:`), `2` not configured (`-Live` only), `1` broken.
`-Offline` never proves access: `READY: blocked (...)` lists the missing env names.
{verify_note}
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
| structure + readiness | `pwsh -NoProfile -File scripts/verify.ps1 -Offline` | exit 0, `STATUS: OK (offline)`, `READY:` line |
| selfcheck | `pwsh -NoProfile -File scripts/selfcheck.ps1` | `SELFCHECK: OK` |
| live smoke | `pwsh -NoProfile -File scripts/verify.ps1 -Live` | `STATUS: OK (live)` and one evidence line |
| repo check | `pwsh -NoProfile -File $env:USERPROFILE\\.config\\kilo\\scripts\\verify_repo.ps1 -Repo .` | `STATUS: OK` |
| harness lint | `python -X utf8 C:\\Work\\Python\\harness-playbook\\scripts\\harness_lint.py --repo {dir}` | `0 findings` |

## Rules that always hold

- No secrets in the repo: environment variable names only (`CONTRACT.md` lists them).
- No write operation without an explicit user decision and a confirmation argument.
- Every new failure gets a `FAILURES.md` row in the same change as the fix.
- Contract changes bump `Version` and are announced to consumers by commit message prefix `contract:`.
- Generated files are not hand-edited: change `harness-playbook/inventory/integrations.json` and
  regenerate (see `.kilo/harness.md`). Status lives in `state.json`.

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

1. Read `CONTRACT.md` at the hub root `C:\\Work\\Python\\{dir}` (auth names, endpoints, limits).
   If the hub is checked out elsewhere, use that root; never copy its text.
2. Run the gate from the hub root:
   `pwsh -NoProfile -File scripts/verify.ps1 -Offline`
   - exit `0` and `READY: yes` — configured; continue;
   - exit `0` and `READY: blocked (...)` — not configured (status `{status}`); report the missing
     env names, do not call the service, stop;
   - exit `1` — broken repository; fix before calling the service.
3. On a service error, read the matching row in `FAILURES.md` and apply the action there.
4. For a live check use `-Live`; exit `2` means not configured. Report the exact evidence line,
   not a summary.

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
- Decisions followed: `ADR 0001, ADR 0003`
- Initialized: {initialized}
- Regenerate: `python -X utf8 C:\\Work\\Python\\harness-playbook\\scripts\\new_integration_hub.py --only {key} --force`
  (keeps `.memory/`; change the registry first, never hand-edit generated files)

## Verify

- Command: `pwsh -NoProfile -File scripts/verify.ps1 -Offline`
- Success: exit 0, `STATUS: OK (offline)`, and a `READY:` line
- Scope: required files, boot trio, `state.json`, skill file and env presence; it prints the token
  expiry from `state.json`. `selfcheck.ps1` adds autoload, skill frontmatter, failure-matrix,
  secret-pattern, encoding, contract/README/registry sync and token-expiry checks. The registry
  comes from `HARNESS_REGISTRY` or the sibling `harness-playbook` checkout; when it is absent the
  sync check is a WARN, and `-RequireRegistry` turns that into a failure.
- CI: `.github/workflows/gate.yml` runs `-Offline` and `selfcheck.ps1` on every push (no secrets).
- Not covered: service availability and credentials — `READY:` only shows env presence; use
  `-Live` to prove access
- Full gate: `verify.ps1 -Live` plus the consumer project's own tests

## Known exceptions

| Finding | Why accepted | Review by |
|---|---|---|
| live smoke is local-only (no CI job holds credentials) | the token lives only in the User env; the CI gate is secretless | 2027-02-01 |
"""

PROGRESS = """# Progress — {dir}

## Status

- **{status}** — {mode}
- Contract version: {version} ({date})

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
  pwsh -NoProfile -File scripts/verify.ps1 -Offline -EnvSource Process   # negative test: ignore User env
Exit: 0 = structure OK (read READY:), 2 = not configured in -Live, 1 = broken.
#>
[CmdletBinding()]
param(
    [switch]$Offline,
    [switch]$Live,
    [ValidateSet('Auto', 'Process')][string]$EnvSource = 'Auto'
)
$ErrorActionPreference = 'Stop'
if ($Offline -and $Live) {
    Write-Output 'STATUS: FAIL (-Offline and -Live are mutually exclusive)'
    exit 1
}
$root = Split-Path -Parent $PSScriptRoot
$required = @('README.md', 'CONTRACT.md', 'FAILURES.md', 'AGENTS.md', 'kilo.json', 'state.json', '.kilo\\skills\\{slug}\\SKILL.md', '.kilo\\harness.md', '.memory\\project_brief.md', '.memory\\active_context.md', '.memory\\progress.md', 'evals\\tasks.md')
$missing = @()
foreach ($f in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $f))) { $missing += $f }
}
if ($missing.Count -gt 0) {
    Write-Output ("STATUS: FAIL (missing: " + ($missing -join ', ') + ")")
    exit 1
}
function Get-HubEnv([string]$Name) {
    $value = [Environment]::GetEnvironmentVariable($Name, 'Process')
    if (-not $value -and $EnvSource -ne 'Process' -and $env:OS -eq 'Windows_NT') {
        $value = [Environment]::GetEnvironmentVariable($Name, 'User')
    }
    return $value
}
$names = @({env_array})
$state = @()
$missingEnv = @()
foreach ($n in $names) {
    $value = Get-HubEnv $n
    if ($value) {
        $state += ($n + '=set')
    } else {
        $state += ($n + '=missing')
        $missingEnv += $n
    }
}
try { $hubState = Get-Content -LiteralPath (Join-Path $root 'state.json') -Raw | ConvertFrom-Json }
catch { Write-Output 'STATUS: FAIL (state.json is missing or invalid)'; exit 1 }
Write-Output ("ENV: " + ($state -join ' '))
Write-Output ("STATE: status=" + $hubState.status + " contract=" + $hubState.contract_version)
if ($hubState.token_expires_on) {
    $expires = $hubState.token_expires_on
    if ($expires -is [datetime]) { $expires = $expires.ToString('yyyy-MM-dd') }
    Write-Output ("EXPIRES: " + $expires)
}
{host_block}
if ($missingEnv.Count -gt 0) {
    Write-Output ("READY: blocked (missing: " + ($missingEnv -join ', ') + ")")
} else {
    Write-Output 'READY: yes (env present; run -Live to prove access)'
}
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
    $evidence = @(& {
{smoke}
    }) -join ' '
    Write-Output ('EVIDENCE: ' + $evidence)
    Write-Output 'STATUS: OK (live)'
    exit 0
} catch {
    Write-Output ("STATUS: FAIL (live smoke: " + $_.Exception.Message + ")")
    exit 1
}
"""

KILO_JSON = """{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "deepseek/deepseek-flash",
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
      "git checkout *": "ask",
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
    "write": {
      ".env*": "deny",
      "**/.env*": "deny",
      ".git/**": "deny",
      "**/.git/**": "deny",
      "node_modules/**": "deny",
      "**/node_modules/**": "deny",
      "_private/**": "deny",
      "**/_private/**": "deny",
      "*": "allow"
    },
    "edit": {
      ".env*": "deny",
      "**/.env*": "deny",
      ".git/**": "deny",
      "**/.git/**": "deny",
      "node_modules/**": "deny",
      "**/node_modules/**": "deny",
      "_private/**": "deny",
      "**/_private/**": "deny",
      "*": "allow"
    },
    "glob": "allow",
    "grep": "allow",
    "webfetch": "allow",
    "skill": "allow",
    "task": {
      "*": "deny",
      "general": "allow",
      "explore": "allow",
      "reviewer": "allow",
      "cheap-worker": "allow"
    }
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

GATE_WORKFLOW = """name: gate

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  offline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Structure and readiness
        shell: pwsh
        run: pwsh -NoProfile -File ./scripts/verify.ps1 -Offline
      - name: Harness selfcheck (registry sync skipped without a sibling checkout)
        shell: pwsh
        run: pwsh -NoProfile -File ./scripts/selfcheck.ps1
"""

STATE = """{
  "contract_version": {version},
  "status": "{status}",
  "mode": "{mode}",
  "updated": "{date}"{token_expires}
}
"""

SELFCHECK = """<#
Read-only harness self-check for this integration hub.
Usage: pwsh -NoProfile -File scripts/selfcheck.ps1
Exit: 0 = OK, 1 = violations.
#>
[CmdletBinding()]
param([switch]$RequireRegistry)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$fail = New-Object System.Collections.Generic.List[string]
$warn = New-Object System.Collections.Generic.List[string]
$checks = 0
function Add-Fail([string]$Message) { $script:fail.Add($Message) }
function Add-Warn([string]$Message) { $script:warn.Add($Message) }
# ConvertFrom-Json turns ISO dates into [datetime]; normalise back to yyyy-MM-dd.
function Get-IsoDate([object]$Value) {
    if ($null -eq $Value) { return $null }
    if ($Value -is [datetime]) { return $Value.ToString('yyyy-MM-dd') }
    $text = [string]$Value
    if ($text -match '^\\d{4}-\\d{2}-\\d{2}$') { return $text }
    return $null
}

# 1. kilo.json autoload set and skills path
$checks++
$cfgPath = Join-Path $root 'kilo.json'
$cfg = $null
if (-not (Test-Path -LiteralPath $cfgPath)) {
    Add-Fail 'kilo.json is missing'
} else {
    try { $cfg = Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json }
    catch { Add-Fail 'kilo.json is not valid JSON' }
}
if ($cfg) {
    foreach ($item in @('AGENTS.md', '.memory/project_brief.md', '.memory/active_context.md', '.memory/progress.md')) {
        if ($cfg.instructions -notcontains $item) { Add-Fail ('kilo.json instructions missing ' + $item) }
    }
    if ($cfg.skills.paths -notcontains '.kilo/skills') { Add-Fail 'kilo.json skills.paths missing .kilo/skills' }
}

# 2. skill frontmatter
$checks++
$skillPath = Join-Path $root '.kilo/skills/{slug}/SKILL.md'
if (-not (Test-Path -LiteralPath $skillPath)) {
    Add-Fail 'skill file is missing'
} else {
    $skill = Get-Content -LiteralPath $skillPath -Raw
    if ($skill -notmatch '(?s)^---\\s*\\r?\\n(.*?)\\r?\\n---') {
        Add-Fail 'skill frontmatter is missing'
    } else {
        $head = $Matches[1]
        if ($head -notmatch '(?m)^name:\\s*{slug}\\s*$') { Add-Fail 'skill name does not match the directory' }
        if ($head -notmatch '(?m)^description:\\s*\\S+') { Add-Fail 'skill description is missing' }
    }
}

# 3. failure matrix rows
$checks++
$failuresPath = Join-Path $root 'FAILURES.md'
$rows = 0
if (-not (Test-Path -LiteralPath $failuresPath)) {
    Add-Fail 'FAILURES.md is missing'
} else {
    foreach ($line in (Get-Content -LiteralPath $failuresPath)) {
        if ($line -notmatch '^\\|') { continue }
        if ($line -match '^\\|\\s*-') { continue }
        if ($line -match '^\\|\\s*Symptom') { continue }
        $cells = $line.Split('|')
        if ($cells.Count -lt 6) { Add-Fail ('FAILURES row has fewer than 4 columns: ' + $line); continue }
        for ($i = 1; $i -le 4; $i++) {
            if ([string]::IsNullOrWhiteSpace($cells[$i])) { Add-Fail ('FAILURES row has an empty cell: ' + $line) }
        }
        $rows++
    }
    if ($rows -eq 0) { Add-Fail 'FAILURES.md has no rows' }
}

# 4. secret-like values in every tracked text file
$checks++
$patterns = @(
    'Api-key\\s+[A-Za-z0-9_-]{16,}',
    'Bearer\\s+[A-Za-z0-9._-]{16,}',
    'OAuth\\s+[A-Za-z0-9._-]{20,}',
    'y0_[A-Za-z0-9_-]{20,}',
    'YC_API_KEY\\s*=\\s*\\S+',
    'client_secret\\s*[:=]\\s*\\S{8,}',
    'https?://\\S*(token|secret|password|api_key)='
)
$textFiles = @()
try {
    $textFiles = @(& git -C $root ls-files --cached --others --exclude-standard 2>$null)
} catch {
    $textFiles = @()
}
if (-not $textFiles) {
    $textFiles = @(Get-ChildItem -LiteralPath $root -Recurse -File |
        ForEach-Object { $_.FullName.Substring($root.Length + 1) -replace '\\\\', '/' })
    $textFiles = @($textFiles | Where-Object { $_ -notmatch '(^|/)\\.git/' })
}
foreach ($rel in $textFiles) {
    if ($rel -notmatch '\\.(md|json|ps1|py|ya?ml|txt|toml)$') { continue }
    $path = Join-Path $root $rel
    if (-not (Test-Path -LiteralPath $path)) { continue }
    $text = Get-Content -LiteralPath $path -Raw
    $hits = @($patterns | Where-Object { $text -match $_ })
    if ($hits.Count -gt 0) { Add-Fail ('secret-like value in ' + $rel) }
}

# 5. UTF-8 without BOM and no replacement characters
$checks++
foreach ($rel in $textFiles) {
    if ($rel -notmatch '\\.(md|json|ps1|py|ya?ml|txt|toml)$') { continue }
    $path = Join-Path $root $rel
    if (-not (Test-Path -LiteralPath $path)) { continue }
    $bytes = [IO.File]::ReadAllBytes($path)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { Add-Fail ('BOM in ' + $rel) }
    if ((Get-Content -LiteralPath $path -Raw).Contains([char]0xFFFD)) { Add-Fail ('replacement character in ' + $rel) }
}

# 6. state.json
$checks++
$statePath = Join-Path $root 'state.json'
$state = $null
if (-not (Test-Path -LiteralPath $statePath)) {
    Add-Fail 'state.json is missing'
} else {
    try { $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json }
    catch { Add-Fail 'state.json is not valid JSON' }
}
if ($state) {
    if ($state.status -notin @('live', 'partial', 'blocked', 'deferred')) { Add-Fail ('state.json has an unknown status: ' + $state.status) }
    if (($state.contract_version -as [int]) -lt 1) { Add-Fail 'state.json contract_version is not a positive integer' }
}

# 7. contract header sync: CONTRACT.md version, status and date vs state.json
$checks++
$contractPath = Join-Path $root 'CONTRACT.md'
if (-not (Test-Path -LiteralPath $contractPath)) {
    Add-Fail 'CONTRACT.md is missing'
} else {
    $contractText = Get-Content -LiteralPath $contractPath -Raw
    if ($contractText -notmatch 'Version:\\s*(\\d+)') {
        Add-Fail 'CONTRACT.md has no Version line'
    } elseif ($state -and (($Matches[1] -as [int]) -ne ($state.contract_version -as [int]))) {
        Add-Fail ('CONTRACT.md Version ' + $Matches[1] + ' != state.json contract_version ' + $state.contract_version)
    }
    if ($contractText -notmatch 'status:\\s*\\*\\*(\\w+)\\*\\*') {
        Add-Fail 'CONTRACT.md has no bold status token'
    } elseif ($state -and $Matches[1] -ne $state.status) {
        Add-Fail ('CONTRACT.md status ' + $Matches[1] + ' != state.json status ' + $state.status)
    }
    if ($state -and $state.updated) {
        if (-not (Get-IsoDate $state.updated)) {
            Add-Fail ('state.json updated is not yyyy-MM-dd: ' + $state.updated)
        } elseif ($contractText -match '·\\s*(\\d{4}-\\d{2}-\\d{2})\\s*·' -and $Matches[1] -ne (Get-IsoDate $state.updated)) {
            Add-Fail ('CONTRACT.md date ' + $Matches[1] + ' != state.json updated ' + (Get-IsoDate $state.updated))
        }
    }
}

# 8. README status line sync
$checks++
$readmePath = Join-Path $root 'README.md'
if (-not (Test-Path -LiteralPath $readmePath)) {
    Add-Fail 'README.md is missing'
} else {
    $readmeText = Get-Content -LiteralPath $readmePath -Raw
    if ($readmeText -notmatch 'Status:\\s*\\*\\*(\\w+)\\*\\*') {
        Add-Fail 'README.md has no bold status token'
    } elseif ($state -and $Matches[1] -ne $state.status) {
        Add-Fail ('README.md status ' + $Matches[1] + ' != state.json status ' + $state.status)
    }
}

# 9. registry sync: the hub entry exists and matches state.json
$checks++
$registryPath = $env:HARNESS_REGISTRY
if (-not $registryPath) {
    $registryPath = Join-Path (Split-Path -Parent $root) 'harness-playbook\\inventory\\integrations.json'
}
if (-not (Test-Path -LiteralPath $registryPath)) {
    if ($RequireRegistry) {
        Add-Fail ('registry not found: ' + $registryPath)
    } else {
        Add-Warn ('registry not found, sync check skipped: ' + $registryPath)
    }
} else {
    $registry = $null
    try { $registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json }
    catch { Add-Fail 'registry is not valid JSON' }
    if ($registry) {
        $entry = @($registry.hubs | Where-Object { $_.slug -eq '{slug}' })
        if ($entry.Count -ne 1) {
            Add-Fail ('registry has ' + $entry.Count + ' entries for slug {slug}')
        } elseif ($state) {
            if ($entry[0].status -ne $state.status) {
                Add-Fail ('registry status ' + $entry[0].status + ' != state.json status ' + $state.status)
            }
            $registryVersion = 1
            if ($entry[0].contract_version) { $registryVersion = $entry[0].contract_version -as [int] }
            if ($registryVersion -ne ($state.contract_version -as [int])) {
                Add-Fail ('registry contract_version ' + $registryVersion + ' != state.json contract_version ' + $state.contract_version)
            }
        }
    }
}

# 10. token expiry tracked in state.json
$checks++
if ($state -and $state.token_expires_on) {
    $expiresIso = Get-IsoDate $state.token_expires_on
    if (-not $expiresIso) {
        Add-Fail ('state.json token_expires_on is not yyyy-MM-dd: ' + $state.token_expires_on)
    } else {
        $daysLeft = [int][math]::Floor(([datetime]::ParseExact($expiresIso, 'yyyy-MM-dd', $null).Date - (Get-Date).Date).TotalDays)
        if ($daysLeft -lt 0) {
            Add-Fail ('token expired on ' + $expiresIso + '; re-issue it and update state.json')
        } elseif ($daysLeft -le 30) {
            Add-Warn ('token expires in ' + $daysLeft + ' days (' + $expiresIso + '); rotate it')
        }
    }
}

if ($warn.Count -gt 0) {
    $warn | ForEach-Object { Write-Output ('SELFCHECK: WARN ' + $_) }
}
if ($fail.Count -gt 0) {
    $fail | ForEach-Object { Write-Output ('SELFCHECK: FAIL ' + $_) }
    exit 1
}
Write-Output ('SELFCHECK: OK (' + $checks + ' checks)')
exit 0
"""

EVALS = """# Evals — {dir}

No local runner is wired to this table; every runnable task below has a deterministic grader command.
A `not runnable` row states why it cannot be graded yet and is not a pass.

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
    hosts = hub.get("host_block", "")
    host_block = hosts + "\n" if hosts else ""
    return (VERIFY
            .replace("{slug}", hub["slug"])
            .replace("{dir}", hub["dir"])
            .replace("{status}", hub["status"])
            .replace("{env_array}", env_array)
            .replace("{host_block}\n", host_block)
            .replace("{smoke}", smoke_block))


def eval_row(index, task):
    lowered = task.lower()
    if "not runnable" in lowered or "without confirm" in lowered:
        return f"| {index} | {task} | - (not runnable) | n/a |"
    mode = "-Live" if "-Live" in task else "-Offline"
    expected = "exit 2" if ("exits 2" in lowered or "exit 2" in lowered) else "exit 0"
    return f"| {index} | {task} | `scripts/verify.ps1 {mode}` | {expected} |"


def eval_rows_for(hub):
    explicit = hub.get("eval_rows", [])
    if explicit:
        return [f"| {i} | {row['task']} | {row['grader']} | {row['expected']} |"
                for i, row in enumerate(explicit, 1)]
    return [eval_row(i, task) for i, task in enumerate(hub.get("evals", []), 1)]


def render_state(hub):
    expires = hub.get("token_expires_on")
    return (STATE
            .replace("{version}", str(hub.get("contract_version", 1)))
            .replace("{status}", hub["status"])
            .replace("{mode}", hub["mode"])
            .replace("{date}", DATE)
            .replace("{token_expires}",
                     f',\n  "token_expires_on": "{expires}"' if expires else ""))


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
    eval_rows = "\n".join(eval_rows_for(hub)) or "| - | - | - | - |"
    extra = "".join(
        f"## {section['title']}\n\n{section['body']}\n\n"
        for section in hub.get("extra_sections", []))

    files = {
        "README.md": README.format(
            title=hub["title"], status=hub["status"], mode=hub["mode"], date=DATE,
            summary=hub["summary"], consumers=consumers, slug=hub["slug"]),
        "CONTRACT.md": CONTRACT.format(
            title=hub["title"], date=DATE, status=hub["status"], mode=hub["mode"],
            version=hub.get("contract_version", 1),
            service=hub["service"], summary=hub["summary"],
            auth_list=auth_list or "_(none)_",
            auth_notes=hub.get("auth_notes", ""),
            verify_note=hub.get("verify_note", ""),
            endpoints=endpoints, limits=limits, gotchas=gotchas, consumers=consumers,
            extra=extra),
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
        os.path.join(".kilo", "harness.md"): HARNESS.format(
            dir=hub["dir"], key=hub["key"], slug=hub["slug"],
            initialized=hub.get("initialized", DATE)),
        os.path.join("scripts", "verify.ps1"): render_verify(hub),
        os.path.join("scripts", "selfcheck.ps1"): SELFCHECK.replace("{slug}", hub["slug"]),
        "state.json": render_state(hub),
        os.path.join(".github", "workflows", "gate.yml"): GATE_WORKFLOW,
        os.path.join(".memory", "project_brief.md"): BRIEF.format(
            dir=hub["dir"], service=hub["service"], consumers=consumers,
            status=hub["status"], mode=hub["mode"]),
        os.path.join(".memory", "active_context.md"): ACTIVE.format(
            dir=hub["dir"], status=hub["status"],
            next_step=("Получить доступ: " + ", ".join(hub.get("auth", []))) if hub["status"] == "blocked"
            else "Подключить первого потребителя к контракту и прогнать `-Live`."),
        os.path.join(".memory", "progress.md"): PROGRESS.format(
            dir=hub["dir"], status=hub["status"], mode=hub["mode"], date=DATE,
            version=hub.get("contract_version", 1),
            open_items=open_items),
    }
    files[os.path.join("evals", "tasks.md")] = EVALS.format(
        dir=hub["dir"], rows=eval_rows or "| - | - | - | - |")
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
    parser.add_argument("--force-memory", action="store_true",
                        help="with --force, also rewrite .memory/ (hand-maintained state)")
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
            keep_memory = rel.replace("\\", "/").startswith(".memory/")
            force = args.force and (args.force_memory or not keep_memory)
            if write_if_missing(os.path.join(repo_root, rel), content, force):
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
