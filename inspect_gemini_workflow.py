#!/usr/bin/env python3
"""Get full details of Ziyada Chat Widget - Gemini Flash workflow and test its webhook."""
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

WF_ID = "eO6LzcPrnPT3JlpA"  # Ziyada Chat Widget - Gemini Flash (Cheapest)

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
            return e.code, {"raw": raw.decode("utf-8","ignore")[:1000]}

print(f"=== Ziyada Chat Widget - Gemini Flash ({WF_ID}) ===")
st, wf = n8n("GET", f"/workflows/{WF_ID}")
if st == 200:
    print(f"  Name: {wf.get('name')}")
    print(f"  Active: {wf.get('active')}")
    webhook_id = None
    for node in wf.get("nodes", []):
        ntype = node.get("type","")
        name = node.get("name","")
        print(f"\n  Node: {name}")
        print(f"    type: {ntype}")
        params = node.get("parameters", {})
        if params:
            print(f"    parameters: {json.dumps(params, indent=6)}")
        creds = node.get("credentials", {})
        if creds:
            print(f"    credentials: {json.dumps(creds)}")
        wh_id = node.get("webhookId")
        if wh_id:
            print(f"    webhookId: {wh_id}")
            webhook_id = wh_id
    
    if webhook_id:
        print(f"\n=== WEBHOOK DETAILS ===")
        # chatTrigger uses the webhookId as path
        # URL format: /webhook/<webhookId>/chat  OR just /webhook/<webhookId>
        urls_to_test = [
            f"{N8N_BASE}/webhook/{webhook_id}/chat",
            f"{N8N_BASE}/webhook/{webhook_id}",
        ]
        for url in urls_to_test:
            print(f"\n  Testing: POST {url}")
            try:
                payload = json.dumps({
                    "action": "sendMessage",
                    "chatInput": "ما هي خدمات زيادة سيستم؟",
                    "sessionId": "test-gemini-001"
                }).encode()
                req = urllib.request.Request(url, data=payload, headers={"Content-Type":"application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=30) as r:
                    body = r.read().decode()
                    print(f"  ✓ {r.status}: {body[:500]}")
                    break
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8","ignore")
                print(f"  ✗ HTTP {e.code}: {body[:400]}")
            except Exception as ex:
                print(f"  ✗ Error: {ex}")
else:
    print(f"Error {st}: {wf}")

# Also check last executions
print(f"\n=== Last 5 executions of {WF_ID} ===")
st2, execs = n8n("GET", f"/executions?workflowId={WF_ID}&limit=5")
if st2 == 200:
    for e in execs.get("data", []):
        print(f"  id={e.get('id')} status={e.get('status')} started={str(e.get('startedAt',''))[:19]}")
else:
    print(f"  Error {st2}: {execs}")
