---
id: HP-004
title: Write memory last, one Write per file
status: proven
applies_when: Closing a session that touched autoloaded instructions or `.memory/`.
does_not_apply_when: The session only edited code and did not touch memory.
evidence:
  projects: [linear-tech-bi, global harness]
  measured: "2026-11-01 audit: 370 edits of autoloaded files, 339 mid-session, 116 full reprefills ≈ $3.46 (21% of spend)"
requires: [HP-002]
files: [.memory/active_context.md, .memory/progress.md, .memory/system_patterns.md]
verification: "git diff --stat .memory -> one changed block per file, no interleaved edits"
sources: [https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents, https://kilocode.ai/docs/customize/custom-rules]
enforcement: advisory
token_cost: lowers
since: 2026-11-05
last_reviewed: 2026-11-05
---

## Problem

Every edit of an autoloaded file invalidates the provider prefix cache; the next request re-sends
the whole context at miss price. A closeout series of 8–17 small memory edits can cost several
full reprefills.

## Solution

Source: `linear-tech-bi/.kilo/command/closeout.md`.

1. Run all gates and checks **before** touching memory.
2. Draft the resume pointer; do not write yet.
3. In one turn, one full-file `Write` per memory file. No tool call between writes.
4. Stop. No further tool calls after `/memory-end`.

## Trade-offs

- Full-file `Write` can be larger than an `Edit`; still cheaper than a cache miss.
- A correction discovered after the write costs a reprefill; batch corrections instead.

## Migration notes

1. Move live notes to `.run/session-notes.md` (not autoloaded).
2. Replace multi-edit closeouts with a single write per file.
3. Treat `AGENTS.md`/`kilo.json` edits as their own session.

## Deprecated by

none
