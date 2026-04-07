#!/usr/bin/env python3
"""Inspect workflow 62 nodes and list available credentials."""
import json
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
HEADERS = {"X-N8N-API-KEY": KEY}

# 1. Fetch workflow 62
r = requests.get(f"{BASE}/api/v1/workflows/62MN6oqxOs3levjh", headers=HEADERS)
print(f"Workflow fetch status: {r.status_code}")
wf = r.json()
print(f"Name: {wf.get('name')}  Active: {wf.get('active')}")
print()

# 2. Show get_videos1 and find_video_data1 full node JSON
for node in wf.get("nodes", []):
    if node["name"] in ["get_videos1", "find_video_data1"]:
        print(f"=== {node['name']} ===")
        print(json.dumps({k: v for k, v in node.items() if k != "position"}, indent=2))
        print()

# 3. Save full workflow locally for reference
out_path = "projects/ziyada-system/workflows/workflow_62_snapshot.json"
import os
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump(wf, f, indent=2)
print(f"Saved snapshot to {out_path}")
print()

# 4. List available credentials
r2 = requests.get(f"{BASE}/api/v1/credentials", headers=HEADERS)
print(f"Credentials status: {r2.status_code}")
creds_data = r2.json()
items = creds_data.get("data", creds_data.get("items", []))
for c in items:
    print(f"  id={c['id']}  name={c['name']}  type={c['type']}")
