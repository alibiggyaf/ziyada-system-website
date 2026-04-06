# Ziyada System — Production Launch Checklist
# Domain: ziyadasystem.com | Hosting: Vercel | Date: April 2026

---

## Status Overview

| Task | Status |
|------|--------|
| Website build | ✅ Done |
| Vercel config (vercel.json) | ✅ Done |
| N8N AI Agent chat workflow | ✅ Done (Gemini + AI Agent) |
| GitHub repo | ✅ alibiggyaf/ziyada-system-website |
| N8N lead capture sub-workflow | ✅ Deployed (id: ImrkLJa5mO7TvJmk) |
| Supabase anon key in .env | ✅ Done |
| Email documentation | ✅ Updated (Cloudflare Email Routing = free) |
| **Domain DNS → Vercel** | ⏳ Need to do |
| **Vercel environment variables** | ⏳ Need to do |
| **Supabase Service Role key in N8N** | ⏳ Need to do |
| **HubSpot Private App key** | ⏳ Need to do |
| **Email setup (Cloudflare Routing)** | ⏳ Need to do |
| **Push latest code to GitHub** | ⏳ Need to do |

---

## Step 1 — Push Latest Code to GitHub (5 min)

```bash
cd /path/to/ziyada-system-website
git add docs/DOMAIN_EMAIL_SETUP.md docs/DEPLOYMENT_CHECKLIST.md public/sitemap.xml
git commit -m "Add deployment docs and update sitemap"
git push origin main
```

---

## Step 2 — Deploy to Vercel (10 min)

### If not already connected to Vercel:
1. Go to https://vercel.com/new
2. Click **Import Git Repository**
3. Select `alibiggyaf/ziyada-system-website`
4. Framework: **Vite** (auto-detected)
5. Build command: `npm run build`
6. Output directory: `dist`
7. Click **Deploy**

### Add Environment Variables in Vercel:
Go to: Vercel Dashboard → Project → Settings → Environment Variables

Add ALL of these (copy from your `.env.local`):

```
VITE_SUPABASE_URL          = https://nuyscajjlhxviuyrxzyq.supabase.co
VITE_SUPABASE_ANON_KEY     = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (full key from .env.local)
VITE_CHATBOT_WEBHOOK       = /n8n/webhook/3c9f6cb1-a3ce-4302-8260-6748f093520d/chat
VITE_CHATBOT_ENABLED       = true
VITE_N8N_NSI_WEBHOOK       = /n8n/webhook/ff9622a4-a6ec-4396-b9de-c95bd834c23c/chat
VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK  = /n8n/webhook/trigger-scrape
VITE_N8N_COMPETITOR_GENERATE_WEBHOOK = /n8n/webhook/competitor-generate
VITE_N8N_BLOG_PUBLISHER_WEBHOOK      = /n8n/webhook/publish-blog-draft
VITE_POSTHOG_KEY           = phx_xxxx... (copy from .env.local)
VITE_HOTJAR_ID             = 867a324ef296e
```

**Important:** Set environment for **Production**, **Preview**, and **Development**.

After adding variables: go to **Deployments** → click **Redeploy** on the latest deployment.

---

## Step 3 — Connect ziyadasystem.com Domain (10 min)

### In Vercel:
1. Go to project → **Settings** → **Domains**
2. Add: `ziyadasystem.com`
3. Add: `www.ziyadasystem.com`
4. Vercel shows DNS records to add (copy them)

### In your domain registrar (wherever ziyadasystem.com is registered):
Add these DNS records:

| Type  | Name | Value                | Notes |
|-------|------|----------------------|-------|
| A     | @    | 76.76.21.21          | Root domain |
| CNAME | www  | cname.vercel-dns.com | www subdomain |

**If using Cloudflare DNS:**
- Set both records to **DNS Only** (grey cloud, NOT orange/proxied)
- Vercel needs direct access for SSL provisioning

Wait 1-5 minutes → both domains show green checkmark in Vercel.

**Test:** Open https://ziyadasystem.com in browser → should load with HTTPS.

---

## Step 4 — Set Up Cloudflare Email Routing (10 min — FREE)

> This routes info@ziyadasystem.com → ziyadasystem@gmail.com for free.

1. Log in to https://dash.cloudflare.com/
2. Select `ziyadasystem.com` → Click **Email** → **Email Routing**
3. Click **Enable Email Routing** (auto-adds MX records)
4. Add routing rules — each forwards to `ziyadasystem@gmail.com`:
   - `info@ziyadasystem.com`
   - `ali@ziyadasystem.com`
   - `sales@ziyadasystem.com`
   - `support@ziyadasystem.com`
5. Check Gmail for verification emails → click verify for each

