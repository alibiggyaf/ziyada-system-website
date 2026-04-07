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
    key = os.getenv('N8N_API_KEY', '').strip()
    req = urllib.request.Request(
        f"{base}/api/v1/executions?limit=15",
        headers={'X-N8N-API-KEY': key, 'Accept': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
    for ex in (data.get('data') or []):
        print(ex.get('id'), ex.get('workflowId'), ex.get('mode'), ex.get('status'), ex.get('startedAt'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
