# Ziyada System - User Manual / دليل المستخدم

---

<div dir="rtl" align="right">

# القسم العربي

## دليل مستخدم نظام زيادة

---

### 1. نظرة عامة على النظام

نظام زيادة هو تطبيق ويب أحادي الصفحة (SPA) ثنائي اللغة (عربي/إنجليزي) مبني بتقنية React، مصمم لوكالة تسويق رقمي وأتمتة. يتضمن النظام المكونات الرئيسية التالية:

- **واجهة أمامية ثنائية اللغة**: تطبيق React أحادي الصفحة يدعم اللغتين العربية والإنجليزية مع إمكانية التبديل بين المظهر الداكن والفاتح.
- **الواجهة الخلفية (Supabase)**: قاعدة بيانات ونظام مصادقة مستضاف على Supabase.
- **أتمتة سير العمل (n8n)**: يتضمن روبوت المحادثة، وإشعارات البريد الإلكتروني، ومزامنة HubSpot، ونشر المدونة تلقائيًا.
- **التحليلات**: Google Analytics 4 (GA4)، وPostHog (تسجيل الجلسات ومسارات التحويل)، وHotjar/Contentsquare (خرائط الحرارة وتسجيل الجلسات).
- **لوحة الإدارة**: متاحة على المسار `/admin` ومحمية بنظام مصادقة Supabase Auth.

---

### 2. دليل لوحة الإدارة

#### تسجيل الدخول
انتقل إلى `/admin/login` وأدخل البريد الإلكتروني وكلمة المرور للوصول إلى لوحة الإدارة.

#### لوحة المعلومات (Dashboard)
تعرض إحصائيات عامة تشمل عدد العملاء المحتملين، والحجوزات، والمشتركين، ومقالات المدونة. كما تعرض العناصر الأخيرة ومساعد المحادثة بالذكاء الاصطناعي.

#### إدارة العملاء المحتملين (Leads Manager)
- عرض جميع العملاء المحتملين.
- التصفية حسب الحالة أو الخدمة.
- تغيير الحالة: جديد ← تم التواصل ← مؤهل ← محوّل ← مفقود.
- تصدير البيانات بصيغة CSV.

#### إدارة الحجوزات (Bookings Manager)
- عرض حجوزات الاجتماعات.
- التصفية حسب الحالة.
- إدارة جدولة المواعيد.

#### إدارة المدونة (Blog Manager)
- عرض جميع المقالات.
- التبديل بين حالة النشر والمسودة.
- إنشاء مقالات جديدة.

#### محرر المدونة (Blog Editor)
تصميم بعمودين: نموذج الإدخال على اليسار ومعاينة حية على اليمين. يدعم صيغة Markdown. زر "التوليد بالذكاء الاصطناعي" يرسل الموضوع إلى سير عمل n8n لتوليد مسودة تلقائية.

#### إدارة دراسات الحالة (Cases Manager)
إدارة دراسات الحالة بما في ذلك اسم العميل، والقطاع، والنتائج، والصورة.

#### إدارة الأسئلة الشائعة (FAQ Manager)
إضافة وتعديل وحذف الأسئلة الشائعة مع إمكانية السحب والإفلات لإعادة الترتيب.

#### إدارة الخدمات (Services Manager)
تعديل محتوى صفحات الخدمات.

#### إدارة المشتركين (Subscribers Manager)
عرض مشتركي النشرة البريدية مع إمكانية تصدير البيانات بصيغة CSV.

#### ملخص التحليلات (Analytics Summary)
روابط مباشرة إلى لوحات معلومات GA4 وPostHog وHotjar بالإضافة إلى مقاييس Supabase.

#### الإعدادات (Settings)
معلومات الشركة، وروابط التواصل الاجتماعي، ومفاتيح API للتكاملات، وإدارة مستخدمي الإدارة.

