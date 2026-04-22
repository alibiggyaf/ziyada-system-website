#!/usr/bin/env python3
import json, subprocess

N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
SUPABASE_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

def n8n(method, path, data=None):
    cmd = ["curl", "-s", "-X", method, N8N_BASE + "/api/v1" + path,
           "-H", "X-N8N-API-KEY: " + N8N_KEY, "-H", "Content-Type: application/json"]
    if data:
        cmd += ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try: return json.loads(r.stdout)
    except: return {"raw": r.stdout[:300]}

dispatcher_code = (
    "const body = $json.body || $json;\n"
    "const toolCallList = body.message?.toolCallList || body.toolCallList || [];\n"
    "const SB_URL = '" + SUPABASE_URL + "';\n"
    "const SB_KEY = '" + SUPABASE_KEY + "';\n"
    "\n"
    "const services = [\n"
    "  { id: 1, name: 'أتمتة الأعمال', tag: 'الأكثر طلباً', desc: 'سير عمل n8n + AI توفر 40-80 ساعة شهرياً وتربط جميع الأنظمة.' },\n"
    "  { id: 2, name: 'أنظمة المبيعات CRM', tag: 'الأعلى عائداً', desc: 'هندسة HubSpot/Zoho مع متابعة آلية وتقارير مبيعات دقيقة.' },\n"
    "  { id: 3, name: 'توليد العملاء B2B', tag: 'نتائج سريعة', desc: 'ماكينة عملاء تعمل 24/7 بـ LinkedIn Outreach والأتمتة.' },\n"
    "  { id: 4, name: 'التسويق الرقمي وSEO', tag: 'نمو الإيرادات', desc: 'حملات Google وMeta مع تحسين الظهور.' },\n"
    "  { id: 5, name: 'تطوير المواقع والتطبيقات', tag: 'أساسك الرقمي', desc: 'مواقع React سريعة مع لوحات تحكم مخصصة.' },\n"
    "  { id: 6, name: 'إدارة السوشيال ميديا', tag: 'حضور العلامة', desc: 'محتوى آلي وتقارير شهرية.' }\n"
    "];\n"
    "\n"
    "async function sbPost(path, body) {\n"
    "  return fetch(SB_URL + path, { method: 'POST', headers: { 'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY, 'Content-Type': 'application/json', 'Prefer': 'return=minimal' }, body: JSON.stringify(body) });\n"
    "}\n"
    "async function sbGet(path) {\n"
    "  const r = await fetch(SB_URL + path, { headers: { 'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY } });\n"
    "  return r.json();\n"
    "}\n"
    "\n"
    "const results = [];\n"
    "for (const call of toolCallList) {\n"
    "  const fn = call.function?.name || call.name;\n"
    "  const rawArgs = call.function?.arguments || call.arguments || '{}';\n"
    "  const args = typeof rawArgs === 'string' ? JSON.parse(rawArgs) : rawArgs;\n"
    "  let result = '';\n"
    "  try {\n"
    "    if (fn === 'get_services_info') {\n"
    "      result = 'خدمات زيادة سيستم:\\n' + services.map(s => s.id + '. ' + s.name + ' — ' + s.tag + '\\n' + s.desc).join('\\n\\n');\n"
    "    } else if (fn === 'save_lead') {\n"
    "      await sbPost('/rest/v1/leads', { name: args.name||'', email: args.email||'', phone: args.phone||'', company: args.company||'', industry: args.sector||args.industry||'', challenge: args.challenge||'', services_requested: args.service_interest||'', source: 'voice_assistant', language: 'ar', status: 'new' });\n"
    "      result = 'تم تسجيل بياناتك يا ' + (args.name||'أخوي') + '. سيتواصل معك الفريق قريباً إن شاء الله.';\n"
    "    } else if (fn === 'create_booking_request') {\n"
    "      await sbPost('/rest/v1/voice_booking_requests', { name: args.name||'', phone: args.phone||'', service: args.service||'', preferred_datetime: args.preferred_datetime||'', notes: args.notes||'', status: 'pending', source: 'voice_assistant', created_at: new Date().toISOString() });\n"
    "      result = 'أبشر يا ' + (args.name||'أخوي') + '! تم تسجيل طلب الحجز. سيتواصل معك الفريق لتأكيد الموعد.';\n"
    "    } else if (fn === 'get_conversation_history') {\n"
    "      const phone = args.phone || '';\n"
    "      const q = '/rest/v1/chat_messages?order=created_at.asc&limit=8' + (phone ? '&session_id=ilike.*' + phone + '*' : '');\n"
    "      const hist = await sbGet(q);\n"
    "      result = Array.isArray(hist) && hist.length > 0 ? 'المحادثات السابقة:\\n' + hist.map(m => (m.direction==='inbound'?'العميل: ':'المساعد: ') + (m.content||'')).join('\\n') : 'لا توجد محادثات سابقة.';\n"
    "    } else {\n"
    "      result = 'تم تنفيذ ' + fn + '.';\n"
    "    }\n"
    "  } catch(e) { result = 'خطأ: ' + e.message; }\n"
    "  results.push({ toolCallId: call.id, result });\n"
    "}\n"
    "return [{ json: { results } }];"
)

wf = {
    "name": "Ziyada — VAPI Tools Dispatcher",
    "nodes": [
        {
            "id": "wh1",
            "name": "VAPI Tools Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [240, 300],
            "parameters": {"path": "a1b2c3d4-vapi-tools", "httpMethod": "POST", "responseMode": "lastNode", "options": {}}
        },
        {
            "id": "code1",
            "name": "Dispatch Tools",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300],
            "parameters": {"mode": "runOnceForAllItems", "jsCode": dispatcher_code}
        }
    ],
    "connections": {"VAPI Tools Webhook": {"main": [[{"node": "Dispatch Tools", "type": "main", "index": 0}]]}},
    "settings": {"executionOrder": "v1"}
}

r = n8n("POST", "/workflows", wf)
print("Create:", r.get("id"), r.get("name") or r.get("message", ""))

wf_id = r.get("id")
if wf_id:
    act = n8n("POST", f"/workflows/{wf_id}/activate")
    print("Activate:", act)
    print(f"Webhook: {N8N_BASE}/webhook/a1b2c3d4-vapi-tools")
else:
    print("No ID - full response:", r)
