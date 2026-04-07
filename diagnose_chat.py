#!/usr/bin/env python3
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

def n8n(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# Check the erroring workflow
print("=== eXA9AfEnlRdY06kn (erroring workflow) ===")
st, wf = n8n("GET", "/workflows/eXA9AfEnlRdY06kn")
if st == 200:
    print(f"  Name: {wf.get('name')}")
    print(f"  Active: {wf.get('active')}")
    for node in wf.get("nodes", []):
        print(f"  Node: {node.get('name')} | type: {node.get('type')}")
        params = node.get("parameters", {})
        if "chatTrigger" in node.get("type","") or "webhook" in node.get("type","").lower():
            print(f"    params: {json.dumps(params, indent=4)}")
else:
    print(f"  Error {st}: {wf}")

# Check y7gXaTFEyIDOz7uS
print("\n=== y7gXaTFEyIDOz7uS ===")
st2, wf2 = n8n("GET", "/workflows/y7gXaTFEyIDOz7uS")
if st2 == 200:
    print(f"  Name: {wf2.get('name')}")
    print(f"  Active: {wf2.get('active')}")
    for node in wf2.get("nodes", []):
        print(f"  Node: {node.get('name')} | type: {node.get('type')}")
        params = node.get("parameters", {})
        if "chatTrigger" in node.get("type","") or "webhook" in node.get("type","").lower():
            print(f"    params: {json.dumps(params, indent=4)}")
else:
    print(f"  Error {st2}: {wf2}")

# Check Niche Signal Intelligence  
print("\n=== Niche Signal Intelligence (62MN6oqxOs3levjh) ===")
st3, wf3 = n8n("GET", "/workflows/62MN6oqxOs3levjh")
if st3 == 200:
    print(f"  Name: {wf3.get('name')}")
    print(f"  Active: {wf3.get('active')}")
    for node in wf3.get("nodes", []):
        print(f"  Node: {node.get('name')} | type: {node.get('type')}")
        params = node.get("parameters", {})
        if "chatTrigger" in node.get("type","") or "webhook" in node.get("type","").lower():
            print(f"    params: {json.dumps(params, indent=4)}")
else:
    print(f"  Error {st3}: {wf3}")

# Test current chatbot webhook
print("\n=== Testing /webhook/chat ===")
try:
    payload = json.dumps({"action":"sendMessage","chatInput":"hello","sessionId":"test123"}).encode()
    req = urllib.request.Request(
        "https://n8n.srv953562.hstgr.cloud/webhook/chat",
        data=payload,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        print(f"  Status: {r.status}")
        print(f"  Body: {r.read().decode()[:300]}")
except Exception as e:
    print(f"  Error: {e}")

# Test the NSI webhook
print("\n=== Testing /webhook/ff9622a4-a6ec-4396-b9de-c95bd834c23c/chat ===")
try:
    payload = json.dumps({"action":"sendMessage","chatInput":"hello","sessionId":"test123"}).encode()
    req = urllib.request.Request(
        "https://n8n.srv953562.hstgr.cloud/webhook/ff9622a4-a6ec-4396-b9de-c95bd834c23c/chat",
        data=payload,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"  Status: {r.status}")
        print(f"  Body: {r.read().decode()[:300]}")
except Exception as e:
    print(f"  Error: {e}")
