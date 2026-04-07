#!/usr/bin/env python3
"""Create new Google Sheets credential in n8n with fresh token, then update workflow nodes."""
import json, urllib.request, urllib.error
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID   = "C8JWsE3KIoxr1KgO"
OLD_CRED_ID  = "7Y66oaiIkiRR8O2Q"  # Google Sheets ali.biggy gmail (expired)
OLD_TRIG_ID  = "CQwYp1Fl6sAboeYP"  # Google Sheets Trigger (expired)

OAUTH_CLIENT_ID     = "724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com"
OAUTH_CLIENT_SECRET = "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"

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

# 1. Get fresh token
print("1. Getting fresh token...")
creds = Credentials.from_authorized_user_file(
    'projects/ziyada-system/token.json',
    ['https://www.googleapis.com/auth/spreadsheets']
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
print(f"   access_token ok, expiry={creds.expiry}")

# 2. Try to PATCH the existing credential with fresh token data
print("\n2. Trying to PATCH existing 'Read Intake' credential...")
patch_body = {
    "name": "Google Sheets ali.biggy gmail",
    "data": {
        "oauthTokenData": {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_type": "Bearer",
            "scope": "https://www.googleapis.com/auth/spreadsheets",
            "expiry_date": int(creds.expiry.timestamp() * 1000) if creds.expiry else None,
            "clientId": OAUTH_CLIENT_ID,
            "clientSecret": OAUTH_CLIENT_SECRET,
        }
    }
}
st, resp = n8n("PATCH", f"/credentials/{OLD_CRED_ID}", patch_body)
print(f"   Status: {st}")
if st == 200:
    print("   ✓ Credential patched successfully!")
    print(f"   Name: {resp.get('name')} Type: {resp.get('type')}")
else:
    print(f"   Error: {json.dumps(resp)[:300]}")

# 3. Try to PATCH the trigger credential
print("\n3. Trying to PATCH trigger credential...")
patch_body2 = {
    "name": "Google Sheets Trigger account ali.biggy.af",
    "data": {
        "oauthTokenData": {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_type": "Bearer",
            "scope": "https://www.googleapis.com/auth/spreadsheets",
            "expiry_date": int(creds.expiry.timestamp() * 1000) if creds.expiry else None,
            "clientId": OAUTH_CLIENT_ID,
            "clientSecret": OAUTH_CLIENT_SECRET,
        }
    }
}
st2, resp2 = n8n("PATCH", f"/credentials/{OLD_TRIG_ID}", patch_body2)
print(f"   Status: {st2}")
if st2 == 200:
    print("   ✓ Trigger credential patched successfully!")
else:
    print(f"   Error: {json.dumps(resp2)[:300]}")

# 4. Try creating a new credential (if PATCH doesn't work)
if st != 200:
    print("\n4. PATCH failed - Trying POST (create new credential)...")
    new_cred = {
        "name": "Google Sheets Fresh 2026",
        "type": "googleSheetsOAuth2Api",
        "data": {
            "oauthTokenData": {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_type": "Bearer",
                "scope": "https://www.googleapis.com/auth/spreadsheets",
                "expiry_date": int(creds.expiry.timestamp() * 1000) if creds.expiry else None,
                "clientId": OAUTH_CLIENT_ID,
                "clientSecret": OAUTH_CLIENT_SECRET,
            }
        }
    }
    st3, resp3 = n8n("POST", "/credentials", new_cred)
    print(f"   Status: {st3}")
    if st3 in (200, 201):
        new_id = resp3.get("id", "")
        print(f"   ✓ New credential created! ID: {new_id}")
        # Now update the workflow to use new credential
        print(f"\n5. Updating workflow nodes to use new credential {new_id}...")
        st4, wf = n8n("GET", f"/workflows/{WF_ID}")
        if st4 != 200:
            print(f"   Cannot read workflow: {st4}")
        else:
            nodes = wf.get("nodes", [])
            changed = 0
            for node in nodes:
                creds_field = node.get("credentials", {})
                for cred_name, cred_val in creds_field.items():
                    if isinstance(cred_val, dict) and cred_val.get("id") in (OLD_CRED_ID, OLD_TRIG_ID):
                        cred_val["id"] = new_id
                        cred_val["name"] = "Google Sheets Fresh 2026"
                        changed += 1
            if changed:
                st5, resp5 = n8n("PUT", f"/workflows/{WF_ID}", wf)
                print(f"   Updated {changed} node credential references. Status: {st5}")
            else:
                print(f"   No credential references found to update")
    else:
        print(f"   Error: {json.dumps(resp3)[:300]}")

print("\nDONE")
