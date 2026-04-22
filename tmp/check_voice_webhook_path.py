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
req = urllib.request.Request(f'{base}/api/v1/workflows/ahXJvm6lW0zUHMx8', headers=headers)
with urllib.request.urlopen(req, timeout=40) as r:
    wf = json.loads(r.read().decode('utf-8', 'ignore'))

print('active', wf.get('active'))
for n in wf.get('nodes', []):
    if n.get('type') == 'n8n-nodes-base.webhook':
        p = n.get('parameters', {})
        print('webhook name', n.get('name'))
        print('path', p.get('path'))
        print('method', p.get('httpMethod'))
        print('responseMode', p.get('responseMode'))
