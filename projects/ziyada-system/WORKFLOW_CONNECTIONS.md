# Ziyada System — n8n Workflow Connections

This document summarizes all n8n workflow connections between the website, admin panel, and backend automations as of April 2026.

---

## 1. Ziyada AI Chat Agent — Website
- **Trigger:** Website frontend (chat/contact form)
- **Webhook:** `VITE_CHATBOT_WEBHOOK` (see `.env.local`)
- **Status:** Connected and active

## 2. Chat Lead Capture — Supabase + HubSpot
- **Trigger:** Website frontend forms (lead, booking, proposal)
- **Connection:** Data is inserted into Supabase (`leads` table). n8n workflow syncs new leads to HubSpot (via polling or Supabase trigger).
- **Status:** Indirect connection; no direct webhook call from frontend

## 3. Thmanyah Intelligence Scraper + Email Digest
- **Trigger:** Admin panel (on-demand) or scheduled
- **Webhooks:**
  - `VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK`
  - `VITE_N8N_COMPETITOR_GENERATE_WEBHOOK`
- **Status:** Connected and referenced in code

## 4. Blog Draft Publisher
- **Trigger:** Admin panel (blog editor, "AI Generate" or "Publish")
- **Webhook:** `VITE_N8N_BLOG_PUBLISHER_WEBHOOK`
- **Status:** Connected and referenced in code

## 5. On-Demand Content Generator
- **Trigger:** Admin panel (blog editor "AI Generate")
- **Webhook:** Shares or uses a dedicated n8n webhook (see code)
- **Status:** Connected

---

## .env.local Reference

- `VITE_CHATBOT_WEBHOOK` — AI chat agent (website)
- `VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK` — Competitor scraper
- `VITE_N8N_COMPETITOR_GENERATE_WEBHOOK` — Content generator
- `VITE_N8N_BLOG_PUBLISHER_WEBHOOK` — Blog publisher

---

## Recommendations

- All major workflows are connected and referenced in code or .env files.
- If you add new workflows (e.g., for Thaanyah, trends, or other automations), add their webhook URLs to `.env.local` and document them here.
- For instant HubSpot sync, consider adding a direct webhook call from the frontend on lead submission.
- Ensure all n8n webhooks are protected with a secret and validated in the workflow.

---

_Last reviewed: April 6, 2026_
