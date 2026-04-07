# Workspace Agent Overlay

This file extends workspace behavior without replacing the baseline instructions in `.github/CLAUDE skool Ai-automation society.md`.

## Priority Model

1. Baseline first: `.github/CLAUDE skool Ai-automation society.md`
2. Then this overlay for workspace organization rules
3. Then project-specific instructions inside `projects/<project-name>/`

If there is a conflict, baseline and explicit user request win.

## Project Boundary Rules

- Keep all implementation files inside `projects/<project-name>/`.
- Do not place project scripts, workflows, or assets in workspace root.
- Prefer this mapping:
  - `scripts/` for Python executables
  - `tools/` for shell wrappers
  - `workflows/` for SOPs
  - `docs/` for documentation
  - `assets/` for exports and references
  - `notebooks/` for notebooks

## Search And Filter By Project

When searching, default scope should be the active project path:
- `projects/<project-name>/**`

Only search entire workspace when asked.

## Shared Skills Across All Projects

Shared reusable skills live in `.github/skills/`.

When a user asks to add a new reusable skill:
1. Create `.github/skills/<skill-name>/SKILL.md`
2. Add or update entry in `.github/skills/REGISTRY.md`
3. Keep skill content generic and project-agnostic
4. Add project-specific overrides only under that project folder

## Default Integration Preferences

For workflow implementation requests (especially n8n):

- Assume API-first execution using existing user-provisioned credentials.
- Prefer existing n8n credentials/integrations for OpenAI API, Google APIs, and Apify when relevant.
- For image or video workflow requests, prioritize available OpenAI image/video capabilities and wire nodes accordingly.
- Treat Apify as approved for trend research, social scraping tasks, and lead-generation workflows when requested.
- If a requested provider/model is unavailable (account, region, or API limitation), use the closest available alternative and state the limitation briefly.

Operational guardrails:

- Never hardcode API secrets in code or docs.
- Reference credential names/placeholders and environment variables instead.
- Keep provider wiring modular so a workflow can switch providers with minimal edits.
