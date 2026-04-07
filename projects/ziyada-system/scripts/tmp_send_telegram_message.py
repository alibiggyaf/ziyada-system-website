#!/usr/bin/env python3
import json
import os
import pathlib
import urllib.parse
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
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = '8095556983'
    text = 'hi'
    payload = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
    req = urllib.request.Request(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data=payload,
        method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        print(r.read().decode('utf-8', errors='replace'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