#### ذكاء الاتجاهات (Trend Intelligence)
لوحة معلومات لتحليل اتجاهات YouTube والسوق المتخصص.

---

### 3. إدارة المدونة

- **الإنشاء**: انتقل إلى `/admin` ثم المدونة ثم مقال جديد.
- **تعبئة الحقول**: العنوان، والرابط المختصر (slug)، والملخص، والمحتوى (بصيغة Markdown)، والتصنيف، والوسوم، ورابط صورة الغلاف، وحقول تحسين محركات البحث (SEO).
- **المعاينة**: تعرض المعاينة الحية شكل المقال كما سيظهر على الموقع العام.
- **النشر**: تبديل حالة المقال في قائمة المدونة.
- **التوليد بالذكاء الاصطناعي**: انقر على "التوليد بالذكاء الاصطناعي" ثم أدخل الموضوع وسيقوم سير عمل n8n بتوليد مسودة تلقائيًا.
- **الرابط العام**: تظهر المقالات على المسار `/blog/{slug}`.
- **النشر التلقائي عبر n8n**: يمكن للأدوات الخارجية نشر المقالات عبر نقطة نهاية API.

---

### 4. إدارة العملاء المحتملين والحجوزات

- جميع نماذج الإرسال (التواصل، وطلب العرض، وحجز الاجتماع) تُحفظ في Supabase.
- يتم التقاط معاملات UTM تلقائيًا لتتبع مصادر التسويق.
- حماية من الرسائل العشوائية عبر نظام Honeypot وتحديد معدل الإرسال.
- مسار الحالة: جديد ← تم التواصل ← مؤهل ← محوّل / مفقود.
- إرسال إشعار بالبريد الإلكتروني إلى ziyadasystem@gmail.com عند كل إرسال نموذج.
- إنشاء أو تحديث جهة اتصال في HubSpot تلقائيًا عبر n8n.

---

### 5. مسار إرسال النماذج

```
يرسل المستخدم النموذج ← فحص Honeypot ← فحص تحديد المعدل ← إدراج في Supabase
  ← تشغيل webhook في n8n ← إشعار بالبريد الإلكتروني ← مزامنة HubSpot
  ← تخزين hubspot_contact_id في Supabase
```

---

### 6. التحليلات والتتبع

- **GA4**: مشاهدات الصفحات وأحداث مخصصة (form_start، form_submit، cta_click، service_view، blog_read، conversion).
- **PostHog**: تسجيل الجلسات، وتحديد هوية المستخدم عند إرسال النموذج، وتتبع مسارات التحويل.
- **Hotjar/Contentsquare**: خرائط الحرارة وتسجيل الجلسات.
- **تتبع UTM**: يتم التقاط جميع معاملات utm_source وutm_medium وutm_campaign وutm_content من الروابط وإرفاقها بالنماذج المرسلة.
- **الإعداد**: أضف معرف قياس GA4 الحقيقي في متغير VITE_GA4_ID في ملف `.env.local` عند توفره.

---

### 7. تكامل HubSpot

- يتم التكامل تلقائيًا عبر سير عمل n8n: إرسال النموذج ← إنشاء أو تحديث جهة الاتصال.
- الخصائص المتزامنة: الخدمة المطلوبة، والميزانية، والجدول الزمني، وصفحة المصدر، واللغة، ومعاملات UTM.
- راجع ملف `docs/HUBSPOT_INTEGRATION.md` للحصول على تفاصيل الإعداد الكاملة.

---

### 8. سير عمل n8n

- **روبوت المحادثة**: webhook على VITE_CHATBOT_WEBHOOK، يستخدم نموذج Gemini Flash 2.0.
- **ذكاء الاتجاهات**: webhook على VITE_N8N_NSI_WEBHOOK، تحليل YouTube والسوق المتخصص.
- **مزامنة HubSpot**: يتم تشغيله عبر webhook من Supabase عند إدراج عميل محتمل أو حجز.
- **إشعارات البريد الإلكتروني**: إرسال بريد إلكتروني عند إرسال النماذج.
- **نشر المدونة**: نقطة نهاية API لإنشاء مقالات المدونة تلقائيًا.
- **مثيل n8n**: https://n8n.srv953562.hstgr.cloud

