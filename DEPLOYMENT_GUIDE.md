# Ziyada System Website Deployment & Backend Guide

## Deployment Checklist (VS Code → Vercel)

1. **Install dependencies:**
   ```sh
   npm install
   ```
2. **Test local build:**
   ```sh
   npm run build
   ```
   - If you see errors about missing env vars, check `.env.local` and Vercel dashboard.
3. **Push changes to GitHub:**
   ```sh
   git add .
   git commit -m "fix: update layout, dependencies, or docs"
   git push
   ```
4. **Vercel Project Settings:**
   - Root Directory: `projects/ziyada-system/app/ziyada-system-website`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Set all required env vars in Vercel dashboard (see `.env.example`)
5. **Check Vercel build logs:**
   - Common error: `vite: command not found` → means Vite is missing or wrong root directory.
   - Fix by ensuring Vite is in `devDependencies` and root is correct.
6. **Site should be live at:**
   - Main: https://ziyadasystem.com
   - Vercel: https://ziyada-system-website-<hash>.vercel.app

---

## Backend Connections & URLs

- **Supabase** (database/auth):
  - Dashboard: https://app.supabase.com/project/nuyscajjlhxviuyrxzyq
  - API URL: `VITE_SUPABASE_URL` in `.env.local`
  - Anon Key: `VITE_SUPABASE_ANON_KEY`
- **n8n Workflows** (automation/chat):
  - Main Chatbot: `VITE_CHATBOT_WEBHOOK`
  - Example: https://n8n.srv953562.hstgr.cloud/webhook/0f30c293-c375-45a2-9cf6-d55208de387b
  - Competitor Scraper: `/n8n/webhook/trigger-scrape`
  - Blog Publisher: `/n8n/webhook/publish-blog-draft`
- **Analytics** (optional):
  - Google Analytics 4: `VITE_GA4_ID`
  - PostHog: `VITE_POSTHOG_KEY`
  - Hotjar: `VITE_HOTJAR_ID`
  - Meta Pixel: `VITE_META_PIXEL_ID`

---

## What Each Tool Does

- **Supabase:** Handles user auth, blog posts, and data storage.
- **n8n:** Runs chatbots, lead scraping, blog publishing, and other automations.
- **Vercel:** Hosts the frontend (React/Vite) and handles deployments from GitHub.
- **.env.local:** Stores all API keys and webhook URLs for local dev (must be set in Vercel for production).

---

# دليل النشر والاتصال الخلفي (بالعربية)

## خطوات النشر (من VS Code إلى Vercel)

1. تثبيت الحزم:
   ```sh
   npm install
   ```
2. اختبار البناء المحلي:
   ```sh
   npm run build
   ```
   - إذا ظهرت أخطاء متعلقة بالمتغيرات البيئية، تحقق من ملف `.env.local` ولوحة تحكم Vercel.
3. رفع التغييرات إلى GitHub:
   ```sh
   git add .
   git commit -m "fix: update layout, dependencies, or docs"
   git push
   ```
4. إعدادات مشروع Vercel:
   - مجلد الجذر: `projects/ziyada-system/app/ziyada-system-website`
   - أمر البناء: `npm run build`
   - مجلد الإخراج: `dist`
   - أضف جميع المتغيرات البيئية المطلوبة في لوحة تحكم Vercel (راجع `.env.example`)
5. راقب سجل البناء في Vercel:
   - الخطأ الشائع: `vite: command not found` → يعني أن Vite غير مثبت أو المجلد الجذري غير صحيح.
   - الحل: تأكد أن Vite ضمن `devDependencies` وأن الجذر صحيح.
6. الموقع المباشر:
   - الرئيسي: https://ziyadasystem.com
   - Vercel: https://ziyada-system-website-<hash>.vercel.app

---

## روابط وأدوات الاتصال الخلفي

- **Supabase** (قاعدة البيانات والمصادقة):
  - لوحة التحكم: https://app.supabase.com/project/nuyscajjlhxviuyrxzyq
  - رابط API: `VITE_SUPABASE_URL` في `.env.local`
  - مفتاح Anon: `VITE_SUPABASE_ANON_KEY`
- **n8n** (الأتمتة والدردشة):
  - بوت الدردشة الرئيسي: `VITE_CHATBOT_WEBHOOK`
  - مثال: https://n8n.srv953562.hstgr.cloud/webhook/0f30c293-c375-45a2-9cf6-d55208de387b
  - سكرابر المنافسين: `/n8n/webhook/trigger-scrape`
  - نشر المدونة: `/n8n/webhook/publish-blog-draft`
- **التحليلات (اختياري):**
  - Google Analytics 4: `VITE_GA4_ID`
  - PostHog: `VITE_POSTHOG_KEY`
  - Hotjar: `VITE_HOTJAR_ID`
  - Meta Pixel: `VITE_META_PIXEL_ID`

---

## شرح الأدوات

- **Supabase:** إدارة المستخدمين والمدونة وتخزين البيانات.
- **n8n:** تشغيل بوتات الدردشة، جمع العملاء المحتملين، نشر المدونة، وأتمتة المهام.
- **Vercel:** استضافة الواجهة الأمامية (React/Vite) ونشر التحديثات من GitHub.
- **.env.local:** تخزين جميع مفاتيح API وروابط الويب هوك للتطوير المحلي (يجب إضافتها في Vercel للإنتاج).
