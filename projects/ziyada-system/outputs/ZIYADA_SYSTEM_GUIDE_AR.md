<!--
  دليل نظام زيادة الشامل — Ziyada System Complete Guide
  الإصدار: 1.0 | التاريخ: أبريل 2026
  ألوان العلامة التجارية: #2563eb (أساسي) | #3b82f6 (ثانوي)
  خط عربي: Noto Kufi Arabic | اتجاه: RTL

  تعليمات النسخ إلى Google Docs:
  1. حدد كل المحتوى (Ctrl+A)
  2. انسخ (Ctrl+C)
  3. افتح مستند Google Docs جديد
  4. الصق (Ctrl+V)
  5. عدّل العناوين الرئيسية بلون #2563eb
  6. اضبط المحاذاة إلى RTL من Format > Text > Right-to-left
-->

---

# دليل نظام زيادة الشامل

**Ziyada System Complete Guide**

---

**الإصدار:** 1.0
**التاريخ:** أبريل 2026
**الحالة:** وثيقة تقنية وتشغيلية شاملة
**السرية:** داخلي — فريق زيادة سيستم فقط

---

## جدول المحتويات

1. نظرة عامة على المشروع
2. الهيكل التقني
3. لوحة التحكم (Admin Panel)
4. النماذج والأمان
5. تكامل HubSpot
6. نظام المدونة
7. التحليلات
8. ويدجت المحادثة الذكية
9. استخبارات المنافسين
10. رصد التوجهات
11. النشر والاستضافة
12. الدومين والإيميل
13. قائمة المهام بعد الإطلاق
14. بيانات الوصول
15. الملحقات

---

## 1. نظرة عامة على المشروع

### ما هو نظام زيادة؟

نظام زيادة هو منصة رقمية متكاملة تم بناؤها لتقديم خدمات التسويق الرقمي والأتمتة للشركات السعودية. المنصة تجمع بين موقع إلكتروني احترافي ثنائي اللغة (عربي/إنجليزي)، لوحة تحكم إدارية متقدمة، ونظام أتمتة ذكي يعمل بتقنيات الذكاء الاصطناعي.

### الأهداف الرئيسية

- **توليد العملاء المحتملين** (Lead Generation): نماذج ذكية مع تتبع UTM وحماية ضد السبام
- **أتمتة العمليات**: ربط تلقائي مع HubSpot وأنظمة البريد الإلكتروني عبر n8n
- **إدارة المحتوى**: نظام مدونة متكامل مع SEO وروابط نظيفة
- **ذكاء تنافسي**: رصد وتحليل محتوى المنافسين بشكل آلي
- **تحليلات متقدمة**: تكامل مع GA4 وPostHog وHotjar

### المكونات التقنية الرئيسية

| المكون | التقنية | الوصف |
|--------|---------|-------|
| الواجهة الأمامية | React 18 + Vite 6 | تطبيق SPA ثنائي اللغة |
| قاعدة البيانات | Supabase (PostgreSQL) | بيانات، مصادقة، سياسات أمان RLS |
| الأتمتة | n8n | سير عمل آلي (Chat, HubSpot, Competitor Intel) |
| الاستضافة | Vercel | CDN, SSL, Edge Network |
| التحليلات | GA4, PostHog, Hotjar | تتبع شامل لسلوك المستخدم |

---

## 2. الهيكل التقني

### 2.1 هيكل المشروع (Project Structure)