---

### 9. تحديث المحتوى

- **الأسئلة الشائعة**: لوحة الإدارة > الأسئلة الشائعة > إضافة / تعديل / حذف مع السحب لإعادة الترتيب.
- **الخدمات**: لوحة الإدارة > الخدمات > تعديل المحتوى.
- **دراسات الحالة**: لوحة الإدارة > دراسات الحالة > إضافة / تعديل / حذف.
- **المدونة**: لوحة الإدارة > المدونة > مقال جديد أو تعديل مقال موجود.

---

### 10. متغيرات البيئة

| المتغير | الوصف |
|---------|-------|
| VITE_SUPABASE_URL | رابط مشروع Supabase |
| VITE_SUPABASE_ANON_KEY | المفتاح المجهول لـ Supabase |
| VITE_CHATBOT_WEBHOOK | مسار webhook لروبوت المحادثة في n8n |
| VITE_CHATBOT_ENABLED | تفعيل أو تعطيل أداة المحادثة |
| VITE_N8N_NSI_WEBHOOK | مسار webhook لذكاء الاتجاهات في n8n |
| VITE_GA4_ID | معرف قياس Google Analytics 4 |
| VITE_POSTHOG_KEY | مفتاح API لمشروع PostHog |
| VITE_HOTJAR_ID | معرف موقع Hotjar/Contentsquare |
| VITE_META_PIXEL_ID | معرف بكسل Meta/Facebook |

---

### 11. روابط لوحات المعلومات والأدوات

| الأداة | الرابط |
|--------|--------|
| Supabase | https://supabase.com/dashboard/project/nuyscajjlhxviuyrxzyq |
| n8n | https://n8n.srv953562.hstgr.cloud |
| PostHog | https://us.posthog.com |
| GA4 | https://analytics.google.com (الحساب: 389924895) |
| HubSpot | https://app.hubspot.com |
| Vercel | https://vercel.com (بعد النشر) |

---

### 12. استكشاف الأخطاء وإصلاحها

- **النماذج لا تُرسل**: تحقق من اتصال Supabase (راجع وحدة تحكم المتصفح للأخطاء)، وتأكد من أن سياسات أمان الصفوف (RLS) تسمح بعملية INSERT.
- **المحادثة لا تعمل**: تأكد من أن VITE_CHATBOT_ENABLED=true، وتحقق من أن سير عمل n8n نشط.
- **فشل تسجيل الدخول للإدارة**: تأكد من وجود مستخدم في Supabase Auth بالبريد الإلكتروني وكلمة المرور الصحيحين.
- **التحليلات لا تعمل**: تأكد من أن متغيرات البيئة تحتوي على معرفات حقيقية (وليست عناصر نائبة تحتوي على XXXXXXXXXX).
- **مقالات المدونة لا تظهر**: تأكد من أن المقال منشور (status=published) في لوحة الإدارة.
- **فشل البناء**: شغّل `npm run lint` للتحقق من الأخطاء، وتأكد من أن جميع الاستيرادات صحيحة.

---

### 13. إجراءات الإعداد الأولية للمالك (مرة واحدة)

1. شغّل ملف `supabase-schema.sql` في محرر SQL في Supabase (ينشئ جميع الجداول والسياسات والدوال).
2. أنشئ مستخدم الإدارة الأول: Supabase > Authentication > إضافة مستخدم (بريد إلكتروني + كلمة مرور).
3. عيّن دور المستخدم: حدّث جدول `profiles` واضبط حقل `role` على القيمة `owner` لمستخدمك.
4. اشترِ نطاقًا وقم بتهيئة DNS (سجل CNAME يشير إلى Vercel).
5. انشر على Vercel واضبط متغيرات البيئة.
6. أعدّ سير عمل HubSpot في n8n (راجع `docs/HUBSPOT_INTEGRATION.md`).
7. أضف معرف قياس GA4 إلى متغيرات البيئة عندما يصبح النطاق مباشرًا.
8. راجع وحدّث ملف `og-image.png` بتصميم يحمل هوية العلامة التجارية.

