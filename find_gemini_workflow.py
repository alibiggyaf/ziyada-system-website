#!/usr/bin/env python3
"""Find the Gemini Flash chat workflow and get its webhook details."""
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
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
            return e.code, {"raw": raw.decode("utf-8","ignore")[:800]}

# Search ALL workflows for the Gemini/chat one
print("=== ALL WORKFLOWS (searching for Gemini/chat) ===")
st, data = n8n("GET", "/workflows?limit=100")
target_wf = None
if st == 200:
    all_wfs = data.get("data", [])
    for wf in all_wfs:
        name = wf.get("name", "")
        if "gemini" in name.lower() or "chat" in name.lower() or "ziyada" in name.lower() and "widget" in name.lower():
            print(f"  *** MATCH: ID={wf['id']} | Active={wf.get('active')} | Name={name}")
            if "gemini" in name.lower() or ("chat" in name.lower() and "widget" in name.lower()):
                target_wf = wf['id']
        else:
            print(f"  ID={wf['id']} | Active={wf.get('active')} | Name={name}")

if target_wf:
    print(f"\n=== FOUND TARGET: {target_wf} ===")
    st2, wf_detail = n8n("GET", f"/workflows/{target_wf}")
    if st2 == 200:
        print(f"  Name: {wf_detail.get('name')}")
        print(f"  Active: {wf_detail.get('active')}")
        for node in wf_detail.get("nodes", []):
            ntype = node.get("type","")
            print(f"  Node: {node.get('name')} | type: {ntype}")
            if "chatTrigger" in ntype or "webhook" in ntype.lower():
                print(f"    PARAMS: {json.dumps(node.get('parameters',{}), indent=6)}")
                print(f"    webhookId: {node.get('webhookId','N/A')}")
