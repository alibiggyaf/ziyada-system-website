import json
from pathlib import Path
from urllib.request import Request, urlopen

cfg = {}
for raw in Path('.env').read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    cfg[k.strip()] = v.strip().strip('"').strip("'")

api = (cfg.get('N8N_API_URL') or (cfg.get('N8N_BASE_URL', '').rstrip('/') + '/api/v1')).rstrip('/')
key = cfg.get('N8N_API_KEY', '').strip('"').strip("'")
headers = {'X-N8N-API-KEY': key}

# find by name
req = Request(api + '/workflows?limit=250', headers=headers)
with urlopen(req) as r:
    data = json.loads(r.read().decode())
match = next((w for w in data.get('data', []) if w.get('name') == 'Ziyada system voice chat'), None)
if not match:
    print('NOT_FOUND')
    raise SystemExit(1)
wid = match['id']

req2 = Request(api + f'/workflows/{wid}', headers=headers)
with urlopen(req2) as r:
    wf = json.loads(r.read().decode())

nodes = wf.get('nodes', [])
print(json.dumps({
    'id': wid,
    'active': wf.get('active'),
    'node_count': len(nodes),
    'respond_nodes': [n.get('name') for n in nodes if 'respondToWebhook' in str(n.get('type'))],
    'webhook_nodes': [
        {
            'name': n.get('name'),
            'type': n.get('type'),
            'params': n.get('parameters', {})
        }
        for n in nodes if 'webhook' in str(n.get('type', '')).lower()
    ],
}, ensure_ascii=False))
