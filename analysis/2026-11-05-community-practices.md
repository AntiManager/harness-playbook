# Community practices — research note (2026-11-05)

Scope: what the ecosystem converged on, and what applies to a Kilo + Windows + 21-repo workspace.
Each item is marked **adopt**, **adapt** or **reject**, with the reason.

## Sources

| Source | What it says | Decision |
|---|---|---|
| [AGENTS.md](https://agents.md/) (Linux Foundation, 60k+ repos) | AGENTS.md is a README for agents: setup/build/test commands, conventions, gotchas. Nested files in subprojects; closest file wins. Living documentation. | **adopt** |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | Keep the instruction file short and only include what the model cannot derive from the repo. Give it a runnable pass/fail check. Use deterministic controls (hooks/deny rules) for zero-exception rules; keep guidelines advisory. Skills for procedures; subagents for independent review, parallel work and noisy output. | **adopt** (principles), **adapt** (hooks) |
| [Agent Skills spec](https://agentskills.io/specification) | `SKILL.md` = frontmatter + body. `name` ≤64, lowercase/hyphen, must match the directory; `description` ≤1024 and is the trigger. Progressive disclosure: metadata → instructions (<5k tokens) → references on demand. `SKILL.md` <500 lines. | **adopt** |
| [Kilo docs — Skills](https://kilocode.ai/docs/features/skills) | Kilo implements Agent Skills. Skills load from `.kilo/skills/`; descriptions drive discovery; `/reload` re-scans; project skills override global; shell injection only for trusted locations. | **adopt** |
| [Kilo docs — Custom Modes](https://kilocode.ai/docs/customize/custom-modes) | Agent files in `.kilo/agent(s)/`; `mode: primary/subagent/all`; per-agent model/permission/steps; built-ins can be overridden. | **adopt** (policy in ADR 0005) |
| [Kilo docs — Custom Subagents](https://kilocode.ai/docs/customize/custom-subagents) | Isolated context, own model/permissions, Task/`@` invocation, `permission.task` allowlist, `hidden`/`disable`. | **adopt** |
| [Kilo docs — agents.md](https://kilocode.ai/docs/customize/agents-md) | AGENTS.md root + per-directory dynamic loading; write-protected; precedence over global instructions; Memory Bank deprecated. | **adopt** |
| [Kilo docs — Custom Rules](https://kilocode.ai/docs/customize/custom-rules) | Rules are `instructions` entries in `kilo.jsonc`; loaded in order; best-effort. | **adopt** (already used for `.memory/`) |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | Spec-driven flow: constitution → specify → plan → tasks → implement → converge. Project-local overrides; "start with the smallest change". | **adapt**: adopt `SPEC.md` + convergence, do not install the toolkit |
| [Anthropic — context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Treat context as a finite attention budget; smallest high-signal set; just-in-time retrieval; compaction, structured notes, subagent isolation. | **adopt** (already partly in the harness) |
| [AGENTS.md — nested files](https://agents.md/) | Monorepos ship nested AGENTS.md per package; nearest file takes precedence. | **adopt** |
| [Claude Code — skills frontmatter](https://code.claude.com/docs/en/skills) | `disable-model-invocation`, `context: fork`, `allowed-tools`, `paths` are Claude Code extensions. | **reject for Kilo**: not in the Kilo/Agent Skills surface we use; model invocation control is a command, not a skill field |

## Practices worth adding to the playbook

### P1. Write only what the model cannot derive
Anthropic: if the model can find it by reading the repo, leave it out; include only decisions,
gotchas, deploy/verification commands, and things corrected twice. This trims autoloaded files
and is the strongest lever on fixed prompt cost.
**Playbook change:** rewrite `AGENTS.min.md` around "commands, gotchas, decisions"; move generic
rules (UTF-8, tests-first) to skill triggers or the global layer.

### P2. Separate deterministic from advisory rules
Zero-exception rules belong in permission denies, scripts and gates, not in prose. Prose is for
judgment calls. Kilo's deterministic levers: `permission` (read/edit/bash), project commands that
run a check, and `verify_repo.ps1` / `harness_lint.py`.
**Playbook change:** add `enforcement: deterministic | advisory` to the card schema and mark each
card; add HP-016.

### P3. Always ship a runnable check
A task is not done until a command returns pass/fail. This is already `task-conversion`, but the
playbook should make the *verification recipe* a first-class artifact.
**Playbook change:** add HP-015 and a `verify` command template per archetype.

### P4. Spec before plan
Spec Kit's convergence loop (specify → plan → implement → converge) beats ad-hoc planning on
ambiguous work. We do not need the toolkit: one `SPEC.md` with requirements, edge cases and a
definition of done, then an atomic plan.
**Playbook change:** add HP-013 and `templates/SPEC.md`.

### P5. Progressive disclosure
Skills cost ~100 tokens of metadata until used; the body is paid only on activation. Split large
procedures into a router and references (already HP-006) and keep bodies <500 lines / ~5k tokens.
**Playbook change:** lint enforces the Agent Skills limits; template gets the limits inline.

### P6. Nested instructions for subprojects
The closest AGENTS.md wins. For a monorepo or a repo with a distinct subproject, ship a nested
file instead of growing the root file.
**Playbook change:** add HP-014 and a `templates/AGENTS.nested.md`.

### P7. Subagents are for isolation, not for a better answer
Use a subagent for parallel work, noisy output, or a reviewer that did not see the reasoning.
Cheap models for mechanical jobs; reviewer with read-only tools and a stronger model.
**Playbook change:** fold into HP-010 and ADR 0005; add a model/permission matrix.

### P8. Measure adoption, not just drift
Drift count alone does not say the playbook works. Record which pattern IDs each repo adopted
(`.kilo/harness.md`), then report adoption per pattern and per archetype.
**Playbook change:** machine-readable registry + `harness_lint.py --json` + an adoption section.

### P9. Start with the smallest change
Spec Kit: adapt with a preset or project-local override rather than replacing the whole process.
Our equivalent: a repo gets the archetype's minimal set, not every card.
**Playbook change:** each archetype states the minimum set and an explicit "not now" list.

## Practices to reject

| Practice | Why not |
|---|---|
| Full Spec Kit install (extensions/presets/catalogs) | Too heavy for 21 small repos; we adopt only the artifact shape |
| Claude-only skill fields (`context: fork`, `disable-model-invocation`, `paths`) | Not part of the Kilo skill surface we use; invoking behavior is controlled by commands |
| "Context windows are huge, stop managing context" | Measured here: median 239k, 17/20 sessions above 120k; the 120k ceiling and 4 KB output budget stay |
| Hooks as the first enforcement tool | Kilo hooks are not part of the current harness; use permission denies + scripts + commands until verified |
| Thousands of nested rules | Context rot and maintenance cost; one root file + nested files only where the directory is a real subproject |

## Kilo-specific findings (docs, 2026-11-05)

These are platform facts, not preferences; they change what the playbook should recommend.

1. **AGENTS.md is the primary instruction file and is write-protected.** Kilo prompts for approval
   before an agent edits it. Rollout must treat every `AGENTS.md` edit as an explicit-approved
   change, not a routine file edit.
2. **Per-directory AGENTS.md is dynamically loaded** when the agent reads a file in that directory
   (injected as a system reminder), not at session start. This makes HP-014 cheap: a subproject can
   ship its own rules without growing the root file.
3. **Rule precedence:** agent prompt → project `instructions` → project `AGENTS.md` →
   global `instructions` → skills (on demand). This confirms the boot-trio design; `.memory/`
   files are ordinary instruction files, not the deprecated Memory Bank feature.
4. **Memory Bank is deprecated in favor of AGENTS.md.** Do not add new Memory Bank artifacts; keep
   `.memory/` only as instruction/provenance files referenced by `instructions`.
5. **Skills:** `name` must match the directory; description drives discovery; `/reload` re-scans;
   project skills override global; `skills.paths`/`skills.urls` allow shared/remote skills.
6. **Subagents:** isolated session, own model/permissions, `mode: subagent`, invoked by the Task
   tool or `@name`; `permission.task` can allowlist which subagents a primary may call.
7. **Custom modes** remain available and can be restricted per agent; the ADR 0005 rule (mode only
   when it must be selected before tools, needs a different model/permission profile, and has no
   skill equivalent) is compatible with the platform.
8. **Kilo hooks are not part of the current harness**, so deterministic enforcement stays with
   permission rules, scripts and commands (`verify_repo.ps1`, `harness_lint.py`).

### Adjustments caused by these findings

- HP-014 stays, with a new evidence line: per-directory AGENTS.md is a platform feature.
- `kilo.json.min.jsonc` gains an optional `permission.task` allowlist for subagents.
- Rollout adds an explicit "AGENTS.md is protected: request approval" step.
- No new Memory Bank artifacts; `.memory/` is described as instruction/provenance files.
- The playbook may later publish its skills via `skills.urls`, but not in v2.

## What this changes for the playbook

1. Cards gain `enforcement` and `token_cost`; the schema becomes machine-checkable.
2. The template set gains `SPEC.md`, `AGENTS.nested.md`, `.kilo/harness.md`, `verify` command.
3. The lint grows from drift-only to **schema + skills-spec + links + inventory freshness**.
4. The index gains one global archetype decision tree and an adoption dashboard.
5. The playbook gets its own eval tasks, so "better" is measured, not asserted.
