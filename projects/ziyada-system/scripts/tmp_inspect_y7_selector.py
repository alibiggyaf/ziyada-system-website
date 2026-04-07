#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
for env_path in (ROOT / '.env', PROJECT / '.env'):
    if env_path.exists():
        for raw in env_path.read_text(encoding='utf-8').splitlines():
            s = raw.strip()
            if not s or s.startswith('#') or '=' not in s:
                continue
            k, v = s.split('=', 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

base = (os.getenv('N8N_BASE_URL') or os.getenv('N8N_API_URL') or '').split('/api/')[0].split('/rest/')[0].rstrip('/')
key = os.getenv('N8N_API_KEY', '').strip().strip('"').strip("'")
wf_id = 'y7gXaTFEyIDOz7uS'


def get(path: str):
    req = urllib.request.Request(base + path, headers={'X-N8N-API-KEY': key, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))

execs = get(f"/api/v1/executions?workflowId={urllib.parse.quote(wf_id)}&limit=12").get('data', [])
for ex in execs:
    exid = str(ex.get('id'))
    status = ex.get('status')
    detail = get(f"/api/v1/executions/{urllib.parse.quote(exid)}?includeData=true")
    run_data = detail.get('data', {}).get('resultData', {}).get('runData', {})
    sel = run_data.get('Select New Intake Rows', [])
    norm = run_data.get('Normalize Intake Row Input', [])
    prep = run_data.get('Prepare Content Writer Input', [])
    app = run_data.get('Append Approved Row To Sheet', [])
    pend = run_data.get('Append Pending Row To Sheet', [])
    print(f"ex={exid} status={status} sel={bool(sel)} norm={bool(norm)} prep={bool(prep)} appendA={bool(app)} appendP={bool(pend)}")
    if sel:
        items = sel[0].get('data', {}).get('main', [[ ]])[0]
        if items:
            js = items[0].get('json', {})
            print('  sel', 'request_id=', js.get('request_id', ''), 'company=', js.get('company_name', ''), 'trigger=', js.get('trigger_status', js.get('status', '')))
