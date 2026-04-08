# Ziyada System — Agent Handoff Plan
# خطة تسليم المهام — زيادة سيستم

**Date / التاريخ:** 2026-04-08  
**Status / الحالة:** Frontend deployed ✅ | Supabase RLS fix pending ⏳

---

## 🇬🇧 English Summary

### What Was Fixed

The live website at **ziyadasystem.com** had three problems:

| Problem | Root Cause | Fix Status |
|---------|-----------|------------|
| All forms show error on submit | Supabase RLS missing `anon` INSERT policies | **Code fixed ✅, DB migration pending ⏳** |
| Phone input broken on mobile | `flex` layout with no `minWidth`, overflow | **Fixed & deployed ✅** |
| No celebration on form success | Feature not built | **Built & deployed ✅** |

---

### What Was Done (Already Deployed to Vercel)

**Commit:** `23d2ee8` pushed to `https://github.com/alibiggyaf/ziyada-system-website.git` (branch: `main`)  
Vercel auto-deploys on every push → **ziyadasystem.com**

#### 1. `src/api/siteApi.js` — Form Backend Fix
- **`subscribeEmail()`**: Replaced `SELECT → INSERT` pattern with `supabase.upsert()` using `onConflict: "email"`. Anon role only needs INSERT permission, not SELECT or UPDATE.
- **`bookMeeting()`**: Replaced `SELECT lead → INSERT if not exists` with `supabase.upsert()` using `onConflict: "email", ignoreDuplicates: true`. Same reason.

#### 2. `src/pages/BookMeeting.jsx` — Mobile Phone Input Fix
- Country code `<select>`: fixed `width: 120px`, `maxWidth: 120px`, `flexShrink: 0`
- Phone digit `<input>`: added `minWidth: 0` so it shrinks properly in flex
- All form grids: changed from `gridTemplateColumns: "1fr 1fr"` to `repeat(auto-fit, minmax(220px, 1fr))` — automatically stacks to single column on mobile

#### 3. `src/lib/confetti.js` — New File (Canvas Confetti, Zero Dependencies)
- Lightweight canvas animation with brand colors (`#2563eb`, `#3b82f6`, `#a855f7`, `#fbbf24`, etc.)
- `launchConfetti({ duration, count })` — draws falling rectangular + circular particles
- No npm package needed

#### 4. `src/pages/ThankYou.jsx` — Celebration on Success
- Calls `launchConfetti({ duration: 5000, count: 220 })` in `useEffect` on mount
- Confetti auto-launches when user lands on `/ThankYou` after any form submission

#### 5. `src/components/ziyada/Layout.jsx` — Global CTA Celebration
- Added global `document.addEventListener('click', handler)` in `useEffect`
- Handler checks `e.target.closest('.btn-primary-ziyada')` — fires `launchConfetti({ duration: 2500, count: 100 })` on every primary CTA click across the whole site
- Cleaned up on unmount with `removeEventListener`

#### 6. `fix-supabase-rls.sql` — SQL Script (reference only)
- Created at repo root as documentation
- Contains the exact 6-line SQL that needs to be applied to Supabase

---

### ⏳ ONE REMAINING TASK — Supabase Migration

**This is the only thing left. Forms will NOT work until this is done.**

The Supabase project (`nuyscajjlhxviuyrxzyq`) has RLS enabled on all tables but the INSERT policies for the `anon` role were never created. The website's anon key gets a `42501` RLS violation error on every form submit.

**Use the Supabase MCP tool (`mcp__supabase__apply_migration`) with this exact SQL:**

```sql
-- Fix bookings: allow anonymous INSERT
DROP POLICY IF EXISTS "bookings_insert" ON public.bookings;
CREATE POLICY "bookings_insert" ON public.bookings
  FOR INSERT TO anon, authenticated WITH CHECK (true);

-- Fix leads: allow anonymous INSERT  
DROP POLICY IF EXISTS "leads_insert" ON public.leads;
CREATE POLICY "leads_insert" ON public.leads
  FOR INSERT TO anon, authenticated WITH CHECK (true);

-- Fix subscribers: allow anonymous INSERT (upsert-safe)
DROP POLICY IF EXISTS "subs_insert" ON public.subscribers;
CREATE POLICY "subs_insert" ON public.subscribers
  FOR INSERT TO anon, authenticated WITH CHECK (true);
```

