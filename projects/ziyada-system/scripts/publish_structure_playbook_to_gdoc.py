#!/usr/bin/env python3
"""Publish the workspace structure playbook to Google Docs.

Usage:
  cd projects/ziyada-system
  python3 scripts/publish_structure_playbook_to_gdoc.py

For a full in-place rebuild with heading styles and cleaned markdown markers,
use:
    python3 scripts/rebuild_structure_playbook_doc.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import json
from urllib.parse import urlparse

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


def load_markdown(playbook_path: Path) -> str:
    if not playbook_path.exists():
        raise FileNotFoundError(f"Playbook not found: {playbook_path}")
    return playbook_path.read_text(encoding="utf-8")


def normalize_text(md: str) -> str:
    # Keep markdown headings and bullets readable in Docs.
    lines = [line.rstrip() for line in md.splitlines()]
    return "\n".join(lines).strip() + "\n"


def _extract_first_json_object(raw: str) -> dict:
    depth = 0
    start = None
    for i, ch in enumerate(raw):
        if ch == "{":
            if start is None:
                start = i
            depth += 1
        elif ch == "}":
            if start is not None:
                depth -= 1
                if depth == 0:
                    return json.loads(raw[start : i + 1])
    raise ValueError("No valid JSON object found in credentials content")


def _resolve_credentials_file(project_root: Path) -> tuple[Path, str, list[str]]:
    # Prefer installed-app OAuth clients for local desktop automation.
    candidates = [
        *sorted(project_root.glob("client_secret_*.json")),
        project_root / "credentials.json",
        *sorted(project_root.glob("*client_secret_*.json")),
    ]

    found: list[tuple[Path, str, list[str]]] = []

    for path in candidates:
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = _extract_first_json_object(raw)

        if "installed" in data:
            redirect_uris = data["installed"].get("redirect_uris", [])
            clean_path = project_root / ".tmp" / "credentials.installed.cleaned.json"
            clean_path.parent.mkdir(parents=True, exist_ok=True)
            clean_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            found.append((clean_path, "installed", redirect_uris))
        elif "web" in data:
            redirect_uris = data["web"].get("redirect_uris", [])
            clean_path = project_root / ".tmp" / "credentials.web.cleaned.json"
            clean_path.parent.mkdir(parents=True, exist_ok=True)
            clean_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            found.append((clean_path, "web", redirect_uris))

    for item in found:
        if item[1] == "installed":
            return item
    if found:
        return found[0]

    raise FileNotFoundError(
        "No valid OAuth client JSON found. Place credentials.json or client_secret_*.json in project root."
    )


def _pick_local_server_port(redirect_uris: list[str]) -> int:
    preferred = [8080, 8888]
    ports = set()
    for uri in redirect_uris:
        try:
            parsed = urlparse(uri)
        except Exception:
            continue
        if parsed.hostname in {"localhost", "127.0.0.1"}:
            if parsed.port:
                ports.add(parsed.port)
            elif parsed.scheme in {"http", "https"}:
                ports.add(80)

    for p in preferred:
        if p in ports:
            return p
    return 8080


def get_credentials(project_root: Path) -> Credentials:
    token_path = project_root / "token_docs.json"
    cred_path, client_type, redirect_uris = _resolve_credentials_file(project_root)

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
        # Use deterministic localhost port to avoid redirect_uri mismatch with web clients.
        port = _pick_local_server_port(redirect_uris)
        host = "localhost"
        if client_type == "web":
            flow.redirect_uri = f"http://{host}:{port}"
        creds = flow.run_local_server(host=host, port=port, open_browser=True)

    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def publish_document(creds: Credentials, content: str) -> tuple[str, str]:
    docs_service = build("docs", "v1", credentials=creds)

    title = "Workspace Structure Playbook Template"
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": content,
                    }
                }
            ]
        },
    ).execute()

    # Basic heading formatting for readability.
    heading_requests = []
    idx = 1
    for line in content.splitlines(True):
        line_len = len(line)
        if line.startswith("# "):
            heading_requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + line_len},
                        "paragraphStyle": {"namedStyleType": "HEADING_1"},
                        "fields": "namedStyleType",
                    }
                }
            )
        elif line.startswith("## "):
            heading_requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + line_len},
                        "paragraphStyle": {"namedStyleType": "HEADING_2"},
                        "fields": "namedStyleType",
                    }
                }
            )
        idx += line_len

    if heading_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": heading_requests},
        ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_id, url


def append_to_document(creds: Credentials, doc_id: str, content: str) -> tuple[str, str]:
    docs_service = build("docs", "v1", credentials=creds)
    doc = docs_service.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": end_index},
                        "text": "\n\n" + content,
                    }
                }
            ]
        },
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_id, url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish or append playbook markdown to Google Docs.")
    parser.add_argument(
        "--playbook",
        default="docs/PROJECT_STRUCTURE_PLAYBOOK.md",
        help="Project-relative path to markdown file to publish.",
    )
    parser.add_argument(
        "--doc-id",
        default="",
        help="Existing Google Doc ID. Required when --append is used.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append content to an existing Google Doc instead of creating a new one.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    playbook_path = project_root / args.playbook

    markdown = load_markdown(playbook_path)
    content = normalize_text(markdown)
    creds = get_credentials(project_root)

    if args.append:
        if not args.doc_id:
            raise ValueError("--doc-id is required when using --append")
        doc_id, url = append_to_document(creds, args.doc_id, content)
        print("Google Doc updated successfully")
    else:
        doc_id, url = publish_document(creds, content)
        print("Google Doc created successfully")

    print(f"Document ID: {doc_id}")
    print(f"URL: {url}")


if __name__ == "__main__":
    main()
