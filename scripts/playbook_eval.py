#!/usr/bin/env python3
"""Deterministic self-evals for the harness playbook.

Five checks, no model calls:
  1. playbook self-check passes
  2. drift scan stays within the 2026-11-17 baseline (18 findings; repo count may grow)
  3. an invalid card is rejected
  4. a singular .kilo/skill path is flagged
  5. templates and registry are complete (16 cards, provenance sections)

Usage: python -X utf8 harness-playbook/scripts/playbook_eval.py
Exit 0 = all passed, 1 = one or more failed.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLAYBOOK = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import harness_lint as hl  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str) -> None:
    RESULTS.append((name, ok, detail))


def check_self() -> None:
    problems = hl.self_check(PLAYBOOK)
    check("playbook self-check", not problems, f"{len(problems)} problems" if problems else "0 problems")


def check_drift_baseline() -> None:
    root = os.path.dirname(PLAYBOOK)
    repos, rows, total = hl.scan(root)
    counts = {}
    for row in rows:
        for finding in row["findings"]:
            key = finding.split()[0]
            counts[key] = counts.get(key, 0) + 1
    baseline = {"autoload": 0, "model": 0, "no": 0}
    # S2 cleaned the 2026-11-17 drift to zero, so this is now a hard gate: any finding
    # type or count above the baseline means a repo regressed or the lint broke.
    ok = (
        total <= 0
        and set(counts) <= set(baseline)
        and all(counts.get(k, 0) <= v for k, v in baseline.items())
    )
    check("drift within baseline", ok, f"repos={len(repos)} total={total} counts={counts}")


def check_invalid_card() -> None:
    tmp = tempfile.mkdtemp(prefix="playbook-eval-")
    try:
        for sub in ("patterns", "archetypes", "decisions", "templates", "analysis", "inventory", "sources"):
            os.makedirs(os.path.join(tmp, sub), exist_ok=True)
        registry = {
            "cards": [{"id": "HP-999", "slug": "bad"}],
            "archetypes": [],
            "decisions": [],
            "templates": [],
        }
        with open(os.path.join(tmp, "playbook.json"), "w", encoding="utf-8") as fh:
            json.dump(registry, fh)
        with open(os.path.join(tmp, "patterns", "HP-999-bad.md"), "w", encoding="utf-8") as fh:
            fh.write("---\nid: HP-999\ntitle: Bad\nstatus: maybe\nenforcement: nope\n"
                     "token_cost: huge\nsources: []\n---\nbody\n")
        problems = hl.self_check(tmp)
        ok = any("status invalid" in p for p in problems) and any("no sources" in p for p in problems)
        check("invalid card rejected", ok, f"{len(problems)} problems")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_singular_skills_path() -> None:
    tmp = tempfile.mkdtemp(prefix="playbook-repo-")
    try:
        repo = os.path.join(tmp, "Demo")
        os.makedirs(os.path.join(repo, ".git"))
        with open(os.path.join(repo, "kilo.json"), "w", encoding="utf-8") as fh:
            json.dump({"skills": {"paths": [".kilo/skill"]}}, fh)
        _, rows, _ = hl.scan(tmp)
        ok = len(rows) == 1 and any("skills path" in f for f in rows[0]["findings"])
        check("singular skills path flagged", ok, str(rows[0]["findings"]) if rows else "no row")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_templates_and_registry() -> None:
    with open(os.path.join(PLAYBOOK, "playbook.json"), encoding="utf-8") as fh:
        registry = json.load(fh)
    cards = [entry for entry in registry.get("cards", []) if entry.get("id", "").startswith("HP-")]
    ok = len(cards) == 16
    missing = []
    for rel in registry.get("templates", []):
        if not os.path.isfile(os.path.join(PLAYBOOK, "templates", rel.replace("/", os.sep))):
            missing.append(rel)
    provenance = hl.read(os.path.join(PLAYBOOK, "templates", "harness.md"))
    for section in ("## Composition", "## Verify", "## Known exceptions"):
        if section not in provenance:
            missing.append(f"harness.md:{section}")
    check("16 cards + templates + provenance", ok and not missing,
          f"cards={len(cards)} missing={missing}")


def main() -> int:
    check_self()
    check_drift_baseline()
    check_invalid_card()
    check_singular_skills_path()
    check_templates_and_registry()
    failed = 0
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        failed += 0 if ok else 1
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
