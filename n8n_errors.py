#!/usr/bin/env python3
"""Get n8n execution error details."""
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID   = "C8JWsE3KIoxr1KgO"

HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

def n8n(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# Get full data for the 3 most recent error executions
print("FETCHING ERROR EXECUTION DETAILS")
error_ids = [219323, 219320, 219317]

for eid in error_ids:
    print(f"\n{'='*60}")
    print(f"EXECUTION {eid}")
    st, data = n8n("GET", f"/executions/{eid}?includeData=true")
    if st != 200:
        print(f"  Error fetching: {st} {data}")
        continue

    print(f"  status: {data.get('status')}")
    print(f"  startedAt: {data.get('startedAt')}")
    print(f"  stoppedAt: {data.get('stoppedAt')}")
    
    # Look at run data for errors
    run_data = data.get("data", {})
    result_data = run_data.get("resultData", {})
    run_execution = result_data.get("runData", {})
    
    if not run_execution:
        print("  No runData found")
        # Try to get from executionData
        exec_data = run_data.get("executionData", {})
        print(f"  executionData keys: {list(exec_data.keys())[:10]}")
        continue

    print(f"  Nodes executed: {list(run_execution.keys())}")
    
    for node_name, node_runs in run_execution.items():
        for run in node_runs:
            error = run.get("error")
            if error:
                print(f"\n  !! ERROR in node '{node_name}':")
                print(f"     message: {error.get('message','')[:200]}")
                print(f"     description: {str(error.get('description',''))[:200]}")
            # Check output data
            data_out = run.get("data", {}).get("main", [])
            if data_out:
                for branch in data_out:
                    if branch:
                        print(f"  Node '{node_name}' output: {len(branch)} items")
                        if branch:
                            print(f"    first item keys: {list(branch[0].get('json',{}).keys())[:10]}")
