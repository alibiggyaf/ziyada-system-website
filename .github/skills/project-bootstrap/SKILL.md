---
name: project-bootstrap
description: "Use when creating a new project folder under projects/, setting up WAT subfolders, and initializing project-local docs without modifying baseline Claude instructions."
---

# Project Bootstrap Skill

## Objective

Create a new project folder under `projects/` with consistent WAT structure.

## Steps

1. Create `projects/<project-name>/`
2. Create subfolders:
   - `scripts/`
   - `tools/`
   - `workflows/`
   - `docs/`
   - `assets/`
   - `notebooks/`
   - `outputs/`
   - `.tmp/`
3. Create `projects/<project-name>/README.md` with purpose and run instructions.
4. Keep baseline policy in `.github/CLAUDE skool Ai-automation society.md` untouched.

## Guardrails

- Never move files from other projects into the new project unless explicitly requested.
- Keep credentials scoped to the target project where possible.
- Keep shared reusable guidance in `.github/skills/`.
