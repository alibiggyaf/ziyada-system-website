#!/usr/bin/env python3
import json
import subprocess

N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
WF_ID = "qHAIKXEV4SW8r5Nx"
SB_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"


def n8n(method, path, data=None):
    cmd = [
        "curl",
        "-s",
        "-X",
        method,
        f"{N8N_BASE}/api/v1{path}",
        "-H",
        f"X-N8N-API-KEY: {N8N_KEY}",
        "-H",
        "Content-Type: application/json",
    ]
    if data is not None:
        cmd += ["-d", json.dumps(data, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"raw": r.stdout, "stderr": r.stderr}


wf = n8n("GET", f"/workflows/{WF_ID}")

new_js = f"""const items = $input.all();
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
  const res = await fetch(SB_URL + path, {{
    headers: {{ apikey: SB_KEY, Authorization: 'Bearer ' + SB_KEY }}
  }});
  if (!res.ok) return [];
  try {{ return await res.json(); }} catch(e) {{ return []; }}
}}

const results = [];
for (const call of toolCallList) {{
  const fn = (call.function && call.function.name) || call.name || '';
  const rawArgs = (call.function && call.function.arguments) || call.arguments || '{{}}';
  const args = typeof rawArgs === 'string' ? JSON.parse(rawArgs) : rawArgs;
  let result = '';

  try {{
    if (fn === 'get_services_info') {{
      result = 'خدمات زيادة سيستم:\\n' + services.map(function(s) {{ return s.id + '. ' + s.name + ' — ' + s.tag + '\\n' + s.desc; }}).join('\\n\\n');
    }} else if (fn === 'save_lead') {{
      const write = await sbPost('/rest/v1/voice_assistant_leads', {{
        name: args.name || '',
        phone: args.phone || '',
        email: args.email || '',
        service_interest: args.service_interest || '',
        source: 'voice_assistant',
        created_at: new Date().toISOString()
      }});
      if (write.ok) {{
        result = 'تم تسجيل بياناتك يا ' + (args.name || 'أخوي') + '. سيتواصل معك الفريق قريباً إن شاء الله.';
      }} else {{
        result = 'ثواني عن إذنك، صار خطأ تقني أثناء حفظ بياناتك. ممكن أعيد المحاولة؟';
      }}
    }} else if (fn === 'create_booking_request') {{
      const write = await sbPost('/rest/v1/voice_booking_requests', {{
        name: args.name || '',
        phone: args.phone || '',
        service: args.service || '',
        preferred_datetime: args.preferred_datetime || '',
        notes: args.notes || '',
        status: 'pending',
        source: 'voice_assistant',
        created_at: new Date().toISOString()
      }});
      if (write.ok) {{
        result = 'أبشر يا ' + (args.name || 'أخوي') + '! تم تسجيل طلب الحجز. سيتواصل معك الفريق لتأكيد الموعد.';
      }} else {{
        result = 'لحظة من فضلك، ما قدرنا نسجل الحجز الآن بسبب خطأ تقني. ممكن أعيد المحاولة؟';
      }}
    }} else if (fn === 'get_conversation_history') {{
      const phone = args.phone || '';
      const q = '/rest/v1/chat_messages?order=created_at.asc&limit=8' + (phone ? '&session_id=ilike.*' + phone + '*' : '');
      const hist = await sbGet(q);
      result = Array.isArray(hist) && hist.length > 0
        ? 'المحادثات السابقة:\\n' + hist.map(function(m) {{ return (m.direction === 'inbound' ? 'العميل: ' : 'المساعد: ') + (m.content || ''); }}).join('\\n')
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
        node["parameters"]["jsCode"] = new_js

payload = {
    "name": wf.get("name"),
    "nodes": wf.get("nodes"),
    "connections": wf.get("connections"),
    "settings": wf.get("settings", {}),
}

n8n("POST", f"/workflows/{WF_ID}/deactivate")
updated = n8n("PUT", f"/workflows/{WF_ID}", payload)
react = n8n("POST", f"/workflows/{WF_ID}/activate")

print("updated nodes:", len(updated.get("nodes", [])))
print("active:", react.get("active"))