```
ziyada-system-website/
├── src/
│   ├── App.jsx                    # الموجه الرئيسي (Router)
│   ├── main.jsx                   # نقطة الدخول
│   ├── globals.css                # الأنماط العامة
│   ├── index.css                  # أنماط Tailwind
│   ├── pages.config.js            # إعدادات الصفحات
│   │
│   ├── api/
│   │   └── siteApi.js             # واجهة Supabase API الموحدة
│   │
│   ├── lib/
│   │   ├── supabase.js            # إعداد Supabase Client
│   │   ├── analytics.js           # تتبع GA4 + PostHog + Meta Pixel
│   │   ├── utm.js                 # التقاط معاملات UTM
│   │   ├── rateLimit.js           # تحديد معدل الإرسال (3 / 5 دقائق)
│   │   ├── validation.js          # التحقق من البيانات (Zod)
│   │   ├── useSEO.js              # Hook لإدارة SEO
│   │   ├── query-client.js        # إعداد React Query
│   │   └── utils.js               # أدوات مساعدة (cn, clsx)
│   │
│   ├── components/
│   │   ├── ui/                    # مكونات shadcn/ui
│   │   │   └── floating-chat-widget.jsx  # ويدجت المحادثة الذكية
│   │   └── ziyada/                # مكونات خاصة بزيادة
│   │       ├── Layout.jsx         # التخطيط العام للموقع
│   │       ├── Navbar.jsx         # شريط التنقل
│   │       ├── Footer.jsx         # التذييل
│   │       ├── ThreeBackground.jsx # خلفية Three.js ثلاثية الأبعاد
│   │       ├── Analytics.jsx      # مكون التحليلات
│   │       ├── ROICalculator.jsx  # حاسبة العائد على الاستثمار
│   │       ├── GlassPanel.jsx     # تأثير الزجاج المعتم
│   │       ├── AnimatedServiceCard.jsx # بطاقة خدمة متحركة
│   │       ├── BrandIcons.jsx     # أيقونات العلامة التجارية
│   │       ├── ServiceDetailPage.jsx # صفحة تفاصيل الخدمة
│   │       ├── useScrollReveal.jsx # Hook للظهور عند التمرير
│   │       └── useTranslation.jsx # Hook للترجمة
│   │
│   ├── pages/                     # صفحات الموقع العامة
│   │   ├── Home.jsx               # الرئيسية
│   │   ├── Services.jsx           # الخدمات
│   │   ├── ServiceAutomation.jsx  # خدمة الأتمتة
│   │   ├── ServiceCRM.jsx         # خدمة CRM
│   │   ├── ServiceLeadGen.jsx     # خدمة توليد العملاء
│   │   ├── ServiceMarketing.jsx   # خدمة التسويق
│   │   ├── ServiceWebDev.jsx      # خدمة تطوير المواقع
│   │   ├── ServiceSocial.jsx      # خدمة السوشال ميديا
│   │   ├── About.jsx              # من نحن
│   │   ├── Why.jsx                # لماذا زيادة
│   │   ├── Cases.jsx              # دراسات الحالة
│   │   ├── Blog.jsx               # المدونة
│   │   ├── BlogPost.jsx           # صفحة المقال
│   │   ├── blogContent.jsx        # محتوى المدونة
│   │   ├── BookMeeting.jsx        # حجز اجتماع
│   │   ├── RequestProposal.jsx    # طلب عرض سعر
│   │   ├── Contact.jsx            # تواصل معنا
│   │   ├── FAQ.jsx                # الأسئلة الشائعة
│   │   ├── ThankYou.jsx           # شكراً لك
│   │   ├── Privacy.jsx            # سياسة الخصوصية
│   │   ├── Terms.jsx              # الشروط والأحكام
│   │   └── YouTubeTrendsDashboard.jsx # لوحة رصد التوجهات
│   │
│   ├── admin/                     # لوحة التحكم الإدارية
│   │   ├── AdminLayout.jsx        # تخطيط لوحة التحكم
│   │   ├── AdminLogin.jsx         # صفحة تسجيل الدخول
│   │   ├── AdminAuthProvider.jsx  # مزود المصادقة
│   │   ├── AdminAuthGuard.jsx     # حماية المسارات
│   │   ├── components/            # مكونات مشتركة
│   │   │   ├── DataTable.jsx      # جدول بيانات قابل للتصفية
│   │   │   ├── StatCard.jsx       # بطاقة إحصائيات
│   │   │   ├── StatusBadge.jsx    # شارة الحالة
│   │   │   ├── AdminSidebar.jsx   # القائمة الجانبية
│   │   │   └── AdminTopbar.jsx    # الشريط العلوي
│   │   └── pages/                 # صفحات لوحة التحكم (12 صفحة)
│   │       ├── DashboardHome.jsx
│   │       ├── LeadsManager.jsx
│   │       ├── BookingsManager.jsx
│   │       ├── BlogManager.jsx
│   │       ├── BlogEditor.jsx
│   │       ├── CasesManager.jsx
│   │       ├── FAQManager.jsx
│   │       ├── ServicesManager.jsx
│   │       ├── SubscribersManager.jsx
│   │       ├── AnalyticsSummary.jsx
│   │       ├── SettingsPanel.jsx
│   │       └── CompetitorDashboard.jsx
│   │
│   ├── hooks/                     # Custom React Hooks
│   └── utils/                     # أدوات إضافية
│
├── public/                        # ملفات ثابتة
├── dist/                          # مخرجات البناء
├── scripts/                       # سكريبتات مساعدة
│   └── generate-sitemap.mjs       # توليد Sitemap تلقائي
├── supabase-schema.sql            # مخطط قاعدة البيانات
├── vercel.json                    # إعدادات Vercel
├── vite.config.js                 # إعدادات Vite
├── tailwind.config.js             # إعدادات Tailwind
├── package.json                   # تبعيات المشروع
└── index.html                     # نقطة الدخول HTML
```

### 2.2 التقنيات المستخدمة (Tech Stack)

**الواجهة الأمامية (Frontend):**

| التقنية | الإصدار | الغرض |
|---------|---------|-------|
| React | 18.2 | مكتبة واجهة المستخدم |
| Vite | 6.1 | أداة البناء والتطوير |
| React Router DOM | 6.26 | التوجيه (Routing) |
| TanStack React Query | 5.84 | إدارة حالة الخادم والتخزين المؤقت |
| Tailwind CSS | 3.4 | أنماط CSS |
| shadcn/ui + Radix | متعدد | مكونات واجهة المستخدم |
| Framer Motion | 11.16 | حركات وانتقالات |
| Three.js | 0.171 | خلفية ثلاثية الأبعاد |
| Recharts | 2.15 | رسوم بيانية |
| Lucide React | 0.475 | أيقونات |
| Zod | 3.24 | التحقق من البيانات |
| React Markdown | 9.0 | عرض محتوى Markdown |
| date-fns | 3.6 | معالجة التواريخ |

**الخلفية (Backend):**

| التقنية | الغرض |
|---------|-------|
| Supabase | قاعدة بيانات PostgreSQL + مصادقة + تخزين |
| Supabase Auth | مصادقة المستخدمين (Email/Password) |
| Supabase RLS | سياسات أمان على مستوى الصفوف |
| n8n | أتمتة سير العمل (Webhooks) |

**الأتمتة (Automation - n8n):**

| سير العمل | الوظيفة | الجدولة |
|-----------|---------|---------|
| Chat Webhook | استقبال رسائل الشات بوت | عند الطلب (Webhook) |
| HubSpot Sync | مزامنة العملاء مع HubSpot | عند إدخال عميل جديد |
| Competitor Scraper | رصد محتوى المنافسين (Firecrawl + Apify) | كل 48 ساعة |
| Content Generator | توليد اقتراحات محتوى بالذكاء الاصطناعي | عند الطلب (Webhook) |
| Blog Publisher | نشر مسودة مدونة من اقتراح معتمد | عند الطلب (Webhook) |

**الاستضافة والبنية التحتية:**

| الخدمة | الغرض |
|--------|-------|
| Vercel | استضافة الموقع (CDN, SSL, Edge) |
| Hostinger VPS | استضافة n8n |
| Supabase Cloud | قاعدة البيانات والمصادقة |

### 2.3 واجهة API الموحدة (siteApi.js)

كل التعامل مع Supabase يتم عبر ملف واحد (`src/api/siteApi.js`) باستخدام نمط Entity Client Factory:

