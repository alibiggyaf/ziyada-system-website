#!/usr/bin/env python3
"""
Manual OAuth token exchange.
1. Open the printed URL in your browser
2. Approve access
3. Browser redirects to localhost (page won't load — that's OK!)
4. Copy the FULL URL from browser address bar
5. Paste it here
"""

import json, re, sys
from urllib.parse import urlparse, parse_qs
import requests as req

CLIENT_ID = "724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8080/"
TOKEN_FILE = '/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/token_docs.json'
SCOPES = "https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/drive.file"

auth_url = (
    f"https://accounts.google.com/o/oauth2/auth?"
    f"response_type=code&"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&"
    f"scope={SCOPES.replace(' ', '+')}&"
    f"prompt=consent&"
    f"access_type=offline"
)

print("\n" + "="*60)
print("STEP 1: Open this URL in your browser:")
print("="*60)
print(f"\n{auth_url}\n")
print("="*60)
print("\nSTEP 2: Sign in and click Allow")
print("STEP 3: The page will fail to load (that's normal!)")
print("STEP 4: Copy the FULL URL from the address bar")
print("        It starts with: http://localhost:8080/?...")
print("STEP 5: Paste it below\n")

redirect_url = input("Paste the full redirect URL here: ").strip()

# Extract auth code from URL
parsed = urlparse(redirect_url)
params = parse_qs(parsed.query)

if 'code' not in params:
    print(f"Error: No 'code' found in URL. Got: {params}")
    sys.exit(1)

code = params['code'][0]
print(f"\nExchanging code for token...")

resp = req.post("https://oauth2.googleapis.com/token", data={
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
})

if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)

tokens = resp.json()

token_data = {
    "token": tokens["access_token"],
    "refresh_token": tokens.get("refresh_token", ""),
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scopes": SCOPES.split(" ")
}

with open(TOKEN_FILE, 'w') as f:
    json.dump(token_data, f, indent=2)

print(f"\nToken saved to {TOKEN_FILE}")
print("SUCCESS!")