**To send AS `info@ziyadasystem.com` from Gmail:**
1. Gmail → Settings (⚙️) → See all settings → Accounts and Import
2. **Send mail as** → Add another email address
3. Name: `زيادة سيستم | Ziyada Systems`
4. Email: `info@ziyadasystem.com`
5. SMTP: `smtp.gmail.com`, Port: `587`, Username: `ziyadasystem@gmail.com`
6. Password: Gmail App Password (get from https://myaccount.google.com/apppasswords)
7. Verify and set as default

---

## Step 5 — Set Up Supabase Service Role in N8N (5 min)

The N8N lead capture workflow needs the Supabase **service_role** key (not the anon key).

1. Go to https://supabase.com/dashboard → your project → **Settings** → **API**
2. Copy the `service_role` key (under "Project API Keys")
3. Go to N8N → **Credentials** → **New** → **HTTP Header Auth**
   - Name: `supabaseServiceRole`
   - Header Name: `apikey`
   - Header Value: `<paste service_role key>`
   - Also add second header — Name: `Authorization`, Value: `Bearer <paste service_role key>`
4. Also add the Supabase URL header:
   - Another credential or modify the HTTP request node to include:
   - Header: `Content-Type: application/json`

**OR simpler:** In the Chat Lead Capture workflow, update the Supabase HTTP Request node credentials to use this credential.

---

## Step 6 — Set Up HubSpot Private App (15 min)

1. Log in to HubSpot with `ziyadasystem@gmail.com`
2. Go to: **Settings** (⚙️) → **Integrations** → **Private Apps**
3. Click **Create private app**
4. Name: `Ziyada N8N Integration`
5. Scopes needed:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.objects.deals.read`
   - `crm.objects.deals.write`
6. Click **Create app** → copy the access token (starts with `pat-na1-...`)
7. Go to N8N → **Credentials** → **New** → **HTTP Header Auth**
   - Name: `hubspotApi`
   - Header Name: `Authorization`
   - Header Value: `Bearer pat-na1-xxxx...` (your token)
8. Go to N8N → Workflows → **HubSpot CRM Sync** → import `workflow_hubspot_sync.json`
9. Activate the HubSpot sync workflow

---

## Step 7 — Test Everything End-to-End (20 min)

### Chat Agent Test:
```bash
curl -X POST https://n8n.srv953562.hstgr.cloud/webhook/3c9f6cb1-a3ce-4302-8260-6748f093520d/chat \
  -H "Content-Type: application/json" \
  -d '{"action":"sendMessage","chatInput":"السلام عليكم، وش خدماتكم؟","sessionId":"test-001"}'
```
Expected: Arabic response from AI agent about Ziyada services.

### Contact Form Test:
1. Go to https://ziyadasystem.com/Contact
2. Submit a test form with name + email
3. Check Supabase dashboard → `leads` table → new row should appear
4. Check Gmail → should receive notification

### Booking Test:
1. Go to https://ziyadasystem.com/BookMeeting
2. Fill all fields, pick date/time
3. Submit
4. Check Supabase → `bookings` table → new row
5. Should redirect to /ThankYou page

### HubSpot Sync Test (after Step 6):
1. Submit the contact form
2. Check HubSpot → Contacts → new contact should appear within 1 minute
3. Check HubSpot → Deals → new deal linked to the contact

---

## Remaining Items (Lower Priority)

- [ ] **GA4 Analytics**: Create Google Analytics 4 property → get Measurement ID → add `VITE_GA4_ID` to Vercel env
- [ ] **Meta Pixel**: Create Meta Business Manager pixel → add `VITE_META_PIXEL_ID` to Vercel env
- [ ] **Admin Panel**: Go to ziyadasystem.com/admin/login → set admin password in Supabase `admin_users` table
- [ ] **Blog Posts**: Add initial blog content via ziyadasystem.com/admin/blog
- [ ] **Case Studies**: Add real case studies via ziyadasystem.com/admin/cases
- [ ] **Google Business Profile**: Update with ziyadasystem.com URL and info@ziyadasystem.com

---

## Cost Summary (Monthly)

| Service | Cost |
|---------|------|
| Vercel (free tier) | $0 |
| Supabase (free tier, 500MB) | $0 |
| Cloudflare DNS + Email Routing | $0 |
| N8N (your VPS) | Already paid |
| AI Chat Agent (Gemini Flash) | ~$0.02/month |
| Domain (ziyadasystem.com) | ~$0.84/month (~$10/year) |
| **Total** | **~$0.86/month** |

---

## Quick Reference

| Service | URL | Login |
|---------|-----|-------|
| Website | https://ziyadasystem.com | — |
| Vercel | https://vercel.com/dashboard | GitHub |
| Supabase | https://supabase.com/dashboard | Google/GitHub |
| N8N | https://n8n.srv953562.hstgr.cloud | Your credentials |
| HubSpot | https://app.hubspot.com | ziyadasystem@gmail.com |
| Cloudflare | https://dash.cloudflare.com | Your account |
| GitHub | https://github.com/alibiggyaf/ziyada-system-website | GitHub |
