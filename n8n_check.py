#!/usr/bin/env python3
"""Check n8n workflow status and fix ContentResults tab issue."""
import json, os, sys, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID   = "C8JWsE3KIoxr1KgO"

HEADERS = {
    "X-N8N-API-KEY": N8N_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def n8n(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# 1) Workflow status
print("=" * 60)
print("WORKFLOW STATUS")
st, wf = n8n("GET", f"/workflows/{WF_ID}")
print(f"  Status: {st}")
if st == 200:
    print(f"  Name:   {wf.get('name')}")
    print(f"  Active: {wf.get('active')}")

# 2) Last 10 executions
print()
print("LAST 10 EXECUTIONS")
st2, ex = n8n("GET", "/executions?limit=10&includeData=false")
if st2 == 200:
    for e in ex.get("data", []):
        print(f"  id={e.get('id')} status={e.get('status')} started={str(e.get('startedAt',''))[:19]}")
else:
    print(f"  Error {st2}: {ex}")

# 3) Scan workflow nodes for sheet tab references
if st == 200:
    print()
    print("SHEET TAB REFERENCES IN WORKFLOW NODES")
    for node in wf.get("nodes", []):
        params = node.get("parameters", {})
        for k, v in params.items():
            sv = str(v)
            if "resault" in sv.lower() or "contentresult" in sv.lower() or "content intake" in sv.lower():
                print(f"  Node '{node.get('name')}' param '{k}': {sv[:120]}")
        # Check nested options
        options = params.get("options", {})
        if isinstance(options, dict):
            for k2, v2 in options.items():
                sv2 = str(v2)
                if "resault" in sv2.lower() or "contentresult" in sv2.lower() or "content intake" in sv2.lower():
                    print(f"  Node '{node.get('name')}' options.{k2}: {sv2[:120]}")

print()
print("DONE")
