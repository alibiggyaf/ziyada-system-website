#!/usr/bin/env python3
"""Check the latest 5 executions to find post-deploy ones."""
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

# Get latest 5 executions (any status)
exec_url = f'{base}/api/v1/executions?workflowId={wf_id}&limit=5'
req = urllib.request.Request(exec_url, headers={'X-N8N-API-KEY': api_key})
resp = urllib.request.urlopen(req, context=ctx)
execs = json.loads(resp.read())

for ex in execs.get('data', []):
    eid = ex.get('id')
    status = ex.get('status', '?')
    started = ex.get('startedAt', '?')
    stopped = ex.get('stoppedAt', '?')
    print(f"  {eid}: status={status} {started} -> {stopped}")

# Deep inspect the most recent one
if execs.get('data'):
    latest = execs['data'][0]
    eid = latest['id']
    print(f"\n=== Detail for {eid} ===")
    detail_url = f'{base}/api/v1/executions/{eid}?includeData=true'
    req2 = urllib.request.Request(detail_url, headers={'X-N8N-API-KEY': api_key})
    resp2 = urllib.request.urlopen(req2, context=ctx)
    detail = json.loads(resp2.read())
    rd = detail.get('data', {}).get('resultData', {}).get('runData', {})
    print(f"  Nodes: {list(rd.keys())}")
    for nname, runs in rd.items():
        for run in runs:
            main_data = run.get('data', {}).get('main', [])
            total = sum(len(arr) for arr in main_data if arr)
            err = run.get('error')
            if nname == 'Telegram Source Gate':
                print(f"\n  {nname}: items={total} error={err}")
                for idx, arr in enumerate(main_data):
                    if arr:
                        print(f"    output[{idx}]: {len(arr)} items")
                    else:
                        print(f"    output[{idx}]: empty")
            elif 'Interview' in nname or 'Apify' in nname or 'Market' in nname:
                print(f"  {nname}: items={total} error={err}")
