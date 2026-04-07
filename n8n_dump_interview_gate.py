#!/usr/bin/env python3
import json, urllib.request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID = "C8JWsE3KIoxr1KgO"

req = urllib.request.Request(f"{N8N_URL}/workflows/{WF_ID}", headers={"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"})
with urllib.request.urlopen(req) as r:
    wf = json.loads(r.read())

for n in wf.get('nodes', []):
    if n.get('name') in ['Interview Readiness Gate','Build Interview Pending Row','Build Content Writer Prompts']:
        print('='*70)
        print(n.get('name'), n.get('type'))
        print(json.dumps(n.get('parameters',{}), ensure_ascii=False, indent=2)[:5000])