```javascript
// الكيانات المتاحة (Entities)
siteApi.entities.Lead          // جدول leads
siteApi.entities.Booking       // جدول bookings
siteApi.entities.BlogPost      // جدول blog_posts
siteApi.entities.CaseStudy     // جدول case_studies
siteApi.entities.Subscriber    // جدول subscribers
siteApi.entities.FAQItem       // جدول faq_items
siteApi.entities.Service       // جدول services
siteApi.entities.CompetitorIntel    // جدول competitor_intel
siteApi.entities.ContentSuggestion  // جدول content_suggestions

// العمليات المتاحة لكل كيان
entity.list(sort?, limit?, skip?)        // استعلام مع ترتيب وتصفح
entity.filter(criteria, sort?, limit?)   // تصفية حسب معايير
entity.get(id)                           // جلب سجل واحد
entity.create(payload)                   // إنشاء سجل جديد
entity.update(id, payload)               // تحديث سجل
entity.delete(id)                        // حذف سجل

// الدوال الخاصة (Functions)
siteApi.functions.invoke("submitLead", payload)     // إرسال عميل محتمل
siteApi.functions.invoke("subscribeEmail", payload) // تسجيل مشترك
siteApi.functions.invoke("bookMeeting", payload)    // حجز اجتماع
siteApi.functions.invoke("getAvailableSlots", { date }) // المواعيد المتاحة
siteApi.functions.invoke("n8nWebhook", payload)     // استقبال من n8n

// دوال استخبارات المنافسين
siteApi.functions.triggerCompetitorScrape()
siteApi.functions.generateCompetitorContent(intel_id, platform)
siteApi.functions.publishBlogDraft(suggestion_id)
```

### 2.4 تقسيم الحزم (Code Splitting)

تم تكوين Vite لتقسيم الحزم يدوياً لتحسين الأداء:

```
vendor-react:    react, react-dom, react-router-dom
vendor-query:    @tanstack/react-query
vendor-ui:       framer-motion, lucide-react
vendor-charts:   recharts
vendor-three:    three
vendor-supabase: @supabase/supabase-js
```

كل صفحات لوحة التحكم يتم تحميلها بشكل كسول (Lazy Loading) باستخدام `React.lazy()`.

---

## 3. لوحة التحكم (Admin Panel)

لوحة التحكم متاحة على المسار `/admin` وتتطلب مصادقة عبر Supabase Auth.

### 3.1 المميزات العامة

- **ثنائية اللغة**: تبديل فوري بين العربية والإنجليزية
- **الوضع الداكن/الفاتح**: مع حفظ التفضيل في localStorage
- **تخطيط RTL/LTR**: يتغير تلقائياً حسب اللغة المختارة
- **قائمة جانبية قابلة للطي**: مع Tooltip عند الطي
- **تصميم متجاوب**: يدعم الموبايل عبر Sheet component
- **نمط L Object**: كل صفحة تستخدم كائن `L` ثنائي اللغة

### 3.2 أقسام التنقل

لوحة التحكم مقسمة إلى 4 أقسام:

**القسم الرئيسي:**
- لوحة التحكم (Dashboard)
- العملاء المحتملون (Leads)
- الحجوزات (Bookings)

**قسم المحتوى:**
- المدونة (Blog)
- دراسات الحالة (Cases)
- الأسئلة الشائعة (FAQ)
- الخدمات (Services)

**قسم التسويق:**
- المشتركون (Subscribers)
- رصد التوجهات (Trend Intelligence)
- استخبارات المنافسين (Competitor Intel)

**قسم النظام:**
- التحليلات (Analytics)
- الإعدادات (Settings)

### 3.3 تفاصيل كل صفحة

#### 3.3.1 لوحة التحكم الرئيسية (Dashboard Home)

**المسار:** `/admin`

**المحتويات:**
- 4 بطاقات إحصائيات: إجمالي العملاء المحتملين، حجوزات اليوم، المقالات المنشورة، المشتركون النشطون
- جدول آخر العملاء المحتملين (اسم، بريد، مصدر، حالة)
- جدول آخر الحجوزات (اسم، بريد، تاريخ، وقت، حالة)
- إجراءات سريعة: مقال جديد، عرض جميع العملاء
- عميل ذكي (AI Agent): شات بوت مدمج يعمل عبر n8n webhook

#### 3.3.2 إدارة العملاء المحتملين (Leads Manager)

**المسار:** `/admin/leads`

**المميزات:**
- جدول بيانات قابل للتصفح والفرز
- فلتر حسب الحالة: جديد، تم التواصل، مؤهل، مغلق
- فلتر حسب المصدر: تواصل، عرض سعر، حجز
- بحث بالاسم أو البريد الإلكتروني
- تصدير CSV لجميع البيانات
- حذف العملاء مع تأكيد
- تصفح بالصفحات (Pagination)

**الحقول المعروضة:** الاسم، البريد، الهاتف، الشركة، المصدر، الحالة، التاريخ

#### 3.3.3 إدارة الحجوزات (Bookings Manager)

**المسار:** `/admin/bookings`

**المميزات:**
- فلتر حسب الحالة: معلق، مؤكد، مكتمل، ملغى
- عرض تاريخ ووقت الحجز
- رابط Google Meet لكل حجز
- تحديث حالة الحجز

#### 3.3.4 إدارة المدونة (Blog Manager)

**المسار:** `/admin/blog`

**المميزات:**
- قائمة بجميع المقالات مع حالة النشر
- زر إنشاء مقال جديد
- تعديل المقالات الموجودة
- حذف المقالات

#### 3.3.5 محرر المقالات (Blog Editor)

**المسار:** `/admin/blog/new` أو `/admin/blog/edit/:id`

**المميزات:**
- حقول ثنائية اللغة: عنوان عربي/إنجليزي، مقتطف عربي/إنجليزي، محتوى عربي/إنجليزي
- توليد Slug تلقائي من العنوان الإنجليزي
- معاينة Markdown مباشرة
- حقول SEO: عنوان SEO، وصف ميتا
- حقول وسائط: رابط صورة الغلاف، التصنيف، الوسوم
- تبديل حالة النشر (Published toggle)
- تبديل بين عرض النموذج والمعاينة

