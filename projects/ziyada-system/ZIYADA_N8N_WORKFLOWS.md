# نظام زيادة — توثيق Workflows في n8n
# Ziyada System — n8N Workflows Documentation

> **آخر تحديث / Last Updated:** 10 أبريل 2026 / April 10, 2026
> **المودل المستخدم / AI Model:** `google/gemini-2.0-flash-001` via OpenRouter
> **n8n Instance:** https://n8n.srv953562.hstgr.cloud

---

## فهرس / Index

1. [وكيل المحادثة — Chat Agent](#1-وكيل-المحادثة-chat-agent)
2. [التقاط العملاء المحتملين — Lead Capture](#2-التقاط-العملاء-المحتملين-lead-capture)
3. [مزامنة HubSpot — HubSpot Sync](#3-مزامنة-hubspot-hubspot-sync) ⭐ جديد
4. [إشعار المدير + الرد التلقائي — Admin Notify + Auto-Reply](#4-إشعار-المدير-admin-notify--auto-reply) ⭐ جديد
5. [رصد المنافسين — Competitor Intelligence Scraper](#5-رصد-المنافسين-competitor-intelligence-scraper)
6. [توليد المحتوى — Content Generator](#6-توليد-المحتوى-content-generator)
7. [نشر مقالات المدونة — Blog Draft Publisher](#7-نشر-مقالات-المدونة-blog-draft-publisher)
8. [محرك كتابة المحتوى — Ali Content Writer Engine](#8-محرك-كتابة-المحتوى-ali-content-writer-engine)
9. [ذكاء إشارات السوق — Niche Signal Intelligence](#9-ذكاء-إشارات-السوق-niche-signal-intelligence)
10. [بحث يوتيوب — YouTube Search](#10-بحث-يوتيوب-youtube-search)
11. [اجتماع Google Calendar — Google Meet Booking](#11-google-meet-booking-مخطط) 📋 مخطط

---

## 1. وكيل المحادثة — Chat Agent

| | |
|---|---|
| **الاسم / Name** | Ziyada AI Chat Agent — Website |
| **الـ ID** | `4wO4enlPyFeNduqY` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/4wO4enlPyFeNduqY |
| **الحالة / Status** | ✅ نشط / Active |
| **المودل / Model** | `google/gemini-2.0-flash-001` via OpenRouter |

### أين يُشغَّل؟ / Where is it triggered?
**كل صفحات الموقع** — زر المحادثة العائم في زاوية الصفحة
**All website pages** — Floating chat widget in corner of page

> المكوّن: `src/components/ui/floating-chat-widget.jsx`
> متغير البيئة: `VITE_CHATBOT_WEBHOOK`
> Webhook URL: `https://n8n.srv953562.hstgr.cloud/webhook/0f30c293-c375-45a2-9cf6-d55208de387b`

### التدفق الكامل / Full Flow

```
[المستخدم / User]
     ↓ يكتب رسالة في ويدجت المحادثة
     ↓ Types message in chat widget

[Frontend — floating-chat-widget.jsx]
     ↓ POST → VITE_CHATBOT_WEBHOOK
     ↓ Body: { chatInput, sessionId }

[n8n — Webhook Trigger]
     ↓ يستقبل الطلب / Receives request

[Ziyada AI Agent — LangChain Conversational Agent]
     ↓ OpenRouter LLM (google/gemini-2.0-flash-001)
     ↓ Window Buffer Memory (15 messages)
     ↓ يقرر استخدام أدوات / Decides which tools to use

     ├── [get_services_info] → يشرح خدمات زيادة / Explains Ziyada services
     ├── [book_consultation] → يعطي رابط الحجز / Returns booking link
     └── [capture_lead] → يحفظ بيانات العميل / Saves lead data
              ↓
         [Chat Lead Capture Workflow → Supabase + HubSpot]

[Respond to Webhook]
     ↓ JSON response → Frontend
     ↓ يظهر الرد في الشاشة / Response displayed in chat widget
```

### الأدوات المتاحة للوكيل / Agent Tools
| الأداة | الوظيفة |
|--------|---------|
| `get_services_info` | يشرح خدمات وأسعار زيادة — Explains Ziyada services & pricing |
| `book_consultation` | يعطي رابط استشارة مجانية — Returns free consultation booking link |
| `capture_lead` | يحفظ اسم وبريد وهاتف العميل في Supabase — Saves lead to Supabase |

---

## 2. التقاط العملاء المحتملين — Lead Capture

| | |
|---|---|
| **الاسم / Name** | Chat Lead Capture — Supabase + HubSpot |
| **الـ ID** | `ImrkLJa5mO7TvJmk` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/ImrkLJa5mO7TvJmk |
| **الحالة / Status** | ✅ نشط / Active |
| **نوع التشغيل / Trigger Type** | Sub-workflow (يُشغَّل من وكيل المحادثة) |

### أين يُشغَّل؟ / Where is it triggered?
**لا يُشغَّل مباشرة من الموقع** — يُشغَّل تلقائياً من وكيل المحادثة عند اكتشاف بيانات عميل
**Not triggered directly from website** — Auto-triggered from Chat Agent when lead data is detected

### التدفق الكامل / Full Flow

```
[Chat Agent — capture_lead tool]
     ↓ يرسل: name, email, phone, company, sector, challenge, service_interest
     ↓ Sends: name, email, phone, company, sector, challenge, service_interest

[Prepare Lead Data]
     ↓ يهيئ البيانات / Formats data

[Save Lead to Supabase]
     ↓ POST → Supabase REST API
     ↓ Table: leads (أو contacts)

[Has Email? — IF node]
     ├── نعم / Yes ↓
     │   [Sync to HubSpot]
     │   ↓ POST → HubSpot Contacts API
     │   ↓ ينشئ أو يحدث جهة الاتصال / Creates or updates contact
     │
     └── لا / No → يتجاوز HubSpot / Skips HubSpot

[Return Success]
     ↓ يرسل تأكيد للوكيل / Sends confirmation to Chat Agent
```

---

---

## 3. مزامنة HubSpot — HubSpot Sync

| | |
|---|---|
| **الاسم / Name** | Ziyada - HubSpot Sync |
| **الـ ID** | `1w96DpTzTGxaIlPW` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/1w96DpTzTGxaIlPW |
| **الحالة / Status** | ✅ نشط / Active (rebuilt April 10, 2026) |
| **Webhook** | `/webhook/hubspot-sync` |
| **متغير البيئة** | `VITE_N8N_HUBSPOT_SYNC_WEBHOOK` |

### أين يُشغَّل؟ / Where is it triggered?
كل نماذج الموقع — `triggerHubSpotSync()` في `src/api/siteApi.js` (fire-and-forget)
All website forms — called from `triggerHubSpotSync()` in `siteApi.js`

### التدفق الكامل / Full Flow

```
[Website Form Submit]
     ↓ POST → /webhook/hubspot-sync
     ↓ Body: { type: "lead"|"booking", record: {...} }

[Parse Data — Code Node]
     ↓ يحلل البيانات / Parses email, name, phone, company, bookingDate, type

[Search HubSpot Contact]
     ↓ POST → HubSpot search API (by email)

[Contact Exists? — IF node]
     ├── نعم / Yes → PATCH Update Contact
     └── لا / No  → POST Create Contact

[Is Booking? — IF node]
     ├── نعم / Yes → POST Create Deal (stage: appointmentscheduled)
     └── لا / No  → skip

[Log to Supabase]
     ↓ POST → integration_logs table (service role key)
```

### ملاحظات تقنية / Technical Notes
- Switch V3 node replaced with Code node to avoid `caseSensitive` bug
- HubSpot EU portal: `147540768`, token prefix `pat-eu1-*`
- `availableInMCP: true` in workflow settings

---

## 4. إشعار المدير + الرد التلقائي — Admin Notify + Auto-Reply

| | |
|---|---|
| **الاسم / Name** | Ziyada - Admin Notify + Auto-Reply |
| **الـ ID** | `pw6WYm4N36SXHNl6` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/pw6WYm4N36SXHNl6 |
| **الحالة / Status** | ✅ نشط / Active (rebuilt April 10, 2026) |
| **Webhook** | `/webhook/notify` |
| **متغير البيئة** | `VITE_N8N_NOTIFY_WEBHOOK` |

### أين يُشغَّل؟ / Where is it triggered?
كل نماذج الموقع — `triggerNotify()` في `src/api/siteApi.js` (fire-and-forget)
All website forms — called from `triggerNotify()` in `siteApi.js`

### التدفق الكامل / Full Flow

```
[Website Form Submit]
     ↓ POST → /webhook/notify
     ↓ Body: { type, name, email, phone, company, ... }

[Parse + Build Emails — Code Node]
     ↓ يولد HTML للإيميلين / Generates both email HTMLs
     ↓ adminEmailHtml (dark theme) + autoReplyHtml (light theme)

[Gmail — Send Admin Email]
     ↓ To: ziyadasystem@gmail.com
     ↓ Subject: "Ziyada System | [type] — [name]"

[Has Email? — IF node]
     ├── نعم / Yes → Gmail: Send Auto-Reply to visitor
     └── لا / No  → End
```

### تصميم البريد / Email Design
- **Admin email:** خلفية داكنة `#0a0f1e`، شعار Z بـ SVG، بدون صور خارجية، max-width 520px
- **Auto-reply:** خلفية فاتحة `#f1f5f9`، عربي + إنجليزي، 3 خطوات أفقية compact
- **Mobile-first:** viewport meta tag, 520px max-width, padding محكوم 16px/8px

---

## 5. رصد المنافسين — Competitor Intelligence Scraper

| | |
|---|---|
| **الاسم / Name** | Thmanyah Intelligence Scraper + Email Digest |
| **الـ ID** | `l0zGF9ZrD8Tl1F4f` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/l0zGF9ZrD8Tl1F4f |
| **الحالة / Status** | ✅ نشط / Active |
| **المودل / Model** | `google/gemini-2.0-flash-001` via OpenRouter *(محدّث)* |

### أين يُشغَّل؟ / Where is it triggered?
**صفحة لوحة المنافسين** → `/admin/competitor`
**Competitor Dashboard** → `src/admin/pages/CompetitorDashboard.jsx`
> أيضاً يعمل تلقائياً كل 48 ساعة / Also runs automatically every 48 hours
> زر "بدء الرصد" يرسل لـ: `VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK`

### التدفق الكامل / Full Flow

```
[لوحة التحكم / Admin Dashboard — CompetitorDashboard.jsx]
     ↓ POST → VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK (/webhook/trigger-scrape)
     (أو Schedule Trigger كل 48 ساعة / or auto every 48h)

[Firecrawl — Scrape Thmanyah Articles]
     ↓ يجمع مقالات ثمانية / Scrapes Thmanyah articles

[Apify — Social Scrapers]
     ├── Instagram Scraper
     ├── TikTok Scraper
     └── YouTube Scraper

[Merge All Sources]
     ↓ يدمج كل المصادر / Merges all data

[OpenRouter — Analyze Thmanyah Content]
     ↓ google/gemini-2.0-flash-001
     ↓ يحلل المحتوى ويستخرج رؤى / Analyzes content

[Supabase — Insert Intel]
     ↓ يحفظ التحليل / Saves analysis
     ↓ Table: competitor_intel

[OpenRouter — Generate Content Suggestions]
     ↓ google/gemini-2.0-flash-001
     ↓ يقترح محتوى ردًا على المنافسين / Suggests counter-content

[Supabase — Insert Suggestions]
     ↓ Table: content_suggestions

[Gmail — Send Digest Email]
     ↓ يرسل ملخص أسبوعي / Sends weekly digest email
```

---

## 6. توليد المحتوى — Content Generator

| | |
|---|---|
| **الاسم / Name** | On-Demand Content Generator |
| **الـ ID** | `t6BKcMIadX9in9GM` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/t6BKcMIadX9in9GM |
| **الحالة / Status** | ✅ نشط / Active |
| **المودل / Model** | `google/gemini-2.0-flash-001` via OpenRouter *(محدّث)* |

### أين يُشغَّل؟ / Where is it triggered?
**صفحة لوحة المنافسين** → `/admin/competitor`
زر "توليد محتوى" → `VITE_N8N_COMPETITOR_GENERATE_WEBHOOK`

### التدفق الكامل / Full Flow

```
[CompetitorDashboard.jsx]
     ↓ POST → VITE_N8N_COMPETITOR_GENERATE_WEBHOOK (/webhook/competitor-generate)
     ↓ Body: { intel_id, platform }

[Supabase — Get Intel Record]
     ↓ يجيب سجل التحليل المطلوب / Fetches intel record

[Extract Intel + Platform]
     ↓ يحضّر السياق / Prepares context

[OpenRouter — Generate Platform Content]
     ↓ google/gemini-2.0-flash-001
     ↓ يولّد محتوى مخصص للمنصة (مدونة، تيك توك، إنستغرام..)
     ↓ Generates platform-specific content (blog, TikTok, Instagram...)

[Parse AI Response]
     ↓ يحلل الرد / Parses response

[Supabase — Insert Suggestion]
     ↓ يحفظ الاقتراح / Saves suggestion
     ↓ Table: content_suggestions

[Respond to Webhook]
     ↓ يرسل المحتوى للواجهة / Returns content to frontend
```

---

## 7. نشر مقالات المدونة — Blog Draft Publisher

| | |
|---|---|
| **الاسم / Name** | Blog Draft Publisher |
| **الـ ID** | `7g61zvLQhMyAXxO0` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/7g61zvLQhMyAXxO0 |
| **الحالة / Status** | ✅ نشط / Active |
| **المودل / Model** | لا يستخدم AI — No AI (عمليات Supabase فقط) |

### أين يُشغَّل؟ / Where is it triggered?
**صفحة لوحة المنافسين** → `/admin/competitor`
زر "نشر المقال" → `VITE_N8N_BLOG_PUBLISHER_WEBHOOK`

### التدفق الكامل / Full Flow

```
[CompetitorDashboard.jsx]
     ↓ POST → VITE_N8N_BLOG_PUBLISHER_WEBHOOK (/webhook/publish-blog-draft)
     ↓ Body: { suggestion_id }

[Supabase — Get Suggestion]
     ↓ يجيب مقترح المحتوى / Fetches content suggestion

[Map to Blog Post Schema]
     ↓ يحوّل البيانات لصيغة المدونة / Maps to blog post format

[Supabase — Insert Blog Post]
     ↓ ينشر المقال / Publishes post
     ↓ Table: blog_posts

[Supabase — Update Suggestion Status]
     ↓ يحدث حالة الاقتراح → "published"

[Respond to Webhook]
     ↓ { success: true, blog_post_id }
     ↓ يظهر المقال في الموقع / Post appears on website
```

---

## 8. محرك كتابة المحتوى — Ali Content Writer Engine

| | |
|---|---|
| **الاسم / Name** | Ali Content Writer Engine 2026 |
| **الـ ID** | `C8JWsE3KIoxr1KgO` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/C8JWsE3KIoxr1KgO |
| **الحالة / Status** | ✅ نشط / Active |
| **المودل / Model** | `google/gemini-2.0-flash-001` via OpenRouter *(محدّث)* |

### أين يُشغَّل؟ / Where is it triggered?
- **Webhook** → `/webhook/ziyada-blog-ingest` (يُشغَّل من لوحة التحكم)
- **Telegram Bot** → رسائل تيليجرام مباشرة / Direct Telegram messages
- **جدول زمني / Schedule** → استطلاع Google Sheets / Google Sheets polling

### التدفق الكامل / Full Flow

```
[3 مصادر تشغيل / 3 Trigger Sources]
     ├── Webhook → من لوحة التحكم / from admin panel
     ├── Telegram → رسائل مباشرة / direct messages
     └── Schedule → Google Sheets polling

[Normalize & Prepare Input]
     ↓ يوحّد البيانات الواردة / Normalizes input

[Apify — Market Intelligence]
     ↓ يجمع بيانات السوق / Gathers market data

[OpenRouter — Generate Content]
     ↓ google/gemini-2.0-flash-001
     ↓ يكتب المقال بالكامل / Writes full article

[Google Sheets — Log & Track]
     ↓ يسجّل في جداول البيانات / Logs to spreadsheets

[Approval Gate]
     ├── موافق → Publish to Site (Supabase)
     └── قيد المراجعة → Draft Email Notification

[Telegram — Run Summary]
     ↓ يرسل ملخص العملية / Sends run summary
```

---

## 9. ذكاء إشارات السوق — Niche Signal Intelligence

| | |
|---|---|
| **الاسم / Name** | Niche Signal Intelligence Workflow |
| **الـ ID** | `62MN6oqxOs3levjh` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/62MN6oqxOs3levjh |
| **الحالة / Status** | ✅ نشط / Active |
| **المودل / Model** | `google/gemini-2.0-flash-001` via OpenRouter *(محدّث من gpt-4o)* |

### أين يُشغَّل؟ / Where is it triggered?
**لوحة اتجاهات يوتيوب** → `src/pages/YouTubeTrendsDashboard.jsx`
> متغير البيئة: `VITE_N8N_NSI_WEBHOOK`

### التدفق الكامل / Full Flow

```
[YouTubeTrendsDashboard.jsx]
     ↓ POST → VITE_N8N_NSI_WEBHOOK

[LangChain AI Agent]
     ↓ OpenRouter LLM (google/gemini-2.0-flash-001)
     ↓ Window Buffer Memory

     └── [youtube_search tool]
              ↓ يستدعي YouTube Search Sub-workflow
              ↓ Calls YouTube Search Sub-workflow (INHDUWqaC4WMae1R)
              ↓ يبحث عن مقاطع ذات صلة / Searches for relevant videos

[Response → Frontend Dashboard]
     ↓ يعرض الاتجاهات والرؤى / Displays trends and insights
```

---

## 10. بحث يوتيوب — YouTube Search

| | |
|---|---|
| **الاسم / Name** | Youtube Search Workflow |
| **الـ ID** | `INHDUWqaC4WMae1R` |
| **رابط n8n** | https://n8n.srv953562.hstgr.cloud/workflow/INHDUWqaC4WMae1R |
| **الحالة / Status** | ✅ نشط / Active |
| **نوع التشغيل / Trigger Type** | Sub-workflow (يُشغَّل من NSI Workflow) |

### التدفق / Flow
```
[NSI Workflow — youtube_search tool]
     ↓ يرسل كلمات البحث / Sends search terms

[YouTube API Search]
     ↓ يبحث في يوتيوب / Searches YouTube

[Process & Return Results]
     ↓ يرجع النتائج للـ NSI Agent / Returns results to NSI Agent
```

---

## 11. Google Meet Booking (مخطط / PLANNED)

| | |
|---|---|
| **الاسم / Name** | Ziyada - Google Meet Booking |
| **الـ ID** | غير موجود بعد / Not built yet |
| **الحالة / Status** | 📋 مخطط / Planned |
| **Webhook** | `/webhook/google-meet` |
| **متغير البيئة** | `VITE_N8N_GOOGLE_MEET_WEBHOOK` |

### التدفق المخطط / Planned Flow

```
[bookMeeting() → triggerGoogleMeetWebhook(record)]
     ↓ POST → /webhook/google-meet

[Parse Booking Data]
     ↓ name, email, phone, date, time

[Google Calendar API — Create Event]
     ↓ يضيف حدث مع رابط Google Meet
     ↓ Creates event with Google Meet link
     ↓ Attendees: visitor + ali@ziyadasystem.com

[Gmail — Send Meet Link to Visitor]
     ↓ يرسل رابط الاجتماع للعميل

[Supabase — Update Booking]
     ↓ يضيف google_meet_link في سجل الحجز
     ↓ UPDATE bookings SET google_meet_link = '...'

[Owner (Ali)]
     ↓ يستقبل دعوة Google Calendar → Accept/Decline
```

### متطلبات قبل البناء / Requirements Before Building
1. ربط Google Calendar OAuth2 في N8N Credentials
2. بناء الـ Workflow في N8N
3. إضافة استدعاء `triggerGoogleMeetWebhook()` داخل `bookMeeting()` في `siteApi.js`
4. إضافة حقل `google_meet_link` في جدول `bookings` في Supabase (إذا لم يكن موجوداً)

---

## ملخص تقني — Technical Summary

### Credentials المستخدمة / Credentials Used

| الاسم | الـ ID | الاستخدام |
|-------|--------|-----------|
| OpenRouter API | `DYFykyrsbJl8iJ3P` | HTTP Request nodes |
| OpenRouter (LangChain) | `F8sNj28huRqUSirF` | LangChain LLM nodes |
| APIFY KEY | `tl4E4rvmbIAT5gIL` | Apify scrapers |
| Google Sheets OAuth | `7Y66oaiIkiRR8O2Q` | Google Sheets |
| Gmail OAuth | `z7EaXOPymX2CUhPa` | Email digest + Notify + Auto-reply |
| Telegram API | `PtelPKshJLRYXIvR` | Telegram bot |
| HubSpot Private App | In `.env` as `HUBSPOT_PRIVATE_APP_TOKEN` | HubSpot Sync workflow |
| Supabase Service Role | In `.env` as `SUPABASE_SERVICE_ROLE_KEY` | integration_logs writes |

### متغيرات البيئة — Environment Variables

| المتغير | الـ Workflow | الصفحة | الحالة |
|---------|------------|--------|--------|
| `VITE_CHATBOT_WEBHOOK` | Chat Agent | كل الصفحات | ✅ Active |
| `VITE_N8N_HUBSPOT_SYNC_WEBHOOK` | HubSpot Sync | كل النماذج | ✅ Active |
| `VITE_N8N_NOTIFY_WEBHOOK` | Admin Notify | كل النماذج | ✅ Active |
| `VITE_N8N_GOOGLE_MEET_WEBHOOK` | Google Meet | BookMeeting | 📋 Planned |
| `VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK` | Thmanyah Scraper | `/admin/competitor` | ✅ Active |
| `VITE_N8N_COMPETITOR_GENERATE_WEBHOOK` | Content Generator | `/admin/competitor` | ✅ Active |
| `VITE_N8N_BLOG_PUBLISHER_WEBHOOK` | Blog Publisher | `/admin/competitor` | ✅ Active |
| `VITE_N8N_NSI_WEBHOOK` | NSI Workflow | `/youtube-trends` | ✅ Active |

### حالة جميع الـ Workflows — All Workflow Status

| الـ Workflow | الـ ID | الحالة |
|------------|--------|--------|
| Ziyada Chat Agent | `4wO4enlPyFeNduqY` | ✅ Active |
| Chat Lead Capture | `ImrkLJa5mO7TvJmk` | ✅ Active |
| **HubSpot Sync** | `1w96DpTzTGxaIlPW` | ✅ Active (rebuilt Apr 10) |
| **Admin Notify + Auto-Reply** | `pw6WYm4N36SXHNl6` | ✅ Active (rebuilt Apr 10) |
| Thmanyah Scraper | `l0zGF9ZrD8Tl1F4f` | ✅ Active |
| Content Generator | `t6BKcMIadX9in9GM` | ✅ Active |
| Blog Publisher | `7g61zvLQhMyAXxO0` | ✅ Active |
| Ali Content Writer | `C8JWsE3KIoxr1KgO` | ✅ Active |
| NSI Workflow | `62MN6oqxOs3levjh` | ✅ Active |
| YouTube Search | `INHDUWqaC4WMae1R` | ✅ Active |
| **Google Meet Booking** | — | 📋 Planned |

---

*نظام زيادة — نبنيلك نظام مبيعات يشتغل وأنت نايم*
*Ziyada System — We build you a sales system that works while you sleep*
