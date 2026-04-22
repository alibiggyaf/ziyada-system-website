#!/usr/bin/env python3
import json, subprocess

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
    except:
        return {"raw": r.stdout, "stderr": r.stderr}

wf = n8n("GET", f"/workflows/{WF_ID}")
nodes = wf.get("nodes", [])

normalize_js = f"""const rawBody = $json.body || $json;
const toolCallList = rawBody.message && rawBody.message.toolCallList ? rawBody.message.toolCallList : rawBody.toolCallList || null;
if (toolCallList && toolCallList.length > 0) {{
  return [{{ json: {{ _mode: 'tool_call', toolCallList }} }}];
}}

const p = rawBody.voice || rawBody;
const transcript = String(p.transcript || '').trim();
if (!transcript) throw new Error('Missing transcript');

const normalizedPhone = String(p.phone_e164 || p.phone || '').replace(/\s+/g, '');
const sessionId = p.session_id || (normalizedPhone ? ('phone-' + normalizedPhone) : ('voice-' + Date.now()));

try {{
  await this.helpers.httpRequest({{
    method: 'POST',
    url: '{SB_URL}/rest/v1/chat_sessions?on_conflict=session_id',
    headers: {{
      apikey: '{SB_KEY}',
      Authorization: 'Bearer {SB_KEY}',
      'Content-Type': 'application/json',
      Prefer: 'resolution=merge-duplicates,return=minimal'
    }},
    body: {{ session_id: sessionId }},
    json: true,
  }});
}} catch (e) {{
  // Non-blocking: voice flow should continue even if session upsert fails
}}

const arabicRegex = /[\u0600-\u06ff]/g;
const language = p.language || (arabicRegex.test(transcript) ? 'ar' : 'en');

return [{{
  json: {{
    _mode: 'voice',
    session_id: sessionId,
    message_id: p.message_id || ('msg-' + Date.now()),
    event_ts: p.timestamp || new Date().toISOString(),
    transcript,
    language,
    provider: p.provider || 'vapi',
    phone_e164: normalizedPhone,
    call_id: p.call_id || ''
  }}
}}];"""

for node in nodes:
    if node.get("id") == "normalize-voice":
        node["parameters"]["jsCode"] = normalize_js
    if node.get("id") == "persist-transcript":
        node["parameters"]["url"] = f"{SB_URL}/rest/v1/chat_messages"
        node["parameters"]["jsonBody"] = "={{ { session_id: $json.session_id, role: 'user', content: $json.transcript } }}"
    if node.get("id") == "tool-handler":
        js = node["parameters"].get("jsCode", "")
        js = js.replace(
            "const marker = phone ? ('[phone:' + phone + ']') : '';\n      const url = 'https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/chat_messages?select=session_id,role,content,created_at&order=created_at.asc&limit=12' + (marker ? ('&content=ilike.*' + encodeURIComponent(marker) + '*') : '');",
            "const sessionKey = phone ? ('phone-' + phone) : '';\n      const url = 'https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/chat_messages?select=session_id,role,content,created_at&order=created_at.asc&limit=12' + (sessionKey ? ('&session_id=eq.' + encodeURIComponent(sessionKey)) : '');"
        )
        node["parameters"]["jsCode"] = js

payload = {
    "name": wf.get("name"),
    "nodes": nodes,
    "connections": wf.get("connections"),
    "settings": wf.get("settings", {}),
}

n8n("POST", f"/workflows/{WF_ID}/deactivate")
upd = n8n("PUT", f"/workflows/{WF_ID}", payload)
act = n8n("POST", f"/workflows/{WF_ID}/activate")
print("updated:", upd.get("id"), "active:", act.get("active"))
