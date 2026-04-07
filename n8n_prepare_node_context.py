#!/usr/bin/env python3
import json, urllib.request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID = "C8JWsE3KIoxr1KgO"

req = urllib.request.Request(
    f"{N8N_URL}/workflows/{WF_ID}",
    headers={"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}
)
with urllib.request.urlopen(req) as r:
    wf = json.loads(r.read())

nodes = {n['name']: n for n in wf.get('nodes', [])}
conns = wf.get('connections', {})
name = 'Prepare Content Writer Input'

print('Prepare node exists:', name in nodes)
if name in nodes:
    code = nodes[name].get('parameters', {}).get('jsCode', '')
    print('Code first 500 chars:\n', code[:500])
    print('\nCode around line 20-40:')
    lines = code.split('\n')
    for i, line in enumerate(lines[16:40], start=17):
        print(f"{i:03d}: {line}")

print('\nOutgoing from Prepare:')
out = conns.get(name, {})
print(json.dumps(out, ensure_ascii=False, indent=2)[:2000])

print('\nNodes directly after Prepare:')
for branch in out.get('main', []):
    for target in branch:
        print(' -', target.get('node'))