#### 3.3.6 إدارة دراسات الحالة (Cases Manager)

**المسار:** `/admin/cases`

**المميزات:**
- إدارة CRUD كاملة لدراسات الحالة
- حقول: العميل، الصناعة، التحدي، الحل، النتيجة
- صورة غلاف لكل دراسة
- مقاييس النجاح (Metrics) بصيغة JSON
- ترتيب العرض (Display Order)
- تبديل حالة النشر

#### 3.3.7 إدارة الأسئلة الشائعة (FAQ Manager)

**المسار:** `/admin/faq`

**المميزات:**
- سؤال وجواب ثنائي اللغة
- إعادة ترتيب بالسحب والإفلات (Drag & Drop) عبر @hello-pangea/dnd
- تصنيف الأسئلة
- تبديل حالة النشر

#### 3.3.8 إدارة الخدمات (Services Manager)

**المسار:** `/admin/services`

**المميزات:**
- بطاقات خدمات ثنائية اللغة
- حقول: عنوان، وصف، أيقونة، ميزات (JSON)
- Slug فريد لكل خدمة
- ترتيب العرض
- تبديل حالة النشر

#### 3.3.9 إدارة المشتركين (Subscribers Manager)

**المسار:** `/admin/subscribers`

**المميزات:**
- قائمة المشتركين في النشرة البريدية
- تصدير CSV
- حالة الاشتراك: نشط، غير مشترك
- حالة إرسال بريد الترحيب

#### 3.3.10 ملخص التحليلات (Analytics Summary)

**المسار:** `/admin/analytics`

**المحتويات:**
- **لوحات خارجية**: روابط مباشرة إلى GA4، PostHog، Hotjar مع حالة التفعيل
- **إحصائيات سريعة**: عملاء هذا الشهر، إجمالي العملاء، معدل التحويل التقديري
- **رسوم بيانية**:
  - العملاء حسب المصدر (Pie Chart)
  - العملاء حسب الحالة (Pie Chart)
  - العملاء المحتملين يومياً آخر 30 يوم (Line Chart)

#### 3.3.11 الإعدادات (Settings Panel)

**المسار:** `/admin/settings`

**الأقسام:**
- **معلومات الشركة**: اسم الشركة (عربي/إنجليزي)، البريد، الهاتف، العنوان (عربي/إنجليزي)
- **روابط التواصل الاجتماعي**: Twitter/X، LinkedIn، Instagram، Facebook، WhatsApp
- **مفاتيح التكامل**: GA4 ID، PostHog Key، Hotjar ID (مع إخفاء القيم)
- **إدارة المستخدمين**: عرض مستخدمي النظام، تغيير الأدوار (owner/developer)

#### 3.3.12 استخبارات المنافسين (Competitor Dashboard)

**المسار:** `/admin/competitor`

**المميزات:**
- تحليل محتوى المنافسين (ثمانية كنموذج)
- زر "رصد الآن" لتشغيل سير العمل يدوياً
- عرض آخر تحليلات المنافسين
- توليد اقتراحات محتوى بالذكاء الاصطناعي لمنصات متعددة (Instagram, YouTube, LinkedIn, TikTok, Blog)
- اعتماد اقتراح كمسودة مدونة
- نسخ الخطافات التسويقية (Marketing Hooks)
- Prompts للصور والفيديو والكاروسيل

---

## 4. النماذج والأمان

### 4.1 نماذج الموقع

**نموذج تواصل معنا (`/Contact`):**
- الحقول: الاسم، البريد الإلكتروني، الرسالة
- المصدر: `contact`

**نموذج حجز اجتماع (`/BookMeeting`):**
- الحقول: الاسم، البريد، الهاتف، الشركة، حجم الشركة، الصناعة، التحدي، التاريخ، الوقت
- يُنشئ عميل محتمل تلقائياً إذا لم يكن موجوداً
- نظام مواعيد ذكي: 09:00 - 16:00 مع استبعاد المحجوز

**نموذج طلب عرض سعر (`/RequestProposal`):**
- الحقول: الاسم، البريد الإلكتروني
- المصدر: `proposal`

**نموذج الاشتراك في النشرة (Footer):**
- الحقل: البريد الإلكتروني
- إعادة تنشيط المشتركين غير النشطين تلقائياً (Upsert)

### 4.2 التحقق من البيانات (Validation)

جميع النماذج تستخدم مكتبة **Zod** للتحقق من صحة البيانات:

```javascript
emailSchema    // تحقق من صيغة البريد الإلكتروني
phoneSchema    // تحقق من صيغة رقم الهاتف (7-20 رقم)
nameSchema     // الاسم: 2-100 حرف
bookingSchema  // كل حقول الحجز مطلوبة
proposalSchema // الاسم + البريد
contactSchema  // الاسم + البريد + الرسالة
```

### 4.3 الحماية ضد السبام

**Honeypot Field:**
- حقل مخفي (`website`) يتم إضافته لكل نموذج
- إذا تم ملؤه (من قبل Bot)، يتم تجاهل الإرسال بصمت
- لا يظهر للمستخدم العادي

**تحديد معدل الإرسال (Rate Limiting):**
- الحد الأقصى: 3 إرسالات لكل 5 دقائق لكل نموذج
- يستخدم `sessionStorage` للتتبع
- يفشل بأمان (Fail Open) إذا كان sessionStorage غير متاح

### 4.4 تتبع UTM

جميع النماذج تلتقط وتحفظ معاملات UTM تلقائياً:

```
utm_source, utm_medium, utm_campaign, utm_term, utm_content
```

- يتم التقاطها عند زيارة أي صفحة وحفظها في `sessionStorage`
- يتم إرسالها مع كل نموذج إلى Supabase
- تُستخدم لتحليل مصادر العملاء في لوحة التحليلات

### 4.5 سياسات أمان Supabase (RLS)

