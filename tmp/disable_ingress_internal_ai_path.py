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
headers = {'X-N8N-API-KEY': key, 'Content-Type': 'application/json'}

def api(method, path, payload=None):
    req = urllib.request.Request(base + path, method=method, headers=headers)
    if payload is not None:
        req.data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read().decode('utf-8', 'ignore')
        return json.loads(body) if body else {}

wid = 'qHAIKXEV4SW8r5Nx'
wf = api('GET', f'/api/v1/workflows/{wid}')
conn = wf.get('connections', {})

# Keep logging but stop feeding internal AI path.
conn['Persist Transcript Supabase'] = {'main': [[]]}

# Disconnect dormant internal AI chain from formatter.
conn['Prepare Agent Input'] = {'main': [[]]}
conn['Ziyada Voice AI Agent'] = {'main': [[]]}

wf['connections'] = conn
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings') or {},
}

try:
    api('POST', f'/api/v1/workflows/{wid}/deactivate', {})
except Exception:
    pass
api('PUT', f'/api/v1/workflows/{wid}', payload)
api('POST', f'/api/v1/workflows/{wid}/activate', {})

wf2 = api('GET', f'/api/v1/workflows/{wid}')
print('Persist->', wf2.get('connections', {}).get('Persist Transcript Supabase'))
print('Prepare->', wf2.get('connections', {}).get('Prepare Agent Input'))
print('InternalAgent->', wf2.get('connections', {}).get('Ziyada Voice AI Agent'))
