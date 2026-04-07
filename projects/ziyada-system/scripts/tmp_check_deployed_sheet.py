#!/usr/bin/env python3
"""Check what sheet ID and tab the deployed n8n workflow is actually reading."""
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

url = f'{base}/api/v1/workflows/{wf_id}'
ctx = ssl._create_unverified_context()
req = urllib.request.Request(url, headers={'X-N8N-API-KEY': api_key})
resp = urllib.request.urlopen(req, context=ctx)
wf = json.loads(resp.read())

print(f"Workflow: {wf.get('name')} (id={wf.get('id')}, active={wf.get('active')})")
print()

for node in wf.get('nodes', []):
    ntype = node.get('type', '')
    nname = node.get('name', '')
    if 'Sheets' in ntype or 'Intake' in nname or 'Result' in nname:
        params = node.get('parameters', {})
        print(f"Node: {nname} ({ntype})")
        if 'documentId' in params:
            print(f"  documentId: {json.dumps(params['documentId'], indent=2)}")
        if 'sheetName' in params:
            print(f"  sheetName: {json.dumps(params['sheetName'], indent=2)}")
        creds = node.get('credentials', {})
        if creds:
            print(f"  credentials: {json.dumps(creds, indent=2)}")
        if node.get('onError'):
            print(f"  onError: {node['onError']}")
        print()

# Also fetch last 3 executions with data
print("=== Last 3 executions ===")
exec_url = f'{base}/api/v1/executions?workflowId={wf_id}&limit=3&status=success'
req2 = urllib.request.Request(exec_url, headers={'X-N8N-API-KEY': api_key})
resp2 = urllib.request.urlopen(req2, context=ctx)
execs = json.loads(resp2.read())
for ex in execs.get('data', []):
    eid = ex.get('id')
    print(f"\nExecution {eid} ({ex.get('startedAt')} -> {ex.get('stoppedAt')})")
    # Fetch execution detail with data
    detail_url = f'{base}/api/v1/executions/{eid}'
    req3 = urllib.request.Request(detail_url, headers={'X-N8N-API-KEY': api_key})
    resp3 = urllib.request.urlopen(req3, context=ctx)
    detail = json.loads(resp3.read())
    rd = detail.get('data', {}).get('resultData', {}).get('runData', {})
    # Check Read Intake Rows output
    for nname_key in rd:
        if 'Read Intake' in nname_key or 'Select New' in nname_key:
            runs = rd[nname_key]
            for run in runs:
                data_items = run.get('data', {}).get('main', [[]])[0]
                print(f"  {nname_key}: {len(data_items)} items")
                if len(data_items) <= 3:
                    for item in data_items:
                        j = item.get('json', {})
                        print(f"    company={j.get('company_name','')} trigger={j.get('trigger_status','')} sent={j.get('sent_status','')} workflow={j.get('workflow_status','')}")
                elif data_items:
                    # Just show first and last
                    j = data_items[0].get('json', {})
                    print(f"    [0] company={j.get('company_name','')} trigger={j.get('trigger_status','')} sent={j.get('sent_status','')}")
                    j = data_items[-1].get('json', {})
                    print(f"    [{len(data_items)-1}] company={j.get('company_name','')} trigger={j.get('trigger_status','')} sent={j.get('sent_status','')}")
