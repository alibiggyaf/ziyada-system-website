#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

env = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/.env.local').read_text()
key = ''
for line in env.splitlines():
    if line.startswith('N8N_API_KEY='):
        key = line.split('=', 1)[1].strip().strip('"').strip("'")
        break

base = 'https://n8n.srv953562.hstgr.cloud'
headers = {'X-N8N-API-KEY': key}

req = urllib.request.Request(f'{base}/api/v1/executions?workflowId=qHAIKXEV4SW8r5Nx&limit=10', headers=headers)
with urllib.request.urlopen(req, timeout=40) as r:
    items = json.loads(r.read().decode('utf-8', 'ignore')).get('data', [])

succ = [x['id'] for x in items if x.get('status') == 'success']
print('success ids', succ[:5])
if not succ:
    raise SystemExit(0)

ex_id = succ[0]
req = urllib.request.Request(f'{base}/api/v1/executions/{ex_id}?includeData=true', headers=headers)
with urllib.request.urlopen(req, timeout=40) as r:
    ex = json.loads(r.read().decode('utf-8', 'ignore'))
rd = ex.get('data', {}).get('resultData', {}).get('runData', {})

for node in ['Validate and Normalize Voice', 'Call AI Chat Webhook', 'Format Voice Response']:
    if node not in rd:
        continue
    print('\nNODE', node)
    out = rd[node][0].get('data', {}).get('main', [])
    if out and out[0] and out[0][0]:
        print(json.dumps(out[0][0].get('json', {}), ensure_ascii=False)[:1500])
