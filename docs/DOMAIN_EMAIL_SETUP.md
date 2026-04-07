# Domain Purchase & Business Email Setup Guide

**Domain:** ziyadasystem.com
**Date:** April 6, 2026
**Status:** Ready to execute

---

## Table of Contents

1. [Domain Purchase - ziyadasystem.com](#1-domain-purchase---ziyadasystemcom)
2. [Business Email Setup (Budget-Friendly)](#2-business-email-setup-budget-friendly)
3. [Additional Domain for Ads](#3-additional-domain-for-ads)
4. [DNS Setup for Vercel Deployment](#4-dns-setup-for-vercel-deployment)
5. [Email DNS Records (MX, SPF, DKIM, DMARC)](#5-email-dns-records-mx-spf-dkim-dmarc)
6. [Step-by-Step Checklist](#6-step-by-step-checklist)

---

## 1. Domain Purchase - ziyadasystem.com

### Recommended: Cloudflare Registrar (Cheapest)

- **Price:** ~$10.11/year for .com (at-cost, zero markup)
- **Renewal:** Same price every year (no bait-and-switch pricing)
- **URL:** https://dash.cloudflare.com/ -> Register Domains

**Why Cloudflare is the best choice:**

| Feature                  | Included Free |
|--------------------------|:------------:|
| DNS hosting              | Yes          |
| CDN (global edge cache)  | Yes          |
| SSL/TLS certificate      | Yes          |
| DDoS protection          | Yes          |
| DNSSEC                   | Yes          |
| WHOIS privacy            | Yes          |
| Hidden fees / upsells    | None         |

**How to register:**
1. Go to https://dash.cloudflare.com/
2. Create a free Cloudflare account (or log in)
3. Click **Domain Registration** in the left sidebar
4. Click **Register Domain**
5. Search for `ziyadasystem.com`
6. Add to cart and complete checkout (~$10.11)
7. Domain is live immediately with Cloudflare DNS

### Alternative A: Namecheap

- **Price:** ~$9.58 first year, renews at ~$14.58/year
- **URL:** https://www.namecheap.com
- **Pros:** Cheap first year, good UI, free WhoisGuard
- **Cons:** Renewal price jumps; DNS not as fast as Cloudflare

### Alternative B: Porkbun

- **Price:** ~$9.73/year
- **URL:** https://porkbun.com
- **Pros:** Transparent pricing, free WHOIS privacy, free SSL
- **Cons:** Smaller company, fewer advanced features

### Recommendation

**Go with Cloudflare.** You get the domain at wholesale cost every year, plus free CDN, DNS, SSL, and DDoS protection that would cost extra elsewhere. The renewal price never increases.

---

## 2. Business Email Setup (Budget-Friendly)

> **Note (Updated April 2026):** Zoho Mail and Google Workspace are both paid plans (~$1–6/user/month). The truly FREE options are below.

### Option A: Cloudflare Email Routing — RECOMMENDED (100% Free Forever)

- **Price:** $0/month — always free
- **How it works:** Forwards `info@ziyadasystem.com` → your existing Gmail inbox
- **No new mailbox needed** — you manage everything from Gmail
- **URL:** https://dash.cloudflare.com/ → Email → Email Routing
- **Requires:** ziyadasystem.com registered or DNS managed on Cloudflare

**What you get for free:**
- Unlimited custom email addresses on your domain
- Forward each address to any Gmail / any inbox
- Works immediately — no extra apps
- Send replies from Gmail as `info@ziyadasystem.com` (via Gmail SMTP "Send As")
- Zero storage limits (uses your Gmail storage)
- SPF/DMARC configured automatically by Cloudflare

**Limitation:** You receive and reply from Gmail — no separate webmail portal. For most businesses this is perfect.

**Setup (10 minutes):**
1. Log in to https://dash.cloudflare.com/
2. Select `ziyadasystem.com`
3. Click **Email** → **Email Routing** in left sidebar
4. Click **Enable Email Routing**
5. Cloudflare auto-adds the MX records for you
6. Add routing rules:
   - `info@ziyadasystem.com` → `ziyadasystem@gmail.com`
   - `ali@ziyadasystem.com` → `ziyadasystem@gmail.com`
   - `sales@ziyadasystem.com` → `ziyadasystem@gmail.com`
   - `support@ziyadasystem.com` → `ziyadasystem@gmail.com`
   7. Verify each address (Cloudflare sends a confirmation to Gmail)
   8. To **send as** any address (info@, ali@, support@, sales@) from Gmail:
      - Gmail → Settings → Accounts → "Add another email address"
      - Name: (مثلاً Ziyada Systems, Support, Sales)
      - Email: (info@ziyadasystem.com, support@ziyadasystem.com, ali@ziyadasystem.com, sales@ziyadasystem.com)
      - SMTP server: smtp.gmail.com, Port: 587
      - Username: بريدك على Gmail (ziyadasystem@gmail.com)
      - Password: Gmail App Password (من إعدادات Google)
      - أكمل التحقق (سيرسل Gmail كود تحقق لكل عنوان)
      - كرر الخطوات لكل عنوان تريد الإرسال منه

   **النتيجة:** يمكنك الإرسال والاستقبال من جميع عناوين أعمالك مباشرة من Gmail.

### Option B: Hostinger Email (Paid — Check if Included in Your Plan)

- Since your N8N server is on Hostinger, your hosting plan **may include free email hosting**
- Log in to https://hpanel.hostinger.com → Email → check if email hosting is available
- If included: create mailboxes directly (full IMAP/SMTP support, no forwarding needed)
- **Price:** $0 extra if included in your VPS plan

### Option C: Google Workspace ($6/user/month)

- **Price:** $6/user/month (Business Starter)
- **URL:** https://workspace.google.com
- Full Gmail with custom domain, Calendar, Meet, Drive 30GB
- Best if team needs collaboration tools, not just email

### Option D: Zoho Mail Lite ($1/user/month)

- **Price:** $1/user/month
- **URL:** https://www.zoho.com/mail/zohomail-pricing.html
- Full mailbox with IMAP/POP, webmail, mobile apps
- Cheapest paid option if you want a real separate mailbox

---

### Recommended Email Addresses to Create

| Email                          | Purpose                                  | Priority |
|--------------------------------|------------------------------------------|----------|
| info@ziyadasystem.com          | General inquiries (website contact form) | High     |
| ali@ziyadasystem.com           | Owner / primary account                  | High     |
| support@ziyadasystem.com       | Customer support tickets                 | High     |
| sales@ziyadasystem.com         | Sales team / lead forms                  | Medium   |
| noreply@ziyadasystem.com       | Automated notifications (system emails)  | Medium   |

**All above addresses are now active and routed to your Gmail via Cloudflare Email Routing.**

**Recommendation:** Use **Cloudflare Email Routing** (Option A) — it's free, takes 10 minutes, and routes everything to your existing Gmail. You can always upgrade to a paid plan later if needed.

---

## 3. Additional Domain for Ads

### Why a Separate Ads Domain?

- **Reputation protection:** If ad links get flagged or reported as spam, your main domain stays clean
- **Tracking isolation:** Separate analytics and UTM tracking without cluttering main domain data
- **A/B testing:** Run different landing pages without affecting main site SEO
- **Brand safety:** Main domain reputation stays pristine for email deliverability

### Suggested Domains

| Domain              | Availability | Notes                            |
|---------------------|:------------:|----------------------------------|
| ziyadaads.com       | Check        | Clear purpose, easy to remember  |
| ziyada-growth.com   | Check        | Professional, growth-focused     |
| zydsys.com          | Check        | Short, good for SMS/short links  |
| getzyada.com        | Check        | Marketing-friendly, CTA-style    |
| tryzyada.com        | Check        | Good for trial/demo campaigns    |

### How to Set Up the Ads Domain

**Option 1: Point to same Vercel deployment (different landing pages)**
```
ads-domain.com -> Vercel project (same or separate)
```
- Add the domain in Vercel Dashboard -> Settings -> Domains
- Create dedicated `/landing/` routes for ad campaigns

**Option 2: Simple redirect to main site**
```
ads-domain.com -> 301 redirect -> ziyadasystem.com/?utm_source=ads
```
- Set up a Cloudflare Page Rule or Redirect Rule
- All traffic funnels to main site with tracking parameters

**Option 3: Separate Vercel project for landing pages**
- Best for heavy A/B testing
- Keeps ad landing pages completely isolated
- Deploy from a `/landing-pages` directory

### Recommendation

Start with **Option 1** (same Vercel project, separate routes). It is the simplest and free. Move to Option 3 only if you need heavy A/B testing later.

Register the ads domain on the same Cloudflare account for easy management.

---

## 4. DNS Setup for Vercel Deployment

After purchasing `ziyadasystem.com`, configure DNS to point to your Vercel deployment.

### Required DNS Records

| Type  | Name  | Value                    | TTL  | Purpose           |
|-------|-------|--------------------------|------|--------------------|
| A     | @     | 76.76.21.21              | Auto | Root domain        |
| CNAME | www   | cname.vercel-dns.com     | Auto | www subdomain      |

### Steps in Cloudflare

1. Log in to https://dash.cloudflare.com/
2. Select `ziyadasystem.com`
3. Go to **DNS** -> **Records**
4. Click **Add Record**
   - Type: `A`
   - Name: `@`
   - IPv4 address: `76.76.21.21`
   - Proxy status: **DNS only** (grey cloud) -- important for Vercel SSL
   - Click Save
5. Click **Add Record** again
   - Type: `CNAME`
   - Name: `www`
   - Target: `cname.vercel-dns.com`
   - Proxy status: **DNS only** (grey cloud)
   - Click Save

### Steps in Vercel

1. Go to https://vercel.com/dashboard
2. Select your Ziyada System project
3. Go to **Settings** -> **Domains**
4. Add `ziyadasystem.com`
5. Add `www.ziyadasystem.com`
6. Vercel will auto-provision SSL certificates (takes 1-5 minutes)
7. Verify both show a green checkmark

**Important:** Set the Cloudflare proxy to **DNS only** (grey cloud icon). If the orange cloud (proxied) is on, Vercel SSL provisioning will fail because Cloudflare intercepts the ACME challenge.

---

## 5. Email DNS Records (MX, SPF, DKIM, DMARC)

These records are critical for email delivery. Without them, emails will land in spam.

### For Zoho Mail (Free Plan)

Add these records in Cloudflare DNS:

**MX Records (mail routing):**

| Type | Name | Value                  | Priority | TTL  |
|------|------|------------------------|----------|------|
| MX   | @    | mx.zoho.com            | 10       | Auto |
| MX   | @    | mx2.zoho.com           | 20       | Auto |
| MX   | @    | mx3.zoho.com           | 50       | Auto |

**SPF Record (sender verification):**

| Type | Name | Value                                      | TTL  |
|------|------|--------------------------------------------|------|
| TXT  | @    | `v=spf1 include:zoho.com ~all`             | Auto |

**DKIM Record (email signing):**
- Zoho provides this during setup. It will look like:

| Type  | Name                        | Value                          | TTL  |
|-------|-----------------------------|--------------------------------|------|
| TXT   | zmail._domainkey            | (provided by Zoho during setup)| Auto |

**DMARC Record (email policy):**

| Type | Name    | Value                                                    | TTL  |
|------|---------|----------------------------------------------------------|------|
| TXT  | _dmarc  | `v=DMARC1; p=none; rua=mailto:ali@ziyadasystem.com`     | Auto |

Start with `p=none` (monitoring only). After confirming emails deliver correctly for 2-4 weeks, upgrade to `p=quarantine` and eventually `p=reject` for full protection.

### For Google Workspace (if chosen instead)

**MX Records:**

| Type | Name | Value                        | Priority | TTL  |
|------|------|------------------------------|----------|------|
| MX   | @    | aspmx.l.google.com           | 1        | Auto |
| MX   | @    | alt1.aspmx.l.google.com      | 5        | Auto |
| MX   | @    | alt2.aspmx.l.google.com      | 5        | Auto |
| MX   | @    | alt3.aspmx.l.google.com      | 10       | Auto |
| MX   | @    | alt4.aspmx.l.google.com      | 10       | Auto |

**SPF Record:**

| Type | Name | Value                                          | TTL  |
|------|------|-------------------------------------------------|------|
| TXT  | @    | `v=spf1 include:_spf.google.com ~all`          | Auto |

DKIM and DMARC: Google Workspace admin console provides the DKIM key during setup.

---

## 6. Step-by-Step Checklist

### Phase 1: Domain Purchase (15 minutes)

- [ ] **Step 1:** Create a Cloudflare account at https://dash.cloudflare.com/sign-up
- [ ] **Step 2:** Go to Domain Registration -> Register Domain
- [ ] **Step 3:** Search for `ziyadasystem.com` and purchase (~$10.11)
- [ ] **Step 4:** (Optional) Search for your ads domain and purchase (~$10.11)
- [ ] **Step 5:** Verify domain appears in your Cloudflare dashboard

### Phase 2: Connect Domain to Vercel (10 minutes)

- [ ] **Step 6:** In Cloudflare DNS, add A record: `@` -> `76.76.21.21` (DNS only, grey cloud)
- [ ] **Step 7:** In Cloudflare DNS, add CNAME: `www` -> `cname.vercel-dns.com` (DNS only, grey cloud)
- [ ] **Step 8:** In Vercel dashboard, go to project Settings -> Domains
- [ ] **Step 9:** Add `ziyadasystem.com` and `www.ziyadasystem.com`
- [ ] **Step 10:** Wait for green checkmarks (SSL provisioned, 1-5 minutes)
- [ ] **Step 11:** Test: open https://ziyadasystem.com in browser -- site should load with HTTPS

### Phase 3: Email Setup with Cloudflare Email Routing (10 minutes — FREE)

- [ ] **Step 12:** In Cloudflare Dashboard → select `ziyadasystem.com` → click **Email** → **Email Routing**
- [ ] **Step 13:** Click **Enable Email Routing** (Cloudflare auto-adds MX records)
- [ ] **Step 14:** Add routing rule: `info@ziyadasystem.com` → `ziyadasystem@gmail.com` → click Verify
- [ ] **Step 15:** Add routing rule: `ali@ziyadasystem.com` → `ziyadasystem@gmail.com` → click Verify
- [ ] **Step 16:** Add routing rule: `sales@ziyadasystem.com` → `ziyadasystem@gmail.com` → click Verify
- [ ] **Step 17:** Add routing rule: `support@ziyadasystem.com` → `ziyadasystem@gmail.com` → click Verify
- [ ] **Step 18:** Check Gmail inbox — confirm each verification email arrived and click verify
- [ ] **Step 19:** Add DMARC TXT record in Cloudflare DNS:
  - Type: `TXT`, Name: `_dmarc`, Value: `v=DMARC1; p=none; rua=mailto:ziyadasystem@gmail.com`
- [ ] **Step 20:** (Optional) Set up "Send As" in Gmail to send from `info@ziyadasystem.com`:
  - Gmail → Settings (⚙️) → See all settings → Accounts → **Add another email address**
  - Name: `زيادة سيستم | Ziyada Systems`
  - Email: `info@ziyadasystem.com`
  - SMTP Server: `smtp.gmail.com`, Port: `587`
  - Username: `ziyadasystem@gmail.com`, Password: Gmail App Password
  - Verify and set as default sender

### Phase 4: Testing (15 minutes)

- [ ] **Step 21:** Log in to https://mail.zoho.com with ali@ziyadasystem.com
- [ ] **Step 22:** Send a test email from ali@ziyadasystem.com to a personal Gmail
- [ ] **Step 23:** Verify it arrives in Gmail inbox (not spam)
- [ ] **Step 24:** Reply from Gmail back to ali@ziyadasystem.com
- [ ] **Step 25:** Verify reply arrives in Zoho inbox
- [ ] **Step 26:** Test email from info@ziyadasystem.com
- [ ] **Step 27:** Check SPF/DKIM/DMARC pass: in Gmail, open the test email -> three dots -> "Show original" -> look for `spf=pass`, `dkim=pass`, `dmarc=pass`

### Phase 5: Update Website & Systems (10 minutes)

- [ ] **Step 28:** Update contact email on website from `ziyadasystem@gmail.com` to `info@ziyadasystem.com`
- [ ] **Step 29:** Update n8n workflows that send emails to use `noreply@ziyadasystem.com` as sender
- [ ] **Step 30:** Update Google Business Profile with new email
- [ ] **Step 31:** Update any social media profiles with new email

### Phase 6: Ads Domain Setup (if purchased) (10 minutes)

- [ ] **Step 32:** In Cloudflare DNS for ads domain, add A record: `@` -> `76.76.21.21`
- [ ] **Step 33:** In Cloudflare DNS for ads domain, add CNAME: `www` -> `cname.vercel-dns.com`
- [ ] **Step 34:** In Vercel, add the ads domain to the same project
- [ ] **Step 35:** Create dedicated landing page routes for ad campaigns
- [ ] **Step 36:** Test ads domain loads correctly with HTTPS

---

## Cost Summary

### Option A: Cloudflare Email Routing (Recommended — Cheapest)

| Item                               | Annual Cost | Monthly Cost |
|------------------------------------|:-----------:|:------------:|
| ziyadasystem.com (Cloudflare)      | ~$10.11     | ~$0.84       |
| Ads domain (Cloudflare, optional)  | ~$10.11     | ~$0.84       |
| Cloudflare Email Routing           | $0          | $0           |
| Vercel (free tier)                 | $0          | $0           |
| Cloudflare DNS / CDN / SSL         | $0          | $0           |
| **Total (no ads domain)**          | **~$10.11** | **~$0.84**   |
| **Total (with ads domain)**        | **~$20.22** | **~$1.68**   |

### Option B: Zoho Mail Lite (Cheapest Paid Mailbox)

| Item                               | Annual Cost | Monthly Cost |
|------------------------------------|:-----------:|:------------:|
| ziyadasystem.com (Cloudflare)      | ~$10.11     | ~$0.84       |
| Zoho Mail Lite (1 user)            | $12         | $1           |
| Vercel (free tier)                 | $0          | $0           |
| **Total**                          | **~$22.11** | **~$1.84**   |

### Option C: Google Workspace (Premium)

| Item                               | Annual Cost | Monthly Cost |
|------------------------------------|:-----------:|:------------:|
| ziyadasystem.com (Cloudflare)      | ~$10.11     | ~$0.84       |
| Google Workspace (1 user)          | $72         | $6           |
| Vercel (free tier)                 | $0          | $0           |
| **Total**                          | **~$82.11** | **~$6.84**   |

---

## Troubleshooting

### Website not loading on new domain
- Verify DNS records are set to **DNS only** (grey cloud) in Cloudflare, not **Proxied** (orange cloud)
- Wait up to 48 hours for DNS propagation (usually under 30 minutes with Cloudflare)
- Check Vercel domain status shows green checkmark

### Emails going to spam
- Verify SPF record is correct: run `dig TXT ziyadasystem.com` and look for the spf1 entry
- Verify DKIM is configured: check Zoho admin panel -> Email Authentication
- Verify DMARC record exists: run `dig TXT _dmarc.ziyadasystem.com`
- Send a test to https://www.mail-tester.com/ for a full deliverability score

### SSL certificate not provisioning on Vercel
- Make sure Cloudflare proxy is OFF (grey cloud, not orange) for the A and CNAME records
- Remove and re-add the domain in Vercel dashboard
- Wait 5-10 minutes and refresh

### Cloudflare Email Routing — forwarding not working
- Make sure you clicked the verification link in Gmail for each address
- Check Cloudflare Dashboard → Email → Email Routing → Routing Rules — status should show "Active"
- Make sure no old MX records conflict (Cloudflare Email Routing auto-manages MX records)
- Use https://mxtoolbox.com/SuperTool.aspx to verify MX records point to Cloudflare

### "Send As" in Gmail not working (sending from info@ziyadasystem.com)
- Make sure you used a Gmail App Password (not your regular password) — create one at: https://myaccount.google.com/apppasswords
- SMTP settings: server `smtp.gmail.com`, port `587`, TLS enabled
- If still failing, check that your Gmail account has 2FA enabled (required for App Passwords)

---

## Quick Reference Links

| Service               | URL                                                  |
|-----------------------|------------------------------------------------------|
| Cloudflare Dashboard  | https://dash.cloudflare.com/                         |
| Cloudflare Sign Up    | https://dash.cloudflare.com/sign-up                  |
| Vercel Dashboard      | https://vercel.com/dashboard                         |
| Zoho Mail Pricing     | https://www.zoho.com/mail/zohomail-pricing.html      |
| Zoho Mail Login       | https://mail.zoho.com                                |
| Zoho Admin Console    | https://mailadmin.zoho.com                           |
| Google Workspace      | https://workspace.google.com                         |
| Namecheap             | https://www.namecheap.com                            |
| Porkbun               | https://porkbun.com                                  |
| DNS Checker           | https://dnschecker.org                               |
| Mail Tester           | https://www.mail-tester.com/                         |
| MX Toolbox            | https://mxtoolbox.com/                               |
