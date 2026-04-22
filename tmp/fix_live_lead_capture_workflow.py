#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

env = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/.env.local').read_text()
n8n_key = ''
sb_key = ''
for line in env.splitlines():
    if line.startswith('N8N_API_KEY='):
        n8n_key = line.split('=', 1)[1].strip().strip('"').strip("'")
    if line.startswith('SUPABASE_SERVICE_ROLE_KEY='):
        sb_key = line.split('=', 1)[1].strip().strip('"').strip("'")

base = 'https://n8n.srv953562.hstgr.cloud'
wid = 'ImrkLJa5mO7TvJmk'
headers = {'X-N8N-API-KEY': n8n_key, 'Content-Type': 'application/json'}

def api(method, path, payload=None):
    req = urllib.request.Request(base + path, method=method, headers=headers)
    if payload is not None:
        req.data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read().decode('utf-8', 'ignore')
        return json.loads(body) if body else {}

wf = api('GET', f'/api/v1/workflows/{wid}')
for node in wf['nodes']:
    if node.get('name') == 'Save Lead to Supabase':
        params = node.setdefault('parameters', {})
        params.pop('authentication', None)
        params.pop('genericAuthType', None)
        params['sendHeaders'] = True
        params['headerParameters'] = {
            'parameters': [
                {'name': 'apikey', 'value': sb_key},
                {'name': 'Authorization', 'value': f'Bearer {sb_key}'},
                {'name': 'Content-Type', 'value': 'application/json'},
                {'name': 'Prefer', 'value': 'return=representation'},
            ]
        }
        node.pop('credentials', None)
        break
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
for node in wf2['nodes']:
    if node.get('name') == 'Save Lead to Supabase':
        print(json.dumps({
            'has_credentials': 'credentials' in node,
            'headers': node.get('parameters', {}).get('headerParameters', {})
        }, ensure_ascii=False))
        break
