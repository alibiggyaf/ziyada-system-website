#!/usr/bin/env python3
"""
OAuth refresh for token_docs.json (Docs + Drive scopes).

Usage:
  # Mode 1 - auto (starts local server, opens browser, saves token):
  python3 refresh_token_docs.py --auto

  # Mode 2 - get auth URL only (print and open browser):
  python3 refresh_token_docs.py --get-url

  # Mode 3 - exchange code/redirect URL for token:
  python3 refresh_token_docs.py --url "http://localhost:8080/?code=4/0A...&scope=..."
"""
import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Required to allow http://localhost redirect URIs with google-auth-oauthlib
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from google_auth_oauthlib.flow import Flow

PROJECT_DIR = Path(__file__).resolve().parents[1]

CLIENT_SECRET = str(PROJECT_DIR / "client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json")
TOKEN_OUT = str(PROJECT_DIR / "token_docs.json")

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]
REDIRECT_URI = "http://localhost:8080/"


def make_flow():
    return Flow.from_client_secrets_file(
        CLIENT_SECRET, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )


def cmd_get_url():
    flow = make_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    print()
    print("=" * 70)
    print("  افتح هذا الرابط في المتصفح / Open this URL in your browser:")
    print()
    print(f"  {auth_url}")
    print()
    print("  بعد الموافقة ستظهر صفحة 'This site can't be reached' — هذا طبيعي")
    print("  انسخ الرابط الكامل من شريط العنوان ثم نفّذ:")
    print()
    print('  python3 refresh_token_docs.py --url "http://localhost:8080/?code=..."')
    print("=" * 70)
    print()
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass


def cmd_exchange(redirect_response: str):
    flow = make_flow()
    try:
        flow.fetch_token(authorization_response=redirect_response)
    except Exception as e:
        print(f"❌ Error fetching token: {e}")
        sys.exit(1)

    creds = flow.credentials
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
    print(f"\n✅ Token saved to: {TOKEN_OUT}\n")


def cmd_auto(port: int = 8080):
    """Start a local server, open browser, capture callback, save token automatically."""
    captured = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            captured["path"] = self.path
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0f172a;color:#e2e8f0">
                <h2 style="color:#3b82f6">&#10003; Authorization Complete!</h2>
                <p>Token saved successfully. You can close this tab.</p>
                </body></html>
            """)

        def log_message(self, format, *args):
            pass  # silence server logs

    try:
        server = HTTPServer(("localhost", port), CallbackHandler)
    except OSError:
        print(f"❌ Port {port} is in use. Try: python3 refresh_token_docs.py --auto --port 8081")
        sys.exit(1)

    flow = make_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    print(f"\n🌐 Opening browser for Google authorization...")
    print(f"   If browser doesn't open, visit:\n   {auth_url}\n")
    webbrowser.open(auth_url)

    print(f"⏳ Waiting for callback on port {port}...")
    server.handle_request()  # handle exactly one request then stop

    if "path" not in captured:
        print("❌ No callback received.")
        sys.exit(1)

    redirect_response = f"http://localhost:{port}{captured['path']}"
    try:
        flow.fetch_token(authorization_response=redirect_response)
    except Exception as e:
        print(f"❌ Error fetching token: {e}")
        sys.exit(1)

    creds = flow.credentials
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
    print(f"\n✅ Token saved to: {TOKEN_OUT}\n")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--auto":
        port = 8080
        if "--port" in args:
            idx = args.index("--port")
            port = int(args[idx + 1])
        cmd_auto(port)
        return
    if args[0] == "--get-url":
        cmd_get_url()
        return
    if args[0] == "--url" and len(args) >= 2:
        cmd_exchange(args[1])
        return
    # If a bare URL was passed directly
    if args[0].startswith("http"):
        cmd_exchange(args[0])
        return
    print("Usage:")
    print("  python3 refresh_token_docs.py --auto          # recommended")
    print("  python3 refresh_token_docs.py --get-url")
    print('  python3 refresh_token_docs.py --url "http://localhost:8080/?code=..."')
    sys.exit(1)


if __name__ == "__main__":
    main()

