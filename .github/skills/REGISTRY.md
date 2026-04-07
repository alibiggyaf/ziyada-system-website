# Shared Skills Registry

Use this registry for reusable skills that should work across all projects.

## How Skills Are Added

1. Create a folder: `.github/skills/<skill-name>/`
2. Add `SKILL.md` in that folder
3. Add one line in this registry with status and intent
4. Keep reusable logic generic; add project-specific details in project docs

## Registered Skills

- `project-bootstrap` - status: active - creates standard folder structure and starter docs for a new project.
- `google-workspace-oauth-setup` - status: active - standardizes Google Workspace OAuth bootstrap and validation inside project-scoped folders.

## Usage Rule

- If request is project-specific, apply the skill inside `projects/<project-name>/` only.
- If request is cross-project, use shared skill behavior from this registry.
