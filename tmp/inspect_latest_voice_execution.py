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

req = urllib.request.Request(f'{base}/api/v1/executions?workflowId=ahXJvm6lW0zUHMx8&limit=5&includeData=true', headers=headers)
with urllib.request.urlopen(req, timeout=40) as r:
    data = json.loads(r.read().decode('utf-8', 'ignore')).get('data', [])

if not data:
    print('no executions')
    raise SystemExit(0)

eid = data[0]['id']
print('execution', eid, 'status', data[0].get('status'))
req = urllib.request.Request(f'{base}/api/v1/executions/{eid}?includeData=true', headers=headers)
with urllib.request.urlopen(req, timeout=40) as r:
    ex = json.loads(r.read().decode('utf-8', 'ignore'))

rd = ex.get('data', {}).get('resultData', {}).get('runData', {})
print('nodes', list(rd.keys()))
for node in ['Prepare Voice Event', 'capture_lead', 'book_consultation', 'Ziyada Voice AI Agent', 'Respond to Voice Widget']:
    if node not in rd:
        continue
    print('\nNODE', node)
    entry = rd[node][0]
    if entry.get('error'):
        print('error', json.dumps(entry.get('error'), ensure_ascii=False)[:1000])
    out = entry.get('data', {}).get('main', [])
    if out and out[0] and out[0][0]:
        print(json.dumps(out[0][0].get('json', {}), ensure_ascii=False)[:1500])
