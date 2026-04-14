# Ziyada System Website — Agent Handoff Document

**Project**: Ziyada System Website (ziyadasystem.com)  
**Date written**: April 8, 2026  
**Purpose**: Comprehensive handoff for a new AI agent continuing this work. Read this entire document before taking any action.

---

## 1. Project Overview

A bilingual (Arabic RTL / English) React + Vite website for a Saudi digital-growth company. The site has a public frontend and an admin panel.

| Item | Value |
|---|---|
| **Local path** | `/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/` |
| **Tech stack** | React 18, Vite 6, TailwindCSS, Supabase, N8N workflows |
| **Local dev URL** | `http://localhost:5173` |
| **Production URL** | `https://ziyadasystem.com` (Vercel) |
| **Supabase project** | `https://nuyscajjlhxviuyrxzyq.supabase.co` |
| **N8N instance** | `https://n8n.srv953562.hstgr.cloud` |
| **Git branch** | `main` |

---

## 2. Critical File Map

```
src/
├── App.jsx                          — All routes (lazy-loaded admin)
├── main.jsx                         — Entry point + ErrorBoundary
├── index.css                        — Global styles
├── api/
│   └── siteApi.js                   — ALL Supabase + N8N API calls
├── lib/
│   ├── supabase.js                  — Supabase client init
│   ├── validation.js                — Zod schemas for all forms
│   ├── utm.js                       — UTM param capture
│   ├── rateLimit.js                 — Client-side rate limiting
│   └── analytics.js                 — GA4 / PostHog / Meta Pixel
├── pages/
│   ├── BookMeeting.jsx              — Booking form (→ Supabase bookings table)
│   ├── RequestProposal.jsx          — Proposal form (→ Supabase leads table)
│   └── Contact.jsx                  — Contact form (→ Supabase leads table)
├── admin/
│   ├── AdminAuthProvider.jsx        — Supabase auth context
│   ├── AdminLogin.jsx               — /admin/login page
│   ├── ResetPassword.jsx            — /admin/reset-password (request email)
│   └── ResetPasswordConfirm.jsx     — /admin/reset-password-confirm (NEW — set new password)
└── components/
    ├── ziyada/
    │   ├── Layout.jsx               — Public site wrapper (ThreeBackground, Navbar, Footer, Chat)
    │   ├── Navbar.jsx               — Top navigation
    │   ├── Footer.jsx               — Footer
    │   ├── ThreeBackground.jsx      — Animated Three.js background
    │   └── BrandIcons.jsx           — Custom SVG icon set
    └── ui/
        └── floating-chat-widget.jsx — AI chat widget (uses VITE_CHATBOT_WEBHOOK)

.env.local                           — Frontend secrets (NOT committed to git)
.gitignore                           — Fixed in this session
SECURITY.md                          — NEW security rules document
```

---

## 3. Environment Variables Reference

**File**: `.env.local` (local only, never committed)

```env
# Chat widget (full URL — chatbot workflow)
VITE_CHATBOT_WEBHOOK=https://n8n.srv953562.hstgr.cloud/webhook/0f30c293-c375-45a2-9cf6-d55208de387b
VITE_CHATBOT_ENABLED=true

# HubSpot CRM sync — fires after every form submission (fire-and-forget)
VITE_N8N_HUBSPOT_SYNC_WEBHOOK=/n8n/webhook/hubspot-sync

# Competitor intelligence workflows
VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK=/n8n/webhook/trigger-scrape
VITE_N8N_COMPETITOR_GENERATE_WEBHOOK=/n8n/webhook/competitor-generate
VITE_N8N_BLOG_PUBLISHER_WEBHOOK=/n8n/webhook/publish-blog-draft

# Supabase (anon key — safe for frontend, protected by RLS)
VITE_SUPABASE_URL=https://nuyscajjlhxviuyrxzyq.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbG...

# Analytics
VITE_HOTJAR_ID=867a324ef296e
VITE_GA4_ID=
VITE_POSTHOG_KEY=
VITE_META_PIXEL_ID=
```

