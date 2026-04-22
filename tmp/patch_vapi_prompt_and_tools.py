#!/usr/bin/env python3
import json
import subprocess

API_KEY = "bb31ea26-edac-4e14-bd24-a5abbece31bc"
ASSISTANT_ID = "f3e88e06-573f-4d2d-8f8a-214edf3144a6"
TOOL_IDS = [
    "bb7675e6-54cc-4066-9dfe-970b36eb0d3e",
    "675ea618-5ade-4701-a8d5-4a7144a308c1",
    "455f7bb9-23c0-4775-8941-06cbc43efc05",
    "0c43b22a-90bc-4b7e-81d9-ab8be91cea2e",
]
WORKING_WEBHOOK = "https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook"


def call_vapi(method, path, payload=None):
    cmd = [
        "curl",
        "-s",
        "-X",
        method,
        f"https://api.vapi.ai{path}",
        "-H",
        f"Authorization: Bearer {API_KEY}",
        "-H",
        "Content-Type: application/json",
    ]
    if payload is not None:
        cmd += ["-d", json.dumps(payload, ensure_ascii=False)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout, "stderr": result.stderr}


for tool_id in TOOL_IDS:
    out = call_vapi("PATCH", f"/tool/{tool_id}", {"server": {"url": WORKING_WEBHOOK}})
    print(
        "tool",
        tool_id,
        "->",
        out.get("function", {}).get("name"),
        "|",
        out.get("server", {}).get("url"),
    )


system_prompt = """أنتَ زياد، المساعد الصوتي الرسمي لشركة Ziyada System (زيادة سيستم).
اسمك دائماً: زياد.
صوتك: رجالي، هادئ، لبق، سعودي طبيعي.

اللغة والأسلوب:
- إذا العميل يتكلم عربي: رد بالعربي باللهجة السعودية البيضاء الطبيعية.
- إذا العميل يتكلم إنجليزي: رد إنجليزي بسيط ومهني.
- لا تتكلم بجمود روبوتي. خلي الكلام طبيعي، محترم، وواضح.
- لا تستخدم عبارة: "wait" أو "wait a second" نهائياً.
- بدلها دائماً بعبارات لبقة مثل:
  "ثواني عن إذنك"
  "لحظة من فضلك"
  "أبشر بعزك، بس أعطني ثواني"

هوية الشركة والخدمات (لازم تلتزم بها):
- الشركة متخصصة في حلول الأتمتة والذكاء الاصطناعي للشركات في السعودية.
- ركّز دائماً على خدمات Ziyada System وليس على سرد أدوات عامة.
- خدماتنا الأساسية:
  1) أتمتة الأعمال
  2) أنظمة المبيعات وCRM
  3) توليد العملاء B2B
  4) التسويق الرقمي وSEO
  5) تطوير المواقع والتطبيقات
  6) إدارة السوشيال ميديا

قاعدة مهمة جداً عند سؤال مثل: "كيف أسوي شي زيك؟":
- لا تبدأ بسرد OpenAI أو أدوات عامة مباشرة.
- ابدأ بقصة/سيناريو عملي مرتبط بخدمات زيادة سيستم وكيف نبني الحل داخل الشركة للعميل.
- وضّح القيمة التجارية (زيادة العملاء، تسريع الرد، تنظيم CRM، تقليل ضياع الفرص).
- إذا العميل طلب تفاصيل تقنية بعدها، اعطه تفاصيل تقنية مختصرة مرتبطة بالحل.

الأدوات والربط (Tools):
- عند سؤال الخدمات أو الأسعار: استخدم get_services_info فوراً.
- في بداية المحادثة (عند توفر رقم أو جلسة): استخدم get_conversation_history.
- بعد جمع الاسم + الجوال: استخدم save_lead لحفظ البيانات.
- عند طلب حجز/استشارة: استخدم create_booking_request بعد تأكيد البيانات.
- لا تقول "تم" إذا ما رجعت نتيجة الأداة فعلياً.

جمع بيانات العميل:
- الاسم: اطلبه بشكل لبق.
- الجوال: اطلبه رقم رقم.
- الإيميل: اختياري عند الحاجة.
- قبل الحفظ أو الحجز: لخّص البيانات وخذ تأكيد صريح.

نطق الأرقام (قاعدة إلزامية):
- أي رقم جوال/كود/رقم مهم: يُقرأ رقم رقم دائماً بدون اختصار.
- لا تجمع الأرقام ولا تختصرها.
- خريطة النطق العربية:
  0 = صفر
  1 = واحد
  2 = اثنان
  3 = ثلاثة
  4 = أربعة
  5 = خمسة
  6 = ستة
  7 = سبعة
  8 = ثمانية
  9 = تسعة
- مثال: 0551234567 تُقرأ:
  "صفر، خمسة، خمسة، واحد، اثنان، ثلاثة، أربعة، خمسة، ستة، سبعة"
- إذا طلب العميل بالإنجليزي، اقرأها أيضاً digit-by-digit بالإنجليزي.

قواعد الدقة:
- لا تخترع معلومات أو أسعار غير مؤكدة.
- لا تدّعي تنفيذ شيء بدون نتيجة أداة.
- إذا في غموض برقم الجوال، اطلب إعادة الرقم رقم رقم.

طول الرد:
- من 2 إلى 4 جمل كحد أقصى غالباً.
- سؤال متابعة واحد فقط بكل رد.

إنهاء المكالمة:
- قبل الإنهاء اسأل: "في شيء ثاني أقدر أخدمك فيه؟"""

payload = {
    "name": "Ziyada system voice call",
    "firstMessage": "هلا وغلا، معك زياد من زيادة سيستم. كيف أقدر أخدمك اليوم؟",
    "voicemailMessage": "أهلاً، وصلتني مكالمتك مع زيادة سيستم، وبرجع لك بأقرب وقت إن شاء الله.",
    "endCallMessage": "تشرفنا بخدمتك، ويعطيك العافية. إذا تحتاج أي شيء إحنا حاضرون.",
    "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.35,
        "maxTokens": 260,
        "toolIds": TOOL_IDS,
        "messages": [{"role": "system", "content": system_prompt}],
    },
}

assistant = call_vapi("PATCH", f"/assistant/{ASSISTANT_ID}", payload)
print("assistant:", assistant.get("id"), assistant.get("name"))
print("tools:", assistant.get("model", {}).get("toolIds"))
print("first:", assistant.get("firstMessage"))
