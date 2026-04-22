#!/usr/bin/env python3
"""Fix VAPI assistant and create n8n dispatcher - uses curl to bypass Cloudflare"""

import json, subprocess, sys

N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"

VAPI_BASE = "https://api.vapi.ai"
VAPI_KEY = "bb31ea26-edac-4e14-bd24-a5abbece31bc"
VAPI_ASSISTANT_ID = "f3e88e06-573f-4d2d-8f8a-214edf3144a6"
OLD_MCP_TOOL_ID = "5ec716b1-c099-4598-b1b9-bb9e9408e656"

SUPABASE_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

DISPATCHER_URL = f"{N8N_BASE}/webhook/vapi-tools"

def curl(method, url, headers, data=None):
    cmd = ["curl", "-s", "-X", method, url]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", json.dumps(data)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"CURL ERROR: {result.stderr[:200]}")
        return None
    try:
        return json.loads(result.stdout)
    except:
        print(f"CURL RESPONSE (non-JSON): {result.stdout[:200]}")
        return {"raw": result.stdout}

def n8n(method, path, data=None):
    return curl(method, f"{N8N_BASE}/api/v1{path}",
                {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}, data)

def vapi(method, path, data=None):
    return curl(method, f"{VAPI_BASE}{path}",
                {"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"}, data)

# ─── STEP 1: n8n Dispatcher Workflow ─────────────────────────────────────────
print("=" * 60)
print("STEP 1: Creating n8n VAPI Tools Dispatcher...")

dispatcher_code = r"""const body = $json.body || $json;
const toolCallList = body.message?.toolCallList || body.toolCallList || [];
const SUPABASE_URL = 'https://nuyscajjlhxviuyrxzyq.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k';

const services = [
  { id: 1, name: 'أتمتة الأعمال', en: 'Business Automation', tag: 'الأكثر طلباً', desc: 'سير عمل آلية باستخدام n8n والذكاء الاصطناعي توفر 40-80 ساعة شهرياً وتربط جميع الأنظمة بدون أخطاء بشرية.' },
  { id: 2, name: 'أنظمة المبيعات وإدارة العملاء CRM', en: 'CRM & Sales Systems', tag: 'الأعلى عائداً', desc: 'هندسة CRM متكاملة (HubSpot/Zoho) مع متابعة آلية للعملاء المحتملين وتقارير مبيعات دقيقة. يقلص دورة البيع بـ25%+.' },
  { id: 3, name: 'توليد العملاء والنمو', en: 'Lead Generation & Growth', tag: 'نتائج سريعة', desc: 'ماكينة عملاء B2B تعمل 24/7 بالجمع بين LinkedIn Outreach والبيانات والأتمتة.' },
  { id: 4, name: 'التسويق الرقمي وSEO', en: 'Digital Marketing & SEO', tag: 'نمو الإيرادات', desc: 'حملات Google وMeta + تحسين الظهور في محركات البحث والأدوات الذكية مثل ChatGPT وGoogle AI.' },
  { id: 5, name: 'تطوير المواقع والتطبيقات', en: 'Web & App Development', tag: 'أساسك الرقمي', desc: 'مواقع React/Next.js سريعة مع لوحات تحكم مخصصة وتكامل كامل مع جميع الأنظمة.' },
  { id: 6, name: 'إدارة السوشيال ميديا', en: 'Social Media Management', tag: 'حضور العلامة', desc: 'إدارة كاملة للحضور الرقمي مع محتوى آلي ومبدع وتقارير أداء شهرية.' }
];

async function fetchSupabase(endpoint, options) {
  const resp = await fetch(SUPABASE_URL + endpoint, {
    ...options,
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });
  return await resp.json();
}

const results = [];

for (const call of toolCallList) {
  const fn = call.function?.name || call.name;
  const rawArgs = call.function?.arguments || call.arguments || '{}';
  const args = typeof rawArgs === 'string' ? JSON.parse(rawArgs) : rawArgs;
  let result = '';

  try {
    if (fn === 'get_services_info') {
      result = 'خدمات زيادة سيستم:\n' + services.map(s =>
        s.id + '. ' + s.name + ' — ' + s.tag + '\n' + s.desc
      ).join('\n\n');
    }
    else if (fn === 'save_lead') {
      await fetchSupabase('/rest/v1/voice_assistant_leads', {
        method: 'POST',
        headers: { 'Prefer': 'return=minimal' },
        body: JSON.stringify({
          name: args.name || '',
          phone: args.phone || '',
          email: args.email || '',
          service_interest: args.service_interest || '',
          source: 'voice_assistant',
          created_at: new Date().toISOString()
        })
      });
      result = 'تم تسجيل بياناتك يا ' + (args.name || 'أخوي') + '. سيتواصل معك فريق زيادة سيستم قريباً إن شاء الله.';
    }
    else if (fn === 'create_booking_request') {
      await fetchSupabase('/rest/v1/voice_booking_requests', {
        method: 'POST',
        headers: { 'Prefer': 'return=minimal' },
        body: JSON.stringify({
          name: args.name || '',
          phone: args.phone || '',
          service: args.service || '',
          preferred_datetime: args.preferred_datetime || '',
          notes: args.notes || '',
          status: 'pending',
          source: 'voice_assistant',
          created_at: new Date().toISOString()
        })
      });
      result = 'أبشر يا ' + (args.name || 'أخوي') + '! تم تسجيل طلب حجز ' + (args.service || 'الخدمة') + '. سيتواصل معك الفريق لتأكيد الموعد.';
    }
    else if (fn === 'get_conversation_history') {
      const phone = args.phone || '';
      const session_id = args.session_id || '';
      let query = '/rest/v1/chat_messages?order=created_at.asc&limit=8';
      if (phone) query += '&session_id=ilike.*' + phone + '*';
      const history = await fetchSupabase(query, { method: 'GET' });
      if (Array.isArray(history) && history.length > 0) {
        result = 'المحادثات السابقة:\n' + history.map(m =>
          (m.direction === 'inbound' ? 'العميل: ' : 'زياد: ') + (m.content || '')
        ).join('\n');
      } else {
        result = 'لا توجد محادثات سابقة لهذا العميل.';
      }
    }
    else {
      result = 'تم تنفيذ ' + fn + ' بنجاح.';
    }
  } catch(e) {
    result = 'حدث خطأ في تنفيذ ' + fn + ': ' + e.message;
  }

  results.push({ toolCallId: call.id, result });
}

return [{ json: { results } }];"""

