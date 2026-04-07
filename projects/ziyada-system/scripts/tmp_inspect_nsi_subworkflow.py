#!/usr/bin/env python3
import json
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
H = {"X-N8N-API-KEY": KEY}

for wf_id in ["INHDUWqaC4WMae1R", "N9DveO781xbNf8qs", "62MN6oqxOs3levjh"]:
    r = requests.get(f"{BASE}/api/v1/workflows/{wf_id}", headers=H, timeout=20)
    print("---", wf_id, "status", r.status_code)
    if r.status_code != 200:
        print(r.text[:400])
        continue
    wf = r.json()
    print("name:", wf.get("name"), "active:", wf.get("active"))
    nodes = wf.get("nodes", [])
    types = [n.get("type") for n in nodes]
    print("node_count:", len(nodes))
    print("has_execute_workflow_trigger:", any(t == "n8n-nodes-base.executeWorkflowTrigger" for t in types))
    print("has_youtube_node:", any(t == "n8n-nodes-base.youTube" for t in types))
    for n in nodes[:8]:
        print(" -", n.get("name"), "::", n.get("type"))
    print()