**Migration name:** `fix_anon_insert_rls_policies`

**After applying, verify with:**
```sql
SELECT tablename, policyname, cmd, roles
FROM pg_policies
WHERE tablename IN ('bookings', 'leads', 'subscribers') AND cmd = 'INSERT'
ORDER BY tablename;
```
Expected: 3 rows, each with `roles = {anon,authenticated}`.

**Then test with curl:**
```bash
curl -X POST "https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/leads" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzNjk0MzAsImV4cCI6MjA5MDk0NTQzMH0.8pMN29L6WYRBB64LyhnH1hCDr0ZnBwhImmm4ubhwSp8" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzNjk0MzAsImV4cCI6MjA5MDk0NTQzMH0.8pMN29L6WYRBB64LyhnH1hCDr0ZnBwhImmm4ubhwSp8" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"name":"Test","email":"verify-fix@test.com","source":"contact","language":"ar","status":"new"}'
```
Expected response: a JSON object with an `id` field. Then delete the test record.

---

### Key Credentials & URLs

| Item | Value |
|------|-------|
| Live site | https://ziyadasystem.com |
| GitHub repo | https://github.com/alibiggyaf/ziyada-system-website |
| Supabase project | https://nuyscajjlhxviuyrxzyq.supabase.co |
| Supabase anon key | In `projects/ziyada-system/app/ziyada-system-website/.env.local` |
| Supabase service role | In `projects/ziyada-system/.env` as `SUPABASE_SERVICE_ROLE_KEY` |
| N8N instance | https://n8n.srv953562.hstgr.cloud |
| N8N API key | In `projects/ziyada-system/.env` as `N8N_API_KEY` |
| Chat webhook | `https://n8n.srv953562.hstgr.cloud/webhook/0f30c293-c375-45a2-9cf6-d55208de387b` |

---

### Forms & Their Flow

| Form | Page | Supabase Table | siteApi function |
|------|------|---------------|-----------------|
| Book Meeting | `/BookMeeting` | `bookings` + `leads` (upsert) | `bookMeeting()` |
| Contact | `/Contact` | `leads` | `submitContact()` |
| Request Proposal | `/RequestProposal` | `leads` | `submitLead()` |
| Newsletter | Footer | `subscribers` (upsert) | `subscribeEmail()` |

All forms redirect to `/ThankYou` on success, which triggers the confetti celebration.

---

---

## 🇸🇦 العربي — ملخص المهام

### ما تم إصلاحه

الموقع المباشر على **ziyadasystem.com** كان به ثلاث مشاكل:

| المشكلة | السبب الجذري | حالة الإصلاح |
|---------|-------------|-------------|
| جميع النماذج تُظهر خطأ عند الإرسال | سياسات RLS في Supabase لا تسمح لدور `anon` بالإدراج | **الكود مُصلح ✅، Migration قيد الانتظار ⏳** |
| مربع الهاتف معطوب على الموبايل | مشكلة في CSS Flex بدون `minWidth` | **مُصلح ومنشور ✅** |
| لا يوجد احتفال عند نجاح النموذج | الميزة لم تكن موجودة | **تم البناء والنشر ✅** |

---

### ما تم إنجازه (منشور بالفعل على Vercel)

**الـ Commit:** `23d2ee8` — مرفوع إلى GitHub، وVercel ينشر تلقائياً.

#### 1. `src/api/siteApi.js` — إصلاح الباكيند
- **`subscribeEmail()`**: استبدال `SELECT → INSERT` بـ `upsert` مع `onConflict: "email"`.
- **`bookMeeting()`**: استبدال التحقق من وجود العميل بـ `upsert` مع `ignoreDuplicates: true`.
- **السبب**: دور `anon` يحتاج فقط صلاحية INSERT، وليس SELECT أو UPDATE.

#### 2. `src/pages/BookMeeting.jsx` — إصلاح الهاتف في الموبايل
- حقل اختيار رمز الدولة: عرض ثابت `120px` مع `flexShrink: 0`.
- حقل أرقام الهاتف: إضافة `minWidth: 0` حتى يتقلص بشكل صحيح.
- شبكة النموذج: تغيير من `1fr 1fr` ثابتة إلى `repeat(auto-fit, minmax(220px, 1fr))` — تتكدس عموديًا تلقائياً على الشاشات الصغيرة.

