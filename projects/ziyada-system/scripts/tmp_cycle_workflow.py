#!/usr/bin/env python3
"""Deactivate, update, and reactivate the workflow to force a fresh load."""
import os, json, urllib.request, ssl, time
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

def api_call(method, path, data=None):
    url = f'{base}{path}'
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method,
                                 headers={'X-N8N-API-KEY': api_key, 'Content-Type': 'application/json'})
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()}")
        return None

# Step 1: Deactivate
print("1. Deactivating workflow...")
result = api_call('PATCH', f'/api/v1/workflows/{wf_id}', {'active': False})
if result:
    print(f"   active={result.get('active')}")

time.sleep(3)

# Step 2: Check the Telegram Source Gate node in the current deployed version
print("\n2. Checking current deployed Telegram Source Gate...")
wf = api_call('GET', f'/api/v1/workflows/{wf_id}')
if wf:
    for node in wf.get('nodes', []):
        if node.get('name') == 'Telegram Source Gate':
            print(f"   typeVersion: {node.get('typeVersion')}")
            print(f"   conditions: {json.dumps(node.get('parameters', {}).get('conditions', {}))}")
            break

time.sleep(2)

# Step 3: Reactivate
print("\n3. Reactivating workflow...")
result = api_call('PATCH', f'/api/v1/workflows/{wf_id}', {'active': True})
if result:
    print(f"   active={result.get('active')}")
else:
    time.sleep(3)
    result = api_call('PATCH', f'/api/v1/workflows/{wf_id}', {'active': True})
    if result:
        print(f"   active={result.get('active')} (retry)")

print("\nDone.")
