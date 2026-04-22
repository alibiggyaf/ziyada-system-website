import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

cfg = {}
for raw in Path('.env').read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    cfg[k.strip()] = v.strip().strip('"').strip("'")

api = (cfg.get('N8N_API_URL') or (cfg.get('N8N_BASE_URL', '').rstrip('/') + '/api/v1')).rstrip('/')
key = cfg.get('N8N_API_KEY', '').strip('"').strip("'")
headers = {'X-N8N-API-KEY': key, 'Content-Type': 'application/json'}

wf_path = Path('projects/ziyada-system/n8n for ziyada system/workflow_voice_ingress.json')
wf = json.loads(wf_path.read_text())
wf['name'] = 'Ziyada system voice chat'
wf.setdefault('settings', {'executionOrder': 'v1'})
wf_payload = {
    'name': wf['name'],
    'nodes': wf.get('nodes', []),
    'connections': wf.get('connections', {}),
    'settings': wf.get('settings', {'executionOrder': 'v1'}),
}

# Find existing workflow by exact name
req = Request(api + '/workflows?limit=250', headers={'X-N8N-API-KEY': key})
with urlopen(req) as r:
    data = json.loads(r.read().decode())

match = next((w for w in data.get('data', []) if w.get('name') == wf['name']), None)
payload = json.dumps(wf_payload).encode()

try:
    if match:
        wid = match['id']
        req2 = Request(api + f'/workflows/{wid}', data=payload, method='PUT', headers=headers)
        with urlopen(req2) as r:
            _ = json.loads(r.read().decode())
        action = 'updated'
    else:
        req2 = Request(api + '/workflows', data=payload, method='POST', headers=headers)
        with urlopen(req2) as r:
            created = json.loads(r.read().decode())
        wid = created['id']
        action = 'created'
except HTTPError as e:
    print(f"HTTP_ERROR:{e.code}")
    print(e.read().decode())
    raise

# Activate workflow
try:
    req3 = Request(api + f'/workflows/{wid}/activate', data=b'{}', method='POST', headers=headers)
    with urlopen(req3) as r:
        act = json.loads(r.read().decode())
    active = act.get('active', True)
except Exception:
    req3 = Request(api + f'/workflows/{wid}', data=json.dumps({'active': True}).encode(), method='PATCH', headers=headers)
    with urlopen(req3) as r:
        act = json.loads(r.read().decode())
    active = act.get('active', True)

print(json.dumps({'workflow_id': wid, 'name': wf['name'], 'action': action, 'active': active}, ensure_ascii=False))
