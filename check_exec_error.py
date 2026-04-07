#!/usr/bin/env python3
"""Check the latest execution error details."""
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}

WF_ID = "eO6LzcPrnPT3JlpA"

def n8n(method, path):
    url = f"{N8N_URL}{path}"
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, {"raw": raw.decode("utf-8","ignore")[:1000]}

# Get last execution with data
print("Getting last execution with full data...")
st, execs = n8n("GET", f"/executions?workflowId={WF_ID}&limit=3&includeData=true")
if st == 200:
    for exec_item in execs.get("data", [])[:1]:
        exec_id = exec_item.get("id")
        print(f"Execution ID: {exec_id}")
        print(f"Status: {exec_item.get('status')}")
        
        data = exec_item.get("data", {})
        if data:
            result_data = data.get("resultData", {})
            run_data = result_data.get("runData", {})
            error = result_data.get("error", {})
            
            if error:
                print(f"\nTop-level error: {json.dumps(error, indent=2)[:500]}")
            
            for node_name, node_runs in run_data.items():
                for run in node_runs:
                    if run.get("error"):
                        print(f"\n  Node '{node_name}' ERROR:")
                        print(f"    {json.dumps(run['error'], indent=4)[:500]}")
                    else:
                        output = run.get("data", {}).get("main", [[]])
                        if output and output[0]:
                            print(f"\n  Node '{node_name}' OUTPUT:")
                            print(f"    {str(output[0])[:200]}")
else:
    print(f"Error {st}: {execs}")

# Also try to get execution by ID
print("\n\nGetting last 5 executions list...")
st2, execs2 = n8n("GET", f"/executions?workflowId={WF_ID}&limit=5")
if st2 == 200:
    for e in execs2.get("data", []):
        print(f"  id={e.get('id')} status={e.get('status')} started={str(e.get('startedAt',''))[:19]}")
