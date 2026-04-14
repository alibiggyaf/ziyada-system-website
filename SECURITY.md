# Security Guidelines — Ziyada System Website

## Rule #1: No API Keys in Source Code

Never hardcode secrets in `.js`, `.jsx`, `.ts`, `.tsx`, or any other source file.

**Before any `git push`, run this check:**
```bash
grep -r "sk-\|eyJhbGci\|pat-eu\|GOCSPX\|fc-\|phx_" src/
```
The result must be empty. If anything is found, do NOT push.

---

## Environment Variables

### Frontend (Vite) — `.env.local`
All variables prefixed with `VITE_` are **bundled into the browser** — they are publicly visible. Only store public/anon keys here:

| Variable | Safe? | Notes |
|---|---|---|
| `VITE_SUPABASE_URL` | ✅ | Public URL, safe |
| `VITE_SUPABASE_ANON_KEY` | ✅ | Protected by Row Level Security (RLS) |
| `VITE_CHATBOT_WEBHOOK` | ✅ | Public webhook endpoint, safe |
| `VITE_N8N_HUBSPOT_SYNC_WEBHOOK` | ✅ | Uses `/n8n/...` proxy path — N8N host not exposed |
| `VITE_GA4_ID`, `VITE_HOTJAR_ID` | ✅ | Analytics IDs, public by design |

### Backend / Server-side — Never in `.env.local`
Keep these out of `.env.local` entirely. They go in your hosting provider's secret management or a `.env` file that is NEVER committed:

- `SUPABASE_SERVICE_ROLE_KEY` — full database access
- `HUBSPOT_PRIVATE_APP_TOKEN` — CRM write access
- `OPENAI_API_KEY` — billing charges
- `N8N_API_KEY` — workflow control
- `TELEGRAM_BOT_TOKEN` — bot access
- `FIRECRAWL_API_KEY` — scraping service
- `SMTP_PASS` — email sending

---

## Git Protection

`.gitignore` excludes:
- `.env`, `.env.*`, `*.local` — all env files
- `**/credentials.json`, `**/token.json` — OAuth tokens
- `client_secret_*.json` — Google service account files

`.env.example` files **should** be committed — they document required variables with placeholder values only.

---

## N8N Webhook Calls from Browser

All N8N webhook calls from the frontend must use the **proxy path** (not the full URL):

```js
// ✅ Correct — routes through Vite proxy (dev) / Vercel rewrite (prod)
VITE_N8N_HUBSPOT_SYNC_WEBHOOK=/n8n/webhook/hubspot-sync

// ❌ Wrong — exposes N8N host URL in browser network logs
const webhook = "https://n8n.srv953562.hstgr.cloud/webhook/hubspot-sync";
```

Exception: `VITE_CHATBOT_WEBHOOK` uses the full URL because the chat widget makes cross-origin requests that the proxy cannot intercept in production.

---

## HubSpot Sync Pattern

HubSpot sync is **fire-and-forget** — it must never block or fail a user's form submission:

```js
// triggerHubSpotSync() in siteApi.js uses .catch() — never throws
triggerHubSpotSync("lead", inserted); // non-blocking
return { success: true };             // form succeeds regardless
```

---

## Supabase Row Level Security

The Supabase anon key is safe to expose in the frontend because RLS policies enforce:
- Public insert allowed only for: `leads`, `bookings`, `subscribers`
- Public read allowed only for: published `blog_posts`, `case_studies`, `faq_items`, `services`
- Admin read/write requires authenticated session (admin panel only)
- Service role (full access) is only used in N8N server-side workflows — never in frontend code
