#!/usr/bin/env python3
"""Get n8n success execution details to see what rows are being processed."""
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"

HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}

def n8n(method, path):
    req = urllib.request.Request(f"{N8N_URL}{path}", headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# Get the most recent 3 SUCCESS executions
print("CHECKING MOST RECENT SUCCESS EXECUTIONS")
st, data = n8n("GET", "/executions?limit=20&includeData=false")
success_ids = [e["id"] for e in data.get("data", []) if e.get("status") == "success"][:3]
print(f"Success execution IDs: {success_ids}")

for eid in success_ids:
    print(f"\n{'='*60}")
    print(f"EXECUTION {eid}")
    st2, ex = n8n("GET", f"/executions/{eid}?includeData=true")
    if st2 != 200:
        print(f"  Error: {st2}")
        continue

    run_data = ex.get("data", {}).get("resultData", {}).get("runData", {})
    print(f"  Nodes run: {list(run_data.keys())}")
    
    # Check Read Intake Rows output
    ri = run_data.get("Read Intake Rows", [])
    if ri:
        out = ri[0].get("data", {}).get("main", [[]])
        items = out[0] if out else []
        print(f"  Read Intake Rows → {len(items)} rows returned from sheet")
        for item in items[:5]:
            j = item.get("json", {})
            print(f"    row: {list(j.items())[:6]}")
    else:
        print("  Read Intake Rows: NOT EXECUTED")

    # Check Select New Intake Rows (filter)
    si = run_data.get("Select New Intake Rows", [])
    if si:
        out = si[0].get("data", {}).get("main", [[]])
        items = out[0] if out else []
        print(f"  Select New Intake Rows → {len(items)} rows after filtering")
        for item in items[:3]:
            j = item.get("json", {})
            cn = j.get("company_name") or j.get("companyName") or j.get("row_number", "?")
            status = j.get("trigger_status") or j.get("send_status") or j.get("status","?")
            print(f"    company={cn} status={status}")
    else:
        print("  Select New Intake Rows: NOT EXECUTED / 0 items")

    # Check for any errors
    for node_name, node_runs in run_data.items():
        for run in node_runs:
            err = run.get("error")
            if err:
                print(f"  !! ERROR in '{node_name}': {err.get('message','')[:150]}")
