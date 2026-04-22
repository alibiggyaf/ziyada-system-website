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

list_req = urllib.request.Request(f'{base}/api/v1/executions?workflowId=qHAIKXEV4SW8r5Nx&limit=10', headers=headers)
with urllib.request.urlopen(list_req, timeout=40) as r:
    data = json.loads(r.read().decode('utf-8', 'ignore'))

success_ids = [x['id'] for x in data.get('data', []) if x.get('status') == 'success']
print('success ids:', success_ids[:5])
if not success_ids:
    raise SystemExit(0)

ex_id = success_ids[0]
detail_req = urllib.request.Request(f'{base}/api/v1/executions/{ex_id}?includeData=true', headers=headers)
with urllib.request.urlopen(detail_req, timeout=40) as r:
    ex = json.loads(r.read().decode('utf-8', 'ignore'))

run_data = ex.get('data', {}).get('resultData', {}).get('runData', {})
for node in ['Validate Input', 'Normalize Event', 'Call Voice Agent', 'Respond Output']:
    if node not in run_data:
        continue
    print('\nNODE:', node)
    entry = run_data[node][0]
    if entry.get('error'):
        print('error', json.dumps(entry.get('error'), ensure_ascii=False)[:1200])
    out = entry.get('data', {}).get('main', [])
    if out and out[0] and out[0][0]:
        print(json.dumps(out[0][0].get('json', {}), ensure_ascii=False)[:2000])
