# Sources

Primary sources behind the playbook. Each card cites at least one entry (URL or local evidence);
the analysis notes hold the adopt/adapt/reject reasoning.

| ID | Source | Used for |
|---|---|---|
| S1 | [AGENTS.md standard](https://agents.md/) | minimal AGENTS.md, nested files, living documentation |
| S2 | [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | write-only-what-is-not-derivable, runnable checks, deterministic vs advisory |
| S3 | [Agent Skills specification](https://agentskills.io/specification) | skill frontmatter, name/description limits, progressive disclosure |
| S4 | [Kilo — Skills](https://kilocode.ai/docs/features/skills) | skill locations, description-driven discovery, reload |
| S5 | [Kilo — Custom Modes](https://kilocode.ai/docs/customize/custom-modes) | agent modes, permissions, model routing |
| S6 | [Kilo — Custom Subagents](https://kilocode.ai/docs/customize/custom-subagents) | isolated context, `permission.task`, manual `@` invocation |
| S7 | [Kilo — agents.md](https://kilocode.ai/docs/customize/agents-md) | root + per-directory loading, write protection, precedence |
| S8 | [Kilo — Custom Rules](https://kilocode.ai/docs/customize/custom-rules) | `instructions` entries, load order, best-effort limits |
| S9 | [GitHub Spec Kit](https://github.com/github/spec-kit) | spec → plan → tasks → converge, smallest change |
| S10 | [Anthropic — context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | attention budget, just-in-time retrieval, compaction, subagents |
| S11 | Local: `~/.config/kilo/scripts/check_harness.py`, `verify_repo.ps1` | deterministic acceptance |
| S12 | Local: `.run/kilo/harness-inventory.md`, `harness-drift.md` | 21-repo evidence base |
| S13 | Local: `linear-tech-bi/.kilo/command/closeout.md` | executable closeout |
| S14 | Local: `Proc_library/.kilo/skills/app-pipeline/` | router skill |

Notes:
- S1/S2 were re-read 2026-11-11 for the community refresh; they are stable enough to cite, but the
  Claude page moves faster (model/effort/hook sections change). Re-check when a card is edited.
- S2/S3/S4/S7/S9 are external and can change; re-check when a card is edited.
- Local sources are dated snapshots; a stale path is a lint finding.
- Claude-only skill fields (`context: fork`, `disable-model-invocation`, `paths`) are not used here.