| الجدول | إدراج عام | قراءة عامة | قراءة مصادق عليها | تعديل/حذف |
|--------|-----------|------------|-------------------|-----------|
| leads | نعم | لا | نعم | مصادق عليه فقط |
| bookings | نعم | لا | نعم | مصادق عليه فقط |
| blog_posts | لا | المنشور فقط | نعم (الكل) | مصادق عليه فقط |
| case_studies | لا | المنشور فقط | نعم (الكل) | مصادق عليه فقط |
| subscribers | نعم | لا | نعم | مصادق عليه فقط |
| faq_items | لا | المنشور فقط | نعم (الكل) | مصادق عليه فقط |
| services | لا | المنشور فقط | نعم (الكل) | مصادق عليه فقط |
| settings | لا | لا | نعم | مصادق عليه فقط |
| profiles | لا | لا | نعم | صاحب الحساب فقط |

---

## 5. تكامل HubSpot

### 5.1 نظرة عامة

يتم مزامنة العملاء المحتملين من Supabase إلى HubSpot تلقائياً عبر سير عمل n8n:

```
Supabase (New Lead) → n8n Trigger → HubSpot Contact + Deal
```

### 5.2 تفاصيل سير العمل

1. **الاستقبال**: عند إدخال عميل جديد في جدول `leads`
2. **التحقق من التكرار**: البحث عن جهة اتصال موجودة بنفس البريد في HubSpot
3. **الإنشاء/التحديث**:
   - إنشاء جهة اتصال (Contact) جديدة أو تحديث الموجودة
   - إنشاء صفقة (Deal) مرتبطة بالجهة
4. **حفظ المعرف**: تحديث حقل `hubspot_contact_id` و `hubspot_deal_id` في Supabase

### 5.3 الخصائص المخصصة (Custom Properties)

| خاصية HubSpot | حقل Supabase | الوصف |
|----------------|--------------|-------|
| email | email | البريد الإلكتروني |
| firstname | name | الاسم |
| phone | phone | الهاتف |
| company | company | الشركة |
| lead_source | source | المصدر (contact/proposal/booking) |
| utm_source | utm_source | مصدر الحملة |
| utm_medium | utm_medium | وسيط الحملة |
| utm_campaign | utm_campaign | اسم الحملة |

---

## 6. نظام المدونة

### 6.1 عرض المدونة (Frontend)

**صفحة قائمة المقالات:** `/Blog`
- عرض شبكي للمقالات المنشورة
- صورة غلاف، عنوان، مقتطف
- فلترة حسب التصنيف

**صفحة المقال:** `/blog/:slug`
- روابط نظيفة (Clean URLs) باستخدام الـ Slug
- عرض Markdown عبر `react-markdown`
- حقول SEO ديناميكية (عنوان، وصف ميتا)
- دعم ثنائي اللغة

### 6.2 إدارة المدونة (Admin)

- إنشاء وتعديل المقالات عبر محرر غني
- معاينة Markdown مباشرة
- حقول SEO متقدمة
- إدارة التصنيفات والوسوم
- تبديل حالة النشر

### 6.3 نشر آلي عبر n8n

يمكن نشر مقالات عبر n8n webhook:

```
POST /n8n/webhook/[ID]/publish-blog-draft
Body: { suggestion_id: "..." }
```

سير العمل:
1. استلام اقتراح محتوى معتمد من لوحة استخبارات المنافسين
2. تحويله إلى مسودة مدونة
3. إدخاله في جدول `blog_posts` عبر `n8nWebhook` function

---

## 7. التحليلات

### 7.1 Google Analytics 4 (GA4)

**الأحداث المتتبعة:**

| الحدث | الوصف | المعاملات |
|-------|-------|----------|
| page_view | زيارة صفحة | page_path |
| form_start | بدء ملء نموذج | form (contact/booking/proposal) |
| form_submit | إرسال نموذج | form |

**الإعداد:**
- يتم تحميل gtag.js في `index.html`
- GA4 Measurement ID يُحفظ في إعدادات لوحة التحكم
- التتبع يتم عبر `window.gtag()` في `analytics.js`

### 7.2 PostHog

**المميزات:**
- Autocapture: تتبع تلقائي لكل النقرات والتفاعلات
- Session Replay: تسجيل جلسات المستخدمين
- Feature Flags: تحكم في الميزات عن بُعد
- تعريف المستخدم: `posthog.identify(email)`
- أحداث مخصصة: `posthog.capture(event, properties)`

### 7.3 Hotjar

**المميزات:**
- Heatmaps: خرائط حرارية لنقرات المستخدمين
- Session Recordings: تسجيل كامل لجلسات التصفح
- Surveys: استبيانات مضمنة

### 7.4 Meta Pixel (Facebook)

- تتبع أحداث مخصصة عبر `fbq('trackCustom', ...)`
- يُفعل تلقائياً إذا كان `window.fbq` متاحاً

### 7.5 تكوين التحليلات في الموقع

ملف `src/lib/analytics.js` يوفر واجهة موحدة:

```javascript
trackEvent(eventName, properties)  // يرسل لـ GA4 + PostHog + Meta
identifyUser(email, properties)    // يعرّف المستخدم في PostHog
trackPageView(path)                // يرسل page_view لـ GA4 + PostHog
```

---

## 8. ويدجت المحادثة الذكية (Chat Widget)

### 8.1 نظرة عامة

ويدجت محادثة عائم يظهر في الزاوية السفلية من الموقع، يتيح للزوار التحدث مع مساعد زيادة الذكي.

**الملف:** `src/components/ui/floating-chat-widget.jsx`

### 8.2 المميزات

- **ثنائي اللغة**: عربي/إنجليزي مع تبديل فوري
- **RTL/LTR**: يتكيف مع اتجاه اللغة
- **الوضع الداكن/الفاتح**: يتبع إعدادات الموقع
- **رسائل سريعة**: أزرار محددة مسبقاً (خدماتنا، احجز استشارة، اطلب عرض سعر)
- **حالة غير متصل**: رسالة بديلة مع زر حجز استشارة
- **حركات سلسة**: باستخدام Framer Motion