wf = {
    "name": "Ziyada — VAPI Tools Dispatcher",
    "active": True,
    "nodes": [
        {
            "id": "wh1",
            "name": "VAPI Tools Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [240, 300],
            "parameters": {
                "path": "vapi-tools",
                "httpMethod": "POST",
                "responseMode": "lastNode",
                "options": {}
            }
        },
        {
            "id": "code1",
            "name": "Dispatch Tools",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": dispatcher_code
            }
        }
    ],
    "connections": {
        "VAPI Tools Webhook": {
            "main": [[{"node": "Dispatch Tools", "type": "main", "index": 0}]]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

r = n8n("POST", "/workflows", wf)
if r and r.get("id"):
    wf_id = r["id"]
    print(f"Workflow created: {wf_id}")
    act = n8n("POST", f"/workflows/{wf_id}/activate")
    print(f"Activated: {act}")
else:
    print(f"Failed to create workflow: {r}")

# ─── STEP 2: Delete old MCP tool ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2: Deleting old broken MCP tool...")
r = curl("DELETE", f"{VAPI_BASE}/tool/{OLD_MCP_TOOL_ID}",
         {"Authorization": f"Bearer {VAPI_KEY}"})
print(f"Delete result: {r}")

# ─── STEP 3: Create 4 Function Tools ─────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3: Creating VAPI function tools...")

tools = [
    {
        "type": "function",
        "async": False,
        "server": {"url": DISPATCHER_URL},
        "function": {
            "name": "get_services_info",
            "description": "Get list of Ziyada System services with descriptions. Call when user asks about services, what you offer, or pricing. استخدم عند سؤال العميل عن الخدمات أو الأسعار.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "enum": ["ar", "en"], "description": "Response language"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "async": False,
        "server": {"url": DISPATCHER_URL},
        "function": {
            "name": "save_lead",
            "description": "Save customer lead info to database. Call AFTER collecting name AND phone number. استخدم بعد جمع اسم العميل ورقم جواله.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer full name"},
                    "phone": {"type": "string", "description": "Phone number 05XXXXXXXX"},
                    "email": {"type": "string", "description": "Email address (optional)"},
                    "service_interest": {"type": "string", "description": "Which service they are interested in"}
                },
                "required": ["name", "phone"]
            }
        }
    },
    {
        "type": "function",
        "async": False,
        "server": {"url": DISPATCHER_URL},
        "function": {
            "name": "create_booking_request",
            "description": "Create a service booking or consultation request. Call when user wants to book or schedule. استخدم عند رغبة العميل في حجز خدمة أو موعد.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name"},
                    "phone": {"type": "string", "description": "Customer phone"},
                    "service": {"type": "string", "description": "Service to book"},
                    "preferred_datetime": {"type": "string", "description": "Preferred date and time"},
                    "notes": {"type": "string", "description": "Additional notes"}
                },
                "required": ["name", "phone", "service"]
            }
        }
    },
    {
        "type": "function",
        "async": False,
        "server": {"url": DISPATCHER_URL},
        "function": {
            "name": "get_conversation_history",
            "description": "Get previous conversations for this customer from chat history. Call at start of call to have context. استخدم في بداية المحادثة لمعرفة سياق المحادثات السابقة.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "session_id": {"type": "string", "description": "Session ID if available"}
                },
                "required": []
            }
        }
    }
]

tool_ids = []
for t in tools:
    r = vapi("POST", "/tool", t)
    if r and r.get("id"):
        tool_ids.append(r["id"])
        print(f"  Created: {t['function']['name']} → {r['id']}")
    else:
        print(f"  FAILED: {t['function']['name']} → {r}")

print(f"\nTool IDs: {tool_ids}")

