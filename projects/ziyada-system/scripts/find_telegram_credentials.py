#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import urllib.request
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJECT = pathlib.Path(__file__).resolve().parents[1]


def load_env() -> None:
    for p in (ROOT / '.env', PROJECT / '.env'):
        if not p.exists():
            continue
        for raw in p.read_text(encoding='utf-8').splitlines():
            s = raw.strip()
            if not s or s.startswith('#') or '=' not in s:
                continue
            k, v = s.split('=', 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


def api_get(path: str):
    base = os.environ.get('N8N_BASE_URL', '').rstrip('/')
    key = os.environ.get('N8N_API_KEY', '')
    req = urllib.request.Request(
        f"{base}{path}",
        headers={"X-N8N-API-KEY": key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8', errors='replace'))


def main() -> int:
    load_env()
    data = api_get('/api/v1/workflows')
    items = data.get('data', []) if isinstance(data, dict) else data
    found = []
    for wf in items:
        wf_id = wf.get('id')
        one = api_get(f"/api/v1/workflows/{urllib.parse.quote(str(wf_id))}")
        for node in one.get('nodes', []):
            if node.get('type') == 'n8n-nodes-base.telegramTrigger':
                creds = node.get('credentials', {})
                tg = creds.get('telegramApi') if isinstance(creds, dict) else None
                found.append({
                    'workflow_id': wf_id,
                    'workflow_name': one.get('name'),
                    'node_name': node.get('name'),
                    'credential': tg,
                })
    print(json.dumps(found, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