**Important**: N8N webhook calls from the browser use the `/n8n/...` proxy path (not the full URL). The Vite dev server and Vercel rewrite both proxy `/n8n/:path*` → `https://n8n.srv953562.hstgr.cloud/:path*`. The chatbot webhook is the exception — it uses the full URL.

---

## 4. What Was Done In This Session

### 4.1 White Screen / App Crash Fix
- **Problem**: `TypeError: Cannot read properties of null (reading 'useEffect')` at `QueryClientProvider`. Caused by duplicate React instances.
- **Fix**: Added `resolve.dedupe: ['react', 'react-dom', 'react-router-dom']` to `vite.config.js`.
- **Also added**: Global `ErrorBoundary` class component in `src/main.jsx` to show readable errors instead of blank white screen (dev helper — shows stack trace on screen).
- **File**: `vite.config.js`, `src/main.jsx`

### 4.2 Horizontal Scroll Fix
- **Problem**: Page could be scrolled horizontally on desktop and mobile.
- **Fix**: Added `overflow-x: hidden; max-width: 100vw` to `html` and `body` in `src/index.css`. Also added `overflowX: 'hidden', maxWidth: '100vw'` to the root wrapper div in `src/components/ziyada/Layout.jsx`.
- **Files**: `src/index.css`, `src/components/ziyada/Layout.jsx`

### 4.3 Password Reset Flow — New Page
- **Problem**: Supabase sends reset emails with a link to `/admin/reset-password-confirm` but that route did not exist, causing a 404.
- **Fix**: Created `src/admin/ResetPasswordConfirm.jsx` — handles `PASSWORD_RECOVERY` Supabase auth event, lets user set new password, redirects to `/admin/login` on success.
- **Also updated**: `src/App.jsx` — added lazy import and route for `/admin/reset-password-confirm`.
- **Files**: `src/admin/ResetPasswordConfirm.jsx` (NEW), `src/App.jsx`
- **⚠️ MANUAL STEP STILL REQUIRED**: In Supabase dashboard → Authentication → URL Configuration → Redirect URLs, add:
  - `https://ziyadasystem.com/admin/reset-password-confirm`
  - `http://localhost:5173/admin/reset-password-confirm`

### 4.4 BookMeeting Form Fixes
- **Problem 1 — Silent failure**: `bookMeeting()` in `siteApi.js` returned the raw Supabase record, but the form checked `res.data?.success` (always `undefined`), so the form never redirected to `/ThankYou` even on success.
  - **Fix**: `bookMeeting()` now returns `{ success: true, ...savedBooking }`.
- **Problem 2 — Phone field**: Was optional, no country code selector, accepted junk numbers.
  - **Fix**: Added country code dropdown (🇸🇦🇦🇪🇰🇼🇶🇦🇧🇭🇴🇲🇯🇴🇪🇬) with digit hint placeholders. Phone is now **required**. Combined as `+966XXXXXXXXX` before validation. New `phoneSchemaRequired` Zod schema validates E.164 format.
- **Problem 3 — Industry dropdown**: English-only values in both AR/EN mode. Missing Saudi-relevant sectors.
  - **Fix**: Replaced with 13 bilingual options including Real Estate, Healthcare, Food & Restaurants, Construction, Financial Services, Travel & Tourism, Media & Marketing.
- **Also added**: Field-level error messages under each input, email placeholder `you@company.com`.
- **Files**: `src/pages/BookMeeting.jsx`, `src/lib/validation.js`, `src/api/siteApi.js`

### 4.5 Contact Form — Backend Integration Fix
- **Problem**: Contact form called a hardcoded N8N chatbot webhook URL directly via `fetch()`. No data was saved to Supabase. No HubSpot sync. Wrong webhook endpoint.
- **Fix**: Replaced with `siteApi.functions.invoke("submitContact", ...)` which:
  1. Saves to Supabase `leads` table with `source="contact"`
  2. Triggers HubSpot sync (non-blocking, fire-and-forget)
- **Removed**: Hardcoded `contactFormWebhook` URL from source code.
- **Files**: `src/pages/Contact.jsx`, `src/api/siteApi.js`

