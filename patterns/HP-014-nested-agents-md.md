---
id: HP-014
title: Use a nested AGENTS.md for a real subproject
status: candidate
applies_when: A repo contains a subproject with its own stack, commands or conventions.
does_not_apply_when: The whole repo is one stack; a nested file only duplicates the root.
evidence:
  projects: [workspace]
  measured: "Kilo loads a per-directory AGENTS.md dynamically when a file in that directory is read"
sources: [https://agents.md/, https://kilocode.ai/docs/customize/agents-md]
enforcement: deterministic
token_cost: lowers
since: 2026-11-05
requires: [HP-001]
files: [<subproject>/AGENTS.md]
verification: "read a file in the subproject -> its AGENTS.md is injected; root file did not grow"
last_reviewed: 2026-11-05
---

## Problem

A monorepo or mixed repo grows one root `AGENTS.md` until it is too long to autoload and too vague
to be useful. Rules for a backend package are paid for on every frontend task.

## Solution

Ship `<subproject>/AGENTS.md` with only that subproject's rules:

- stack and commands
- local conventions and gotchas
- pointers to the local docs

The root file keeps repo-wide rules and points to the subproject file. The nearest file wins.
Kilo loads it when the agent reads a file in that directory, not at session start.

## Trade-offs

- More files to maintain; each needs the same write protection review.
- A nested file can contradict the root; state precedence explicitly when it does.

## Migration notes

1. Identify a directory that is a real subproject (own manifest, tests, deploy).
2. Move only that directory's rules out of the root file.
3. Leave a one-line pointer in the root.
4. Verify by reading a file in the subproject and checking the injected reminder.

## Deprecated by

none
