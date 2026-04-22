#!/usr/bin/env python3
import json, subprocess

N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
WF_ID = "qHAIKXEV4SW8r5Nx"
SB_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"
CHAT_SESSION_ID = "00000000-0000-4000-8000-000000000001"


def curl_json(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except:
        return {"raw": r.stdout, "stderr": r.stderr}


def n8n(method, path, data=None):
    cmd = ["curl", "-s", "-X", method, f"{N8N_BASE}/api/v1{path}", "-H", f"X-N8N-API-KEY: {N8N_KEY}", "-H", "Content-Type: application/json"]
    if data is not None:
        cmd += ["-d", json.dumps(data, ensure_ascii=False)]
    return curl_json(cmd)

# Ensure chat_sessions row exists
cmd = [
    "curl", "-s", "-X", "POST", f"{SB_URL}/rest/v1/chat_sessions",
    "-H", f"apikey: {SB_KEY}",
    "-H", f"Authorization: Bearer {SB_KEY}",
    "-H", "Content-Type: application/json",
    "-H", "Prefer: resolution=merge-duplicates,return=representation",
    "-d", json.dumps({"id": CHAT_SESSION_ID}),
]
sess = curl_json(cmd)
print("chat_session upsert:", str(sess)[:180])

wf = n8n("GET", f"/workflows/{WF_ID}")
nodes = wf.get("nodes", [])

for node in nodes:
    if node.get("id") == "persist-transcript":
        node["parameters"]["url"] = f"{SB_URL}/rest/v1/chat_messages"
        node["parameters"]["jsonBody"] = "={{ { session_id: '" + CHAT_SESSION_ID + "', role: 'user', content: ('[phone:' + ($json.phone_e164 || 'unknown') + '] ' + $json.transcript) } }}"
    if node.get("id") == "tool-handler":
        js = node["parameters"].get("jsCode", "")
        js = js.replace(
            "const sessionKey = phone ? ('phone-' + phone) : '';\n      const url = 'https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/chat_messages?select=session_id,role,content,created_at&order=created_at.asc&limit=12' + (sessionKey ? ('&session_id=eq.' + encodeURIComponent(sessionKey)) : '');",
            "const marker = phone ? ('[phone:' + phone + ']') : '';\n      const url = 'https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/chat_messages?select=session_id,role,content,created_at&order=created_at.asc&limit=12' + (marker ? ('&content=ilike.*' + encodeURIComponent(marker) + '*') : '');"
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