### 4.6 HubSpot CRM Sync — All Forms
- **Problem**: N8N HubSpot sync workflow existed (`workflow_hubspot_sync.json`) but was never called from the frontend.
- **Fix**: Added `triggerHubSpotSync(type, record)` helper in `siteApi.js` — fire-and-forget, never throws, logs a `console.warn` on failure. Called automatically after every successful `submitLead`, `submitContact`, and `bookMeeting` call.
- **New env var**: `VITE_N8N_HUBSPOT_SYNC_WEBHOOK=/n8n/webhook/hubspot-sync`
- **Files**: `src/api/siteApi.js`, `.env.local`
- **⚠️ REQUIRES**: The N8N `workflow_hubspot_sync.json` workflow must be active in N8N. If not active, sync fails silently (form still works).

### 4.7 RequestProposal Form
- No code changes needed — it already calls `siteApi.functions.invoke("submitLead", ...)` correctly. HubSpot sync is now triggered automatically via the `submitLead` function fix above.

### 4.8 .gitignore Fix
- **Problem**: File contained unresolved git merge conflict markers (`<<<<<<< HEAD` etc.) making it invalid. Env files may not have been properly excluded.
- **Fix**: Rewrote entire `.gitignore` merging rules from both conflict branches.
- **Verified**: `git check-ignore -v .env .env.local` confirms both are now properly ignored. Neither `.env` nor `.env.local` are tracked in git history.
- **File**: `.gitignore`

### 4.9 Security Cleanup
- **Removed**: Hardcoded webhook URL from `Contact.jsx`
- **Created**: `SECURITY.md` — documents all rules about secrets, proxy pattern, RLS explanation, pre-push check command.
- **Confirmed**: `grep -r "sk-\|pat-eu\|GOCSPX\|fc-[a-z]" src/` returns no matches (no secrets in source).
- **Files**: `SECURITY.md` (NEW), `src/pages/Contact.jsx`

---

## 5. Changes By File (Complete List)

| File | Status | Summary |
|---|---|---|
| `vite.config.js` | Modified | Added React deduplication, dev proxy `/n8n` |
| `src/main.jsx` | Modified | Added ErrorBoundary wrapper |
| `src/index.css` | Modified | Added `overflow-x: hidden` on html/body |
| `src/App.jsx` | Modified | Added `ResetPasswordConfirm` lazy import + route |
| `src/admin/ResetPasswordConfirm.jsx` | **NEW** | Password reset confirmation page |
| `src/components/ziyada/Layout.jsx` | Modified | Added `overflowX: hidden` to root wrapper |
| `src/lib/validation.js` | Modified | Added `phoneSchemaRequired`, updated `bookingSchema` |
| `src/api/siteApi.js` | Modified | Fixed `bookMeeting` return, added `triggerHubSpotSync`, `submitContact`, registered in FUNCTIONS map |
| `src/pages/BookMeeting.jsx` | Modified | Country code phone selector, 13 bilingual industries, required phone, field errors |
| `src/pages/Contact.jsx` | Modified | Removed hardcoded URL, now uses `siteApi.submitContact` |
| `.gitignore` | Modified | Fixed merge conflict, now properly excludes all env files |
| `.env.local` | Modified | Added `VITE_N8N_HUBSPOT_SYNC_WEBHOOK` |
| `SECURITY.md` | **NEW** | Security rules and pre-push checklist |

**Untracked new files (not yet committed)**:
- `src/admin/ResetPasswordConfirm.jsx`
- `SECURITY.md`
- `DEPLOYMENT_SECURITY_FUNNEL_CHECKLIST.md` (pre-existing, not written this session)
- `QA_CHECKLIST.md` (pre-existing, not written this session)
- `VERCEL_DEPLOYMENT_TROUBLESHOOT.md` (pre-existing, not written this session)
- `.env.example`, `.env.server.example` (pre-existing)

---

## 6. Remaining Tasks / Known Issues

### 6.1 ⚠️ BEFORE GITHUB UPLOAD (Mandatory)

These must be done before pushing to GitHub:

