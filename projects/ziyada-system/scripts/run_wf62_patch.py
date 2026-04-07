#!/usr/bin/env python3
"""
run_wf62_patch.py — Patch workflow 62 to reference the new Youtube Search sub-workflow.
Sub-workflow was already created with id=INHDUWqaC4WMae1R.
"""
import sys
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJu"
    "OG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcy"
    "MDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
)
H = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}
WF62 = "62MN6oqxOs3levjh"
SUB_ID = "INHDUWqaC4WMae1R"  # Created in previous run
WORKFLOW_NAME = "Niche Signal Intelligence Workflow"
SUBWORKFLOW_NAME = "Niche Signal Search Tool"

# Fetch current workflow 62
r = requests.get(f"{BASE}/api/v1/workflows/{WF62}", headers=H)
wf = r.json()
print("Fetched workflow:", wf.get("name"), "active:", wf.get("active"))

# Update the youtube_search node reference
updated = False
for node in wf.get("nodes", []):
    if node["name"] == "youtube_search":
        old = node["parameters"].get("workflowId", {}).get("value", "?")
        node["parameters"]["workflowId"] = {
            "__rl": True,
            "mode": "list",
            "value": SUB_ID,
            "cachedResultName": SUBWORKFLOW_NAME,
        }
        print(f"Patching youtube_search: {old} -> {SUB_ID}")
        updated = True
        break

if not updated:
    print("ERROR: youtube_search node not found")
    sys.exit(1)

# Print top-level keys to debug
print("Top-level wf keys:", list(wf.keys()))

# Identify which keys might cause "additional properties" error
# Try with progressively fewer keys
allowed_top = {"name", "nodes", "connections", "settings"}
put_body = {k: v for k, v in wf.items() if k in allowed_top}
put_body["name"] = WORKFLOW_NAME

# Clean each node to only have standard fields
node_allowed = {"id", "name", "type", "typeVersion", "position",
                "parameters", "credentials", "disabled",
                "continueOnFail", "alwaysOutputData", "notes",
                "notesInFlow", "onError", "retryOnFail",
                "maxTries", "waitBetweenTries", "executeOnce"}
print("Sample node keys (first node):", list(wf["nodes"][0].keys()) if wf["nodes"] else [])
put_body["nodes"] = [{k: v for k, v in n.items() if k in node_allowed}
                     for n in wf["nodes"]]

print(f"Sending PUT with {len(put_body)} top-level keys: {list(put_body.keys())}")

r2 = requests.put(f"{BASE}/api/v1/workflows/{WF62}", headers=H, json=put_body)
print(f"PUT status: {r2.status_code}")
if r2.status_code not in (200, 201):
    print("Error:", r2.text[:800])
    sys.exit(1)

# Re-activate
r3 = requests.post(f"{BASE}/api/v1/workflows/{WF62}/activate", headers=H)
print(f"Activate status: {r3.status_code}")

# Verify
check = requests.get(f"{BASE}/api/v1/workflows/{WF62}", headers=H).json()
print(f"Verification — active={check.get('active')}")
for n in check.get("nodes", []):
    if n["name"] == "youtube_search":
        ref = n["parameters"].get("workflowId", {})
        print(f"  youtube_search -> id={ref.get('value')}  name={ref.get('cachedResultName')}")
        break

print("Done.")
