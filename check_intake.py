#!/usr/bin/env python3
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json, urllib.request

sid = '1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s'
N8N_URL = 'https://n8n.srv953562.hstgr.cloud/api/v1'
N8N_KEY  = None  # will try to load from env file

# --- Load key ---
try:
    with open('projects/ziyada-system/scripts/deploy_n8n_blog_workflow.py') as f:
        for line in f:
            if 'N8N_API_KEY' in line and '=' in line and "'" in line:
                N8N_KEY = line.split("'")[1]
                break
except: pass

# ---- SHEET ----
c = Credentials.from_authorized_user_file(
    'projects/ziyada-system/token.json',
    ['https://www.googleapis.com/auth/spreadsheets']
)
if c.expired and c.refresh_token:
    c.refresh(Request())
svc = build('sheets', 'v4', credentials=c)

print("=" * 70)
print("CONTENT INTAKE")
print("=" * 70)
v = svc.spreadsheets().values().get(
    spreadsheetId=sid, range='Content Intake!A1:I30'
).execute().get('values', [])

headers = v[0] if v else []
print("Headers:", headers)
print()

aeon_rows = []
for i, row in enumerate(v[1:], start=2):
    while len(row) < len(headers):
        row.append('')
    label = ' | '.join(row).lower()
    marker = '<< AEON' if ('aeon' in label) else ''
    print(f"R{i}: {row}  {marker}")
    if 'aeon' in label:
        aeon_rows.append((i, row))

print()
print("Aeonabaya rows found:", len(aeon_rows))
for rownum, row in aeon_rows:
    for j, h in enumerate(headers):
        print(f"  {h} = {row[j] if j < len(row) else '(empty)'}")

# ---- N8N ----
print()
print("=" * 70)
print("N8N WORKFLOW STATUS")
print("=" * 70)
if N8N_KEY:
    try:
        req = urllib.request.Request(
            f'{N8N_URL}/workflows',
            headers={'X-N8N-API-KEY': N8N_KEY, 'Accept': 'application/json'}
        )
        with urllib.request.urlopen(req) as resp:
            wf_data = json.loads(resp.read())
        wfs = wf_data.get('data', [])
        for wf in wfs:
            print(f"  ID={wf['id']} active={wf.get('active')} name={wf.get('name','')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    print("LAST 5 EXECUTIONS")
    try:
        req = urllib.request.Request(
            f'{N8N_URL}/executions?limit=5&includeData=false',
            headers={'X-N8N-API-KEY': N8N_KEY, 'Accept': 'application/json'}
        )
        with urllib.request.urlopen(req) as resp:
            ex_data = json.loads(resp.read())
        execs = ex_data.get('data', [])
        for ex in execs:
            print(f"  ex={ex.get('id')} status={ex.get('status')} finished={ex.get('finished')} startedAt={ex.get('startedAt', '')[:19]}")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("  No API key found")