1. **Verify `.env` files are clean**  
   Run: `grep -r "sk-\|eyJhbGci\|pat-eu\|GOCSPX\|fc-[a-z]" src/`  
   Must return **zero results** (only CSS false-positives like `-webkit-mask-composite` are OK).

2. **Check git status carefully before committing**  
   Run: `git status` — confirm `.env`, `.env.local`, `.env.server.local` are NOT in the list of files to be staged.

3. **Fix ErrorBoundary in `src/main.jsx`**  
   Currently shows full stack traces in production. Should be conditionally hidden in production:
   ```jsx
   // In ErrorBoundary render():
   if (import.meta.env.DEV) {
     return <div>...</div>  // show stack trace in dev only
   }
   return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#0f172a' }}>
     <p style={{ color: '#94a3b8' }}>Something went wrong. Please refresh the page.</p>
   </div>
   ```

4. **Remove dev ErrorBoundary or make it production-safe** — see item 3 above.

### 6.2 ⚠️ Manual Supabase Dashboard Steps (Required for Password Reset)

In Supabase dashboard → **Authentication → URL Configuration → Redirect URLs**, add:
- `https://ziyadasystem.com/admin/reset-password-confirm`
- `http://localhost:5173/admin/reset-password-confirm`

Without this, reset emails from the production domain will be blocked by Supabase.

### 6.3 ⚠️ N8N Workflow Activation Required (Required for HubSpot CRM)

The HubSpot sync will silently fail until the workflow is activated:
1. Log into N8N at `https://n8n.srv953562.hstgr.cloud`
2. Import `n8n for ziyada systen/workflow_hubspot_sync.json` (if not already imported)
3. Activate the workflow
4. Note the webhook ID → verify it matches `/webhook/hubspot-sync` path
5. Add HubSpot API credentials in N8N credential store

### 6.4 Admin Credentials / User Access

Admin login at `/admin/login` uses Supabase Auth. To find or create admin accounts:
1. Supabase dashboard → **Authentication → Users**
2. Use "Send password recovery" from there, or create new user directly

### 6.5 Nice-to-Have (Lower Priority)

- **RequestProposal form**: Consider adding a phone field (currently has no phone) for better lead quality.
- **Email placeholders**: Contact form currently shows bilingual placeholder (`بريدك الإلكتروني` / `Your email`). Could standardize to `you@company.com` for clarity.
- **Supabase SMTP**: The built-in Supabase mailer is rate-limited to ~2 emails/hour. For production, configure a real SMTP provider (Resend, SendGrid, or Gmail SMTP) in Supabase dashboard → Authentication → Email → SMTP.

---

## 7. GitHub Upload Readiness

### ✅ Ready to commit:
- All source code changes (`.jsx`, `.js`, `.css`, `.json`)
- `SECURITY.md`
- `src/admin/ResetPasswordConfirm.jsx`
- `.gitignore` (fixed)
- `vite.config.js`

### ✅ Safe to commit (already in repo or public by design):
- `.env.example` — placeholder values only, no real keys
- `DEPLOYMENT_SECURITY_FUNNEL_CHECKLIST.md`, `QA_CHECKLIST.md`, `VERCEL_DEPLOYMENT_TROUBLESHOOT.md` — documentation only

### ❌ NEVER commit:
- `.env` — contains OpenAI key, HubSpot token, Supabase service role key, Telegram token, etc.
- `.env.local` — contains Supabase anon key and webhook URLs
- `.env.server.local` — contains SMTP credentials
- `.env.local.backup` — contains PostHog key
- Any `token_*.json` files
- Any `client_secret_*.json` files

### Pre-push checklist:
```bash
# 1. No secrets in source
grep -r "sk-\|eyJhbGci\|pat-eu\|GOCSPX" src/

# 2. Env files not tracked
git status | grep ".env"
# Should show nothing (all .env files must be absent)

# 3. Build succeeds
npm run build

# 4. Fix ErrorBoundary for production (see 6.1 above)
```

