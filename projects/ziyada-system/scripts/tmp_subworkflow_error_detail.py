#!/usr/bin/env python3
import json
import urllib.request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID = "INHDUWqaC4WMae1R"

headers = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}


def get(path):
    req = urllib.request.Request(f"{N8N_URL}{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


raw = get('/executions?limit=50&includeData=false')
items = [e for e in raw.get('data', []) if str(e.get('workflowId')) == WF_ID]
errors = [e for e in items if e.get('status') == 'error']
print('error_count', len(errors))
if not errors:
    raise SystemExit(0)

latest = errors[0]
print('latest_error_execution', latest.get('id'))
ex = get(f"/executions/{latest['id']}?includeData=true")
print('top_error', ex.get('data', {}).get('resultData', {}).get('error'))
run_data = ex.get('data', {}).get('resultData', {}).get('runData', {})
for node, runs in run_data.items():
    for run in runs:
        err = run.get('error')
        if err:
            print('\nNODE:', node)
            print(json.dumps(err, ensure_ascii=False, indent=2)[:3000])
