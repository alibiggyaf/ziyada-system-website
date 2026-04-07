#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import urllib.request

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


def main() -> int:
    load_env()
    base = os.environ.get('N8N_BASE_URL', '').rstrip('/')
    key = os.environ.get('N8N_API_KEY', '')
    wf_id = 'hB1vQyfT3tNuviys'
    req = urllib.request.Request(
        f"{base}/api/v1/workflows/{wf_id}",
        headers={"X-N8N-API-KEY": key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        wf = json.loads(r.read().decode('utf-8', errors='replace'))

    for n in wf.get('nodes', []):
        if n.get('type') == 'n8n-nodes-base.telegramTrigger':
            print(json.dumps(n, ensure_ascii=False, indent=2))
            return 0
    print('not found')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
