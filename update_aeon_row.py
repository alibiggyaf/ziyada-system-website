#!/usr/bin/env python3
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

sid = '1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s'
creds = Credentials.from_authorized_user_file(
    'projects/ziyada-system/token.json',
    ['https://www.googleapis.com/auth/spreadsheets']
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
svc = build('sheets', 'v4', credentials=creds)

vals = svc.spreadsheets().values().get(
    spreadsheetId=sid,
    range='Content Intake!A1:I200'
).execute().get('values', [])

updated = False
for i, row in enumerate(vals[1:], start=2):
    txt = ' | '.join(str(x) for x in row).lower()
    if 'aeonabaya' in txt or (row and str(row[0]).strip() == '3'):
        while len(row) < 9:
            row.append('')
        row[6] = 'start'     # send_status
        row[7] = 'approved'  # approval_status
        if not str(row[8]).strip():
            row[8] = 'Write Arabic marketing content for Aeonabaya focused on modern abayas, premium fabric quality, and clear call-to-action to shop from the website.'
        svc.spreadsheets().values().update(
            spreadsheetId=sid,
            range=f'Content Intake!A{i}:I{i}',
            valueInputOption='RAW',
            body={'values': [row[:9]]}
        ).execute()
        print('UPDATED_ROW', i, row[:9])
        updated = True
        break

print('updated', updated)
