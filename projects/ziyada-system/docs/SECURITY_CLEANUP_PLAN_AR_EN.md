# خطة التنظيف والأمن (عربي/English)

## القسم العربي (AR)

### 1) ما الذي تم تنظيفه الآن

تم تنفيذ تنظيف فعلي داخل المستودع مع أرشفة محلية آمنة خارج Git للمحتوى غير الضروري لتشغيل الموقع المباشر.

- مسار الأرشيف المحلي الآمن:
  - /Users/djbiggy/Downloads/Local Secure Archive/ziyada-cleanup-2026-04-16
- تم نقل الملفات غير الضرورية للتشغيل المباشر (مثل ملفات HTML التجريبية، صور/ملفات وسائط إضافية، ملفات JSON تجريبية، حزم ZIP الأرشيفية) إلى المسار أعلاه.
- تم نقل نسخة الأرشيف الداخلية القديمة للمشروع من:
  - projects/ziyada-system/_archive
  - إلى الأرشيف المحلي الآمن خارج Git.
- تم نقل أدوات غير تشغيلية (Scripts/Debug/Temp) خارج المستودع لتقليل سطح التعرض.

النتيجة: ما يبقى داخل Git موجّه أكثر نحو تشغيل الموقع الفعلي بدل الملفات التجريبية/الأرشيفية.

---

### 2) ما هي المفاتيح/الواجهات التي يجب تغييرها فوراً

> ملاحظة مهمة: حتى بعد نقل الملفات محلياً، أي سرّ كان موجوداً مسبقاً داخل ملفات المشروع/السجل يجب اعتباره مكشوفاً، ويجب تدويره (Rotate).

#### أولوية قصوى (P1) — تدوير فوري

1. مفتاح n8n API (X-N8N-API-KEY)
- لماذا: ظهر كقيمة JWT صريحة داخل أدوات Debug/Automation.
- كيف انكشف: Hardcoded داخل سكربتات Python.
- المخاطر: تحكم كامل في Workflows والتنفيذات.
- الإجراء:
  - إنشاء مفتاح n8n جديد.
  - إلغاء/تعطيل المفتاح القديم فوراً.
  - وضع المفتاح الجديد فقط في بيئة الخادم (.env.local أو Secret Manager) وليس داخل الكود.

2. Supabase service_role key
- لماذا: ظهر بشكل مباشر في سكربتات نشر/استيراد.
- كيف انكشف: قيمة service_role صريحة داخل سكربت.
- المخاطر: صلاحيات كاملة على قاعدة البيانات (حساسة جداً).
- الإجراء:
  - تدوير service_role key فوراً من Supabase.
  - تحديث n8n/الخادم بالقيمة الجديدة فقط عبر متغيرات بيئة آمنة.

3. Google OAuth secrets + refresh/access tokens
- لماذا: ظهرت داخل token.json / token_docs.json / client_secret JSON.
- كيف انكشف: ملفات اعتماد OAuth محفوظة بصيغة نصية.
- المخاطر: وصول غير مصرح لخدمات Google (Sheets/Drive/...)
- الإجراء:
  - إلغاء client secret القديم وإنشاء OAuth client جديد.
  - إبطال refresh tokens الحالية.
  - إعادة المصادقة وإصدار ملفات اعتماد جديدة محلياً فقط.

#### أولوية متوسطة (P2)

4. أي مفاتيح مزودات طرف ثالث في ملفات docs/scripts
- الإجراء: مراجعة سريعة نهائية + نقل كل الأسرار إلى Secret Manager أو متغيرات بيئة فقط.

---

### 3) أين وكيف حصل التعرض (ملخص عملي)

أنماط التعرض التي تم العثور عليها:
- Hardcoded API keys داخل ملفات أدوات/Debug.
- ملفات OAuth token/client_secret محفوظة كنص واضح.
- أمثلة/توثيق تحتوي قيم جاهزة بدل placeholders.

