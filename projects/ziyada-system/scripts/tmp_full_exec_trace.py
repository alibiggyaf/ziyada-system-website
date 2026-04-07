#!/usr/bin/env python3
"""Show ALL node outputs for the latest execution to trace the full flow."""
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

exec_url = f'{base}/api/v1/executions?workflowId={wf_id}&limit=1&status=success'
req = urllib.request.Request(exec_url, headers={'X-N8N-API-KEY': api_key})
resp = urllib.request.urlopen(req, context=ctx)
execs = json.loads(resp.read())

for ex in execs.get('data', []):
    eid = ex.get('id')
    print(f"=== Execution {eid} ({ex.get('startedAt')} -> {ex.get('stoppedAt')}) ===\n")
    
    detail_url = f'{base}/api/v1/executions/{eid}?includeData=true'
    req2 = urllib.request.Request(detail_url, headers={'X-N8N-API-KEY': api_key})
    resp2 = urllib.request.urlopen(req2, context=ctx)
    detail = json.loads(resp2.read())
    
    rd = detail.get('data', {}).get('resultData', {}).get('runData', {})
    
    for nname, runs in rd.items():
        for i, run in enumerate(runs):
            main_data = run.get('data', {}).get('main', [])
            total_items = sum(len(arr) for arr in main_data if arr)
            err = run.get('error')
            status = run.get('executionStatus', '')
            
            print(f"  {nname}")
            print(f"    items={total_items}  error={err}  status={status}")
            
            # For code/function nodes, show the actual output JSON (first item, truncated)
            for arr_idx, arr in enumerate(main_data):
                if not arr:
                    print(f"    output[{arr_idx}]: empty")
                    continue
                for j, item in enumerate(arr[:2]):
                    jj = item.get('json', {})
                    # Truncate long values
                    summary = {}
                    for k, v in jj.items():
                        sv = str(v)
                        summary[k] = sv[:100] + ('...' if len(sv) > 100 else '')
                    print(f"    output[{arr_idx}][{j}]: {json.dumps(summary, ensure_ascii=False)}")
            print()
