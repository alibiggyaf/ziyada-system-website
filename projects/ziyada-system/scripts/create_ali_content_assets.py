#!/usr/bin/env python3
"""Create Ali Content Writer Engine 2026 Google assets (Doc + Slides), and best-effort Sheet.

Uses project tokens already present:
- token_docs.json for Google Docs + Drive
- token.json for Slides + Drive
- best-effort Sheet create via Sheets API using token.json (may fail if scope missing)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ROOT_DIR = PROJECT_DIR.parent.parent

DOC_SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

SLIDES_SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

TITLE_BASE = "Ali Content Writer Engine 2026"
DOC_TITLE = f"{TITLE_BASE} - Content Pack"
SLIDES_TITLE = f"{TITLE_BASE} - Monthly Content Plan"
SHEET_TITLE = TITLE_BASE


def load_env() -> None:
    for env_path in (ROOT_DIR / ".env", PROJECT_DIR / ".env"):
        if not env_path.exists():
            continue
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


def creds_from_token(token_name: str, scopes: list[str]) -> Credentials:
    token_path = PROJECT_DIR / token_name
    if not token_path.exists():
        raise FileNotFoundError(f"Missing token file: {token_path}")
    creds = Credentials.from_authorized_user_file(str(token_path), scopes)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError(f"Invalid token for scopes: {token_name}")
    return creds


def create_doc() -> tuple[str, str]:
    creds = creds_from_token("token_docs.json", DOC_SCOPES)
    docs = build("docs", "v1", credentials=creds)
    doc = docs.documents().create(body={"title": DOC_TITLE}).execute()
    doc_id = doc["documentId"]

    reqs = [
        {"insertText": {"location": {"index": 1}, "text": (
            "Ali Content Writer Engine 2026\n\n"
            "This document is auto-created for content execution outputs.\n"
            "It will contain: social content, blog/article, newsletter, hooks, and execution notes.\n"
        )}},
    ]
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": reqs}).execute()
    return doc_id, f"https://docs.google.com/document/d/{doc_id}/edit"


def create_slides() -> tuple[str, str]:
    creds = creds_from_token("token.json", SLIDES_SCOPES)
    slides = build("slides", "v1", credentials=creds)
    deck = slides.presentations().create(body={"title": SLIDES_TITLE}).execute()
    deck_id = deck["presentationId"]
    return deck_id, f"https://docs.google.com/presentation/d/{deck_id}/edit"


def create_sheet_best_effort() -> tuple[str, str] | tuple[None, None]:
    try:
        creds = creds_from_token("token.json", SHEETS_SCOPES)
        sheets = build("sheets", "v4", credentials=creds)
        sh = sheets.spreadsheets().create(body={"properties": {"title": SHEET_TITLE}}).execute()
        sid = sh["spreadsheetId"]
        return sid, f"https://docs.google.com/spreadsheets/d/{sid}/edit"
    except Exception:
        return None, None


def append_env_values(values: dict[str, str]) -> None:
    env_path = ROOT_DIR / ".env"
    existing = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    lines = existing.splitlines()

    def set_or_add(key: str, value: str) -> None:
        prefix = f"{key}="
        for i, line in enumerate(lines):
            if line.strip().startswith(prefix):
                lines[i] = f'{key}="{value}"'
                return
        lines.append(f'{key}="{value}"')

    for k, v in values.items():
        if v:
            set_or_add(k, v)

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    load_env()

    doc_id, doc_url = create_doc()
    slides_id, slides_url = create_slides()
    sheet_id, sheet_url = create_sheet_best_effort()

    env_updates = {
        "ZIYADA_CONTENT_DOC_URL": doc_url,
        "ZIYADA_CONTENT_SLIDES_URL": slides_url,
    }

    # Only update sheet id if we successfully created one with sheets scope.
    if sheet_id and sheet_url:
        env_updates["ZIYADA_BLOG_SHEET_ID"] = sheet_id

    append_env_values(env_updates)

    result = {
        "doc_id": doc_id,
        "doc_url": doc_url,
        "slides_id": slides_id,
        "slides_url": slides_url,
        "sheet_id": sheet_id,
        "sheet_url": sheet_url,
        "sheet_created": bool(sheet_id),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
