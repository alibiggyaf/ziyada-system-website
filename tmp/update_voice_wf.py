#!/usr/bin/env python3
"""Update existing voice workflow to handle both voice transcripts and VAPI tool calls"""
import json, subprocess

N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
WF_ID = "qHAIKXEV4SW8r5Nx"
SB_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

def n8n(method, path, data=None):
    cmd = ["curl", "-s", "-X", method, N8N_BASE + "/api/v1" + path,
           "-H", "X-N8N-API-KEY: " + N8N_KEY, "-H", "Content-Type: application/json"]
    if data:
        cmd += ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try: return json.loads(r.stdout)
    except: return {"raw": r.stdout[:300]}

# Fetch current workflow
d = n8n("GET", f"/workflows/{WF_ID}")
print("Fetched workflow:", d.get("name"), "nodes:", len(d.get("nodes", [])))

# Node: updated normalize that routes by mode
new_normalize = (
    "const rawBody = $json.body || $json;\n"
    "// VAPI Tool Call routing\n"
    "const toolCallList = rawBody.message && rawBody.message.toolCallList\n"
    "  ? rawBody.message.toolCallList\n"
    "  : rawBody.toolCallList || null;\n"
    "if (toolCallList && toolCallList.length > 0) {\n"
    "  return [{ json: { _mode: 'tool_call', toolCallList } }];\n"
    "}\n"
    "// Normal voice transcript routing\n"
    "const p = rawBody.voice || rawBody;\n"
    "const transcript = String(p.transcript || '').trim();\n"
    "if (!transcript) throw new Error('Missing transcript');\n"
    "const arabicRegex = /[\\u0600-\\u06ff]/g;\n"
    "const language = p.language || (arabicRegex.test(transcript) ? 'ar' : 'en');\n"
    "return [{\n"
    "  json: {\n"
    "    _mode: 'voice',\n"
    "    session_id: p.session_id || ('voice-' + Date.now()),\n"
    "    message_id: p.message_id || ('msg-' + Date.now()),\n"
    "    event_ts: p.timestamp || new Date().toISOString(),\n"
    "    transcript,\n"
    "    language,\n"
    "    provider: p.provider || 'vapi',\n"
    "    phone_e164: p.phone_e164 || p.phone || '',\n"
    "    call_id: p.call_id || ''\n"
    "  }\n"
    "}];\n"
)

# Node: tool handler with all 4 functions + Supabase
tool_handler = (
    "const items = $input.all();\n"
    "const toolCallList = items[0] && items[0].json && items[0].json.toolCallList ? items[0].json.toolCallList : [];\n"
    "const SB_URL = '" + SB_URL + "';\n"
    "const SB_KEY = '" + SB_KEY + "';\n"
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
    "  try { await fetch(SB_URL + path, { method: 'POST', headers: { apikey: SB_KEY, Authorization: 'Bearer ' + SB_KEY, 'Content-Type': 'application/json', Prefer: 'return=minimal' }, body: JSON.stringify(body) }); } catch(e) {}\n"
    "}\n"
    "async function sbGet(path) {\n"
    "  try { const r = await fetch(SB_URL + path, { headers: { apikey: SB_KEY, Authorization: 'Bearer ' + SB_KEY } }); return await r.json(); } catch(e) { return []; }\n"
    "}\n"
    "\n"
    "const results = [];\n"
    "for (const call of toolCallList) {\n"
    "  const fn = (call.function && call.function.name) || call.name || '';\n"
    "  const rawArgs = (call.function && call.function.arguments) || call.arguments || '{}';\n"
    "  const args = typeof rawArgs === 'string' ? JSON.parse(rawArgs) : rawArgs;\n"
    "  let result = '';\n"
    "  try {\n"
    "    if (fn === 'get_services_info') {\n"
    "      result = 'خدمات زيادة سيستم:\\n' + services.map(function(s){ return s.id + '. ' + s.name + ' — ' + s.tag + '\\n' + s.desc; }).join('\\n\\n');\n"
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
    "      result = Array.isArray(hist) && hist.length > 0 ? 'المحادثات السابقة:\\n' + hist.map(function(m){ return (m.direction==='inbound'?'العميل: ':'المساعد: ') + (m.content||''); }).join('\\n') : 'لا توجد محادثات سابقة.';\n"
    "    } else {\n"
    "      result = 'تم تنفيذ ' + fn + '.';\n"
    "    }\n"
    "  } catch(e) { result = 'خطأ: ' + e.message; }\n"
    "  results.push({ toolCallId: call.id, result });\n"
    "}\n"
    "return [{ json: { results } }];\n"
)