#### 3. `src/lib/confetti.js` — ملف جديد (رسوم متحركة بالـ Canvas)
- تأثير احتفالي بألوان براند زيادة (أزرق، بنفسجي، ذهبي، أخضر).
- `launchConfetti({ duration, count })` — جسيمات مستطيلة ودائرية تتساقط.
- بدون أي مكتبات خارجية.

#### 4. `src/pages/ThankYou.jsx` — احتفال عند النجاح
- يطلق `launchConfetti` تلقائيًا عند فتح صفحة `/ThankYou` بعد أي نموذج ناجح.
- المدة: 5 ثوان، 220 جسيمًا.

#### 5. `src/components/ziyada/Layout.jsx` — احتفال على جميع أزرار CTA
- معالج عالمي `document.addEventListener('click')` يراقب كل نقرة.
- عند النقر على أي زر من نوع `.btn-primary-ziyada` في أي صفحة → يطلق الكونفيتي.
- يُزال المعالج عند unmount لتجنب التسرب.

---

### ⏳ المهمة الوحيدة المتبقية — Migration في Supabase

**النماذج لن تعمل حتى يتم تطبيق هذا.**

مشكلة RLS: الجداول `bookings` و `leads` و `subscribers` في Supabase بها حماية RLS مفعّلة، لكن سياسات INSERT لدور `anon` (الزوار غير المسجلين) لم تُنشأ قط.

**استخدم أداة Supabase MCP (`mcp__supabase__apply_migration`) مع هذا SQL:**

```sql
-- السماح للزوار بإدراج الحجوزات
DROP POLICY IF EXISTS "bookings_insert" ON public.bookings;
CREATE POLICY "bookings_insert" ON public.bookings
  FOR INSERT TO anon, authenticated WITH CHECK (true);

-- السماح للزوار بإدراج العملاء المحتملين
DROP POLICY IF EXISTS "leads_insert" ON public.leads;
CREATE POLICY "leads_insert" ON public.leads
  FOR INSERT TO anon, authenticated WITH CHECK (true);

-- السماح للزوار بالاشتراك في النشرة البريدية
DROP POLICY IF EXISTS "subs_insert" ON public.subscribers;
CREATE POLICY "subs_insert" ON public.subscribers
  FOR INSERT TO anon, authenticated WITH CHECK (true);
```

**اسم الـ Migration:** `fix_anon_insert_rls_policies`

**بعد التطبيق، تحقق بهذا الاستعلام:**
```sql
SELECT tablename, policyname, cmd, roles
FROM pg_policies
WHERE tablename IN ('bookings', 'leads', 'subscribers') AND cmd = 'INSERT'
ORDER BY tablename;
```
النتيجة المتوقعة: 3 صفوف، كل منها بـ `roles = {anon,authenticated}`.

---

### مراجع وروابط مهمة

| العنصر | القيمة |
|--------|--------|
| الموقع المباشر | https://ziyadasystem.com |
| GitHub | https://github.com/alibiggyaf/ziyada-system-website |
| Supabase | https://nuyscajjlhxviuyrxzyq.supabase.co |
| N8N | https://n8n.srv953562.hstgr.cloud |
| الـ Chat Webhook (يعمل) | `.../webhook/0f30c293-c375-45a2-9cf6-d55208de387b` |
| ملف المشروع | `projects/ziyada-system/app/ziyada-system-website/` |
| ملف الـ ENV (frontend) | `...website/.env.local` |
| ملف الـ ENV (backend/secrets) | `projects/ziyada-system/.env` |

---

## Checklist for Next Agent / قائمة مهام العميل التالي

- [ ] **Apply Supabase migration** using `mcp__supabase__apply_migration` — SQL above
- [ ] **Verify** with `pg_policies` query — expect 3 rows with `anon` role
- [ ] **Test** booking form on https://ziyadasystem.com/BookMeeting — should redirect to `/ThankYou` with confetti
- [ ] **Test** contact form on https://ziyadasystem.com/Contact — should work
- [ ] **Test** newsletter in footer — should work
- [ ] **Delete** test records inserted during verification from Supabase
- [ ] **Clean up** N8N: delete the unused "Ziyada Forms Handler" workflow (ID: `1Xo5nTVPBI3XNsnl`) — it was created during debugging but is not used by the frontend