---

</div>

---

# English Section

## Ziyada System User Manual

---

### 1. System Overview

Ziyada System is a bilingual (Arabic/English) React single-page application (SPA) built for a digital marketing and automation agency. The system comprises the following core components:

- **Bilingual Frontend**: React SPA supporting Arabic and English with dark/light theme toggling.
- **Backend (Supabase)**: Database and authentication hosted on Supabase.
- **Workflow Automation (n8n)**: Chat bot, email notifications, HubSpot sync, and blog publishing.
- **Analytics**: Google Analytics 4 (GA4), PostHog (session recording + funnels), Hotjar/Contentsquare (heatmaps + session recordings).
- **Admin Panel**: Available at `/admin`, protected by Supabase Auth.

---

### 2. Admin Panel Guide

#### Login
Navigate to `/admin/login` and enter your email and password to access the admin panel.

#### Dashboard
Displays overview stats including leads, bookings, subscribers, and blog posts. Also shows recent items and an AI chat assistant.

#### Leads Manager
- View all leads.
- Filter by status or service.
- Change status: new → contacted → qualified → converted → lost.
- Export data as CSV.

#### Bookings Manager
- View meeting bookings.
- Filter by status.
- Manage scheduling.

#### Blog Manager
- View all posts.
- Toggle publish/draft status.
- Create new posts.

#### Blog Editor
Two-column layout: form on the left, live preview on the right. Supports markdown. The "Generate with AI" button sends the topic to an n8n workflow to generate a draft automatically.

#### Cases Manager
Manage case studies including client name, industry, results, and image.

#### FAQ Manager
Add, edit, and delete FAQs with drag-and-drop reordering.

#### Services Manager
Edit service page content.

#### Subscribers Manager
View newsletter subscribers and export data as CSV.

#### Analytics Summary
Direct links to GA4, PostHog, and Hotjar dashboards plus Supabase metrics.

#### Settings
Company info, social links, integration API keys, and admin user management.

#### Trend Intelligence
YouTube and niche trend analysis dashboard.

---

### 3. Blog Management

- **Create**: Navigate to `/admin` → Blog → New Post.
- **Fill in fields**: Title, slug, excerpt, body (markdown), category, tags, cover image URL, SEO fields.
- **Preview**: The live preview shows how the post will appear on the public site.
- **Publish**: Toggle status in the blog list.
- **AI Generation**: Click "Generate with AI" → enter topic → n8n workflow generates a draft.
- **Public URL**: Posts appear at `/blog/{slug}`.
- **n8n Auto-Publishing**: External tools can publish via API endpoint.

---

### 4. Lead & Booking Management

- All form submissions (Contact, Request Proposal, Book Meeting) go to Supabase.
- UTM parameters are captured automatically for marketing attribution.
- Honeypot and rate limiting prevent spam.
- Status pipeline: new → contacted → qualified → converted / lost.
- Email notification sent to ziyadasystem@gmail.com on each submission.
- HubSpot contact created/updated automatically via n8n.

---

### 5. Form Submission Flow

```
User submits form → Honeypot check → Rate limit check → Supabase INSERT
  → n8n webhook fires → Email notification → HubSpot sync
  → hubspot_contact_id stored back in Supabase
```

---

### 6. Analytics & Tracking

