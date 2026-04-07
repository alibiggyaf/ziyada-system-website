#!/usr/bin/env python3
"""Rebuild the playbook Google Doc with proper heading styles and clean text.

This script replaces the full document body content in place, then applies:
- H1/H2/H3 paragraph styles from markdown headings
- Bullet formatting for '-' list items
- Cleaned text without raw markdown heading markers
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from urllib.parse import urlparse

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

DOC_ID = "1wshq883UJYvSqqjqv1JE_nv9uFucAzrgHGhMiIAbjVM"


@dataclass
class LineSpec:
    text: str
    heading: str | None = None
    bullet: bool = False


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


def _resolve_credentials_file(project_root: Path) -> Path:
    candidates = [
        *sorted(project_root.glob("client_secret_*.json")),
        project_root / "credentials.json",
        *sorted(project_root.glob("*client_secret_*.json")),
    ]

    for path in candidates:
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = _extract_first_json_object(raw)

        if "installed" in data or "web" in data:
            clean_path = project_root / ".tmp" / "credentials.cleaned.json"
            clean_path.parent.mkdir(parents=True, exist_ok=True)
            clean_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return clean_path

    raise FileNotFoundError("No valid OAuth credentials found in project root")


def _pick_local_server_port(redirect_uris: list[str]) -> int:
    preferred = [8080, 8888]
    ports = set()
    for uri in redirect_uris:
        try:
            parsed = urlparse(uri)
        except Exception:
            continue
        if parsed.hostname in {"localhost", "127.0.0.1"} and parsed.port:
            ports.add(parsed.port)
    for p in preferred:
        if p in ports:
            return p
    return 8080


def get_credentials(project_root: Path) -> Credentials:
    token_path = project_root / "token_docs.json"
    cred_path = _resolve_credentials_file(project_root)

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        raw = json.loads(cred_path.read_text(encoding="utf-8"))
        redirect_uris = []
        if "installed" in raw:
            redirect_uris = raw["installed"].get("redirect_uris", [])
        elif "web" in raw:
            redirect_uris = raw["web"].get("redirect_uris", [])

        port = _pick_local_server_port(redirect_uris)
        flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
        creds = flow.run_local_server(host="localhost", port=port, open_browser=True)

    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def parse_markdown(md: str) -> list[LineSpec]:
    specs: list[LineSpec] = []
    numbered_re = re.compile(r"^(\d+)\.\s+")

    for raw in md.splitlines():
        line = raw.rstrip()

        # Drop decorative dividers if present.
        if line.strip().startswith("===") and line.strip().endswith("==="):
            line = line.strip("= ")
            specs.append(LineSpec(text=line, heading="HEADING_2"))
            continue

        if line.startswith("### "):
            specs.append(LineSpec(text=line[4:], heading="HEADING_3"))
            continue
        if line.startswith("## "):
            specs.append(LineSpec(text=line[3:], heading="HEADING_2"))
            continue
        if line.startswith("# "):
            specs.append(LineSpec(text=line[2:], heading="HEADING_1"))
            continue

        if line.startswith("- "):
            text = line[2:]
            specs.append(LineSpec(text=text, bullet=True))
            continue

        # Keep numbered lists as plain text for stable ordering in docs.
        if numbered_re.match(line):
            specs.append(LineSpec(text=line))
            continue

        specs.append(LineSpec(text=line))

    return specs


def build_content_and_requests(specs: list[LineSpec], start_index: int = 1) -> tuple[str, list[dict]]:
    lines = [s.text for s in specs]
    content = "\n".join(lines).rstrip() + "\n"

    requests: list[dict] = []
    idx = start_index
    bullet_ranges: list[tuple[int, int]] = []

    for s in specs:
        line_len = len(s.text) + 1  # includes newline
        if s.heading:
            requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + line_len},
                        "paragraphStyle": {"namedStyleType": s.heading},
                        "fields": "namedStyleType",
                    }
                }
            )
        if s.bullet and len(s.text.strip()) > 0:
            bullet_ranges.append((idx, idx + line_len))
        idx += line_len

    for start, end in bullet_ranges:
        requests.append(
            {
                "createParagraphBullets": {
                    "range": {"startIndex": start, "endIndex": end},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                }
            }
        )

    return content, requests


def rebuild_document(creds: Credentials, doc_id: str, content: str, format_requests: list[dict]) -> str:
    docs = build("docs", "v1", credentials=creds)
    doc = docs.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"]

    requests = [
        {
            "deleteContentRange": {
                "range": {"startIndex": 1, "endIndex": end_index - 1}
            }
        },
        {
            "insertText": {
                "location": {"index": 1},
                "text": content,
            }
        },
    ] + format_requests

    docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
    return f"https://docs.google.com/document/d/{doc_id}/edit"


def main() -> None:
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    en_path = project_root / "docs" / "PROJECT_STRUCTURE_PLAYBOOK.md"
    ar_path = project_root / "docs" / "PROJECT_STRUCTURE_PLAYBOOK_AR.md"

    en_md = en_path.read_text(encoding="utf-8")
    ar_md = ar_path.read_text(encoding="utf-8")

    combined = en_md.strip() + "\n\n# Arabic Section (الملحق العربي)\n\n" + ar_md.strip() + "\n"

    specs = parse_markdown(combined)
    content, format_requests = build_content_and_requests(specs, start_index=1)

    creds = get_credentials(project_root)
    url = rebuild_document(creds, DOC_ID, content, format_requests)

    print("Document rebuilt with proper heading styles")
    print(f"Document ID: {DOC_ID}")
    print(f"URL: {url}")


if __name__ == "__main__":
    main()