أمثلة من المسارات التي ظهر فيها التعرض قبل النقل للأرشيف المحلي:
- projects/ziyada-system/app/ziyada-system-website/*.py (أدوات فحص/Debug)
- projects/ziyada-system/scripts/* (سكربتات n8n/Supabase)
- projects/ziyada-system/token.json
- projects/ziyada-system/token_docs.json
- projects/ziyada-system/client_secret_*.json

---

### 4) هيكل مسارات ملفات .env (Route Structure)

الملفات التي ظهرت في بيئة العمل:
- .env
- .env.local
- projects/ziyada-system/app/ziyada-system-website/.env
- projects/ziyada-system/app/ziyada-system-website/.env.local
- projects/ziyada-system/app/ziyada-system-website/.env.server.local
- projects/ziyada-system/app/ziyada-system-website/.env.local.backup
- projects/ziyada-system/.env.example
- projects/ziyada-system/video-automation/.env.example
- projects/ziyada-system/app/ziyada-system-website/projects/ziyada-system/.env.example

#### توصية هيكلية نهائية

1. للإنتاج (Production):
- لا تستخدم أي .env فعلي داخل Git.
- استخدم Vercel Environment Variables فقط للتطبيق الأمامي.
- استخدم أسرار الخادم (n8n/server env/secret manager) للمفاتيح الحساسة.

2. للتطوير المحلي:
- استخدم فقط:
  - projects/ziyada-system/app/ziyada-system-website/.env.local
  - projects/ziyada-system/app/ziyada-system-website/.env.server.local (للخادم فقط)
- لا تستخدم .env.local.backup داخل المستودع. انقله خارج Git.

3. القاعدة الذهبية:
- أي قيمة سرية = خارج الكود وخارج docs وخارج JSON.
- داخل Git فقط:
  - .env.example بقيم Placeholder.

---

### 5) ما يجب أن يبقى في GitHub فقط

أبقِ فقط ما يلزم لتشغيل الموقع المباشر في المسار الكانوني:
- projects/ziyada-system/app/ziyada-system-website

مع استبعاد:
- أي Demo HTML/أرشيفات ZIP/صور تجريبية/مخرجات مؤقتة.
- أي سكربتات Debug فيها مفاتيح.
- أي token/client_secret JSON.

---

### 6) خطة تنفيذ لاحقة (Ready-to-Run)

1. تدوير أسرار P1 فوراً (n8n, Supabase service_role, Google OAuth).
2. تحديث الأسرار الجديدة داخل:
- Vercel env
- n8n/server secret store
3. تنظيف تاريخ Git للأسرار القديمة (git filter-repo أو BFG) قبل أي نشر عام نهائي.
4. فرض فحص قبل الدفع (pre-push secret scan).

اقتراح فحص سريع قبل أي push:
- grep -R "eyJ\|GOCSPX-\|sk-\|service_role" . --exclude-dir=node_modules --exclude-dir=.git

---

## English Section (EN)

### 1) What was cleaned now

A real cleanup was executed with secure local archiving outside Git for files not required to run the live website.

- Local secure archive path:
  - /Users/djbiggy/Downloads/Local Secure Archive/ziyada-cleanup-2026-04-16
- Non-runtime artifacts (demo HTML, extra media, test JSON, archived ZIP bundles) were moved there.
- Internal project duplicate archive folder was moved out of Git as local-only.
- Non-runtime debug/tooling scripts were moved out to reduce exposure surface.

Result: Git content is now more aligned with live website runtime needs.

---

### 2) APIs/keys that must be rotated now

Important: even after moving files locally, any secret previously present in repo files/history must be considered compromised and rotated.

#### Critical priority (P1)

1. n8n API key (X-N8N-API-KEY)
- Exposure: hardcoded in debug/automation scripts.
- Risk: workflow execution/admin access.
- Action: rotate immediately, revoke old key, keep new key only in secure env.

2. Supabase service_role key
- Exposure: present in automation/import scripts.
- Risk: full DB privileges.
- Action: rotate immediately, update only in secure server/n8n env.

3. Google OAuth client secret + token files
- Exposure: token.json, token_docs.json, client_secret JSON.
- Risk: unauthorized Google API access.
- Action: revoke old OAuth client/refresh tokens, create new client, re-auth securely.

#### Medium priority (P2)

4. Third-party keys embedded in docs/scripts examples
- Action: replace with placeholders only.

---

### 3) Where/how exposure happened

Exposure patterns found:
- Hardcoded secrets in utility/debug scripts.
- OAuth token/client-secret JSON files committed/stored in plaintext.
- Documentation/examples containing real values instead of placeholders.

Pre-archive example areas:
- projects/ziyada-system/app/ziyada-system-website/*.py
- projects/ziyada-system/scripts/*
- projects/ziyada-system/token.json
- projects/ziyada-system/token_docs.json
- projects/ziyada-system/client_secret_*.json

---

### 4) .env route/path structure

Detected env-related files:
- .env
- .env.local
- projects/ziyada-system/app/ziyada-system-website/.env
- projects/ziyada-system/app/ziyada-system-website/.env.local
- projects/ziyada-system/app/ziyada-system-website/.env.server.local
- projects/ziyada-system/app/ziyada-system-website/.env.local.backup
- projects/ziyada-system/.env.example
- projects/ziyada-system/video-automation/.env.example
- projects/ziyada-system/app/ziyada-system-website/projects/ziyada-system/.env.example

Recommended final model:
- Production: Vercel env + server secret manager only.
- Local dev: only app-level .env.local and .env.server.local.
- Git: keep only .env.example placeholders.

---

### 5) What should remain in GitHub

Keep only what is needed for the live canonical website:
- projects/ziyada-system/app/ziyada-system-website

Exclude from GitHub:
- demo/static experiments, zip archives, temporary outputs
- debug scripts with embedded credentials
- token/client_secret json artifacts

---

### 6) Next execution steps

1. Rotate all P1 secrets immediately.
2. Update new values only in secure runtime env stores.
3. Purge secret-bearing git history (git filter-repo/BFG).
4. Enforce pre-push secret scanning.