- **GA4**: Pageviews + custom events (form_start, form_submit, cta_click, service_view, blog_read, conversion).
- **PostHog**: Session recording, user identification on form submit, funnel tracking.
- **Hotjar/Contentsquare**: Heatmaps, session recordings.
- **UTM Tracking**: All utm_source, utm_medium, utm_campaign, utm_content params are captured from URLs and attached to form submissions.
- **Setup**: Add real GA4 Measurement ID to VITE_GA4_ID in `.env.local` when available.

---

### 7. HubSpot Integration

- Automated via n8n workflow: form submission → contact creation/update.
- Custom properties synced: service interest, budget, timeline, source page, language, UTM params.
- See `docs/HUBSPOT_INTEGRATION.md` for detailed setup instructions.

---

### 8. n8n Workflows

- **Chat Bot**: Webhook at VITE_CHATBOT_WEBHOOK, uses Gemini Flash 2.0.
- **Trend Intelligence**: Webhook at VITE_N8N_NSI_WEBHOOK, YouTube/niche analysis.
- **HubSpot Sync**: Triggered by Supabase webhook on lead/booking insert.
- **Email Notifications**: Sends email on form submissions.
- **Blog Publishing**: API endpoint for automated blog post creation.
- **n8n instance**: https://n8n.srv953562.hstgr.cloud

---

### 9. Content Updates

- **FAQ**: Admin → FAQ → Add / Edit / Delete, drag to reorder.
- **Services**: Admin → Services → Edit content.
- **Case Studies**: Admin → Cases → Add / Edit / Delete.
- **Blog**: Admin → Blog → New Post or Edit existing.

---

### 10. Environment Variables

| Variable | Description |
|----------|-------------|
| VITE_SUPABASE_URL | Supabase project URL |
| VITE_SUPABASE_ANON_KEY | Supabase anonymous key |
| VITE_CHATBOT_WEBHOOK | n8n chat bot webhook path |
| VITE_CHATBOT_ENABLED | Enable/disable chat widget |
| VITE_N8N_NSI_WEBHOOK | n8n trend intelligence webhook |
| VITE_GA4_ID | Google Analytics 4 Measurement ID |
| VITE_POSTHOG_KEY | PostHog project API key |
| VITE_HOTJAR_ID | Hotjar/Contentsquare site ID |
| VITE_META_PIXEL_ID | Meta/Facebook Pixel ID |

---

### 11. Dashboard & Tool Links

| Tool | URL |
|------|-----|
| Supabase | https://supabase.com/dashboard/project/nuyscajjlhxviuyrxzyq |
| n8n | https://n8n.srv953562.hstgr.cloud |
| PostHog | https://us.posthog.com |
| GA4 | https://analytics.google.com (Account: 389924895) |
| HubSpot | https://app.hubspot.com |
| Vercel | https://vercel.com (after deployment) |

---

### 12. Troubleshooting

- **Forms not submitting**: Check Supabase connection (browser console for errors), verify RLS policies allow INSERT.
- **Chat not working**: Verify VITE_CHATBOT_ENABLED=true, check n8n workflow is active.
- **Admin login fails**: Verify Supabase Auth user exists with correct email/password.
- **Analytics not tracking**: Check env vars have real IDs (not placeholders with XXXXXXXXXX).
- **Blog posts not showing**: Verify post is published (status=published) in admin.
- **Build fails**: Run `npm run lint` to check for errors, ensure all imports resolve.

---

### 13. Owner Setup Actions (One-Time)

1. Run `supabase-schema.sql` in Supabase SQL Editor (creates all tables, policies, functions).
2. Create initial admin user: Supabase → Authentication → Add User (email + password).
3. Set user role: Update `profiles` table, set `role` to `owner` for your user.
4. Purchase domain and configure DNS (CNAME to Vercel).
5. Deploy to Vercel and set environment variables.
6. Set up n8n HubSpot workflow (see `docs/HUBSPOT_INTEGRATION.md`).
7. Add GA4 Measurement ID to env vars when domain is live.
8. Review and update `og-image.png` with branded design.
