<<<<<<< HEAD
# Ziyada System Website | موقع زيادة سيستم

The official website for Ziyada System — business automation, CRM & sales, customer acquisition, performance marketing, smart websites, and content systems.

## Getting Started

1. Clone the repository
2. Navigate to this directory
3. Install dependencies: `npm install`
4. Create an `.env.local` file for the frontend admin gate:

```
VITE_ADMIN_USER=your-admin-username
VITE_ADMIN_PASS=your-strong-admin-password
```

5. Create an optional `.env.server.local` file for the local API server. Start from `.env.server.example` if you want SMTP-backed email delivery instead of writing to the local outbox.
6. Start the local API server: `npm run dev:api`
7. In a second terminal, run the frontend: `npm run dev`

The frontend proxies `/api` to the local Python server on port `5175`, so both processes are required for forms, the trends dashboard, blog/case CRUD, newsletter signup, and the admin credential reset flow.

## Tech Stack

- React 18 + Vite
- Tailwind CSS + Radix UI
- Framer Motion
- React Router
- Local Python API with JSON-backed storage

## Project Structure

- `src/pages/` — All page components (Home, Services, About, Blog, etc.)
- `src/components/ziyada/` — Ziyada-specific components (Navbar, Footer, ROI Calculator, etc.)
- `src/components/admin/` — Admin dashboard components
- `src/api/siteApi.js` — Local frontend API client
- `local-data/` — Self-owned JSON data store for content, leads, bookings, subscribers, reset tokens, and outbox mail
- `../../scripts/dashboard_api.py` — Local-owned backend API server
=======
# WAT Framework Workspace

This workspace is now organized by project so each client/system stays isolated and scalable.

## Baseline Instructions

The master operating instructions remain in:
- `.github/CLAUDE skool Ai-automation society.md`

That file is the first setup and is intentionally preserved as the baseline.

## Project-First Layout

- `projects/` - All project workspaces, each named by project.
- `.github/` - Shared agent guidance, prompts, and reusable skills metadata.
- `.tmp/` - Workspace-level disposable files.
- `.env` - Workspace-level shared environment values when needed.

## Ziyada System Project

All Ziyada-related work lives in:
- `projects/ziyada-system/`

Project structure:
- `projects/ziyada-system/workflows/` - SOPs and runbooks
- `projects/ziyada-system/tools/` - Shell execution helpers
- `projects/ziyada-system/scripts/` - Python automation scripts
- `projects/ziyada-system/app/` - Product/app code
- `projects/ziyada-system/docs/` - Project docs and trackers
- `projects/ziyada-system/notebooks/` - Jupyter notebooks
- `projects/ziyada-system/assets/` - Brand and export files
- `projects/ziyada-system/.tmp/` - Project temporary data

## Future Projects

To start a new project:
1. Create `projects/<new-project-name>/`
2. Add the same folders used by `projects/ziyada-system/`
3. Keep all scripts/workflows/assets for that project inside its own folder
4. Reuse shared skills from `.github/skills/`

## Principle

Agent reasoning stays shared. Execution files stay project-scoped.
>>>>>>> 84272d5 (Initial commit: full website (frontend, backend, all assets))
