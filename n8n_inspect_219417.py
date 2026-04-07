#!/usr/bin/env python3
import json, urllib.request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
EXEC_ID = "219417"

req = urllib.request.Request(
    f"{N8N_URL}/executions/{EXEC_ID}?includeData=true",
    headers={"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}
)
with urllib.request.urlopen(req) as r:
    ex = json.loads(r.read())

run_data = ex.get("data", {}).get("resultData", {}).get("runData", {})
ri = run_data.get("Read Intake Rows", [])
if not ri:
    print("No Read Intake Rows data")
    raise SystemExit(0)

items = ri[0].get("data", {}).get("main", [[]])[0]
print("rows from Read Intake Rows:", len(items))

def pick_status(row):
    keys = [
        'trigger_status', 'trigger status', 'send_status', 'send status',
        'workflow_status', 'workflow status', 'status', 'request_status', 'request status'
    ]
    for k in keys:
        if k in row and row[k] is not None and str(row[k]).strip() != '':
            return str(row[k]).strip().lower(), k
    return '', ''

selected = []
for it in items:
    row = it.get('json', {})
    st, key = pick_status(row)
    sent = str(row.get('sent_status', row.get('sent status', ''))).strip().lower()
    wst = str(row.get('workflow_status', row.get('workflow status', ''))).strip().lower()
    req = str(row.get('request_id', row.get('requestId', ''))).strip()
    rnum = row.get('row_number', row.get('rowNumber', ''))
    cname = row.get('company_name', row.get('company', ''))
    link = row.get('company_link', row.get('website', row.get('url', '')))

    qualifies = bool(st in ('start', 'continue') and sent not in ('done','finish') and wst not in ('done','completed') and (req or rnum))
    print(f"row={rnum} req={req} company={cname!r} status={st!r} via={key} sent={sent!r} wf={wst!r} link={'Y' if str(link).strip() else 'N'} qualifies={qualifies}")
    if qualifies:
        selected.append((rnum, req, cname, st))

print("\nqualifying rows:", len(selected))
for s in selected[:10]:
    print(" ", s)

sn = run_data.get('Select New Intake Rows', [])
if sn:
    out = sn[0].get('data', {}).get('main', [[]])[0]
    print("\nactual Select New Intake Rows output items:", len(out))
    for o in out:
        j = o.get('json', {})
        print(" ", j.get('row_number'), j.get('request_id'), j.get('company_name'), j.get('send_status'), j.get('trigger_status'))
