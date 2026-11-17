---
id: HP-015
title: Give every repo a runnable verification recipe
status: proven
applies_when: Every repo; any change that claims to be done.
does_not_apply_when: Never — the recipe can be as small as one command.
evidence:
  projects: [linear-tech-bi, factory-system, global harness]
  measured: "closeout gates; verify_repo.ps1 ~0.5 KB; check_harness.py problems: 0"
sources: [https://code.claude.com/docs/en/best-practices, ~/.config/kilo/scripts/verify_repo.ps1]
enforcement: deterministic
token_cost: neutral
since: 2026-11-05
requires: [HP-007]
files: [.kilo/harness.md, .kilo/command/verify.md]
verification: "run the recorded command -> exit 0 and the recorded success line"
last_reviewed: 2026-11-05
---

## Problem

"Done" is asserted from the diff. Without a pass/fail command, the agent cannot close its own loop
and the user becomes the test suite.

## Solution

Record one recipe per repo in `.kilo/harness.md`:

```markdown
## Verify
- Command: <exact command>
- Success: <exit code 0 + key line>
- Scope: <what it covers>
- Not covered: <what still needs a human>
```

Optionally add `.kilo/command/verify.md` that runs it. The recipe should be the narrowest check that
covers the change, plus the repo-wide check when the change is broad.

## Trade-offs

- A stale recipe is worse than none; update it when commands change.
- Full suites are slow; keep a fast default and name the full gate.

## Migration notes

1. Ask: what command proves this repo still works?
2. Record it with its success line in `.kilo/harness.md`.
3. Use it as the acceptance step in plans and closeouts.

## Deprecated by

none
