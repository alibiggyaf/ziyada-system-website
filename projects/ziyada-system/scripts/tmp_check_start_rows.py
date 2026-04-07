#!/usr/bin/env python3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sheet_id = '1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s'
tab = 'Content Intake'
creds = Credentials.from_authorized_user_file('projects/ziyada-system/token_sheets.json', ['https://www.googleapis.com/auth/spreadsheets'])
svc = build('sheets', 'v4', credentials=creds, cache_discovery=False)
vals = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range=f'{tab}!A1:AZ').execute().get('values', [])
if not vals:
    raise SystemExit('empty')
headers = vals[0]
idx = {h: i for i, h in enumerate(headers)}
for rn, row in enumerate(vals[1:], start=2):
    trig_i = idx.get('trigger_status')
    trig = row[trig_i].strip().lower() if trig_i is not None and trig_i < len(row) else ''
    if trig == 'start':
        req_i = idx.get('request_id')
        sent_i = idx.get('sent_status')
        wf_i = idx.get('workflow_status')
        appr_i = idx.get('approval_status')
        comp_i = idx.get('company_name')
        link_i = idx.get('company_link')
        req = row[req_i] if req_i is not None and req_i < len(row) else ''
        sent = row[sent_i] if sent_i is not None and sent_i < len(row) else ''
        wf = row[wf_i] if wf_i is not None and wf_i < len(row) else ''
        appr = row[appr_i] if appr_i is not None and appr_i < len(row) else ''
        comp = row[comp_i] if comp_i is not None and comp_i < len(row) else ''
        link = row[link_i] if link_i is not None and link_i < len(row) else ''
        print(f'row={rn} req={req} company={comp} link={link} approval={appr} sent={sent} workflow={wf}')
