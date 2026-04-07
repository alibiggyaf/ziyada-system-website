#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
]


def load_env() -> None:
    for env_path in (ROOT_DIR / '.env', PROJECT_DIR / '.env'):
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
    spreadsheet_id = os.getenv('ZIYADA_BLOG_SHEET_ID', '').strip()
    tab = os.getenv('ZIYADA_CHAT_STATE_TAB', 'Chat State').strip() or 'Chat State'

    token_path = PROJECT_DIR / 'token.json'
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build('sheets', 'v4', credentials=creds)

    data = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{tab}!A1:Z2000",
    ).execute()
    values = data.get('values', [])
    if not values:
        print('no rows')
        return 0
    headers = values[0]
    rows = values[1:]
    print('headers:', headers)
    print('rows_count:', len(rows))
    for r in rows[-5:]:
        d = {headers[i]: r[i] if i < len(r) else '' for i in range(len(headers))}
        print(d)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
