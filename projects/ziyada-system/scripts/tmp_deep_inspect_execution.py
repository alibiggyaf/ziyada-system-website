#!/usr/bin/env python3
"""Deep inspect last execution to see what each node returns."""
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

# Get last execution
exec_url = f'{base}/api/v1/executions?workflowId={wf_id}&limit=1&status=success'
req = urllib.request.Request(exec_url, headers={'X-N8N-API-KEY': api_key})
resp = urllib.request.urlopen(req, context=ctx)
execs = json.loads(resp.read())

for ex in execs.get('data', []):
    eid = ex.get('id')
    print(f"=== Execution {eid} ===")
    
    detail_url = f'{base}/api/v1/executions/{eid}?includeData=true'
    req2 = urllib.request.Request(detail_url, headers={'X-N8N-API-KEY': api_key})
    resp2 = urllib.request.urlopen(req2, context=ctx)
    detail = json.loads(resp2.read())
    
    rd = detail.get('data', {}).get('resultData', {}).get('runData', {})
    
    if not rd:
        print("  No runData found!")
        print("  Keys in detail:", list(detail.keys()))
        print("  Keys in detail.data:", list(detail.get('data', {}).keys()))
        rd_alt = detail.get('data', {}).get('resultData', {})
        print("  Keys in resultData:", list(rd_alt.keys()))
        continue
    
    print(f"  Nodes executed: {list(rd.keys())}")
    print()
    
    for nname, runs in rd.items():
        for i, run in enumerate(runs):
            main_data = run.get('data', {}).get('main', [])
            total_items = sum(len(arr) for arr in main_data if arr)
            
            # Check if node had an error
            err = run.get('error')
            
            print(f"  [{nname}] run={i} items={total_items} error={err}")
            
            if nname in ('Read Intake Rows', 'Select New Intake Rows', 'Normalize Intake Row Input'):
                for arr_idx, arr in enumerate(main_data):
                    if arr:
                        print(f"    output[{arr_idx}]: {len(arr)} items")
                        for j, item in enumerate(arr[:5]):
                            jj = item.get('json', {})
                            cn = jj.get('company_name', jj.get('company', ''))
                            ts = jj.get('trigger_status', jj.get('trigger status', ''))
                            ss = jj.get('sent_status', jj.get('sent status', ''))
                            ws = jj.get('workflow_status', jj.get('workflow status', ''))
                            rid = jj.get('request_id', '')
                            print(f"      [{j}] company={cn!r} trigger={ts!r} sent={ss!r} wf={ws!r} req={rid!r}")
                        if len(arr) > 5:
                            print(f"      ... and {len(arr)-5} more")