### 8.3 الاتصال بـ n8n

```
الويدجت → POST /n8n/webhook/[ID]/chat → n8n Workflow → Gemini Flash 2.0 → Response
```

**إعدادات البيئة:**
```
VITE_CHATBOT_WEBHOOK=/n8n/webhook/[ID]/chat
VITE_CHATBOT_ENABLED=true
```

### 8.4 نموذج الذكاء الاصطناعي

- **النموذج المستخدم**: Gemini Flash 2.0
- **التكلفة**: ~$0.02/شهر لـ 1000 رسالة
- **سرعة الاستجابة**: ~500ms
- **الحصول على مفتاح API**: https://aistudio.google.com/app/apikey

### 8.5 صيغ الاستجابة المدعومة

الويدجت يدعم تلقائياً عدة صيغ استجابة:
- `output` (الافتراضي)
- `text`
- `response`
- `message`
- `choices[0].message.content` (OpenAI format)
- `content`

---

## 9. استخبارات المنافسين (Competitor Intelligence)

### 9.1 نظرة عامة

نظام آلي لرصد وتحليل محتوى المنافسين (ثمانية كنموذج) وتوليد أفكار محتوى لزيادة.

### 9.2 جداول Supabase

**جدول `competitor_intel`:**
- بيانات المحتوى المرصود من المنافسين
- تحليل GPT-4o لكل محتوى
- تاريخ الرصد

**جدول `content_suggestions`:**
- اقتراحات محتوى مولدة بالذكاء الاصطناعي
- المنصة المستهدفة (Instagram, YouTube, LinkedIn, TikTok, Blog)
- حالة الاقتراح: معلق، معتمد، مرفوض، منشور
- Prompts للصور والفيديو والكاروسيل والحركة

### 9.3 سير العمل (n8n Workflows)

**1. Thmanyah Scraper (كل 48 ساعة):**
```
Cron (48h) → Firecrawl Scrape → Apify Extract → GPT-4o Analysis → Supabase Insert → Gmail Digest
```

**2. Content Generator (عند الطلب):**
```
Webhook POST → Read Intel → GPT-4o Generate → Insert content_suggestions
```

**3. Blog Publisher (عند الطلب):**
```
Webhook POST → Read Suggestion → Format as Blog Draft → Insert blog_posts
```

### 9.4 متغيرات البيئة

```
VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK=/n8n/webhook/[ID]/trigger-scrape
VITE_N8N_COMPETITOR_GENERATE_WEBHOOK=/n8n/webhook/[ID]/competitor-generate
VITE_N8N_BLOG_PUBLISHER_WEBHOOK=/n8n/webhook/[ID]/publish-blog-draft
```

---

## 10. رصد التوجهات (Trend Intelligence)

### 10.1 نظرة عامة

لوحة ذكاء لرصد توجهات YouTube في نيتشات محددة.

**المسار:** `/admin/trends`

### 10.2 المميزات

- تحليل توجهات YouTube حسب المجال
- إحصائيات النيتش (المشاهدات، التفاعل، النمو)
- اقتراحات مواضيع محتوى
- بيانات محدثة دورياً

---

## 11. النشر والاستضافة

### 11.1 Vercel Configuration

**ملف `vercel.json`:**

**Rewrites (إعادة التوجيه):**
- `/n8n/:path*` → يتم توجيهه إلى `https://n8n.srv953562.hstgr.cloud/:path*`
- كل المسارات الأخرى → `/index.html` (SPA routing)

**Security Headers:**

| Header | القيمة | الغرض |
|--------|--------|-------|
| X-Content-Type-Options | nosniff | منع تخمين نوع الملف |
| X-Frame-Options | DENY | منع التضمين في iframe |
| X-XSS-Protection | 1; mode=block | حماية من XSS |
| Referrer-Policy | strict-origin-when-cross-origin | تحكم في معلومات المرجع |
| Permissions-Policy | camera=(), microphone=(), geolocation=() | تعطيل الأذونات غير المطلوبة |
| Content-Security-Policy | (مفصل أدناه) | تحكم في مصادر المحتوى |

**Content Security Policy (CSP):**
```
default-src:  'self'
script-src:   'self' + Google Tag Manager + GA4 + PostHog + Contentsquare + Facebook
style-src:    'self' + Google Fonts
font-src:     'self' + Google Fonts
img-src:      'self' + data: + blob: + https:
connect-src:  'self' + Supabase + GA4 + PostHog + n8n
frame-ancestors: 'none'
```

**Cache Control:**
- الأصول الثابتة (`/assets/*`): `public, max-age=31536000, immutable` (سنة كاملة)
- باقي الملفات: `no-cache`

### 11.2 Vite Dev Server

**Proxy Configuration:**
```javascript
"/n8n" → "https://n8n.srv953562.hstgr.cloud"
// مع changeOrigin و rewrite لإزالة /n8n prefix
```

### 11.3 خطوات النشر

1. Push إلى GitHub repository
2. Vercel يلتقط التغييرات تلقائياً (Auto-deploy)
3. يتم تشغيل `generate-sitemap.mjs` ثم `vite build`
4. النشر إلى Edge Network العالمي

### 11.4 متغيرات البيئة (Environment Variables)

يجب إعدادها في Vercel Dashboard:

```
VITE_SUPABASE_URL=https://nuyscajjlhxviuyrxzyq.supabase.co
VITE_SUPABASE_ANON_KEY=[مفتاح Supabase Anonymous]
VITE_CHATBOT_WEBHOOK=/n8n/webhook/[ID]/chat
VITE_CHATBOT_ENABLED=true
VITE_N8N_HOST=https://n8n.srv953562.hstgr.cloud
VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK=/n8n/webhook/[ID]/trigger-scrape
VITE_N8N_COMPETITOR_GENERATE_WEBHOOK=/n8n/webhook/[ID]/competitor-generate
VITE_N8N_BLOG_PUBLISHER_WEBHOOK=/n8n/webhook/[ID]/publish-blog-draft
```

