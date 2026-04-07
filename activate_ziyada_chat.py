#!/usr/bin/env python3
"""Activate the Ziyada Chat workflow."""
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

WF_ID = "i5t3T3vgM5lFOEWo"
WEBHOOK_ID = "ziyada-web-chat-2026"
WEBHOOK_URL = f"{N8N_BASE}/webhook/{WEBHOOK_ID}/chat"

def n8n(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, {"raw": raw.decode("utf-8","ignore")[:800]}

# Try POST /activate
print(f"Activating workflow {WF_ID}...")
st, result = n8n("POST", f"/workflows/{WF_ID}/activate")
print(f"  POST /activate: {st} -> {result}")

if st != 200:
    # Try GET to see available methods
    print("\nChecking workflow state...")
    st2, wf = n8n("GET", f"/workflows/{WF_ID}")
    print(f"  Active: {wf.get('active')}")
    print(f"  Name: {wf.get('name')}")

    # Try PUT with full workflow body and active=true
    print("\nTrying PUT with active=true...")
    wf["active"] = True
    # Remove read-only fields if needed
    for key in ["createdAt", "updatedAt", "versionId"]:
        wf.pop(key, None)
    st3, r3 = n8n("PUT", f"/workflows/{WF_ID}", wf)
    print(f"  PUT: {st3} -> {json.dumps(r3)[:200]}")

# Test webhook
print(f"\nTesting webhook...")
try:
    payload = json.dumps({
        "action": "sendMessage",
        "chatInput": "Hello, what services does Ziyada System offer?",
        "sessionId": "test-001"
    }).encode()
    req = urllib.request.Request(
        WEBHOOK_URL, data=payload,
        headers={"Content-Type":"application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode()
        print(f"  ✓ {r.status}: {body[:500]}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8","ignore")
    print(f"  ✗ HTTP {e.code}: {body[:500]}")
except Exception as ex:
    print(f"  ✗ Error: {ex}")
