#!/usr/bin/env python3
"""Organize the Ziyada result sheet into a clean, searchable, deduplicated layout."""

from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]

DEFAULT_SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
DEFAULT_RESULTS_TAB = "resault"
DEFAULT_ARCHIVE_TAB = "resault_archive"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CANON_HEADERS = [
    "request_id",
    "created_at",
    "company_name",
    "company_link",
    "industry",
    "target_audience",
    "topic",
    "approval_status",
    "workflow_status",
    "trigger_status",
    "sent_status",
    "publish_target",
    "Post Type",
    "SUBJECT",
    "TITLE",
    "hook_1",
    "hook_2",
    "hook_3",
    "hook_4",
    "hook_5",
    "Content for instagram",
    "Content for X",
    "Content for Tiktok",
    "Content for Facebook",
    "Content for linkedin",
    "Caption",
    "Website Blogs & Article",
    "Keywords used",
    "Hashtags",
    "Image Prompt",
    "Image Prompt to paste in banana",
    "output",
    "search_company",
    "search_url",
    "search_topic",
    "search_all",
    "author",
    "language",
    "prompt_text",
    "writer_prompt_version",
    "approved_by",
    "approval_notes",
    "approval_date",
]


def load_env_files() -> None:
    for env_path in (ROOT_DIR / ".env", PROJECT_DIR / ".env"):
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ[key] = value


def normalize_header(text: str) -> str:
    return text.strip().lower().replace(" ", "_")


def col_index_to_a1(col_index: int) -> str:
    value = col_index + 1
    letters: List[str] = []
    while value > 0:
        value, rem = divmod(value - 1, 26)
        letters.append(chr(ord("A") + rem))
    return "".join(reversed(letters))


def load_credentials(token_path: Path) -> Credentials:
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.valid:
        return creds
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds
    raise RuntimeError("token.json is invalid for Sheets scope")


def get_sheet_id_by_name(service, spreadsheet_id: str, tab_name: str) -> int:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        if props.get("title") == tab_name:
            return int(props["sheetId"])
    raise RuntimeError(f"Tab not found: {tab_name}")


def ensure_tab_exists(service, spreadsheet_id: str, tab_name: str) -> None:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    titles = {s.get("properties", {}).get("title") for s in meta.get("sheets", [])}
    if tab_name in titles:
        return
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]},
    ).execute()


def get_value(row: List[str], index_map: Dict[str, int], key: str) -> str:
    idx = index_map.get(normalize_header(key))
    if idx is None or idx >= len(row):
        return ""
    return str(row[idx]).strip()


def split_hooks(row: List[str], index_map: Dict[str, int]) -> List[str]:
    hooks: List[str] = []
    for key in ["hook_1", "hook_2", "hook_3", "hook_4", "hook_5"]:
        v = get_value(row, index_map, key)
        if v:
            hooks.append(v)

    if not hooks:
        merged = get_value(row, index_map, "5 strong HOOKS") or get_value(row, index_map, "hooks_raw")
        if merged:
            # Support common separators in current sheet.
            raw_parts = (
                merged.replace("\n", "|")
                .replace("•", "|")
                .replace("؛", "|")
                .split("|")
            )
            hooks = [p.strip(" -") for p in raw_parts if p.strip()]

    hooks = hooks[:5]
    while len(hooks) < 5:
        hooks.append("")
    return hooks


