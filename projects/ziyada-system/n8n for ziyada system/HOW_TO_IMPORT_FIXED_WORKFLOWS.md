# دليل استيراد الـ Workflows المُصلحة — زيادة سيستم

## الملفات المطلوب استيرادها (بالترتيب)

| الملف | الغرض |
|---|---|
| `workflow_lead_processor.json` | استقبال البيانات ← Supabase ← إيميل ← Google Calendar |
| `workflow_ziyada_ai_chat_agent_FIXED.json` | الـ Chat Bot على الموقع |

---

## الخطوة 1 — إعداد الاعتمادات (Credentials) في n8n

قبل الاستيراد، تأكد من وجود هذه الاعتمادات في n8n → Settings → Credentials:

### أ) Supabase (HTTP Header Auth)
- **Name:** `supabaseServiceRole`
- **Header Name:** `apikey`
- **Header Value:** مفتاح الـ Service Role من Supabase → Settings → API

### ب) Gmail OAuth2
- **Name:** `Gmail — ziyadasystem@gmail.com`
- **Type:** Gmail OAuth2
- وصّل حساب `ziyadasystem@gmail.com`

### ج) Google Calendar OAuth2
- **Name:** `Google Calendar — ziyadasystem@gmail.com`
- **Type:** Google Calendar OAuth2
- وصّل نفس حساب `ziyadasystem@gmail.com`

> ⚠️ **مهم:** الـ Gmail و Google Calendar يستخدمان نفس حساب Google — يمكنك استخدام نفس OAuth credential للاثنين إذا دعم n8n ذلك، أو أنشئ اثنين منفصلين.

---

## الخطوة 2 — استيراد workflow_lead_processor.json (أولاً)

1. n8n → Workflows → **+** → **Import from file**
2. اختر `workflow_lead_processor.json`
3. افتح الـ workflow بعد الاستيراد
4. تحقق من كل node وربط الاعتمادات:
   - **Save to Supabase** → اختر `supabaseServiceRole`
   - **Send Email Notification** → اختر `Gmail — ziyadasystem@gmail.com`
   - **Create Calendar Follow-up** → اختر `Google Calendar — ziyadasystem@gmail.com`
5. اضغط **Save**
6. اضغط **Activate** (المفتاح يصير أخضر)
7. تحقق من الـ webhook URL: يجب أن يكون `https://n8n.srv953562.hstgr.cloud/webhook/ziyada-lead-intake`

---

## الخطوة 3 — استيراد workflow_ziyada_ai_chat_agent_FIXED.json (ثانياً)

1. n8n → Workflows → **+** → **Import from file**
2. اختر `workflow_ziyada_ai_chat_agent_FIXED.json`
3. افتح الـ workflow بعد الاستيراد
4. تحقق من الـ nodes:
   - **GPT-4o-mini** → اختر `OpenAI API` credential
   - **capture_lead** → لا يحتاج credential (HTTP Request عادي إلى webhook)
5. اضغط **Save**
6. اضغط **Activate**

> ⚠️ **إذا كان عندك workflow قديم باسم "Ziyada AI Chat Agent"** → احذفه أو عطّله قبل تفعيل الجديد لتجنب التعارض.

---

## الخطوة 4 — اختبار الـ Pipeline الكامل

افتح الـ Chat Test Panel في n8n أو اختبر من الموقع. جرّب هذا السيناريو:

```
أنت:     السلام عليكم
البوت:   السلام عليكم، يا هلا! ...

أنت:     أبي أعرف عن خدماتكم
البوت:   [يسأل عن القطاع والتحدي]

أنت:     عندي مطعم وأبي أتمتة
البوت:   [يشرح خدمة الأتمتة ويطلب البيانات]

أنت:     اسمي محمد العمري، جوالي 0501234567، إيميلي m@test.com
البوت:   "ممتاز! سأسجّل بياناتك:
          • الاسم: محمد العمري
          • الجوال: 0501234567
          • الإيميل: m@test.com
          صحيحة؟"

أنت:     نعم
البوت:   "تم تسجيلك! الفريق يتواصل معك خلال ساعات..."
```

**بعد إرسال "نعم"، تحقق من:**
1. ✅ Supabase → جدول `leads` → صف جديد بالبيانات
2. ✅ Gmail → inbox لـ ziyadasystem@gmail.com → إيميل تنبيه
3. ✅ Google Calendar → حدث "متابعة مع محمد العمري" في اليوم التالي

---

## ما تم إصلاحه في هذا الإصدار

| المشكلة | الحل |
|---|---|
| البوت يرسل رابط Calendly خاطئ | حظر صريح + أداة `get_booking_link` تُعيد الرابط الصحيح فقط |
| `capture_lead` لا يعمل (placeholder ID) | تم استبداله بـ HTTP POST مباشرة إلى webhook حقيقي |
| لا إيميل تنبيه عند استقبال عميل | إضافة Gmail node → يرسل إيميل تفصيلي لـ ziyadasystem@gmail.com |
| لا تحديث للتقويم | إضافة Google Calendar node → ينشئ حدث متابعة في اليوم التالي |
| البيانات تُحفظ ناقصة | يطلب البوت الاسم + الجوال + الإيميل ثلاثتهم، ويؤكدها قبل الحفظ |
| درجة الحرارة مرتفعة (0.7) | تم خفضها إلى 0.4 لردود أكثر احترافية وأقل هلوسة |

---

## ملاحظات مهمة

- الـ Calendar event يُنشأ في **اليوم التالي الساعة 10:00 صباحاً بتوقيت الرياض** كتذكير للمتابعة
- التوقيت يمكن تعديله في node **Create Calendar Follow-up** → حقل `start`
- إذا أراد العميل حجز موعد بنفسه، يوجّهه البوت إلى: **ziyadasystem.com/BookMeeting**
- لا تعدّل ملفات `workflow_ziyada_ai_chat_agent.json` القديمة — استخدم `_FIXED.json` فقط
