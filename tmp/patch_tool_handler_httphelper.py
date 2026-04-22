#!/usr/bin/env python3
import json, subprocess

N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
WF_ID = "qHAIKXEV4SW8r5Nx"
SB_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

def n8n(method, path, data=None):
    cmd = ["curl","-s","-X",method,f"{N8N_BASE}/api/v1{path}","-H",f"X-N8N-API-KEY: {N8N_KEY}","-H","Content-Type: application/json"]
    if data is not None:
        cmd += ["-d", json.dumps(data, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try: return json.loads(r.stdout)
    except: return {"raw": r.stdout, "stderr": r.stderr}

wf = n8n("GET", f"/workflows/{WF_ID}")

js = f"""const items = $input.all();
const toolCallList = items[0]?.json?.toolCallList || [];

function headers() {{
  return {{
    apikey: '{SB_KEY}',
    Authorization: 'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    Prefer: 'return=representation'
  }};
}}

const services = [
  {{ id: 1, name: 'أتمتة الأعمال', tag: 'الأكثر طلباً', desc: 'سير عمل n8n + AI توفر 40-80 ساعة شهرياً وتربط جميع الأنظمة.' }},
  {{ id: 2, name: 'أنظمة المبيعات CRM', tag: 'الأعلى عائداً', desc: 'هندسة HubSpot/Zoho مع متابعة آلية وتقارير مبيعات دقيقة.' }},
  {{ id: 3, name: 'توليد العملاء B2B', tag: 'نتائج سريعة', desc: 'ماكينة عملاء تعمل 24/7 بـ LinkedIn Outreach والأتمتة.' }},
  {{ id: 4, name: 'التسويق الرقمي وSEO', tag: 'نمو الإيرادات', desc: 'حملات Google وMeta مع تحسين الظهور.' }},
  {{ id: 5, name: 'تطوير المواقع والتطبيقات', tag: 'أساسك الرقمي', desc: 'مواقع React سريعة مع لوحات تحكم مخصصة.' }},
  {{ id: 6, name: 'إدارة السوشيال ميديا', tag: 'حضور العلامة', desc: 'محتوى آلي وتقارير شهرية.' }}
];

function fallbackEmailFromPhone(phone) {{
  const p = String(phone || '').replace(/[^0-9+]/g, '');
  return p ? ('voice-' + p.replace(/\+/g, '') + '@ziyada.local') : 'voice-unknown@ziyada.local';
}}

function guessBookingDateTime(input) {{
  const now = new Date();
  const date = now.toISOString().slice(0, 10);
  let time = '10:00';
  const txt = String(input || '');
  const m = txt.match(/(\d{{1,2}}):(\d{{2}})/);
  if (m) time = m[1].padStart(2, '0') + ':' + m[2];
  return {{ date, time }};
}}

const results = [];

for (const call of toolCallList) {{
  const fn = call.function?.name || call.name || '';
  const rawArgs = call.function?.arguments || call.arguments || '{{}}';
  const args = typeof rawArgs === 'string' ? JSON.parse(rawArgs) : rawArgs;

  let result = '';
  try {{
    if (fn === 'get_services_info') {{
      result = 'خدمات زيادة سيستم:\\n' + services.map(s => s.id + '. ' + s.name + ' — ' + s.tag + '\\n' + s.desc).join('\\n\\n');
    }} else if (fn === 'save_lead') {{
      const payload = {{
        name: args.name || null,
        email: args.email || fallbackEmailFromPhone(args.phone),
        phone: args.phone || null,
        services_requested: args.service_interest ? [String(args.service_interest)] : [],
        source: 'voice_assistant',
        language: 'ar',
        status: 'new'
      }};
      await this.helpers.httpRequest({{
        method: 'POST',
        url: '{SB_URL}/rest/v1/leads',
        headers: headers(),
        body: payload,
        json: true,
      }});
      result = 'تم تسجيل بياناتك يا ' + (args.name || 'أخوي') + '. سيتواصل معك الفريق قريباً إن شاء الله.';
    }} else if (fn === 'create_booking_request') {{
      const dt = guessBookingDateTime(args.preferred_datetime || '');
      const payload = {{
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
      }};
      await this.helpers.httpRequest({{
        method: 'POST',
        url: '{SB_URL}/rest/v1/bookings',
        headers: headers(),
        body: payload,
        json: true,
      }});
      result = 'أبشر يا ' + (args.name || 'أخوي') + '! تم تسجيل طلب الحجز. سيتواصل معك الفريق لتأكيد الموعد.';
    }} else if (fn === 'get_conversation_history') {{
      const phone = String(args.phone || '').trim();
      const sessionKey = phone ? ('phone-' + phone) : '';
      const url = '{SB_URL}/rest/v1/chat_messages?select=session_id,role,content,created_at&order=created_at.asc&limit=12' + (sessionKey ? ('&session_id=eq.' + encodeURIComponent(sessionKey)) : '');
      const hist = await this.helpers.httpRequest({{
        method: 'GET',
        url,
        headers: headers(),
        json: true,
      }});
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

return [{{ json: {{ results }} }}];
"""

for node in wf.get("nodes", []):
    if node.get("id") == "tool-handler":
        node["parameters"]["jsCode"] = js

payload = {
    "name": wf.get("name"),
    "nodes": wf.get("nodes"),
    "connections": wf.get("connections"),
    "settings": wf.get("settings", {}),
}

n8n("POST", f"/workflows/{WF_ID}/deactivate")
upd = n8n("PUT", f"/workflows/{WF_ID}", payload)
act = n8n("POST", f"/workflows/{WF_ID}/activate")
print("updated:", upd.get("id"), "active:", act.get("active"))