def map_row(row: List[str], index_map: Dict[str, int], fallback_id: str) -> List[str]:
    hooks = split_hooks(row, index_map)

    request_id = get_value(row, index_map, "request_id") or fallback_id
    company_name = get_value(row, index_map, "company_name")
    company_link = get_value(row, index_map, "company_link")
    topic = get_value(row, index_map, "topic")
    title = get_value(row, index_map, "TITLE") or get_value(row, index_map, "title_ar") or topic
    subject = get_value(row, index_map, "SUBJECT") or title

    content_ig = get_value(row, index_map, "Content for instagram") or get_value(row, index_map, "content_ar")
    website_article = get_value(row, index_map, "Website Blogs & Article") or get_value(row, index_map, "content_ar")

    search_company = company_name.lower()
    search_url = company_link.lower()
    search_topic = topic.lower()
    search_all = " | ".join([company_name, company_link, topic, request_id]).lower()

    record = {
        "request_id": request_id,
        "created_at": get_value(row, index_map, "created_at"),
        "company_name": company_name,
        "company_link": company_link,
        "industry": get_value(row, index_map, "industry"),
        "target_audience": get_value(row, index_map, "target_audience"),
        "topic": topic,
        "approval_status": get_value(row, index_map, "approval_status"),
        "workflow_status": get_value(row, index_map, "workflow_status"),
        "trigger_status": get_value(row, index_map, "trigger_status"),
        "sent_status": get_value(row, index_map, "sent_status"),
        "publish_target": get_value(row, index_map, "publish_target"),
        "Post Type": get_value(row, index_map, "Post Type") or "carousel",
        "SUBJECT": subject,
        "TITLE": title,
        "hook_1": hooks[0],
        "hook_2": hooks[1],
        "hook_3": hooks[2],
        "hook_4": hooks[3],
        "hook_5": hooks[4],
        "Content for instagram": content_ig,
        "Content for X": get_value(row, index_map, "Content for X"),
        "Content for Tiktok": get_value(row, index_map, "Content for Tiktok"),
        "Content for Facebook": get_value(row, index_map, "Content for Facebook"),
        "Content for linkedin": get_value(row, index_map, "Content for linkedin"),
        "Caption": get_value(row, index_map, "Caption") or get_value(row, index_map, "excerpt_ar"),
        "Website Blogs & Article": website_article,
        "Keywords used": get_value(row, index_map, "Keywords used") or get_value(row, index_map, "seo_keywords"),
        "Hashtags": get_value(row, index_map, "Hashtags") or get_value(row, index_map, "tags"),
        "Image Prompt": get_value(row, index_map, "Image Prompt"),
        "Image Prompt to paste in banana": get_value(row, index_map, "Image Prompt to paste in banana"),
        "output": get_value(row, index_map, "output"),
        "search_company": search_company,
        "search_url": search_url,
        "search_topic": search_topic,
        "search_all": search_all,
        "author": get_value(row, index_map, "author"),
        "language": get_value(row, index_map, "language"),
        "prompt_text": get_value(row, index_map, "prompt_text"),
        "writer_prompt_version": get_value(row, index_map, "writer_prompt_version"),
        "approved_by": get_value(row, index_map, "approved_by"),
        "approval_notes": get_value(row, index_map, "approval_notes"),
        "approval_date": get_value(row, index_map, "approval_date"),
    }

    return [record[h] for h in CANON_HEADERS]


def dedupe_rows(headers: List[str], rows: List[List[str]]) -> List[List[str]]:
    idx = {normalize_header(h): i for i, h in enumerate(headers)}
    req_i = idx.get("request_id")
    created_i = idx.get("created_at")

    by_id: Dict[str, Tuple[float, List[str]]] = {}
    fallback_rows: List[List[str]] = []

    for row in rows:
        req = row[req_i].strip() if req_i is not None and req_i < len(row) else ""
        if not req:
            fallback_rows.append(row)
            continue

        created = row[created_i].strip() if created_i is not None and created_i < len(row) else ""
        score = 0.0
        if created:
            try:
                score = datetime.fromisoformat(created.replace("Z", "+00:00")).timestamp()
            except Exception:
                score = 0.0
        prev = by_id.get(req)
        if prev is None or score >= prev[0]:
            by_id[req] = (score, row)

    kept = [v[1] for v in by_id.values()]
    kept.extend(fallback_rows)

    def sort_key(r: List[str]) -> float:
        if created_i is None or created_i >= len(r):
            return 0.0
        val = r[created_i].strip()
        if not val:
            return 0.0
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.0

    kept.sort(key=sort_key, reverse=True)
    return kept


