#!/usr/bin/env python3
"""Manual OAuth flow — paste the auth code from browser."""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file',
]

TOKEN_FILE = '/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/token_docs.json'

CLIENT_CONFIG = {
    "installed": {
        "client_id": "724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com",
        "project_id": "avian-album-467523-s1",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
    }
}

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
creds = flow.run_console()

with open(TOKEN_FILE, 'w') as f:
    f.write(creds.to_json())

print(f"\nToken saved to: {TOKEN_FILE}")
print("Now run: python3 scripts/create_sales_guide_gdoc.py")
