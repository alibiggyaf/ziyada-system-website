#!/usr/bin/env python3
import json, urllib.request, urllib.parse

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID = "C8JWsE3KIoxr1KgO"

headers = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}

def get(path):
    req = urllib.request.Request(f"{N8N_URL}{path}", headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Pull many recent executions and filter by workflowId locally
raw = get('/executions?limit=100&includeData=false')
all_execs = raw.get('data', [])
blog_execs = [e for e in all_execs if str(e.get('workflowId')) == WF_ID]

print(f"Total recent executions fetched: {len(all_execs)}")
print(f"Blog workflow executions found: {len(blog_execs)}")
for e in blog_execs[:15]:
    print(f"id={e.get('id')} status={e.get('status')} started={e.get('startedAt')} stopped={e.get('stoppedAt')}")

if not blog_execs:
    raise SystemExit(0)

latest = blog_execs[0]
print("\nInspect latest blog execution:", latest.get('id'))
ex = get(f"/executions/{latest['id']}?includeData=true")
run_data = ex.get('data', {}).get('resultData', {}).get('runData', {})
print("Nodes:", list(run_data.keys()))

if 'Read Intake Rows' in run_data:
    items = run_data['Read Intake Rows'][0].get('data', {}).get('main', [[]])[0]
    print('Read Intake Rows items:', len(items))
    for it in items[:8]:
        j = it.get('json', {})
        print('  row', j.get('row_number'), j.get('request_id'), j.get('company_name'), j.get('send_status'), j.get('trigger_status'))

if 'Select New Intake Rows' in run_data:
    items = run_data['Select New Intake Rows'][0].get('data', {}).get('main', [[]])[0]
    print('Select New Intake Rows items:', len(items))
    for it in items[:8]:
        j = it.get('json', {})
        print('  SELECTED row', j.get('row_number'), j.get('request_id'), j.get('company_name'), j.get('send_status'), j.get('trigger_status'))

# print errors
for node, runs in run_data.items():
    for r in runs:
        err = r.get('error')
        if err:
            print(f"ERROR in {node}: {err.get('message')}")
