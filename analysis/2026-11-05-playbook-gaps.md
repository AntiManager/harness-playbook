# Playbook review — gap analysis (2026-11-05)

State reviewed: `harness-playbook/` after Steps 1–5 (12 cards, 5 archetypes, 6 templates, 4 ADRs,
`harness_lint.py`, 2 commands). Baseline evidence: 21 repos, 44 drift findings.

## Scorecard

| Dimension | State | Verdict |
|---|---|---|
| Evidence per pattern | projects + measured/verification on every card | good |
| Governance | promotion rules, ADRs, provenance intent | good, but provenance is not enforced |
| Machine checks | drift scan reproduces the snapshot, `--repo`, exit code | good |
| Card schema | frontmatter is documented but unchecked | partial |
| Templates | AGENTS/kilo.json/memory/skill/command | partial — no SPEC, nested AGENTS, verify, provenance file |
| Archetypes | composition + anti-patterns per type | partial — no single decision tree, no "not now" minimum |
| Sources | none | missing |
| Adoption metrics | none | missing |
| Playbook evals | none | missing |
| Skill-quality gates | empty-description only (repo drift), not the playbook's own skills | missing |
| Rollout protocol | ADR 0004 gives the order | partial — no batches, no per-repo acceptance sheet |

## Gaps, prioritized

### G1 — No community baseline (high)
The playbook is internally consistent but not benchmarked against the ecosystem. No citations means
it cannot distinguish an in-house convention from a standard.
**Fix:** `analysis/2026-11-05-community-practices.md` (done) + a `sources/` index in the playbook;
each new card must cite at least one source or a measured in-repo result.

### G2 — Autoloaded guidance is more prescriptive than the model needs (high)
`AGENTS.min.md` carries generic rules (UTF-8, tests-first) that the model can derive or that the
global layer already covers. Anthropic's rule: write only what the model cannot see.
**Fix:** rewrite the template around commands, gotchas, decisions and verification; keep generic
rules as skill triggers.

### G3 — Deterministic vs advisory is not explicit (high)
A card does not say whether it is enforced by the harness or is a judgment call. This is the main
source of "the rule was in AGENTS.md but did not happen".
**Fix:** add `enforcement: deterministic | advisory` to the card schema; add HP-016; lint the value.

### G4 — No spec artifact (high)
Plans are strong, but there is no written spec to plan against on ambiguous work. Spec Kit's
converge loop addresses exactly the failure mode we hit (build the wrong thing, then re-plan).
**Fix:** add HP-013 and `templates/SPEC.md`; reference it from `/task` and the plan checklist.

### G5 — Templates miss three proven artifacts (medium)
No `SPEC.md`, no nested `AGENTS.md`, no `.kilo/harness.md` provenance/verify recipe.
**Fix:** add all three; document when each is used.

### G6 — Lint validates repos, not the playbook (medium)
`harness_lint.py` scans project drift only. A broken card, duplicate ID, dangling link or an
invalid skill name would pass.
**Fix:** lint v2 — card frontmatter/status/ID uniqueness/line cap, markdown links, skills spec
(`name` == dir, description ≤1024, body <500 lines), inventory freshness, `--json`.

### G7 — No adoption measurement (medium)
Pattern status is manual; no repo records which patterns it uses, so `proven` cannot be audited.
**Fix:** `.kilo/harness.md` per repo + a `playbook.json` registry + an adoption report in lint.

### G8 — Archetype selection is fragmented (medium)
Five local decision trees, no single entry point. A new repo owner must read all five.
**Fix:** `archetypes/README.md` with one tree and a composition matrix.

### G9 — No evals for the playbook (medium)
"Improved" is asserted, not measured. The workspace already has an eval runner and task format.
**Fix:** 5 deterministic tasks: init from archetype, audit a drifted repo, reject an invalid card,
detect a singular skills path, produce the provenance file. Run before/after a playbook change.

### G10 — Rollout is a single line in ADR 0004 (medium)
Twenty-one repos need batching, a pilot, and a per-repo acceptance sheet; "one repo per session"
is necessary but not sufficient.
**Fix:** rollout section in the plan: pilot → worst → medium → rest; per-repo checklist and
commands; stop conditions.

### G11 — Pattern count vs density (low)
12 cards is fine, but HP-006 (router) and HP-017 (progressive disclosure) would overlap, and
HP-010 (delegation) overlaps ADR 0005. Merge instead of adding near-duplicates.
**Fix:** keep 12 cards, add only 4 (013–016); fold subagent policy into HP-010; fold skill limits
into HP-006.

### G12 — Token cost is not stated per pattern (low)
Some patterns lower cost (router, minimal AGENTS, memory write-last), others raise it (extra
artifacts). A card should say which.
**Fix:** `token_cost: lowers | neutral | raises` in the schema.

## Target state (v2)

```
harness-playbook/
  README.md                  # index + adoption summary + decision tree link
  playbook.json              # machine-readable registry (cards, status, enforcement, cost)
  patterns/HP-00X.md         # 16 cards, schema v2, each <=100 lines
  archetypes/README.md       # one decision tree + composition matrix
  archetypes/*.md            # 5 archetypes with minimum set + "not now"
  templates/
    AGENTS.min.md            # trimmed to commands/gotchas/decisions
    AGENTS.nested.md
    SPEC.md
    kilo.json.min.jsonc
    memory/*
    SKILL.md.tmpl
    command.md.tmpl
    command.verify.md
    harness.md               # provenance + verify recipe
  analysis/                  # dated research notes
  inventory/                 # dated snapshots
  decisions/                 # ADRs 0001-0005
  scripts/harness_lint.py    # drift + schema + links + skills spec + --json
```

## Acceptance for v2

- `harness_lint.py` exits 0 on the playbook (schema, links, skills, registry) and still reports repo
  drift with the same counts as the 2026-11-05 snapshot.
- 16 cards, each with `status`, `enforcement`, `token_cost`, evidence and a verification command.
- 5 eval tasks defined and run; before/after results recorded.
- Templates instantiate in `%TEMP%\kilo\playbook-smoke` and pass `verify_repo.ps1`.
- `check_harness.py` on the global layer stays 0; commands 18 → 20 (`/harness-eval` optional).
