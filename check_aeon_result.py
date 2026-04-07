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
    range='resault!A1:Q400'
).execute().get('values', [])

matches = []
for i, row in enumerate(vals[1:], start=2):
    text = ' | '.join(str(x) for x in row).lower()
    if 'aeonabaya' in text or 'aeon abaya' in text or (row and str(row[0]).strip() == '3'):
        matches.append((i, row))

print('matches', len(matches))
if matches:
    print('latest', matches[-1])