def main() -> int:
    load_env_files()

    parser = argparse.ArgumentParser(description="Organize/dedupe Ziyada resault tab")
    parser.add_argument("--sheet-id", default=os.getenv("ZIYADA_BLOG_SHEET_ID", DEFAULT_SHEET_ID))
    parser.add_argument("--results-tab", default=os.getenv("ZIYADA_BLOG_RESULTS_SHEET_TAB", DEFAULT_RESULTS_TAB))
    parser.add_argument("--archive-tab", default=DEFAULT_ARCHIVE_TAB)
    parser.add_argument("--token", default=str(PROJECT_DIR / "token.json"))
    args = parser.parse_args()

    creds = load_credentials(Path(args.token))
    service = build("sheets", "v4", credentials=creds)

    # Read existing result tab.
    read_range = f"{args.results_tab}!A1:ZZ5000"
    values = service.spreadsheets().values().get(spreadsheetId=args.sheet_id, range=read_range).execute().get("values", [])
    if not values:
        raise RuntimeError(f"No data found in tab: {args.results_tab}")

    old_headers = values[0]
    old_rows = values[1:]
    old_idx = {normalize_header(h): i for i, h in enumerate(old_headers)}

    # Archive raw snapshot before rewrite.
    ensure_tab_exists(service, args.sheet_id, args.archive_tab)
    archive_stamp = datetime.utcnow().isoformat() + "Z"
    archive_header = ["archived_at", "source_tab"] + old_headers
    archive_rows = [[archive_stamp, args.results_tab] + row for row in old_rows]

    service.spreadsheets().values().append(
        spreadsheetId=args.sheet_id,
        range=f"{args.archive_tab}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [archive_header] + archive_rows},
    ).execute()

    # Build canonical rows.
    mapped_rows: List[List[str]] = []
    for row_no, row in enumerate(old_rows, start=2):
        fallback_id = f"REQ-MIG-{datetime.utcnow().strftime('%Y%m%d')}-{row_no:04d}"
        mapped_rows.append(map_row(row, old_idx, fallback_id))

    # Remove empty rows and dedupe by request_id.
    non_empty = [r for r in mapped_rows if any(str(x).strip() for x in r)]
    deduped = dedupe_rows(CANON_HEADERS, non_empty)

    # Rewrite result tab with canonical schema.
    service.spreadsheets().values().clear(
        spreadsheetId=args.sheet_id,
        range=f"{args.results_tab}!A1:ZZ5000",
        body={},
    ).execute()

    service.spreadsheets().values().update(
        spreadsheetId=args.sheet_id,
        range=f"{args.results_tab}!A1",
        valueInputOption="RAW",
        body={"values": [CANON_HEADERS] + deduped},
    ).execute()

    # Add filter + frozen header for easier ID/company/URL searching.
    sheet_id = get_sheet_id_by_name(service, args.sheet_id, args.results_tab)
    row_count = max(2, len(deduped) + 1)
    col_count = len(CANON_HEADERS)

    service.spreadsheets().batchUpdate(
        spreadsheetId=args.sheet_id,
        body={
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                        "fields": "gridProperties.frozenRowCount",
                    }
                },
                {
                    "setBasicFilter": {
                        "filter": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": row_count,
                                "startColumnIndex": 0,
                                "endColumnIndex": col_count,
                            }
                        }
                    }
                },
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": col_count,
                        }
                    }
                },
            ]
        },
    ).execute()

    print(f"Organized tab: {args.results_tab}")
    print(f"Original columns: {len(old_headers)} | Canonical columns: {len(CANON_HEADERS)}")
    print(f"Rows before: {len(old_rows)} | Rows after dedupe: {len(deduped)}")
    print(f"Archive snapshot appended to: {args.archive_tab}")
    print("Hooks are split into hook_1..hook_5 columns and searchable helper columns were added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
