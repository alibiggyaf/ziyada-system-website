#!/usr/bin/env python3
"""One-time OAuth setup for YouTube trend report scopes.

Usage:
    python3 scripts/setup_youtube_report_oauth.py --manual
  python3 scripts/setup_youtube_report_oauth.py --print-url
  python3 scripts/setup_youtube_report_oauth.py --exchange-code '<code_or_redirect_url>'
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2 import MismatchingStateError


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
TOKEN_PATH = PROJECT_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.compose",
]


def _report_saved_scopes() -> None:
    data = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    saved_scopes = set(data.get("scopes") or [])
    required_scopes = set(SCOPES)
    missing = sorted(required_scopes - saved_scopes)
    print(f"Saved token to {TOKEN_PATH}")
    print("Saved scopes:")
    for scope in sorted(saved_scopes):
        print(f"- {scope}")
    if missing:
        print("Missing scopes:")
        for scope in missing:
            print(f"- {scope}")
    else:
        print("All required report scopes are present.")


def _load_client_config() -> dict:
    candidates = [
        PROJECT_DIR / "client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json",
        PROJECT_DIR / "credentials.json",
        PROJECT_DIR / ".tmp" / "credentials.installed.cleaned.json",
        PROJECT_DIR / ".tmp" / "credentials.cleaned.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore").strip()
        if not raw:
            continue
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            continue
        data = json.loads(raw[start : end + 1])
        if "installed" in data:
            return data["installed"]
        if "web" in data:
            return data["web"]
    raise RuntimeError("No valid OAuth client config found in project files")


def _select_redirect_uri(client: dict, port: int = 8080) -> str:
    """Pick an exact redirect URI that exists in OAuth client config.

    Using an exact match avoids Google's "request is invalid" errors caused by
    subtle mismatches like trailing slashes.
    """
    uris = client.get("redirect_uris") or []
    preferred = [
        f"http://localhost:{port}/",
        f"http://127.0.0.1:{port}/",
        f"http://localhost:{port}",
        f"http://127.0.0.1:{port}",
        "http://localhost/",
        "http://127.0.0.1/",
        "http://localhost",
        "http://127.0.0.1",
    ]
    for candidate in preferred:
        if candidate in uris:
            return candidate
    if uris:
        return uris[0]
    return f"http://localhost:{port}"


def _auth_url(client_id: str, redirect_uri: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    return "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)


def _extract_code(value: str) -> str:
    text = value.strip()
    if text.startswith("http://") or text.startswith("https://"):
        parsed = urlparse(text)
        q = parse_qs(parsed.query)
        return q.get("code", [""])[0]
    return text


def _exchange_code(client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    encoded = urlencode(payload).encode("utf-8")
    with urlopen("https://oauth2.googleapis.com/token", data=encoded) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup OAuth token for YouTube trend report")
    parser.add_argument("--manual", action="store_true", help="One-step mode: print URL, then prompt for redirect URL/code")
    parser.add_argument("--print-url", action="store_true")
    parser.add_argument("--exchange-code", default="")
    parser.add_argument("--local-server", action="store_true", help="Run localhost callback server; prints URL if browser cannot auto-open")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    client = _load_client_config()
    client_id = client["client_id"]
    client_secret = client["client_secret"]
    redirect_uri = _select_redirect_uri(client, port=args.port)

    if args.manual:
        url = _auth_url(client_id, redirect_uri)
        print("Open this URL in your browser, approve access, then paste the full redirected URL (or just code):")
        print(f"Using redirect_uri: {redirect_uri}")
        print("Note: do not open localhost manually before consent. Google will redirect you there after approval.")
        print(url)
        user_input = input("\nPaste redirect URL or code: ").strip()
        code = _extract_code(user_input)
        if not code:
            raise SystemExit("Could not parse authorization code")
        token = _exchange_code(client_id, client_secret, code, redirect_uri)
        if "access_token" not in token:
            raise SystemExit(f"Token exchange failed: {token}")

        creds = Credentials(
            token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES,
        )
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        _report_saved_scopes()
        return

    if args.print_url:
        print(f"redirect_uri={redirect_uri}")
        print(_auth_url(client_id, redirect_uri))
        return

    if args.local_server:
        # Local callback flow. Avoid browser auto-open because some systems block osascript.
        flow = InstalledAppFlow.from_client_config({"installed": client}, SCOPES)
        # Host 127.0.0.1 avoids localhost resolution issues on some setups.
        print(f"Waiting for OAuth callback on http://127.0.0.1:{args.port}/ ...")
        try:
            creds = flow.run_local_server(host="127.0.0.1", port=args.port, open_browser=False)
        except MismatchingStateError:
            print("\nOAuth state mismatch detected.")
            print("This usually means the approved URL came from an older run or a different app/session.")
            print("Retry with a fresh URL from this exact command, or use manual fallback:")
            print("1) Run with --print-url and open only that URL")
            print("2) After Google redirects to localhost, copy the full URL from browser")
            print("3) Run with --exchange-code '<full_redirect_url>'")
            raise SystemExit(1)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        _report_saved_scopes()
        return

    if args.exchange_code:
        code = _extract_code(args.exchange_code)
        if not code:
            raise SystemExit("Could not parse authorization code")
        token = _exchange_code(client_id, client_secret, code, redirect_uri)
        if "access_token" not in token:
            raise SystemExit(f"Token exchange failed: {token}")

        creds = Credentials(
            token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES,
        )
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        _report_saved_scopes()
        return

    raise SystemExit("Use --manual, --print-url, --exchange-code, or --local-server")


if __name__ == "__main__":
    main()
