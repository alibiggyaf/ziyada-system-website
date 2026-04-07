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
    wf = os.getenv('N8N_BLOG_WORKFLOW_ID', '').strip() or 'y7gXaTFEyIDOz7uS'

    req = urllib.request.Request(
        f"{base}/api/v1/workflows/{wf}",
        headers={'X-N8N-API-KEY': key, 'Accept': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())

    print('workflow', data.get('name'), 'active', data.get('active'))
    for node in data.get('nodes', []):
        if node.get('name') in ('Prepare Content Writer Input', 'Build Telegram Run Summary'):
            code = (node.get('parameters', {}) or {}).get('jsCode') or ''
            print('\nNODE', node.get('name'))
            print('has telegramChatId:', 'telegramChatId' in code)
            print('has robust isTelegram:', '|| !!telegramChatId' in code)
            print('has summary prep fallback:', 'chatId = input.telegram_chat_id || prep.telegram_chat_id ||' in code)
            if node.get('name') == 'Build Telegram Run Summary':
                print('has isInterviewPending:', 'isInterviewPending' in code)
        if node.get('name') == 'Interview Readiness Gate':
            cond = ((node.get('parameters', {}) or {}).get('conditions', {}) or {}).get('boolean', [])
            print('\nNODE Interview Readiness Gate condition:', cond)

    connections = data.get('connections', {}) or {}
    print('\nCONNECTION Build Interview Pending Row:', connections.get('Build Interview Pending Row'))
    print('CONNECTION Append Interview Pending Row:', connections.get('Append Interview Pending Row'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
