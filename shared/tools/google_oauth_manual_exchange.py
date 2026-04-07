#!/usr/bin/env python3
"""Universal Google OAuth helper for projects that hit localhost/browser callback issues.

This helper avoids auto-opening browser and supports a reliable manual flow.

Examples:
  python3 shared/tools/google_oauth_manual_exchange.py \
    --client-file projects/ziyada-system/credentials.json \
    --token-file projects/ziyada-system/token.json \
    --scopes "https://www.googleapis.com/auth/youtube.readonly,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/gmail.compose"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen

from google.oauth2.credentials import Credentials


def load_client(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="ignore").strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError(f"Invalid JSON in client file: {path}")
    data = json.loads(raw[start : end + 1])
    if "installed" in data:
        return data["installed"]
    if "web" in data:
        return data["web"]
    raise RuntimeError(f"No installed/web client entry in: {path}")


def auth_url(client_id: str, redirect_uri: str, scopes: list[str]) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    return "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)


def extract_code(value: str) -> str:
    text = value.strip()
    if text.startswith("http://") or text.startswith("https://"):
        parsed = urlparse(text)
        q = parse_qs(parsed.query)
        return q.get("code", [""])[0]
    return text


def exchange_code(client_id: str, client_secret: str, redirect_uri: str, code: str) -> dict:
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
    parser = argparse.ArgumentParser(description="Universal manual Google OAuth helper")
    parser.add_argument("--client-file", required=True)
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--scopes", required=True, help="Comma-separated scopes")
    parser.add_argument("--redirect-uri", default="http://localhost:8080/")
    args = parser.parse_args()

    client_file = Path(args.client_file)
    token_file = Path(args.token_file)
    scopes = [s.strip() for s in args.scopes.split(",") if s.strip()]

    client = load_client(client_file)
    client_id = client["client_id"]
    client_secret = client["client_secret"]

    url = auth_url(client_id, args.redirect_uri, scopes)
    print("Open this URL in browser, approve, then paste redirect URL (or code):")
    print(url)

    user_input = input("\nPaste redirect URL or code: ").strip()
    code = extract_code(user_input)
    if not code:
        raise SystemExit("Could not parse authorization code")

    token = exchange_code(client_id, client_secret, args.redirect_uri, code)
    if "access_token" not in token:
        raise SystemExit(f"Token exchange failed: {token}")

    creds = Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )

    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    print(f"Saved token: {token_file}")


if __name__ == "__main__":
    main()
