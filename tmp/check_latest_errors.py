#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

env = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/.env.local').read_text()
key = ''
for line in env.splitlines():
    if line.startswith('N8N_API_KEY='):
        key = line.split('=', 1)[1].strip().strip('"').strip("'")
        break

base = 'https://n8n.srv953562.hstgr.cloud'
headers = {'X-N8N-API-KEY': key}
for wid in ['qHAIKXEV4SW8r5Nx', 'ahXJvm6lW0zUHMx8']:
    req = urllib.request.Request(f'{base}/api/v1/executions?workflowId={wid}&limit=3&includeData=true', headers=headers)
    with urllib.request.urlopen(req, timeout=40) as r:
        ex = json.loads(r.read().decode('utf-8', 'ignore')).get('data', [])
    print('\nWF', wid)
    for item in ex:
        print('id', item.get('id'), 'status', item.get('status'))
        if item.get('status') == 'error':
            eid = item.get('id')
            dreq = urllib.request.Request(f'{base}/api/v1/executions/{eid}?includeData=true', headers=headers)
            with urllib.request.urlopen(dreq, timeout=40) as rr:
                det = json.loads(rr.read().decode('utf-8', 'ignore'))
            err = det.get('data', {}).get('resultData', {}).get('error')
            last = det.get('data', {}).get('resultData', {}).get('lastNodeExecuted')
            print(' lastNode', last)
            print(' error', json.dumps(err, ensure_ascii=False)[:800])
            break