# Update normalize node code
nodes = d.get("nodes", [])
for i, node in enumerate(nodes):
    if node["id"] == "normalize-voice":
        nodes[i]["parameters"]["jsCode"] = new_normalize
        print("Updated normalize-voice node")

# Check if tool-handler and route-mode already exist
existing_ids = {n["id"] for n in nodes}

if "route-mode" not in existing_ids:
    nodes.append({
        "id": "route-mode",
        "name": "Route Mode",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [680, 300],
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{
                    "id": "c1",
                    "leftValue": "={{ $json._mode }}",
                    "rightValue": "tool_call",
                    "operator": {"type": "string", "operation": "equals"}
                }],
                "combinator": "and"
            },
            "options": {}
        }
    })
    print("Added route-mode node")

if "tool-handler" not in existing_ids:
    nodes.append({
        "id": "tool-handler",
        "name": "Handle Tool Calls",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [900, 180],
        "parameters": {"mode": "runOnceForAllItems", "jsCode": tool_handler}
    })
    print("Added tool-handler node")

# Rebuild connections
conn = d.get("connections", {})

# Normalize -> Route Mode (was: Normalize -> Persist)
conn["Validate and Normalize Voice"] = {
    "main": [[{"node": "Route Mode", "type": "main", "index": 0}]]
}

# Route Mode: true (tool_call) -> Handle Tool Calls, false (voice) -> Persist Transcript
conn["Route Mode"] = {
    "main": [
        [{"node": "Handle Tool Calls", "type": "main", "index": 0}],  # output 0 = true
        [{"node": "Persist Transcript Supabase", "type": "main", "index": 0}]   # output 1 = false
    ]
}

d["nodes"] = nodes
d["connections"] = conn

# Build PUT payload (only send what n8n accepts)
put_payload = {
    "name": d["name"],
    "nodes": nodes,
    "connections": conn,
    "settings": d.get("settings", {"executionOrder": "v1"})
}

# Deactivate, update, reactivate
print("Deactivating...")
n8n("POST", f"/workflows/{WF_ID}/deactivate")

print("Updating...")
result = n8n("PUT", f"/workflows/{WF_ID}", put_payload)
if result.get("id"):
    print("Updated OK:", result.get("name"), "nodes:", len(result.get("nodes", [])))
else:
    print("Update failed:", result)

print("Reactivating...")
act = n8n("POST", f"/workflows/{WF_ID}/activate")
print("Active:", act.get("active"))

# Test tool call
import time
time.sleep(2)
print("\nTesting tool call on voice-ingress-webhook...")
test_cmd = [
    "curl", "-s", "-X", "POST",
    "https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook",
    "-H", "Content-Type: application/json",
    "-d", json.dumps({
        "message": {
            "toolCallList": [{
                "id": "test-tc-1",
                "function": {"name": "get_services_info", "arguments": "{}"}
            }]
        }
    })
]
import subprocess
r = subprocess.run(test_cmd, capture_output=True, text=True)
print("Response:", r.stdout[:500])

print("\nTesting voice transcript still works...")
test_voice = [
    "curl", "-s", "-X", "POST",
    "https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook",
    "-H", "Content-Type: application/json",
    "-d", json.dumps({"voice": {"session_id": "test-123", "transcript": "وش خدمات زيادة سيستم؟", "language": "ar", "provider": "vapi"}})
]
r2 = subprocess.run(test_voice, capture_output=True, text=True)
print("Voice response:", r2.stdout[:200])
