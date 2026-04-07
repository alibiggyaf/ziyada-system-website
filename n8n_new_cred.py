#!/usr/bin/env python3
"""Try different credential schema structures to create a valid Google Sheets credential."""
import json, urllib.request, urllib.error
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID   = "C8JWsE3KIoxr1KgO"
OLD_CRED_ID = "7Y66oaiIkiRR8O2Q"

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

# Get fresh token
creds = Credentials.from_authorized_user_file(
    'projects/ziyada-system/token.json',
    ['https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive']
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

expiry_ms = int(creds.expiry.timestamp() * 1000) if creds.expiry else 9999999999000

print("Trying different credential schemas...\n")

# Schema variant 1: flat oauthTokenData with clientId/Secret
schemas = [
    ("flat_with_client", {
        "name": "Google Sheets ALI Fresh",
        "type": "googleSheetsOAuth2Api",
        "data": {
            "oauthTokenData": {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "scope": "https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive",
                "token_type": "Bearer",
                "expiry_date": expiry_ms,
            },
            "clientId": OAUTH_CLIENT_ID,
            "clientSecret": OAUTH_CLIENT_SECRET,
        }
    }),
    ("flat_only_tokens", {
        "name": "Google Sheets ALI Fresh",
        "type": "googleSheetsOAuth2Api",
        "data": {
            "oauthTokenData": {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "scope": "https://www.googleapis.com/auth/spreadsheets",
                "token_type": "Bearer",
                "expiry_date": expiry_ms,
            }
        }
    }),
    ("no_nesting", {
        "name": "Google Sheets ALI Fresh",
        "type": "googleSheetsOAuth2Api",
        "data": {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "scope": "https://www.googleapis.com/auth/spreadsheets",
            "token_type": "Bearer",
            "expiry_date": expiry_ms,
        }
    }),
]

for name, body in schemas:
    st, resp = n8n("POST", "/credentials", body)
    cred_id = resp.get("id") if st in (200, 201) else None
    print(f"Schema '{name}': status={st} id={cred_id}")
    if st in (200, 201):
        print(f"  ✓ Created credential ID: {cred_id}")
        # Update workflow to reference new credential
        print("  Updating workflow nodes...")
        st_wf, wf = n8n("GET", f"/workflows/{WF_ID}")
        if st_wf == 200:
            nodes = wf.get("nodes", [])
            changed = 0
            for node in nodes:
                crds = node.get("credentials", {})
                for ck, cv in crds.items():
                    if isinstance(cv, dict) and cv.get("id") == OLD_CRED_ID:
                        cv["id"] = cred_id
                        cv["name"] = "Google Sheets ALI Fresh"
                        changed += 1
            if changed:
                st_up, r_up = n8n("PUT", f"/workflows/{WF_ID}", wf)
                print(f"  Updated {changed} references in workflow. PUT status={st_up}")
            else:
                print(f"  No old credential refs found in workflow")
        break  # Stop trying schemas on first success
    else:
        err = resp.get("message","")[:200]
        print(f"  Error: {err}")
    print()
