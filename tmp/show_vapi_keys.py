#!/usr/bin/env python3
from pathlib import Path
import json
import requests


def read_env(path: str) -> dict:
    env = {}
    p = Path(path)
    if not p.exists():
        return env
    for raw in p.read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith('#') or '=' not in s:
            continue
        k, v = s.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


root = read_env('/Users/djbiggy/Downloads/Claude Code- File Agents/.env.local')
app = read_env('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/.env.local')
api_key = root.get('VAPI_API_KEY') or app.get('VAPI_API_KEY')
assistant_id = app.get('VAPI_ASSISTANT_ID') or app.get('VITE_VAPI_ASSISTANT_ID')
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
resp = requests.get(f'https://api.vapi.ai/assistant/{assistant_id}', headers=headers, timeout=30)
resp.raise_for_status()
a = resp.json()

print('top_keys=', sorted(a.keys()))
for key in ['analysisPlan', 'artifactPlan', 'server', 'model']:
    val = a.get(key)
    if isinstance(val, dict):
        print(f'{key}_keys=', sorted(val.keys()))
    else:
        print(f'{key}_type=', type(val).__name__)

# Print likely fields that may hold structured schema
for k in sorted(a.keys()):
    if 'schema' in k.lower() or 'struct' in k.lower() or 'json' in k.lower() or 'analysis' in k.lower():
        print('candidate:', k)

print('analysisPlan=', json.dumps(a.get('analysisPlan'), ensure_ascii=False)[:1500])
