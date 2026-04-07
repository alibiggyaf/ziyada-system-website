#!/usr/bin/env python3
import json
import os
import pathlib
import urllib.request


def load_env() -> None:
    root = pathlib.Path(__file__).resolve().parents[3]
    for p in [root / '.env']:
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
    base = os.getenv('N8N_BASE_URL', '').rstrip('/')
    key = os.getenv('N8N_API_KEY', '')
    wf = os.getenv('N8N_BLOG_WORKFLOW_ID', 'y7gXaTFEyIDOz7uS')
    req = urllib.request.Request(
        f"{base}/api/v1/workflows/{wf}",
        headers={'X-N8N-API-KEY': key, 'Accept': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    print('workflow_name:', d.get('name'))
    print('workflow_url:', f"{base}/workflow/{wf}")
    for n in d.get('nodes', []):
        if n.get('type') == 'n8n-nodes-base.googleSheets':
            params = n.get('parameters', {})
            doc = ((params.get('documentId') or {}).get('value')) if isinstance(params.get('documentId'), dict) else None
            sheet_name = ((params.get('sheetName') or {}).get('value')) if isinstance(params.get('sheetName'), dict) else None
            if doc:
                print('sheet_id:', doc, 'node:', n.get('name'), 'tab:', sheet_name)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