# ─── STEP 4: Update VAPI Assistant ───────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4: Updating VAPI assistant...")

system_prompt = """أنتَ زياد، المساعد الصوتي الذكي لشركة Ziyada System — متخصص في حلول الأتمتة والذكاء الاصطناعي للشركات في السعودية.
تحدث باللهجة السعودية البيضاء وباختصار. إذا المستخدم يتكلم عربي، رد عربي. إذا إنجليزي، رد إنجليزي.

■ شخصيتك: مستشار تقني ودود، محترم، عملي. مثل صديق يفهم في التكنولوجيا والأعمال.

■ معلومات الشركة:
- الاسم: Ziyada System  زيادة سيستم
- التخصص: حلول الأتمتة والذكاء الاصطناعي للشركات السعودية
- موقعنا: ziyadasystem.com

■ خدماتنا الستة الرئيسية:
1. أتمتة الأعمال (الأكثر طلباً): سير عمل n8n + AI توفر 40-80 ساعة شهرياً
2. أنظمة المبيعات وCRM (الأعلى عائداً): HubSpot/Zoho مع متابعة آلية وتقارير
3. توليد العملاء B2B (نتائج سريعة): LinkedIn automation + بيانات + أتمتة
4. التسويق الرقمي وSEO: Google وMeta مع تحسين الظهور
5. تطوير المواقع والتطبيقات: React/Next.js مع لوحات تحكم مخصصة
6. إدارة السوشيال ميديا: محتوى آلي وتقارير شهرية

■ تعليمات الأدوات (TOOLS) - مهم جداً:
- عند سؤال عن الخدمات أو الأسعار: استخدم get_services_info فوراً
- في بداية كل محادثة: استخدم get_conversation_history لمعرفة السياق السابق
- بعد جمع الاسم والجوال: استخدم save_lead لحفظ بيانات العميل
- عند طلب حجز موعد أو استشارة: استخدم create_booking_request

■ جمع بيانات العميل:
- الاسم: اطلبه طبيعياً "شو اسمك الكريم؟"
- الجوال: اطلبه بصيغة "لو سمحت اذكر الجوال رقم رقم"
- أعد قراءة الرقم رقماً رقماً وتأكد منه قبل الحفظ
- البريد: اختياري، اطلبه فقط عند الحاجة

■ قواعد أساسية:
1. لا تدّعي معلومة مجهولة ولا تخترع أرقاماً
2. لا تقل "تم الحجز" إلا بعد تأكيد العميل وتنفيذ create_booking_request
3. إذا قاطعك العميل: توقف فوراً وقل "تفضل"

■ أسلوب الرد:
- 2 إلى 4 جمل كحد أقصى
- سؤال متابعة واحد فقط في كل رد
- بدون bullet points أو formatting في الكلام

■ ألفاظ مفضلة: أبشر، حاضر، ولا يهمك، من عيوني، يعطيك العافية، يا غالي

■ الخاتمة: دائماً اسأل "في شي ثاني أقدر أساعدك فيه؟" قبل إنهاء المحادثة."""

payload = {
    "name": "Ziyada system voice call",
    "firstMessage": "أهلاً وسهلاً، معك زياد من Ziyada System — كيف أقدر أخدمك اليوم؟",
    "voicemailMessage": "أهلاً، تواصلت مع Ziyada System. سنعاود الاتصال بك قريباً إن شاء الله.",
    "endCallMessage": "شكراً لتواصلك مع Ziyada System — يوم سعيد إن شاء الله، وأبشر دائماً.",
    "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "maxTokens": 220,
        "temperature": 0.4,
        "toolIds": tool_ids,
        "messages": [{"role": "system", "content": system_prompt}]
    }
}

r = vapi("PATCH", f"/assistant/{VAPI_ASSISTANT_ID}", payload)
if r and r.get("id"):
    print("Assistant updated successfully!")
    print(f"  Tools attached: {r.get('model', {}).get('toolIds')}")
else:
    print(f"Failed: {r}")

print("\n" + "=" * 60)
print("DONE! Summary:")
print(f"  Dispatcher webhook: {DISPATCHER_URL}")
print(f"  Tool IDs: {tool_ids}")
print(f"\nManual SQL for Supabase (run in SQL Editor):")
print("""
CREATE TABLE IF NOT EXISTS voice_assistant_leads (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text, phone text, email text,
  service_interest text, source text DEFAULT 'voice_assistant',
  notes text, created_at timestamptz DEFAULT now()
);
CREATE TABLE IF NOT EXISTS voice_booking_requests (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text, phone text, service text, preferred_datetime text,
  notes text, status text DEFAULT 'pending',
  source text DEFAULT 'voice_assistant', created_at timestamptz DEFAULT now()
);
CREATE TABLE IF NOT EXISTS voice_assistant_sessions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id text UNIQUE, phone text, call_id text,
  channel text DEFAULT 'voice', messages jsonb DEFAULT '[]',
  summary text, language text DEFAULT 'ar',
  started_at timestamptz DEFAULT now(), ended_at timestamptz,
  created_at timestamptz DEFAULT now()
);
""")
