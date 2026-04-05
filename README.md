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
