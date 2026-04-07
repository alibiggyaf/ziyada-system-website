# Workspace Structure Playbook

## Executive Summary

This playbook is the standard template for organizing multi-project work in one workspace.

It keeps shared guidance global, keeps implementation isolated by project, and makes future scaling predictable.

## Core Principle

Shared reasoning stays global. Execution files stay project-scoped.

## Source Of Truth And Precedence

1. Global baseline instruction file:
	.github/CLAUDE skool Ai-automation society.md
2. Workspace overlay rules:
	.github/AGENTS.md
3. Project-level docs and workflows:
	projects/<project-name>/docs and projects/<project-name>/workflows

If guidance conflicts, baseline plus explicit user request take priority.

## Workspace Layout Standard

- .github/ - shared agent guidance, prompts, and reusable skills
- projects/ - all project-specific workspaces
- shared/ - reusable scripts and templates
- .tmp/ - temporary workspace-level files
- .env - shared environment values only when truly cross-project

## Project Naming Standard

Create every initiative under:

projects/<project-name>/

Examples:
- projects/ziyada-system/
- projects/new-client-growth/

## Standard Project Folder Template

Every project should contain:

- scripts/ - Python automations and executables
- tools/ - shell wrappers and deterministic runners
- workflows/ - SOPs and execution flows
- docs/ - plans, trackers, decisions, runbooks
- assets/ - brand files, exports, and references
- notebooks/ - exploratory notebooks
- outputs/ - generated artifacts and logs
- .tmp/ - disposable temp files
- app/ - product codebases

## Folder Responsibilities

### scripts/

Python files that call APIs, transform data, send drafts, build docs/slides, or run automation tasks.

### tools/

Shell entry points used to run repeatable command sequences.

### workflows/

Human-readable SOPs that define objective, inputs, sequence, edge cases, and expected outputs.

### docs/

Operational documentation for humans: implementation trackers, architecture notes, checklists, and project rules.

### assets/

Static references and exports such as html, pdf, png, svg, zip, and source reference files.

### outputs/

Execution outputs and logs, including auth and validation logs.

### app/

Application source code (frontend, backend, serverless functions).

## Active Example In This Workspace

All Ziyada work is now scoped in:

projects/ziyada-system/

This includes scripts, tools, workflows, docs, assets, notebooks, outputs, credentials, and app code.

## Skills System For All Future Projects

Shared skills location:
- .github/skills/

Registry:
- .github/skills/REGISTRY.md

Current reusable skills:
- project-bootstrap
- google-workspace-oauth-setup

## How To Add A New Shared Skill

1. Create folder:
	.github/skills/<skill-name>/
2. Add SKILL file:
	.github/skills/<skill-name>/SKILL.md
3. Include YAML frontmatter with clear description triggers
4. Register the skill in:
	.github/skills/REGISTRY.md
5. Keep shared skill logic generic
6. Put project-specific details in project docs and workflows

## New Project Bootstrap

Run:

shared/tools/new_project.sh <project-name>

This creates the standard folder structure and starter README automatically.

## Explorer And Search Rules

Default search scope should be one project at a time:

projects/<project-name>/**

Use full workspace search only when explicitly needed.

VS Code support files:
- ziyada-projects.code-workspace
- .vscode/settings.json

## Security Rules

1. Keep credentials and token files inside each project folder.
2. Never commit credentials or tokens.
3. Use shared .env only for truly cross-project secrets.
4. Regenerate tokens when OAuth scopes change.
5. Keep cleanup artifacts in project .tmp or outputs/logs.

## Human Onboarding Checklist

1. Open workspace and confirm baseline file exists.
2. Open target project folder under projects/.
3. Read workflows before running scripts.
4. Check docs for current status and known constraints.
5. Execute scripts from the project root.
6. Save logs to outputs/logs.
7. Update docs when process changes.

## New Project Checklist

1. Run shared/tools/new_project.sh <project-name>
2. Add project README purpose and scope
3. Add first workflow in workflows/
4. Add first script in scripts/
5. Validate OAuth and credential placement
6. Run first test and capture logs
7. Document outcomes in docs/

## Monthly Maintenance Checklist

1. Verify workspace root has no project implementation files.
2. Verify token and credential files are ignored.
3. Verify each project has workflows and docs.
4. Verify shared skills registry is updated.
5. Archive old logs and generated outputs.

## Copy-Paste Starter Template

Use this block when creating a new project README:

# <project-name>

## Purpose
Describe what this project is for.

## Structure
- scripts/: Python automations
- tools/: Shell wrappers
- workflows/: SOP and execution flows
- docs/: Documentation and trackers
- assets/: Exports and references
- notebooks/: Research and experiments
- outputs/: Generated artifacts
- .tmp/: Disposable temporary files
- app/: Application code

## Baseline
Global baseline instructions are in:
.github/CLAUDE skool Ai-automation society.md

Project-level instructions should extend baseline, not replace it.
