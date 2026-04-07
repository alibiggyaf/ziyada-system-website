#!/usr/bin/env python3
import json, urllib.request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID = "C8JWsE3KIoxr1KgO"

headers = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}

def get(path):
    req = urllib.request.Request(f"{N8N_URL}{path}", headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

raw = get('/executions?limit=100&includeData=false')
blog_execs = [e for e in raw.get('data', []) if str(e.get('workflowId')) == WF_ID]
err = next((e for e in blog_execs if e.get('status') == 'error'), None)
if not err:
    print('No error executions found')
    raise SystemExit(0)

print('Latest error execution:', err['id'])
ex = get(f"/executions/{err['id']}?includeData=true")
run_data = ex.get('data', {}).get('resultData', {}).get('runData', {})
for node, runs in run_data.items():
    for r in runs:
        er = r.get('error')
        if er:
            print('\nNODE:', node)
            print(json.dumps(er, ensure_ascii=False, indent=2))
