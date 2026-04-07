#!/usr/bin/env python3
import json
import os
import pathlib
import urllib.request


def load_env() -> None:
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


def main() -> int:
    load_env()
    base = os.getenv('N8N_BASE_URL', '').strip().rstrip('/')
    path = os.getenv('N8N_BLOG_TRIGGER_PATH', 'ali-content-writer-engine-2026-ingest').strip().strip('/')
    url = f"{base}/webhook/{path}"
    text = "اسم الشركة روابط العقارية نشاطها مطور عقاري ومشاريع، القطاع العقاري، الجمهور المستهدف الباحثين عن شقق تمليك وبرنامج سكني والاستثمار من خلال الشقق، رابط الموقع https://www.instagram.com/rawabet_sa/"
    payload = {
        'update_id': 99999977,
        'message': {
            'message_id': 919,
            'date': 1774032222,
            'text': text,
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
        print('status', r.status)
        print(r.read().decode('utf-8', errors='replace'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
