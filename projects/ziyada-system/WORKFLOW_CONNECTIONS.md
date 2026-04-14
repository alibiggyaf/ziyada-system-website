# Ziyada System — n8n Workflow Connections

This document summarizes all n8n workflow connections between the website, admin panel, and backend automations.

> **Last Updated:** April 10, 2026

---

## 1. Ziyada AI Chat Agent — Website

- **Trigger:** Floating chat widget on all website pages
- **Webhook:** `VITE_CHATBOT_WEBHOOK`
- **URL:** `https://n8n.srv953562.hstgr.cloud/webhook/0f30c293-c375-45a2-9cf6-d55208de387b`
- **N8N Workflow ID:** `4wO4enlPyFeNduqY`
- **Status:** ✅ Active

**Flow:** User message → N8N AI Agent (Gemini Flash) → response displayed in chat widget

---

## 2. HubSpot Sync — Lead & Booking CRM Sync

- **Trigger:** Website forms (Contact, BookMeeting, RequestProposal)
- **Webhook:** `VITE_N8N_HUBSPOT_SYNC_WEBHOOK`
- **URL:** `https://n8n.srv953562.hstgr.cloud/webhook/hubspot-sync`
- **N8N Workflow ID:** `1w96DpTzTGxaIlPW`
- **Status:** ✅ Active (rebuilt April 10, 2026)
- **Frontend caller:** `triggerHubSpotSync()` in `src/api/siteApi.js` (fire-and-forget)

**Flow:**
```
Form submit → Supabase saves record
     ↓
triggerHubSpotSync("lead"|"booking", record)
     ↓
N8N: Parse Data → Search HubSpot contact by email
     → If exists: PATCH update contact
     → If new: POST create contact
     → If booking type: POST create deal (stage: appointmentscheduled)
     ↓
Log to Supabase (integration_logs table)
```

---

## 3. Admin Notify + Auto-Reply — Email Notifications

- **Trigger:** Website forms (same as HubSpot Sync — every submission)
- **Webhook:** `VITE_N8N_NOTIFY_WEBHOOK`
- **URL:** `https://n8n.srv953562.hstgr.cloud/webhook/notify`
- **N8N Workflow ID:** `pw6WYm4N36SXHNl6`
- **Status:** ✅ Active (rebuilt April 10, 2026)
- **Frontend caller:** `triggerNotify()` in `src/api/siteApi.js` (fire-and-forget)

**Flow:**
```
Form submit
     ↓
triggerNotify(type, record)
     ↓
N8N: Parse → Generate both email HTMLs (Code node)
     ↓
Gmail: Send admin email to ziyadasystem@gmail.com
     ↓
IF visitor email present:
     → Gmail: Send auto-reply to visitor
```

**Email Design:**
- Admin email: dark theme (`#0a0f1e`), inline SVG Z logo, compact 520px
- Visitor auto-reply: light theme (`#f1f5f9`), Arabic + English, 520px mobile-optimized
- No external images, no emojis — brand-consistent

---

## 4. Google Meet Booking — Calendar Integration (PLANNED)

- **Trigger:** `bookMeeting()` function in `src/api/siteApi.js`
- **Webhook:** `VITE_N8N_GOOGLE_MEET_WEBHOOK`
- **URL:** `https://n8n.srv953562.hstgr.cloud/webhook/google-meet`
- **N8N Workflow ID:** Not built yet
- **Status:** 📋 PLANNED — env var exists in vercel.json but frontend never calls it yet

**Planned Flow:**
```
bookMeeting() → triggerGoogleMeetWebhook(bookingRecord)
     ↓
N8N: Parse booking data
     ↓
Google Calendar API: Create event with Google Meet link
     ↓
Gmail: Send Meet link to visitor email
     ↓
Owner (Ali): Receives calendar invite → Accept/Decline
     ↓
Supabase: Update booking with google_meet_link
```

**Required before building:**
1. Connect Google Calendar OAuth2 in N8N credentials
2. Build the N8N workflow
3. Add `triggerGoogleMeetWebhook()` call inside `bookMeeting()` in `siteApi.js`

---

## 5. Chat Lead Capture — Supabase + HubSpot (sub-workflow)

- **Trigger:** Chat Agent `capture_lead` tool (internal, not from frontend directly)
- **N8N Workflow ID:** `ImrkLJa5mO7TvJmk`
- **Status:** ✅ Active

---

## 6. Thmanyah Intelligence Scraper + Email Digest

- **Trigger:** Admin panel (`/admin/competitor`) or scheduled every 48h
- **Webhook:** `VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK`
- **N8N Workflow ID:** `l0zGF9ZrD8Tl1F4f`
- **Status:** ✅ Active

---

## 7. On-Demand Content Generator

- **Trigger:** Admin panel (`/admin/competitor`)
- **Webhook:** `VITE_N8N_COMPETITOR_GENERATE_WEBHOOK`
- **N8N Workflow ID:** `t6BKcMIadX9in9GM`
- **Status:** ✅ Active

---

## 8. Blog Draft Publisher

- **Trigger:** Admin panel (`/admin/competitor`)
- **Webhook:** `VITE_N8N_BLOG_PUBLISHER_WEBHOOK`
- **N8N Workflow ID:** `7g61zvLQhMyAXxO0`
- **Status:** ✅ Active

---

## 9. Ali Content Writer Engine 2026

- **Trigger:** Webhook (`/webhook/ziyada-blog-ingest`), Telegram, or Google Sheets schedule
- **N8N Workflow ID:** `C8JWsE3KIoxr1KgO`
- **Status:** ✅ Active

---

## 10. Niche Signal Intelligence

- **Trigger:** YouTube Trends Dashboard page
- **Webhook:** `VITE_N8N_NSI_WEBHOOK`
- **N8N Workflow ID:** `62MN6oqxOs3levjh`
- **Status:** ✅ Active

---

## Environment Variables Reference

| Variable | Webhook Path | Status |
|----------|-------------|--------|
| `VITE_CHATBOT_WEBHOOK` | `/webhook/0f30c293-...` | ✅ Active |
| `VITE_N8N_HUBSPOT_SYNC_WEBHOOK` | `/webhook/hubspot-sync` | ✅ Active |
| `VITE_N8N_NOTIFY_WEBHOOK` | `/webhook/notify` | ✅ Active |
| `VITE_N8N_GOOGLE_MEET_WEBHOOK` | `/webhook/google-meet` | 📋 Planned |
| `VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK` | `/webhook/trigger-scrape` | ✅ Active |
| `VITE_N8N_COMPETITOR_GENERATE_WEBHOOK` | `/webhook/competitor-generate` | ✅ Active |
| `VITE_N8N_BLOG_PUBLISHER_WEBHOOK` | `/webhook/publish-blog-draft` | ✅ Active |
| `VITE_N8N_NSI_WEBHOOK` | `/webhook/nsi` | ✅ Active |

All env vars are in `vercel.json` (production) and `.env.local` (dev).

---

## Team Email Connections Plan

See `EMAIL_TEAM_PLAN.md` for the recommended setup to give team members
professional `@ziyadasystem.com` email addresses at minimum cost.

---

_Ziyada System — نبنيلك نظام مبيعات يشتغل وأنت نايم_
