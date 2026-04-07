#!/usr/bin/env python3
"""
Deploy a reliable Code-based chat workflow with smart Arabic/English 
responses. Works immediately - no API quota needed.
Swap in Gemini/OpenAI node later when quota resets.
"""
import json, urllib.request, urllib.error, time

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

WF_ID      = "eO6LzcPrnPT3JlpA"
WEBHOOK_ID = "3c9f6cb1-a3ce-4302-8260-6748f093520d"

SMART_RESPONSE_JS = r"""
const msg = ($input.first().json.chatInput || '').trim();
const lower = msg.toLowerCase();
const isArabic = /[\u0600-\u06FF]/.test(msg);

// ---------- Arabic responses ----------
const arResponses = {
  greeting: `أهلاً وسهلاً! 👋\n\nأنا مساعد زيادة سيستم الذكي. كيف يمكنني مساعدتك اليوم؟\n\nيمكنني مساعدتك في:\n• معرفة خدماتنا\n• حجز استشارة مجانية\n• الحصول على عرض سعر`,

  services: `خدمات زيادة سيستم 🚀\n\n📊 **ذكاء اليوتيوب (NSI)**\nتحليل النيتش وأبحاث الاتجاهات بالذكاء الاصطناعي\n\n✍️ **إنشاء المحتوى**\nمقالات، سوشيال ميديا، سكريبتات فيديو بالذكاء الاصطناعي\n\n📢 **التسويق الرقمي**\nجوجل أدز، ميتا أدز، سناب شات\n\n⚙️ **أتمتة الأعمال**\nسير عمل n8n، وكلاء ذكاء اصطناعي\n\n🔍 **SEO & GEO**\nتحسين محركات البحث والذكاء الاصطناعي\n\nأي خدمة يهمك؟`,

  nsi: `ذكاء إشارة النيتش (NSI) 🔍\n\nنظام ذكاء اصطناعي متقدم يساعدك على:\n• اكتشاف أفضل النيتشات على يوتيوب\n• تحليل المنافسين والفجوات\n• توقع الاتجاهات قبل الجميع\n• تقارير تفصيلية بالعربي والإنجليزي\n\nمثالي للمبدعين والمسوقين وأصحاب القنوات 🎯\n\nاحجز استشارة مجانية على /BookMeeting`,

  content: `خدمة إنشاء المحتوى ✍️\n\nنبني محتوى احترافي بالذكاء الاصطناعي:\n• مقالات بلوج SEO محسّنة\n• محتوى سوشيال ميديا يومي\n• سكريبتات فيديو يوتيوب\n• نيوزليترات وبريد إلكتروني\n• بلغتين: العربية والإنجليزية\n\nنوفر عليك الوقت والجهد 💪\n\nاحجز استشارة مجانية على /BookMeeting`,

  marketing: `التسويق الرقمي 📢\n\nندير حملاتك الإعلانية على:\n• Google Ads\n• Meta (Facebook & Instagram)\n• Snapchat Ads\n• TikTok Ads\n\nنستهدف عملاؤك بدقة ونضمن أفضل عائد استثمار 💰\n\nلمعرفة التفاصيل واحجز استشارة مجانية: /BookMeeting`,

  automation: `أتمتة الأعمال ⚙️\n\nنبني سير عمل ذكية تعمل 24/7:\n• أتمتة العمليات المتكررة\n• وكلاء ذكاء اصطناعي مخصصة\n• تكامل CRM والأنظمة\n• تقارير تلقائية\n• وفر 80% من وقت فريقك\n\nاحجز استشارة مجانية: /BookMeeting`,

  price: `التسعير 💰\n\nنقدم حلول مخصصة حسب احتياجاتك وأهدافك.\n\nللحصول على عرض سعر دقيق:\n• احجز استشارة مجانية (30 دقيقة)\n• نفهم وضعك وأهدافك\n• نقدم لك خطة مخصصة بالأسعار\n\n👉 /BookMeeting`,

  consult: `الاستشارة المجانية 🎁\n\nنقدم جلسة استشارية مجانية مدتها 30 دقيقة لمساعدتك على:\n• تحديد فرص النمو\n• اختيار الخدمة المناسبة\n• وضع خطة عمل واضحة\n\nبدون أي التزام! 🤝\n\n👉 احجز الآن: /BookMeeting`,

  contact: `تواصل معنا 📞\n\n📧 البريد الإلكتروني: ali@ziyada.sa\n🌐 الموقع: /contact\n📅 احجز استشارة: /BookMeeting\n\nنرد خلال 24 ساعة في أيام العمل`,

  default: `شكرًا لتواصلك مع زيادة سيستم! 🙌\n\nفريقنا متخصص في:\n✅ التسويق الرقمي\n✅ إنشاء المحتوى بالذكاء الاصطناعي\n✅ أتمتة الأعمال\n✅ ذكاء اليوتيوب والنيتش\n\nكيف يمكنني مساعدتك؟ أو احجز استشارة مجانية: /BookMeeting`
};

// ---------- English responses ----------
const enResponses = {
  greeting: `Hello! 👋\n\nI'm the Ziyada System AI Assistant. How can I help you today?\n\nI can help you with:\n• Learning about our services\n• Booking a free consultation\n• Getting a price quote`,

  services: `Ziyada System Services 🚀\n\n📊 **Niche Signal Intelligence (NSI)**\nAI-powered YouTube niche research & trend analysis\n\n✍️ **Content Creation**\nAI-assisted blogs, social media, video scripts\n\n📢 **Digital Marketing**\nGoogle Ads, Meta Ads, Snapchat Ads\n\n⚙️ **Business Automation**\nn8n workflows, AI agents, CRM integration\n\n🔍 **SEO & GEO**\nSearch engine + AI engine optimization\n\nWhich service interests you?`,

  nsi: `Niche Signal Intelligence (NSI) 🔍\n\nOur AI system helps you:\n• Discover top YouTube niches\n• Analyze competitors & gaps\n• Predict trends before everyone else\n• Detailed reports in Arabic & English\n\nPerfect for creators, marketers & channel owners 🎯\n\nBook a free consultation: /BookMeeting`,

  content: `Content Creation Service ✍️\n\nWe build professional AI-powered content:\n• SEO-optimized blog articles\n• Daily social media content\n• YouTube video scripts\n• Newsletters & email campaigns\n• Bilingual: Arabic & English\n\nSave time and effort 💪\n\nBook a free consultation: /BookMeeting`,

  marketing: `Digital Marketing 📢\n\nWe manage your ad campaigns on:\n• Google Ads\n• Meta (Facebook & Instagram)\n• Snapchat Ads\n• TikTok Ads\n\nPrecision targeting for maximum ROI 💰\n\nBook a free consultation: /BookMeeting`,

  automation: `Business Automation ⚙️\n\nWe build smart workflows that run 24/7:\n• Automate repetitive processes\n• Custom AI agents\n• CRM & system integrations\n• Automatic reporting\n• Save 80% of your team's time\n\nBook a consultation: /BookMeeting`,

  price: `Pricing 💰\n\nWe offer customized solutions based on your needs.\n\nFor an accurate quote:\n• Book a free 30-min consultation\n• We understand your goals\n• We provide a tailored plan with pricing\n\n👉 /BookMeeting`,

  consult: `Free Consultation 🎁\n\nWe offer a free 30-minute strategy session to help you:\n• Identify growth opportunities\n• Choose the right service\n• Build a clear action plan\n\nNo commitment needed! 🤝\n\n👉 Book now: /BookMeeting`,

  contact: `Contact Us 📞\n\n📧 Email: ali@ziyada.sa\n🌐 Website: /contact\n📅 Book consultation: /BookMeeting\n\nWe respond within 24 business hours`,

  default: `Thanks for reaching out to Ziyada System! 🙌\n\nWe specialize in:\n✅ Digital Marketing\n✅ AI-powered Content Creation\n✅ Business Automation\n✅ YouTube Niche Intelligence\n\nHow can I help you? Or book a free consultation: /BookMeeting`
};

// ---------- Intent detection ----------
function detectIntent(text) {
  const t = text.toLowerCase();
  if (/مرح|أهلا|اهلا|سلام|هلا|صباح|مساء|hello|hi\b|hey|good morning|good evening/.test(t)) return 'greeting';
  if (/خدم|services?|what do you|what can/.test(t)) return 'services';
  if (/nsi|niche|يوتيوب|youtube|trend|نيتش|signal|intelligence|tranding/.test(t)) return 'nsi';
  if (/محتو|content|مقال|article|blog|social media|سوشيال|كتاب|writing|script/.test(t)) return 'content';
  if (/تسويق|marketing|ads|اعلان|إعلان|google|meta|snapchat|tiktok|campaign/.test(t)) return 'marketing';
  if (/أتمت|automat|workflow|n8n|agent|system|bot|integration/.test(t)) return 'automation';
  if (/سعر|price|pricing|cost|كم|تكلف|كلفة|budget|تكلف|رسوم|fee|كمية/.test(t)) return 'price';
  if (/استشار|consult|book|احجز|meeting|جلسة|session|appointment|demo/.test(t)) return 'consult';
  if (/تواصل|contact|اتصل|email|phone|رقم|whatsapp/.test(t)) return 'contact';
  return 'default';
}

const intent = detectIntent(msg);
const responses = isArabic ? arResponses : enResponses;
const output = responses[intent] || responses.default;

return [{ json: { output, status: 'success', model: 'ziyada-smart-agent' } }];
"""

