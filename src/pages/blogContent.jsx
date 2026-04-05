/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║               ZIYADA BLOG CONTENT MANAGEMENT FILE               ║
 * ╠══════════════════════════════════════════════════════════════════╣
 * ║  Edit this file to manage blog articles without touching the    ║
 * ║  database. Posts here act as FALLBACK / STATIC content when     ║
 * ║  no database posts exist for the given slug.                    ║
 * ║                                                                  ║
 * ║  Fields per post:                                               ║
 * ║   slug          — unique URL key                                ║
 * ║   title_ar/en   — title in Arabic / English                     ║
 * ║   excerpt_ar/en — short description for listing cards           ║
 * ║   content_ar/en — full Markdown article body                    ║
 * ║   cover_image   — URL (Unsplash or uploaded)                    ║
 * ║   category      — e.g. "automation", "crm", "marketing"         ║
 * ║   tags          — string array                                  ║
 * ║   author        — author display name                           ║
 * ║   published     — true / false                                  ║
 * ║   published_date— "YYYY-MM-DD"                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

export const staticPosts = [
  {
    slug: "why-automation-changes-everything",
    title_ar: "لماذا تُغيّر الأتمتة كل شيء في عملك؟",
    title_en: "Why Automation Changes Everything in Your Business",
    excerpt_ar: "اكتشف كيف تحوّل الأتمتة العمليات اليدوية إلى آلة تعمل 24/7 دون تدخل بشري.",
    excerpt_en: "Discover how automation turns manual processes into a 24/7 machine without human intervention.",
    cover_image: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
    category: "automation",
    tags: ["أتمتة", "n8n", "ذكاء اصطناعي"],
    author: "فريق زيادة",
    published: true,
    published_date: "2025-01-10",
    content_ar: `## لماذا تُغيّر الأتمتة كل شيء؟

في عالم الأعمال اليوم، **الوقت = المال**. كل مهمة يدوية تُكلّفك ساعات يمكن استثمارها في النمو.

### ما الذي تحلّه الأتمتة؟

- **المتابعة اليدوية** مع العملاء المحتملين
- **إرسال الفواتير** والتقارير الدورية
- **تحديث قواعد البيانات** بعد كل عملية
- **الردود التلقائية** على الاستفسارات الشائعة

### كيف نبني نظام أتمتة؟

1. **تحديد العمليات** القابلة للأتمتة
2. **ربط الأدوات** عبر n8n أو Make
3. **الاختبار والتحسين** المستمر
4. **المراقبة التلقائية** للأخطاء

> "الأتمتة لا تُلغي الوظائف، بل تُحرّر طاقة الفريق للتركيز على القرارات الاستراتيجية."

### النتائج الفعلية

شركة في قطاع التجزئة وفّرت **40 ساعة أسبوعياً** بعد أتمتة عمليات الطلبات فقط.
`,
    content_en: `## Why Automation Changes Everything

In today's business world, **time = money**. Every manual task costs hours that could be invested in growth.

### What Does Automation Solve?

- **Manual follow-ups** with leads
- **Sending invoices** and periodic reports
- **Updating databases** after each operation
- **Automatic replies** to common inquiries

### How We Build Automation Systems

1. **Identify** automatable processes
2. **Connect tools** via n8n or Make
3. **Test and optimize** continuously
4. **Monitor** automatically for errors

> "Automation doesn't eliminate jobs — it frees your team's energy to focus on strategic decisions."

### Real Results

A retail company saved **40 hours per week** just by automating order operations.
`,
  },
  {
    slug: "crm-sales-engineering",
    title_ar: "هندسة CRM: كيف تختصر دورة المبيعات إلى نصفها؟",
    title_en: "CRM Engineering: How to Cut Your Sales Cycle in Half",
    excerpt_ar: "نظام CRM مُهندَس بشكل صحيح يمكنه مضاعفة إيراداتك دون زيادة فريق المبيعات.",
    excerpt_en: "A properly engineered CRM can double your revenue without increasing your sales team.",
    cover_image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
    category: "crm",
    tags: ["CRM", "مبيعات", "HubSpot"],
    author: "فريق زيادة",
    published: true,
    published_date: "2025-01-20",
    content_ar: `## هندسة CRM: ما الفرق؟

معظم الشركات تملك CRM لكن لا تستخدمه بشكل صحيح. الهندسة الصحيحة تعني:

### المكونات الأساسية

| المكوّن | الوظيفة |
|---------|---------|
| Pipeline واضح | تتبع كل صفقة في مرحلتها الصحيحة |
| Automation داخلي | متابعة تلقائية بعد كل تفاعل |
| تقارير دقيقة | معرفة مصدر كل عميل |

### الخطأ الشائع

**90% من الشركات** تُدخل بيانات في CRM لكن لا تبني عليه workflows.

### النتيجة المتوقعة

- تقليص دورة المبيعات بنسبة **40-60%**
- زيادة معدل الإغلاق بـ **25%**
- توفير **15 ساعة** أسبوعياً لكل مندوب مبيعات
`,
    content_en: `## CRM Engineering: What's the Difference?

Most companies have a CRM but don't use it correctly. Proper engineering means:

### Core Components

| Component | Function |
|-----------|----------|
| Clear Pipeline | Track every deal at the right stage |
| Internal Automation | Automatic follow-up after every interaction |
| Accurate Reports | Know the source of every client |

### The Common Mistake

**90% of companies** enter data into CRM but don't build workflows on top of it.

### Expected Results

- Shorten sales cycle by **40-60%**
- Increase close rate by **25%**
- Save **15 hours** per week per sales rep
`,
  },
  {
    slug: "b2b-lead-generation-machine",
    title_ar: "بناء ماكينة توليد عملاء B2B: الدليل العملي",
    title_en: "Building a B2B Lead Generation Machine: The Practical Guide",
    excerpt_ar: "كيف تبني نظاماً يُولّد عملاء محتملين مؤهلين بشكل مستمر باستخدام الأتمتة والبيانات.",
    excerpt_en: "How to build a system that continuously generates qualified leads using automation and data.",
    cover_image: "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&q=80",
    category: "lead-generation",
    tags: ["توليد العملاء", "B2B", "أتمتة"],
    author: "فريق زيادة",
    published: true,
    published_date: "2025-02-05",
    content_ar: `## ماكينة توليد العملاء

توليد العملاء ليس حدثاً — إنه **نظام**. هذا هو الفرق بين الشركات التي تنمو وتلك التي تتوقف.

### المكونات الثلاثة للماكينة

#### 1. مصادر الجذب (Top of Funnel)
- محتوى LinkedIn مستهدف
- إعلانات مدفوعة بجمهور دقيق
- SEO لاستقطاب باحثين جاهزين

#### 2. نظام التأهيل (Middle of Funnel)
\`\`\`
زيارة الموقع → تحميل مورد مجاني → تسجيل بالبريد → تسلسل إيميل تلقائي → اجتماع
\`\`\`

#### 3. إغلاق المبيعات (Bottom of Funnel)
- عرض سعر مخصص خلال 24 ساعة
- متابعة تلقائية عبر CRM
- نظام إحالة للعملاء الراضين

### الأرقام المتوقعة

بعد 90 يوماً من تشغيل النظام:
- **200-500** زيارة أسبوعية مؤهلة
- **15-30** عميل محتمل أسبوعياً
- **3-8** صفقات مغلقة شهرياً
`,
    content_en: `## The Lead Generation Machine

Lead generation is not an event — it's a **system**. This is the difference between companies that grow and those that stagnate.

### The Three Machine Components

#### 1. Attraction Sources (Top of Funnel)
- Targeted LinkedIn content
- Paid ads with precise audience
- SEO to attract ready searchers

#### 2. Qualification System (Middle of Funnel)
\`\`\`
Site visit → Free resource download → Email registration → Automated email sequence → Meeting
\`\`\`

#### 3. Sales Closing (Bottom of Funnel)
- Custom proposal within 24 hours
- Automatic follow-up via CRM
- Referral system for satisfied clients

### Expected Numbers

After 90 days of running the system:
- **200-500** qualified weekly visits
- **15-30** leads per week
- **3-8** closed deals per month
`,
  },
];

export default staticPosts;