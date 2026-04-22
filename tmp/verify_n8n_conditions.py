#!/usr/bin/env python3
from pathlib import Path
import json
import requests


def read_env(path: str) -> dict:
    env = {}
    p = Path(path)
    if not p.exists():
        return env
    for raw in p.read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith('#') or '=' not in s:
            continue
        k, v = s.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

app = read_env('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/.env.local')
api = (app.get('N8N_API_URL') or '').rstrip('/')
key = app.get('N8N_API_KEY')
headers = {'X-N8N-API-KEY': key}

wf_list = requests.get(f'{api}/workflows?limit=250', headers=headers, timeout=40)
wf_list.raise_for_status()
items = wf_list.json().get('data', [])

# Find likely workflow candidates
candidates = []
for w in items:
    n = (w.get('name') or '').lower()
    if 'google meet' in n or 'voice' in n or 'booking' in n or 'ziyada system voice chat' in n:
        candidates.append((w.get('id'), w.get('name'), w.get('active')))

print('CANDIDATES')
for cid, cname, cactive in candidates:
    print(f'- {cid} | {cname} | active={cactive}')

print('\nONLY_BOOKINGS_NODES')
for cid, cname, _ in candidates:
    wf = requests.get(f'{api}/workflows/{cid}', headers=headers, timeout=40)
    if wf.status_code != 200:
        continue
    data = wf.json()
    for node in data.get('nodes', []):
        if (node.get('name') or '').strip().lower() == 'only bookings':
            params = node.get('parameters', {})
            print(json.dumps({
                'workflowId': cid,
                'workflowName': cname,
                'nodeType': node.get('type'),
                'nodeVersion': node.get('typeVersion'),
                'parameters': params,
            }, ensure_ascii=False))
