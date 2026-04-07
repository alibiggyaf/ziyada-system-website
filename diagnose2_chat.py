#!/usr/bin/env python3
"""Deep diagnostic: check credentials, NSI node full config, and create Ziyada chat workflow."""
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

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
            return e.code, {"raw": raw.decode("utf-8","ignore")[:500]}

# List credentials (names only, no secrets)
print("=== CREDENTIALS ===")
st, creds = n8n("GET", "/credentials?limit=50")
if st == 200:
    for c in creds.get("data", []):
        print(f"  ID={c.get('id')} | Type={c.get('type')} | Name={c.get('name')}")
else:
    print(f"  Error {st}: {creds}")

# Get NSI workflow full node details (chatTrigger node specifically)
print("\n=== NSI chatTrigger node (full) ===")
st2, wf = n8n("GET", "/workflows/62MN6oqxOs3levjh")
if st2 == 200:
    for node in wf.get("nodes", []):
        if "chatTrigger" in node.get("type", ""):
            print(json.dumps(node, indent=2))
        if "openAi" in node.get("type","") or "Gemini" in node.get("name","") or "openai" in node.get("type","").lower():
            print(f"  LLM Node: {node.get('name')} credentials={json.dumps(node.get('credentials',{}))}")

# Check execution errors for the NSI workflow
print("\n=== NSI (62MN6oqxOs3levjh) - last 5 executions ===")
st3, execs = n8n("GET", "/executions?workflowId=62MN6oqxOs3levjh&limit=5")
if st3 == 200:
    for e in execs.get("data", []):
        print(f"  id={e.get('id')} status={e.get('status')} started={str(e.get('startedAt',''))[:19]}")
else:
    print(f"  Error {st3}: {execs}")
