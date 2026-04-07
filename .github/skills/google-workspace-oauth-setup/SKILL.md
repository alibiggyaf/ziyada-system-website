---
name: google-workspace-oauth-setup
description: "Use when setting up or validating Google Workspace OAuth for Docs/Slides/Gmail scripts in any project, including token generation, credential checks, and first-run validation flow."
---

# Google Workspace OAuth Setup Skill

## Objective

Set up and verify OAuth credentials for Google Workspace automation scripts in a project-scoped way.

## When To Use

- New project needs Gmail/Docs/Slides API access
- Existing project has token or credentials errors
- You need to run first-time OAuth consent and persist token files

## Inputs

- Project path under `projects/<project-name>/`
- OAuth client file (`client_secret_*.json` or `credentials.json`)
- Target APIs and scopes

## Standard Flow

1. Confirm you are operating inside `projects/<project-name>/`.
2. Validate credentials file exists and is readable.
3. Run the project OAuth test/bootstrap script from `scripts/`.
4. Complete browser consent flow and store token in project scope.
5. Re-run test to verify API calls work.
6. Record warnings/errors in `outputs/logs/`.

## Guardrails

- Keep OAuth files inside the project folder, not workspace root.
- Never commit token or credential files.
- If scope changes, regenerate token and re-test.
- Avoid mixing credentials across projects.
