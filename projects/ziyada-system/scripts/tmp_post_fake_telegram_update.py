#!/usr/bin/env python3
import json
import os
import pathlib
import urllib.request


def load_env():
    root = pathlib.Path(__file__).resolve().parents[3]
    project = pathlib.Path(__file__).resolve().parents[1]
    for env_path in (root / '.env', project / '.env'):
        if not env_path.exists():
            continue
        for raw in env_path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


def main():
    load_env()
    url = 'https://n8n.srv953562.hstgr.cloud/webhook/ali-content-writer-engine-2026-telegram/webhook'
    payload = {
        'update_id': 99999999,
        'message': {
            'message_id': 777,
            'date': 1774031000,
            'text': 'hi',
            'chat': {'id': 8095556983, 'type': 'private'},
            'from': {'id': 8095556983, 'is_bot': False, 'first_name': 'Ali'},
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        method='POST',
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode('utf-8', errors='replace')
    print(raw)


if __name__ == '__main__':
    main()
