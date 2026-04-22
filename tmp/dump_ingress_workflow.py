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

req = urllib.request.Request(
    'https://n8n.srv953562.hstgr.cloud/api/v1/workflows/qHAIKXEV4SW8r5Nx',
    headers={'X-N8N-API-KEY': key},
)
with urllib.request.urlopen(req, timeout=40) as r:
    wf = json.loads(r.read().decode('utf-8', 'ignore'))

print('nodes', len(wf['nodes']))
for n in wf['nodes']:
    print('-', n['name'], '|', n['type'])
print('connection keys', list(wf.get('connections', {}).keys()))
print('route mode', json.dumps(wf.get('connections', {}).get('Route Mode', {}), ensure_ascii=False))
