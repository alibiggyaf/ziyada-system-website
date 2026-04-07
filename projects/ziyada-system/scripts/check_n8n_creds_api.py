#!/usr/bin/env python3
"""Check n8n credentials API options and YouTube node compatibility."""
import json
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
HEADERS = {"X-N8N-API-KEY": KEY}

# Try various credential endpoints
endpoints = [
    "/api/v1/credentials",
    "/api/v1/credential",
    "/rest/credentials",
    "/rest/credential-types",
]
for ep in endpoints:
    r = requests.request("GET", f"{BASE}{ep}", headers=HEADERS)
    print(f"GET {ep} -> {r.status_code}")
    if r.status_code == 200:
        d = r.json()
        items = d.get("data", d.get("items", [d] if isinstance(d, dict) else d[:5] if isinstance(d, list) else []))
        for c in items[:20]:
            if isinstance(c, dict):
                print(f"  id={c.get('id')} name={c.get('name')} type={c.get('type')}")
        break

# Check n8n version
rv = requests.get(f"{BASE}/rest/settings", headers=HEADERS)
print(f"\n/rest/settings -> {rv.status_code}")
if rv.status_code == 200:
    s = rv.json()
    print(f"  version: {s.get('data', {}).get('versionCli', s.get('versionCli', '?'))}")

# Check which env vars are set on n8n side (via a dry-run or test node?)
# Try to check if GOOGLE_API_KEY is accessible - this is only visible in workflow execution
# Instead check if there's an existing googleApi credential
r3 = requests.get(f"{BASE}/rest/credentials", headers=HEADERS)
print(f"\n/rest/credentials -> {r3.status_code}")
if r3.status_code == 200:
    data = r3.json()
    items = data.get("data", data if isinstance(data, list) else [])
    for c in items:
        if isinstance(c, dict):
            print(f"  id={c.get('id')} name={c.get('name')} type={c.get('type')}")