### Verdict: **NOT READY YET**
Fix the ErrorBoundary production safety issue (item 6.1 #3) before uploading. Everything else is clean.

---

## 8. Data Flow Summary

### Form Submission Flow (all three forms)
```
User fills form
  → Client-side Zod validation
  → Honeypot check (spam detection)
  → Rate limit check (3 req / 5 min)
  → siteApi.functions.invoke(...)
      → Supabase INSERT into leads/bookings table
      → triggerHubSpotSync() ← fire-and-forget, non-blocking
          → N8N /webhook/hubspot-sync
              → Create/update HubSpot contact + deal
              → Update Supabase row with HubSpot IDs
  → Analytics tracking (GA4, PostHog, Meta Pixel)
  → navigate("/ThankYou")
```

### Supabase Tables Used by Forms
| Table | Written by | Notes |
|---|---|---|
| `leads` | Contact form, RequestProposal, BookMeeting (auto) | source field = "contact" / "proposal" / "booking" |
| `bookings` | BookMeeting form | status = "pending" |
| `subscribers` | Newsletter signup (Footer) | status = "active" |

### Admin Panel Tables (read/write via authenticated session)
`blog_posts`, `case_studies`, `faq_items`, `services`, `competitor_intel`, `content_suggestions`, `profiles`

---

## 9. Tools & Skills Needed for This Project

The new agent should be familiar with:

### Code Tools
- **React / JSX** — functional components, hooks (`useState`, `useEffect`, `useRef`, `useCallback`), context, lazy loading
- **Vite** — config (`resolve.dedupe`, `server.proxy`), env vars (`import.meta.env.VITE_*`), build optimization
- **TailwindCSS** — utility classes, custom CSS variables (`var(--accent-primary)`)
- **Zod** — schema validation, `.safeParse()`, bilingual error messages
- **React Router v6** — `<Routes>`, `<Route>`, `useNavigate`, `useOutletContext`, lazy `<Suspense>`
- **Supabase JS client** — `.from().insert().select().single()`, `.auth.*`, RLS awareness
- **framer-motion** — animation (used in chat widget)

### Platform Skills
- **Supabase Dashboard** — Auth users, URL config for redirects, SMTP settings, table editor
- **N8N** — Import workflows, activate webhooks, check execution logs, manage credentials
- **Vercel** — Environment variables panel (for production secrets), deployment logs
- **Git** — Checking tracked files, `.gitignore` troubleshooting, pre-push secret audits

### Agent Workflow
- **Plan Mode** (`/plan`)— Use before any multi-file change to write a plan first
- **Explore agents** — Use subagent_type=`Explore` to read codebase before editing
- **TodoWrite** — Track multi-step tasks
- **ErrorBoundary pattern** — Always wrap React root in an error boundary to catch white-screen crashes
- **Dev server testing** — Start with `npm run dev`, open Chrome (not Comet browser — Comet has rendering issues), test forms manually then verify Supabase tables

### Security Rules (must follow)
- Never hardcode API keys or webhook URLs in `.jsx`/`.js` source files
- Always use `import.meta.env.VITE_*` for frontend config
- Always use the `/n8n/...` proxy path for N8N webhook calls (not the full `https://n8n.srv953562.hstgr.cloud/...` URL) — except for the chatbot which already uses the full URL
- Run `grep -r "sk-\|eyJhbGci\|pat-eu" src/` before any commit
- `VITE_SUPABASE_ANON_KEY` is safe to expose — protected by Supabase RLS policies

---

## 10. Quick Start for New Agent

```bash
# 1. Navigate to project
cd "/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website"

# 2. Start dev server
npm run dev
# → http://localhost:5173

# 3. Open in Chrome (NOT Comet browser — Comet has white-screen rendering issues)
open -a "Google Chrome" "http://localhost:5173/Home"

# 4. Test forms
open -a "Google Chrome" "http://localhost:5173/BookMeeting"
open -a "Google Chrome" "http://localhost:5173/Contact"
open -a "Google Chrome" "http://localhost:5173/RequestProposal"

# 5. Admin panel
open -a "Google Chrome" "http://localhost:5173/admin/login"

# 6. Build check (must pass before any GitHub push)
npm run build
```

---

*Document written by Claude Sonnet 4.6 — April 8, 2026*