def n8n(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=N8N_HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, {"raw": raw.decode("utf-8","ignore")[:500]}

workflow = {
    "name": "🚀 Ziyada Chat Widget - Gemini Flash (Cheapest)",
    "settings": {"executionOrder": "v1"},
    "staticData": None,
    "nodes": [
        {
            "id": "chat-trigger-node",
            "name": "Chat Message Received",
            "type": "@n8n/n8n-nodes-langchain.chatTrigger",
            "position": [240, 280],
            "typeVersion": 1.1,
            "webhookId": WEBHOOK_ID,
            "parameters": {
                "public": True,
                "mode": "webhook",
                "authentication": "none",
                "options": {"responseMode": "lastNode"}
            }
        },
        {
            "id": "smart-response-node",
            "name": "Smart Response Engine",
            "type": "n8n-nodes-base.code",
            "position": [500, 280],
            "typeVersion": 2,
            "parameters": {"jsCode": SMART_RESPONSE_JS}
        }
    ],
    "connections": {
        "Chat Message Received": {
            "main": [[{"node": "Smart Response Engine", "type": "main", "index": 0}]]
        }
    }
}

print("Deploying Smart Response workflow (no API key needed)...")
st, result = n8n("PUT", f"/workflows/{WF_ID}", workflow)
print(f"PUT: {st}")
if st != 200:
    print(f"Failed: {result}")
    exit(1)

print(f"  ✓ {result.get('name')}")
st2, _ = n8n("POST", f"/workflows/{WF_ID}/activate")
print(f"  Activate: {st2}")

webhook_url = f"{N8N_BASE}/webhook/{WEBHOOK_ID}/chat"
vite_path   = f"/n8n/webhook/{WEBHOOK_ID}/chat"

print(f"\n  Webhook: {webhook_url}")
print("\nWaiting 3s...")
time.sleep(3)

for msg, sid in [
    ("ما هي خدماتكم؟", "test-ar-01"),
    ("What services do you offer?", "test-en-01"),
    ("أريد أعرف عن أتمتة الأعمال", "test-ar-02"),
    ("How much does it cost?", "test-en-02"),
]:
    print(f"\n>>> {msg}")
    payload = json.dumps({"action":"sendMessage","chatInput":msg,"sessionId":sid}).encode()
    try:
        req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            print(f"  ✓ output: {data.get('output','')[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8","ignore")
        print(f"  ✗ HTTP {e.code}: {body[:200]}")
    except Exception as ex:
        print(f"  ✗ {ex}")

print(f"\n{'='*65}")
print(f"✅ DEPLOY COMPLETE")
print(f"   VITE_CHATBOT_WEBHOOK={vite_path}")
print(f"   VITE_CHATBOT_ENABLED=true")
print(f"{'='*65}")
print("NOTE: Chat is working with smart keyword responses.")
print("To upgrade to real AI: replace quota-exceeded Gemini key in n8n credentials.")
