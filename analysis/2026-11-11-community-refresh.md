# Community refresh — 2026-11-11

Re-read of the two primary sources behind HP-001/HP-013/HP-015/HP-016, after the playbook v2
rollout. Web search was unavailable (403); both pages were fetched directly and are current.
Verdicts below are what changes in the harness, not a summary of the articles.

## What was re-read

| Source | Fresh signal (2026) | Verdict |
|---|---|---|
| [AGENTS.md](https://agents.md/) (Linux Foundation) | Still "a README for agents": setup/build/test, gotchas; nested files, closest wins; 60k+ repos; write only what helps an agent work | **confirmed** — HP-001/HP-014 unchanged |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | Deterministic vs non-deterministic instructions; "write only what it cannot see"; a runnable check is the highest-value line; spec interview → `SPEC.md` → fresh session; skills for procedures; <200-line memory file; hooks/deny for zero-exception rules; subagents for parallelism/isolation, not a better answer | **adopt** (spec interview, check-first), **adapt** (hooks → gates), **reject** (long instruction files) |

## Deltas applied

1. **`/spec` command** (HP-013 was a template only). Ambiguous request → interview → `SPEC.md`
   with testable requirements, then `/task` and an atomic plan. `/task` now routes ambiguity there.
2. **Playbook section in `HARNESS.md`** updated from HP-001…HP-012 to v2 (16 cards, `playbook.json`,
   `sources/`, lint + eval commands, current drift baseline 17 findings).
3. **HP-008 gap closed** in `linear-tech`: `.run/` added to `.gitignore`.
4. **Client-knowledge pointer** added to the global manifest: `linear-tech` and `linear-tech-bi`
   are one client organization; the vault path is referenced, never copied.

## Rejected or deferred

| Practice | Why |
|---|---|
| "1M window, stop managing context" | Our constraint is DeepSeek prefix-cache cost: measured 239k median, 17/20 sessions >120k. The 120k checkpoint, 4 KB tool result and batch rule stay. |
| Claude `Stop` hook as the completion gate | No Kilo hook surface in this harness. Substitute: deterministic gate (`gates.ps1`, `verify_repo.ps1`, `harness_lint.py`) named in the task acceptance. |
| `.claude/rules/` path-scoped files | Kilo uses nested `AGENTS.md` (HP-014); adding a second mechanism would fork the rule body. |
| More subagents / more MCP | Costs tokens on every request; existing policy (ADR 0005) already covers isolation use. |

## Rollout state after this change

- 21 repos, 17 drift findings: 7 without `AGENTS.md`, 5 with a pinned model (ADR 0001), 5
  autoloading 5 files instead of 4 (ADR 0003). Cleanup remains batched, one repo per session.
- Both client repos lint clean (`--repo linear-tech`, `--repo linear-tech-bi` → 0 findings) and
  carry `.kilo/harness.md` provenance with a verify recipe.
- Global layer: `check_harness.py` 0 problems, `harness_lint.py --self` 0 problems,
  `playbook_eval.py` 5/5.
