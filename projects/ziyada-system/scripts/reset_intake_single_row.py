#!/usr/bin/env python3
"""Reset Content Intake tab to a single fresh row.

This script keeps the header row, clears all existing intake data rows,
and appends one randomized sample company row for review.
"""

from __future__ import annotations

import argparse
import os
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
DEFAULT_SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
DEFAULT_TAB = "Content Intake"

SAMPLE_COMPANIES: List[Dict[str, str]] = [
    {
        "company_name": "Nabaa Fleet Analytics",
        "industry": "Logistics Analytics",
        "target_audience": "Operations directors at regional transport firms",
        "company_link": "https://nabaafleet.com",
        "topic": "How route-level AI insights reduce empty-mile costs in GCC logistics",
        "writer_task": "Write a bilingual authority post with practical KPI examples and one clear CTA.",
    },
    {
        "company_name": "Sahra MedOps Cloud",
        "industry": "Healthcare Operations Software",
        "target_audience": "Hospital COO teams and clinic administrators",
        "company_link": "https://sahramedops.io",
        "topic": "AI workflow automation for reducing outpatient waiting times",
        "writer_task": "Create an Arabic-first thought leadership draft with measurable outcomes and a concise executive summary.",
    },
    {
        "company_name": "Atlas Retail Signals",
        "industry": "Retail Intelligence",
        "target_audience": "Omnichannel retail growth managers",
        "company_link": "https://atlasretailsignals.ai",
        "topic": "Three automation plays for improving repeat purchase rate in Saudi ecommerce",
        "writer_task": "Draft a practical post with one framework, one example, and one conversion-focused CTA.",
    },
]


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


def get_service(token_path: Path):
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
    if not creds.valid:
        raise RuntimeError(f"{token_path} is invalid for Sheets scope")
    return build("sheets", "v4", credentials=creds)


def get_headers(service, spreadsheet_id: str, tab: str) -> List[str]:
    values = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{tab}!1:1")
        .execute()
        .get("values", [])
    )
    if not values or not values[0]:
        raise RuntimeError(f"No headers found in '{tab}' row 1")
    return [str(v).strip() for v in values[0]]


def reset_rows(service, spreadsheet_id: str, tab: str) -> None:
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"{tab}!A2:ZZ",
        body={},
    ).execute()


def build_row(headers: List[str], seed: Dict[str, str]) -> List[str]:
    request_id = f"REQ-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    created_at = datetime.now(timezone.utc).isoformat()

    defaults = {
        "request_id": request_id,
        "company_name": seed["company_name"],
        "industry": seed["industry"],
        "target_audience": seed["target_audience"],
        "company_link": seed["company_link"],
        "topic": seed["topic"],
        "trigger_status": "start",
        "sent_status": "pending",
        "approval_status": "approved",
        "writer_task": seed["writer_task"],
        "created_at": created_at,
        "workflow_status": "pending",
        "budget_mode": "balanced",
    }

    row: List[str] = []
    for header in headers:
        key = header.strip().lower().replace(" ", "_")
        row.append(str(defaults.get(key, "")))
    return row


def append_row(service, spreadsheet_id: str, tab: str, row: List[str]) -> None:
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab}!A2",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()


def main() -> int:
    load_env()

    parser = argparse.ArgumentParser(description="Reset intake tab and add one random row")
    parser.add_argument("--sheet-id", default=os.getenv("ZIYADA_BLOG_SHEET_ID", DEFAULT_SHEET_ID))
    parser.add_argument("--tab", default=os.getenv("ZIYADA_BLOG_REQUEST_SHEET_TAB", DEFAULT_TAB))
    parser.add_argument("--token", default=str(PROJECT_DIR / "token_sheets.json"))
    args = parser.parse_args()

    token_path = Path(args.token)
    service = get_service(token_path)

    headers = get_headers(service, args.sheet_id, args.tab)
    sample = random.choice(SAMPLE_COMPANIES)

    reset_rows(service, args.sheet_id, args.tab)
    append_row(service, args.sheet_id, args.tab, build_row(headers, sample))

    print(f"Reset intake tab '{args.tab}' and inserted one row for: {sample['company_name']}")
    print(f"Spreadsheet ID: {args.sheet_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
