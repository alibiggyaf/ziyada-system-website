# Ziyada System — Team Email Setup Plan
# خطة البريد الإلكتروني للفريق — زيادة سيستم

> **Created:** April 10, 2026  
> **Goal:** Give team members professional `@ziyadasystem.com` emails at minimum cost

---

## The Problem

You need professional team emails like:
- `ali@ziyadasystem.com` (founder)
- `info@ziyadasystem.com` (general inquiries)
- `support@ziyadasystem.com` (client support)
- `team@ziyadasystem.com` (internal team)

But you want the minimum possible spending.

---

## Recommended Solution: Cloudflare Email Routing (FREE) + Gmail Send As

**Total cost: $0/month** (as long as domain is on Cloudflare)

### How It Works

```
Someone emails info@ziyadasystem.com
          ↓
Cloudflare Email Routing receives it
          ↓
Forwards to → ziyadasystem@gmail.com (or any Gmail)
          ↓
You read it in Gmail, with "To: info@ziyadasystem.com" shown
```

For SENDING from the custom address:
```
You compose in Gmail
→ Switch "From" dropdown to info@ziyadasystem.com
→ Email sends via SMTP with your custom domain as sender
```

### Setup Steps

#### Step 1 — Enable Cloudflare Email Routing
1. Go to Cloudflare dashboard → select `ziyadasystem.com`
2. Click **Email** → **Email Routing**
3. Click **Enable Email Routing**
4. Cloudflare will auto-add the required MX records

#### Step 2 — Add Team Email Addresses
For each address, add a routing rule:

| Custom Address | Routes To (Gmail) |
|---------------|------------------|
| `ali@ziyadasystem.com` | `alibiggy.af@gmail.com` (founder) |
| `info@ziyadasystem.com` | `ziyadasystem@gmail.com` |
| `support@ziyadasystem.com` | `ziyadasystem@gmail.com` |
| `sales@ziyadasystem.com` | team member's Gmail |

#### Step 3 — Send From Custom Domain in Gmail (Gmail Send As)

For each Gmail account that needs to SEND from `@ziyadasystem.com`:

1. Open Gmail → Settings → **See all settings** → **Accounts and Import**
2. Under "Send mail as" → click **Add another email address**
3. Enter: Name = `زيادة سيستم`, Email = `info@ziyadasystem.com`
4. **SMTP Server:** Use one of these free SMTP relays:

**Option A — ImprovMX (FREE SMTP relay)**
- Register at improvmx.com (free plan)
- SMTP: `smtp.improvmx.com`, Port: `587`
- Username: `info@ziyadasystem.com`
- Password: ImprovMX SMTP password

**Option B — Brevo/Sendinblue (FREE 300 emails/day)**
- Register at brevo.com
- SMTP: `smtp-relay.brevo.com`, Port: `587`
- Username: your Brevo email
- Password: Brevo SMTP key

5. Gmail sends a verification email to `info@ziyadasystem.com` → it forwards to your Gmail → click verify link

---

## Alternative: Google Workspace (Best Quality, ~$6/user/month)

| Feature | Cloudflare Free | Google Workspace |
|---------|----------------|------------------|
| Receiving | ✅ Full | ✅ Full |
| Sending from @domain | ✅ Via Gmail SMTP | ✅ Native |
| Storage | 15GB Gmail | 30GB per user |
| Calendar sharing | ❌ No team calendar | ✅ Full Google Calendar |
| Meet integration | ❌ | ✅ |
| Admin control | ❌ | ✅ |
| Cost | $0 | ~$6/user/month |

**Recommendation:** Start with the free Cloudflare setup. Upgrade to Google Workspace only when the team grows beyond 3 people and needs shared calendars or admin control.

---

## Quick Addresses to Create First

| Address | Purpose | Routes To |
|---------|---------|-----------|
| `ali@ziyadasystem.com` | Founder personal | alibiggy.af@gmail.com |
| `info@ziyadasystem.com` | Public contact | ziyadasystem@gmail.com |
| `support@ziyadasystem.com` | Client support | ziyadasystem@gmail.com |

---

## Connection to N8N / Automated Emails

All automated emails from N8N workflows (admin notifications, auto-replies) currently send **FROM** Gmail OAuth (`ziyadasystem@gmail.com`).

Once Gmail Send As is configured, you can update the Gmail node in N8N to send from `info@ziyadasystem.com` or `noreply@ziyadasystem.com` — it will still use the same Gmail OAuth credential but display the custom sender address.

**N8N workflows that send email:**
- `pw6WYm4N36SXHNl6` — Admin Notify + Auto-Reply
- `l0zGF9ZrD8Tl1F4f` — Thmanyah Scraper Digest

---

## Status

- [ ] Enable Cloudflare Email Routing for `ziyadasystem.com`
- [ ] Add routing rules for all team addresses
- [ ] Set up Gmail Send As via ImprovMX SMTP
- [ ] Test receive + send for each address
- [ ] (Optional) Upgrade to Google Workspace when team grows

---

_For questions: see also [WORKFLOW_CONNECTIONS.md](WORKFLOW_CONNECTIONS.md)_
