#!/usr/bin/env python3
"""
One-shot OAuth2 flow for Google Slides + Drive.
Uses InstalledAppFlow.run_local_server — starts a local server,
opens your browser, captures the auth code automatically,
and saves token.json in this scripts/ folder.
"""
import json
import os
import sys

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS = os.path.join(
    SCRIPT_DIR, "..",
    "client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json"
)
TOKEN_OUT = os.path.join(SCRIPT_DIR, "token.json")
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

def main():
    from google_auth_oauthlib.flow import InstalledAppFlow

    print("\n" + "=" * 60)
    print("  Ziyada System — Google Slides OAuth Setup")
    print("=" * 60)
    print("\nA browser window will open. Please approve access.")
    print("This terminal will wait until you approve...\n")

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, scopes=SCOPES)
    creds = flow.run_local_server(
        port=8080,
        prompt="consent",
        success_message=(
            "<html><body style='background:#0f172a;color:#e2e8f0;"
            "font-family:sans-serif;display:flex;align-items:center;"
            "justify-content:center;height:100vh;margin:0;'>"
            "<div style='text-align:center;'>"
            "<h1 style='color:#3b82f6;font-size:2.5rem;'>&#10003; Authenticated!</h1>"
            "<p style='color:#8b5cf6;font-size:1.2rem;'>Ziyada System is authorised.<br>"
            "You can close this tab and return to VS Code.</p>"
            "</div></body></html>"
        ),
        open_browser=True,
    )

    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes),
    }
    with open(TOKEN_OUT, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"\n[SUCCESS] token.json saved to:\n  {TOKEN_OUT}")
    print("\nRunning the brand guideline deck builder now...")

if __name__ == "__main__":
    main()