---

## 12. الدومين والإيميل

### 12.1 إعداد النطاق

- **النطاق:** ziyadasystem.com
- **المسجل:** (يتم تحديده)
- **DNS:** يُوجه إلى Vercel

### 12.2 سجلات DNS المطلوبة

| النوع | الاسم | القيمة | الغرض |
|-------|-------|--------|-------|
| A | @ | 76.76.21.21 | Vercel IP |
| CNAME | www | cname.vercel-dns.com | Vercel redirect |
| TXT | @ | (Vercel verification) | إثبات الملكية |
| MX | @ | (حسب مزود البريد) | البريد الإلكتروني |

### 12.3 البريد الإلكتروني

- **البريد الرئيسي:** ziyadasystem@gmail.com
- **بريد العمل:** (يتم إعداده مع النطاق)
- يُستخدم لاستقبال:
  - إشعارات العملاء المحتملين الجدد
  - ملخص رصد المنافسين (Gmail Digest)
  - إشعارات الحجوزات

---

## 13. قائمة المهام بعد الإطلاق

### المرحلة الأولى: الإعداد الأساسي (يوم 1)

- [ ] 1. تشغيل `supabase-schema.sql` في Supabase SQL Editor
- [ ] 2. إنشاء مستخدم Admin في Supabase Auth (ziyadasystem@gmail.com)
- [ ] 3. التأكد من إنشاء سجل profiles تلقائياً عبر Trigger
- [ ] 4. تحديث متغيرات البيئة في Vercel
- [ ] 5. ربط النطاق ziyadasystem.com بـ Vercel
- [ ] 6. التحقق من شهادة SSL تعمل بشكل صحيح

### المرحلة الثانية: إعداد n8n (يوم 1-2)

- [ ] 7. إنشاء Credentials في n8n:
  - `firecrawlApi` (HTTP Header Auth)
  - `apifyApi` (HTTP Header Auth)
  - `supabaseServiceKey` (HTTP Header Auth)
  - `geminiApi` (API Key)
  - `hubspotApi` (API Key)
- [ ] 8. استيراد ملفات JSON لسير العمل الخمسة
- [ ] 9. نسخ Webhook IDs وتحديث `.env.local` / Vercel env vars
- [ ] 10. تفعيل جميع سير العمل في n8n
- [ ] 11. اختبار Chat Widget يدوياً

### المرحلة الثالثة: المحتوى (يوم 2-3)

- [ ] 12. إضافة الخدمات الأساسية في لوحة التحكم
- [ ] 13. إضافة 2-3 دراسات حالة
- [ ] 14. إضافة 10+ سؤال شائع (FAQ)
- [ ] 15. كتابة 3-5 مقالات مدونة أولية
- [ ] 16. التأكد من صور الغلاف والمحتوى البصري

### المرحلة الرابعة: التحليلات (يوم 3)

- [ ] 17. إعداد Google Analytics 4 وإدخال Measurement ID
- [ ] 18. إعداد PostHog وإدخال Project Key
- [ ] 19. إعداد Hotjar وإدخال Site ID
- [ ] 20. التحقق من أن التتبع يعمل على الإنتاج (production)
- [ ] 21. إعداد Meta Pixel إذا كانت هناك إعلانات Facebook

### المرحلة الخامسة: التكاملات (يوم 3-4)

- [ ] 22. إعداد HubSpot CRM وربطه عبر n8n
- [ ] 23. اختبار مزامنة عميل محتمل → HubSpot
- [ ] 24. التحقق من اكتشاف التكرار يعمل
- [ ] 25. تفعيل سير عمل Competitor Scraper
- [ ] 26. التحقق من Gmail Digest يصل بشكل صحيح

### المرحلة السادسة: الاختبار النهائي (يوم 4-5)

- [ ] 27. اختبار جميع النماذج (تواصل، حجز، عرض سعر، اشتراك)
- [ ] 28. اختبار Honeypot يعمل (ملء حقل مخفي)
- [ ] 29. اختبار Rate Limiting يعمل (3+ إرسالات سريعة)
- [ ] 30. اختبار UTM Tracking (إضافة ?utm_source=test)
- [ ] 31. اختبار لوحة التحكم بالكامل (كل الـ 12 صفحة)
- [ ] 32. اختبار الموقع على الموبايل (iOS + Android)
- [ ] 33. اختبار التبديل بين العربية والإنجليزية
- [ ] 34. اختبار الوضع الداكن والفاتح
- [ ] 35. فحص سرعة الموقع عبر Google PageSpeed Insights
- [ ] 36. فحص SEO عبر Google Search Console

### المرحلة السابعة: الإطلاق (يوم 5)

- [ ] 37. إزالة أي بيانات اختبارية
- [ ] 38. التأكد من أن sitemap.xml يتم توليده بشكل صحيح
- [ ] 39. إرسال الموقع لـ Google Search Console
- [ ] 40. مشاركة الرابط مع الفريق

---

## 14. بيانات الوصول

### 14.1 Supabase

| البند | القيمة |
|-------|--------|
| Dashboard | https://supabase.com/dashboard/project/nuyscajjlhxviuyrxzyq |
| Project URL | https://nuyscajjlhxviuyrxzyq.supabase.co |
| المنطقة | (يُحدد من Dashboard) |

### 14.2 لوحة التحكم (Admin Panel)

| البند | القيمة |
|-------|--------|
| الرابط | https://ziyadasystem.com/admin |
| بريد الدخول | ziyadasystem@gmail.com |
| المصادقة | Supabase Auth (Email/Password) |

### 14.3 n8n

| البند | القيمة |
|-------|--------|
| Dashboard | https://n8n.srv953562.hstgr.cloud |
| الاستضافة | Hostinger VPS |
| Chat Webhook ID | 390b23bb-a7e4-48c4-8768-c3b89cc0ef36 |

