#!/usr/bin/env python3
"""Check the Telegram Source Gate condition and Interview Readiness Gate condition as deployed."""
import os, json, urllib.request, ssl
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for ep in (Path(__file__).resolve().parents[1] / '.env', ROOT / '.env'):
    if ep.exists():
        for raw in ep.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip().strip('"')

base = os.environ['N8N_BASE_URL'].rstrip('/')
api_key = os.environ['N8N_API_KEY']
wf_id = os.environ.get('N8N_BLOG_WORKFLOW_ID', 'C8JWsE3KIoxr1KgO')

ctx = ssl._create_unverified_context()
url = f'{base}/api/v1/workflows/{wf_id}'
req = urllib.request.Request(url, headers={'X-N8N-API-KEY': api_key})
resp = urllib.request.urlopen(req, context=ctx)
wf = json.loads(resp.read())

for node in wf.get('nodes', []):
    nname = node.get('name', '')
    if nname in ('Telegram Source Gate', 'Interview Readiness Gate'):
        print(f"=== {nname} ===")
        print(json.dumps(node.get('parameters', {}), indent=2, ensure_ascii=False))
        print()

# Also show connections
conns = wf.get('connections', {})
for k in ('Telegram Source Gate', 'Interview Readiness Gate', 'Read Chat State Rows', 'Hydrate Telegram Context'):
    if k in conns:
        print(f"=== Connections: {k} ===")
        print(json.dumps(conns[k], indent=2, ensure_ascii=False))
        print()
