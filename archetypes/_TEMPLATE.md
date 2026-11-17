---
name: archetype-slug
status: proven              # proven | candidate | deprecated
applies_when: Project type and signals that select this archetype.
source_projects: [repo-a, repo-b]
patterns: [HP-001, HP-002, HP-003]
last_reviewed: 2026-11-05
---

# Archetype — <name>

## Decision tree

1. Signal → choose this archetype.
2. Counter-signal → choose `<other archetype>` instead.

## Minimal composition

| Layer | Files | Pattern |
|---|---|---|
| Instructions | `AGENTS.md`, `.memory/` boot trio | HP-001, HP-002 |
| Config | `kilo.json` (skills path, permissions, no model pin) | HP-003, HP-012 |
| Commands | `.kilo/command/*.md` | HP-005, HP-009 |
| Skills | `.kilo/skills/*/SKILL.md` | HP-006 |

## Required commands and skills

List the minimum set with their trigger. No project-specific skill bodies here.

## Anti-patterns

What not to copy from the source projects, and why.

## Verification

Commands that must pass on a newly composed repo, with expected output.

## Sources

Paths to the source projects' harness files (read on demand).