### 14.4 Vercel

| البند | القيمة |
|-------|--------|
| Dashboard | https://vercel.com (يتم إعداده) |
| Auto-deploy | من GitHub عند Push |

### 14.5 خدمات إضافية

| الخدمة | الحساب | الغرض |
|--------|--------|-------|
| Google Analytics 4 | ziyadasystem@gmail.com | تحليلات الموقع |
| PostHog | (يتم إعداده) | تحليلات المنتج |
| Hotjar | (يتم إعداده) | خرائط حرارية |
| HubSpot | (يتم إعداده) | CRM |
| Google AI Studio | (يتم إعداده) | Gemini API للشات بوت |

---

## 15. الملحقات

### 15.1 مخطط قاعدة البيانات (Database Schema)

**الجداول الرئيسية:**

| الجدول | الحقول الرئيسية | الوصف |
|--------|----------------|-------|
| leads | id, name, email, phone, company, source, status, utm_*, hubspot_contact_id | العملاء المحتملون |
| bookings | id, lead_name, lead_email, booking_date, booking_time, status, google_meet_link | الحجوزات |
| blog_posts | id, slug, title_ar/en, content_ar/en, category, tags, seo_title, published | المقالات |
| case_studies | id, title_ar/en, client, industry, challenge/solution/result_ar/en, metrics | دراسات الحالة |
| subscribers | id, email, name, language, status, welcome_email_sent | المشتركون |
| faq_items | id, question_ar/en, answer_ar/en, category, display_order, published | الأسئلة الشائعة |
| services | id, slug, title_ar/en, description_ar/en, icon, features, published | الخدمات |
| settings | key, value (jsonb) | إعدادات النظام |
| profiles | id, role (owner/developer), display_name | ملفات المستخدمين |
| competitor_intel | (محدد في SQL منفصل) | بيانات استخبارات المنافسين |
| content_suggestions | (محدد في SQL منفصل) | اقتراحات المحتوى المولدة |

### 15.2 الفهارس (Indexes)

```sql
idx_leads_status        ON leads(status)
idx_leads_created       ON leads(created_at DESC)
idx_bookings_date       ON bookings(booking_date)
idx_blog_posts_slug     ON blog_posts(slug)
idx_blog_posts_published ON blog_posts(published)
idx_subscribers_email   ON subscribers(email)
idx_faq_items_order     ON faq_items(display_order)
idx_services_order      ON services(display_order)
```

### 15.3 Triggers

**`on_auth_user_created`:**
- يعمل بعد إنشاء مستخدم جديد في `auth.users`
- ينشئ سجل تلقائي في `profiles` مع دور `developer`
- يستخدم `display_name` من بيانات المستخدم أو البريد الإلكتروني

### 15.4 صفحات الموقع العام

| الصفحة | المسار | الوصف |
|--------|--------|-------|
| الرئيسية | /Home | الصفحة الرئيسية مع خلفية Three.js |
| الخدمات | /Services | قائمة الخدمات |
| أتمتة الأعمال | /Services/automation | تفاصيل خدمة الأتمتة |
| إدارة العلاقات | /Services/crm | تفاصيل خدمة CRM |
| توليد العملاء | /Services/lead-generation | تفاصيل توليد العملاء |
| التسويق الرقمي | /Services/marketing | تفاصيل التسويق |
| تطوير المواقع | /Services/web-development | تفاصيل تطوير المواقع |
| السوشال ميديا | /Services/social-media | تفاصيل إدارة السوشال ميديا |
| من نحن | /About | صفحة عن زيادة |
| لماذا زيادة | /Why | أسباب اختيار زيادة |
| دراسات الحالة | /Cases | قصص النجاح |
| المدونة | /Blog | قائمة المقالات |
| مقال | /blog/:slug | صفحة المقال بالـ Slug |
| حجز اجتماع | /BookMeeting | نموذج حجز اجتماع |
| طلب عرض سعر | /RequestProposal | نموذج طلب عرض سعر |
| تواصل معنا | /Contact | نموذج التواصل |
| الأسئلة الشائعة | /FAQ | صفحة FAQ |
| شكراً | /ThankYou | صفحة الشكر بعد الإرسال |
| الخصوصية | /Privacy | سياسة الخصوصية |
| الشروط | /Terms | الشروط والأحكام |

### 15.5 إعادة التوجيهات (Redirects)

| المسار القديم | المسار الجديد |
|--------------|--------------|
| / | /Home |
| /AdminDashboard | /admin |
| /trend-intelligence | /admin/trends |
| /youtube-trends | /admin/trends |
| /Services/seo-sem | /Services/marketing |

### 15.6 التبعيات الرئيسية (Dependencies)

**الإنتاج (Production):**
- React 18.2, React DOM, React Router DOM 6.26
- @supabase/supabase-js 2.101
- @tanstack/react-query 5.84
- Framer Motion 11.16
- Three.js 0.171
- Recharts 2.15
- Tailwind CSS 3.4 + tailwindcss-animate + tailwind-merge
- shadcn/ui (Radix primitives)
- Zod 3.24
- React Markdown 9.0
- date-fns 3.6
- Lucide React 0.475
- @hello-pangea/dnd 17.0 (Drag & Drop)
- PostHog JS 1.364
- html2canvas + jsPDF (تصدير PDF)

**التطوير (Dev):**
- Vite 6.1
- ESLint 9.19 + plugins
- TypeScript 5.8 (type checking only)
- PostCSS + Autoprefixer
- Sharp (image optimization)
- Playwright 1.58 (testing)

---

## ملاحظات ختامية

هذا الدليل يمثل التوثيق الشامل لنظام زيادة بجميع مكوناته. يجب تحديثه مع كل تغيير جوهري في النظام.

**للتواصل والدعم الفني:**
- البريد: ziyadasystem@gmail.com
- لوحة التحكم: https://ziyadasystem.com/admin

---

*تم إعداد هذا الدليل بواسطة فريق زيادة سيستم -- أبريل 2026*

---
