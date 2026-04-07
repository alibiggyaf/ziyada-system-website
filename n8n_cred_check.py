#!/usr/bin/env python3
"""Try to refresh the n8n Google Sheets credential using our local token.
First reads the current credential schema, then tries to patch it."""
import json, urllib.request, urllib.error
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

N8N_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL  = "https://n8n.srv953562.hstgr.cloud/api/v1"
CRED_ID  = "7Y66oaiIkiRR8O2Q"   # Google Sheets ali.biggy gmail
TRIG_ID  = "CQwYp1Fl6sAboeYP"   # Google Sheets Trigger

HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

def n8n(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# 1. Get fresh local token
print("1. Refreshing local token...")
creds = Credentials.from_authorized_user_file(
    'projects/ziyada-system/token.json',
    ['https://www.googleapis.com/auth/spreadsheets']
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    print(f"   Refreshed. New expiry: {creds.expiry}")
else:
    print(f"   Token valid. Expiry: {creds.expiry}")

print(f"   access_token[:40]: {creds.token[:40]}...")
print(f"   refresh_token[:40]: {creds.refresh_token[:40]}...")

# 2. Read current n8n credential structure
print("\n2. Reading n8n credential structure...")
st, cred_data = n8n("GET", f"/credentials/{CRED_ID}")
print(f"   Status: {st}")
if st == 200:
    print(f"   Name: {cred_data.get('name')}")
    print(f"   Type: {cred_data.get('type')}")
    # The actual credential data keys (not values, as they may be hidden)
    d = cred_data.get("data", {})
    print(f"   Data keys: {list(d.keys()) if isinstance(d, dict) else 'encrypted'}")
    print(f"   Full cred (sanitized): {json.dumps({k: '***' if 'token' in k.lower() or 'secret' in k.lower() else v for k,v in cred_data.items() if k != 'data'}, indent=2)}")
else:
    print(f"   Error: {cred_data}")

print("\n3. Reading TRIGGER credential structure...")
st2, cred2 = n8n("GET", f"/credentials/{TRIG_ID}")
print(f"   Status: {st2}")
if st2 == 200:
    print(f"   Name: {cred2.get('name')}")
    print(f"   Type: {cred2.get('type')}")
    d2 = cred2.get("data", {})
    print(f"   Data keys: {list(d2.keys()) if isinstance(d2, dict) else 'encrypted/hidden'}")
