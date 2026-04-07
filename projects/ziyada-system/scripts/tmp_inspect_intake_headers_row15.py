#!/usr/bin/env python3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sheet_id = '1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s'
tab = 'Content Intake'
row_num = 15

creds = Credentials.from_authorized_user_file('projects/ziyada-system/token_sheets.json', ['https://www.googleapis.com/auth/spreadsheets'])
svc = build('sheets', 'v4', credentials=creds, cache_discovery=False)
vals = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range=f'{tab}!A1:AZ{row_num}').execute().get('values', [])
if len(vals) < row_num:
    raise SystemExit('row missing')
headers = vals[0]
row = vals[row_num - 1]
print('headers_count', len(headers))
for i, h in enumerate(headers, start=1):
    if h.strip():
        v = row[i-1] if i-1 < len(row) else ''
        print(f'{i:02d} | {h} | {v}')
