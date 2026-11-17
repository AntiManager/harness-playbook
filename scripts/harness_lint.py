#!/usr/bin/env python3
"""Read-only harness checks: repo drift and playbook self-validation.

Usage:
    python -X utf8 harness-playbook/scripts/harness_lint.py [root] [--repo NAME] [--self] [--json]

Modes:
  default  repo drift across the workspace (exit 1 when drift exists)
  --self   validate the playbook (card schema, registry, links, skills spec, line caps)
  --json   machine-readable output for the selected mode(s)
  --repo   limit the drift report to one repository

`root` defaults to the workspace (two levels above this script). No file is written.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

ALLOWED_MODELS = {"deepseek/deepseek-flash", "deepseek/deepseek-v4-pro"}
MAX_AGENTS_LINES = 60
MAX_CARD_LINES = 100
MAX_SKILL_BODY_LINES = 500
STD_INSTRUCTIONS = [
    "AGENTS.md",
    ".memory/project_brief.md",
    ".memory/active_context.md",
    ".memory/progress.md",
]
ARTIFACT_DIRS = ("command", "agent", "skill", "skills")
STATUSES = {"proven", "candidate", "deprecated"}
ENFORCEMENT = {"deterministic", "advisory"}
TOKEN_COST = {"lowers", "neutral", "raises"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def parse_jsonc(text: str):
    text = re.sub(r"(?m)^\s*//.*$", "", text)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not match:
        return {}
    out = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip()
    return out


def body_after_frontmatter(text: str) -> str:
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", text, re.S)
    return text[match.end():] if match else text


def artifact_files(base: str) -> list[str]:
    files = []
    for sub in ARTIFACT_DIRS:
        root = os.path.join(base, ".kilo", sub)
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                if name.endswith(".md"):
                    files.append(os.path.join(dirpath, name))
    return files


# ---------------------------------------------------------------- drift scan

def scan(root: str):
    repos = sorted(
        name for name in os.listdir(root)
        if os.path.isdir(os.path.join(root, name, ".git"))
    )
    rows = []
    total_findings = 0
    for repo in repos:
        base = os.path.join(root, repo)
        agents_path = os.path.join(base, "AGENTS.md")
        nested_path = os.path.join(base, ".kilo", "AGENTS.md")
        agents_lines = len(read(agents_path).splitlines()) if os.path.isfile(agents_path) else 0

        cfg = {}
        for cfg_name in ("kilo.json", "kilo.jsonc"):
            cfg_path = os.path.join(base, cfg_name)
            if os.path.isfile(cfg_path):
                cfg = parse_jsonc(read(cfg_path)) or {}
                break

        model = cfg.get("model")
        instructions = cfg.get("instructions") or []
        skills_paths = (cfg.get("skills") or {}).get("paths") or []
        findings = []

        if not os.path.isfile(agents_path) and not os.path.isfile(nested_path):
            findings.append("no AGENTS.md")
        if agents_lines > MAX_AGENTS_LINES:
            findings.append(f"AGENTS {agents_lines}L>{MAX_AGENTS_LINES}")
        if model and model not in ALLOWED_MODELS:
            findings.append(f"model {model}")
        if len(instructions) > len(STD_INSTRUCTIONS):
            findings.append(f"autoload {len(instructions)} files")
        if skills_paths and ".kilo/skills" not in skills_paths:
            findings.append(f"skills path {','.join(skills_paths)}")

        empty = 0
        files = artifact_files(base)
        for path in files:
            if not frontmatter(read(path)).get("description"):
                empty += 1
        if empty:
            findings.append(f"empty desc {empty}/{len(files)}")

        total_findings += len(findings)
        rows.append({
            "repo": repo,
            "model": model or "-",
            "autoload": len(instructions),
            "agents_lines": agents_lines or "-",
            "skills_path": ",".join(skills_paths) or "-",
            "findings": findings,
        })
    return repos, rows, total_findings


# ------------------------------------------------------------ playbook self

def check_links(playbook: str) -> list[str]:
    problems = []
    link_re = re.compile(r"\]\(([^)\s]+)\)")
    for dirpath, _, filenames in os.walk(playbook):
        for name in filenames:
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            text = read(path)
            for target in link_re.findall(text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                clean = target.split("#", 1)[0]
                if not clean:
                    continue
                resolved = os.path.normpath(os.path.join(os.path.dirname(path), clean))
                if not os.path.exists(resolved):
                    problems.append(f"dangling link: {os.path.relpath(path, playbook)} -> {target}")
    return problems


def check_skills(playbook: str) -> list[str]:
    problems = []
    home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    roots = [
        os.path.join(home, ".config", "kilo", "skills"),
        os.path.join(home, ".kilo", "skills"),
    ]
    seen = 0
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            skill_dir = os.path.join(root, name)
            skill_file = os.path.join(skill_dir, "SKILL.md")
            if not os.path.isdir(skill_dir) or not os.path.isfile(skill_file):
                continue
            seen += 1
            text = read(skill_file)
            meta = frontmatter(text)
            if meta.get("name") != name:
                problems.append(f"skill name mismatch: {name} has name={meta.get('name')!r}")
            if not NAME_RE.match(name) or len(name) > 64:
                problems.append(f"skill name invalid: {name}")
            desc = meta.get("description", "")
            if not desc or len(desc) > 1024:
                problems.append(f"skill description invalid: {name} ({len(desc)} chars)")
            body_lines = len(body_after_frontmatter(text).splitlines())
            if body_lines >= MAX_SKILL_BODY_LINES:
                problems.append(f"skill body too long: {name} ({body_lines} lines)")
    if seen == 0:
        problems.append("no skills found to validate")
    return problems


def self_check(playbook: str) -> list[str]:
    problems = []
    registry_path = os.path.join(playbook, "playbook.json")
    registry = parse_jsonc(read(registry_path)) or {}
    if not registry:
        problems.append("playbook.json missing or invalid")
        return problems

    card_ids = set()
    patterns_dir = os.path.join(playbook, "patterns")
    for name in sorted(os.listdir(patterns_dir)):
        if not name.endswith(".md") or name.startswith("_"):
            continue
        path = os.path.join(patterns_dir, name)
        text = read(path)
        meta = frontmatter(text)
        lines = len(text.splitlines())
        card_id = meta.get("id", "")
        card_ids.add(card_id)
        rel = f"patterns/{name}"
        if lines > MAX_CARD_LINES:
            problems.append(f"card too long: {rel} ({lines} lines)")
        if not re.match(r"^HP-\d{3}$", card_id):
            problems.append(f"card id invalid: {rel} ({card_id!r})")
        if not name.startswith(card_id + "-"):
            problems.append(f"card filename/id mismatch: {rel}")
        if meta.get("status") not in STATUSES:
            problems.append(f"card status invalid: {rel} ({meta.get('status')!r})")
        if meta.get("enforcement") not in ENFORCEMENT:
            problems.append(f"card enforcement invalid: {rel} ({meta.get('enforcement')!r})")
        if meta.get("token_cost") not in TOKEN_COST:
            problems.append(f"card token_cost invalid: {rel} ({meta.get('token_cost')!r})")
        if not meta.get("sources") or meta.get("sources") in ("[]", "''", '""'):
            problems.append(f"card has no sources: {rel}")
        if not meta.get("verification"):
            problems.append(f"card has no verification: {rel}")

    registry_ids = {card.get("id") for card in registry.get("cards", [])}
    for missing in sorted(card_ids - registry_ids):
        problems.append(f"registry missing card: {missing}")
    for extra in sorted(registry_ids - card_ids):
        problems.append(f"registry references missing card: {extra}")

    for archetype in registry.get("archetypes", []):
        path = os.path.join(playbook, "archetypes", archetype.get("slug", "") + ".md")
        if not os.path.isfile(path):
            problems.append(f"registry references missing archetype: {archetype.get('slug')}")
    for decision in registry.get("decisions", []):
        slug = decision.get("slug", "")
        matches = [n for n in os.listdir(os.path.join(playbook, "decisions"))
                   if n.startswith(decision.get("id", "") + "-") and n.endswith(slug + ".md")]
        if not matches:
            problems.append(f"registry references missing decision: {decision.get('id')} {slug}")

    problems.extend(check_links(playbook))
    problems.extend(check_skills(playbook))
    return problems


# ------------------------------------------------------------------- output

def print_drift(rows, total):
    print("| repo | model | autoload | AGENTS L | skills path | flags |")
    print("|---|---|---|---|---|---|")
    for row in rows:
        flags = ", ".join(row["findings"])
        print(f"| {row['repo']} | {row['model']} | {row['autoload']} | "
              f"{row['agents_lines']} | {row['skills_path']} | {flags} |")
    counts = Counter(f.split()[0] for row in rows for f in row["findings"])
    print()
    print(f"finding counts: {dict(sorted(counts.items()))}")
    print(f"total findings: {total}")


def main() -> int:
    args = sys.argv[1:]
    repo_filter = None
    if "--repo" in args:
        index = args.index("--repo")
        if index + 1 >= len(args):
            print("--repo needs a repository name")
            return 2
        repo_filter = args[index + 1]
        del args[index:index + 2]

    mode_self = "--self" in args
    mode_json = "--json" in args
    args = [a for a in args if a not in ("--self", "--json")]

    if args:
        root = args[0]
    else:
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isdir(root):
        print(f"not a directory: {root}")
        return 2

    playbook = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if mode_self:
        self_problems = self_check(playbook)
        if mode_json:
            print(json.dumps({"self": {"playbook": playbook, "problems": self_problems}},
                             ensure_ascii=False, indent=2))
        else:
            print(f"playbook: {playbook}")
            print(f"self problems: {len(self_problems)}")
            for problem in self_problems:
                print(f"  - {problem}")
        return 1 if self_problems else 0

    drift_repos, drift_rows, drift_total = scan(root)
    if repo_filter:
        drift_repos = [r for r in drift_repos if r == repo_filter]
        drift_rows = [r for r in drift_rows if r["repo"] == repo_filter]
        drift_total = sum(len(r["findings"]) for r in drift_rows)
        if not drift_repos:
            print(f"repo not found: {repo_filter}")
            return 2

    if mode_json:
        payload = {"drift": {"root": root, "repos": len(drift_repos),
                             "findings": drift_total, "rows": drift_rows}}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"root: {root}")
        print(f"repos: {len(drift_repos)}")
        print_drift(drift_rows, drift_total)

    return 1 if drift_total else 0


if __name__ == "__main__":
    raise SystemExit(main())
