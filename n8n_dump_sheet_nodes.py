#!/usr/bin/env python3
import json, urllib.request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID   = "C8JWsE3KIoxr1KgO"

req = urllib.request.Request(
    f"{N8N_URL}/workflows/{WF_ID}",
    headers={"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}
)
with urllib.request.urlopen(req) as r:
    wf = json.loads(r.read())

for n in wf.get('nodes', []):
    t = n.get('type','')
    if 'googleSheets' in t or 'googleSheetsTrigger' in t:
        print("="*70)
        print("NODE:", n.get('name'))
        print("TYPE:", t)
        print("CREDENTIALS:", n.get('credentials'))
        params = n.get('parameters', {})
        # Print key params likely related to doc/tab/range
        for k in ['documentId','sheetName','triggerOn','event','options','columns','rangeDefinition','valueInputMode','filtersUI','pollTimes','watchFor']:
            if k in params:
                print(f"{k}: {json.dumps(params.get(k), ensure_ascii=False)}")
        # Print all params compact
        print("ALL_PARAMS:")
        print(json.dumps(params, ensure_ascii=False, indent=2)[:2500])
