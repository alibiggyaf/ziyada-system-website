#!/usr/bin/env python3
import json
import subprocess

N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
WF_ID = "qHAIKXEV4SW8r5Nx"
SB_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"


def n8n(method, path, data=None):
    cmd = ["curl", "-s", "-X", method, f"{N8N_BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {N8N_KEY}", "-H", "Content-Type: application/json"]
    if data is not None:
        cmd += ["-d", json.dumps(data, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"raw": r.stdout, "stderr": r.stderr}


wf = n8n("GET", f"/workflows/{WF_ID}")
nodes = wf.get("nodes", [])

normalize_js = """const rawBody = $json.body || $json;
const toolCallList = rawBody.message && rawBody.message.toolCallList ? rawBody.message.toolCallList : rawBody.toolCallList || null;
if (toolCallList && toolCallList.length > 0) {
  return [{ json: { _mode: 'tool_call', toolCallList } }];
}

const p = rawBody.voice || rawBody;
const transcript = String(p.transcript || '').trim();
if (!transcript) throw new Error('Missing transcript');
const arabicRegex = /[\u0600-\u06ff]/g;
const language = p.language || (arabicRegex.test(transcript) ? 'ar' : 'en');

const normalizedPhone = String(p.phone_e164 || p.phone || '').replace(/\s+/g, '');
const defaultSession = normalizedPhone ? ('phone-' + normalizedPhone) : ('voice-' + Date.now());

return [{
  json: {
    _mode: 'voice',
    session_id: p.session_id || defaultSession,
    message_id: p.message_id || ('msg-' + Date.now()),
    event_ts: p.timestamp || new Date().toISOString(),
    transcript,
    language,
    provider: p.provider || 'vapi',
    phone_e164: normalizedPhone,
    call_id: p.call_id || ''
  }
}];"""

tool_handler_js = f"""const items = $input.all();
const toolCallList = items[0] && items[0].json && items[0].json.toolCallList ? items[0].json.toolCallList : [];
const SB_URL = '{SB_URL}';
const SB_KEY = '{SB_KEY}';

const services = [
  {{ id: 1, name: 'أتمتة الأعمال', tag: 'الأكثر طلباً', desc: 'سير عمل n8n + AI توفر 40-80 ساعة شهرياً وتربط جميع الأنظمة.' }},
  {{ id: 2, name: 'أنظمة المبيعات CRM', tag: 'الأعلى عائداً', desc: 'هندسة HubSpot/Zoho مع متابعة آلية وتقارير مبيعات دقيقة.' }},
  {{ id: 3, name: 'توليد العملاء B2B', tag: 'نتائج سريعة', desc: 'ماكينة عملاء تعمل 24/7 بـ LinkedIn Outreach والأتمتة.' }},
  {{ id: 4, name: 'التسويق الرقمي وSEO', tag: 'نمو الإيرادات', desc: 'حملات Google وMeta مع تحسين الظهور.' }},
  {{ id: 5, name: 'تطوير المواقع والتطبيقات', tag: 'أساسك الرقمي', desc: 'مواقع React سريعة مع لوحات تحكم مخصصة.' }},
  {{ id: 6, name: 'إدارة السوشيال ميديا', tag: 'حضور العلامة', desc: 'محتوى آلي وتقارير شهرية.' }}
];

async function sbPost(path, body) {{
  const res = await fetch(SB_URL + path, {{
    method: 'POST',
    headers: {{
      apikey: SB_KEY,
      Authorization: 'Bearer ' + SB_KEY,
      'Content-Type': 'application/json',
      Prefer: 'return=representation'
    }},
    body: JSON.stringify(body)
  }});
  let payload = null;
  try {{ payload = await res.json(); }} catch(e) {{ payload = null; }}
  return {{ ok: res.ok, status: res.status, payload }};
}}

async function sbGet(path) {{
  const res = await fetch(SB_URL + path, {{ headers: {{ apikey: SB_KEY, Authorization: 'Bearer ' + SB_KEY }} }});
  if (!res.ok) return [];
  try {{ return await res.json(); }} catch(e) {{ return []; }}
}}

function fallbackEmailFromPhone(phone) {{
  const p = String(phone || '').replace(/[^0-9+]/g, '');
  if (!p) return 'voice-unknown@ziyada.local';
  return 'voice-' + p.replace(/\+/g, '') + '@ziyada.local';
}}

function guessBookingDateTime(input) {{
  const now = new Date();
  const date = now.toISOString().slice(0,10);
  let time = '10:00';
  const txt = String(input || '').trim();
  const m = txt.match(/(\d{{1,2}}):(\d{{2}})/);
  if (m) time = m[1].padStart(2,'0') + ':' + m[2];
  return {{ date, time }};
}}

const results = [];
for (const call of toolCallList) {{
  const fn = (call.function && call.function.name) || call.name || '';
  const rawArgs = (call.function && call.function.arguments) || call.arguments || '{{}}';
  const args = typeof rawArgs === 'string' ? JSON.parse(rawArgs) : rawArgs;
  let result = '';

  try {{
    if (fn === 'get_services_info') {{
      result = 'خدمات زيادة سيستم:\\n' + services.map(s => s.id + '. ' + s.name + ' — ' + s.tag + '\\n' + s.desc).join('\\n\\n');
    }} else if (fn === 'save_lead') {{
      const lead = await sbPost('/rest/v1/leads', {{
        name: args.name || null,
        email: args.email || fallbackEmailFromPhone(args.phone),
        phone: args.phone || null,
        services_requested: args.service_interest ? [String(args.service_interest)] : [],
        source: 'voice_assistant',
        language: 'ar',
        status: 'new'
      }});

      if (lead.ok) {{
        result = 'تم تسجيل بياناتك يا ' + (args.name || 'أخوي') + '. سيتواصل معك الفريق قريباً إن شاء الله.';
      }} else {{
        result = 'ثواني عن إذنك، صار خطأ تقني أثناء حفظ بياناتك. ممكن أعيد المحاولة؟';
      }}
    }} else if (fn === 'create_booking_request') {{
      const dt = guessBookingDateTime(args.preferred_datetime || '');
      const booking = await sbPost('/rest/v1/bookings', {{
        lead_name: args.name || null,
        lead_email: args.email || fallbackEmailFromPhone(args.phone),
        lead_phone: args.phone || null,
        company: args.company || 'Voice Lead',
        challenge: args.notes || null,
        booking_date: dt.date,
        booking_time: dt.time,
        language: 'ar',
        source: 'voice_assistant',
        status: 'pending'
      }});

      if (booking.ok) {{
        result = 'أبشر يا ' + (args.name || 'أخوي') + '! تم تسجيل طلب الحجز. سيتواصل معك الفريق لتأكيد الموعد.';
      }} else {{
        result = 'لحظة من فضلك، ما قدرنا نسجل الحجز الآن بسبب خطأ تقني. ممكن أعيد المحاولة؟';
      }}
    }} else if (fn === 'get_conversation_history') {{
      const phone = String(args.phone || '').trim();
      const sessionKey = phone ? ('phone-' + phone) : '';
      const q = '/rest/v1/chat_messages?select=session_id,role,content,created_at&order=created_at.asc&limit=12' + (sessionKey ? ('&session_id=eq.' + encodeURIComponent(sessionKey)) : '');
      const hist = await sbGet(q);
      result = Array.isArray(hist) && hist.length > 0
        ? 'المحادثات السابقة:\\n' + hist.map(m => (m.role === 'assistant' ? 'المساعد: ' : 'العميل: ') + (m.content || '')).join('\\n')
        : 'لا توجد محادثات سابقة.';
    }} else {{
      result = 'تم تنفيذ ' + fn + '.';
    }}
  }} catch (e) {{
    result = 'أبشر بعزك، بس أعطني ثواني. صار خطأ تقني بسيط أثناء التنفيذ.';
  }}

  results.push({{ toolCallId: call.id, result }});
}}

return [{{ json: {{ results }} }}];"""

for node in nodes:
    if node.get("id") == "normalize-voice":
        node.setdefault("parameters", {})["jsCode"] = normalize_js
    if node.get("id") == "tool-handler":
        node.setdefault("parameters", {})["jsCode"] = tool_handler_js
    if node.get("id") == "persist-transcript":
        params = node.setdefault("parameters", {})
        params["method"] = "POST"
        params["url"] = f"{SB_URL}/rest/v1/chat_messages"
        params["sendHeaders"] = True
        params["headerParameters"] = {
            "parameters": [
                {"name": "apikey", "value": SB_KEY},
                {"name": "Authorization", "value": f"Bearer {SB_KEY}"},
                {"name": "Content-Type", "value": "application/json"},
                {"name": "Prefer", "value": "return=minimal"},
            ]
        }
        params["sendBody"] = True
        params["specifyBody"] = "json"
        params["jsonBody"] = "={{ { session_id: $json.session_id, role: 'user', content: $json.transcript } }}"
        params["options"] = {"response": {"response": {"neverError": True}}}

payload = {
    "name": wf.get("name"),
    "nodes": nodes,
    "connections": wf.get("connections"),
    "settings": wf.get("settings", {}),
}

n8n("POST", f"/workflows/{WF_ID}/deactivate")
updated = n8n("PUT", f"/workflows/{WF_ID}", payload)
active = n8n("POST", f"/workflows/{WF_ID}/activate")

print("updated:", updated.get("id"), "nodes:", len(updated.get("nodes", [])))
print("active:", active.get("active"))
