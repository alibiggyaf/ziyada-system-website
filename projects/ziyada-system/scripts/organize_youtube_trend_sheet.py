#!/usr/bin/env python3
"""Organize a YouTube trend spreadsheet with branded structure and a non-empty first tab."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


PROJECT_DIR = Path(__file__).resolve().parents[1]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TABS = [
    "Dashboard",
    "WeeklyChannelSnapshot",
    "WeeklyVideoSnapshot",
    "WeeklyInsightsSummary",
    "RunsAudit",
]

HEADERS: Dict[str, List[str]] = {
    "WeeklyChannelSnapshot": [
        "run_id",
        "week_start",
        "week_end",
        "timezone",
        "channel_id",
        "channel_title",
        "subscriber_count",
        "category_label",
        "relevance_score",
        "region_score",
        "final_channel_score",
        "run_cost_usd",
        "data_source",
    ],
    "WeeklyVideoSnapshot": [
        "run_id",
        "week_start",
        "week_end",
        "video_id",
        "video_url",
        "channel_id",
        "title",
        "published_at",
        "views",
        "likes",
        "comments",
        "duration",
        "language_hint",
        "trend_score",
        "region_bucket",
        "run_cost_usd",
        "data_source",
    ],
    "WeeklyInsightsSummary": [
        "run_id",
        "week_start",
        "week_end",
        "top_channel_count",
        "top_video_count",
        "key_findings_en",
        "key_findings_ar",
        "opportunities_en",
        "opportunities_ar",
        "run_cost_usd",
    ],
    "RunsAudit": [
        "run_id",
        "executed_at",
        "mode",
        "week_start",
        "week_end",
        "timezone",
        "api_quota_units_est",
        "apify_calls_used",
        "channels_selected",
        "videos_scored",
        "run_cost_usd",
        "status",
        "error_summary",
    ],
}


def _service(token_path: Path):
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
    if not creds.valid:
        raise RuntimeError("Token is invalid for Sheets scope")
    return build("sheets", "v4", credentials=creds)


def _sheet_id_map(meta: Dict) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        out[str(props.get("title", ""))] = int(props.get("sheetId", 0))
    return out


def _ensure_tabs(service, spreadsheet_id: str, tabs: List[str]) -> None:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing = {s["properties"]["title"] for s in meta.get("sheets", [])}
    requests = []
    for tab in tabs:
        if tab not in existing:
            requests.append({"addSheet": {"properties": {"title": tab}}})
    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
        ).execute()


def _ensure_headers(service, spreadsheet_id: str, tab: str, headers: List[str]) -> None:
    current = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{tab}!A1:ZZ1")
        .execute()
        .get("values", [])
    )
    if current and any(current[0]):
        return
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab}!A1",
        valueInputOption="RAW",
        body={"values": [headers]},
    ).execute()


def _style_tabs(service, spreadsheet_id: str) -> None:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    mapping = _sheet_id_map(meta)

    dark = {"red": 5 / 255, "green": 1 / 255, "blue": 10 / 255}
    violet = {"red": 112 / 255, "green": 0, "blue": 1}
    white = {"red": 1, "green": 1, "blue": 1}
    requests = []

    for tab, sid in mapping.items():
        requests.append(
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sid,
                        "tabColorStyle": {"rgbColor": violet},
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "tabColorStyle,gridProperties.frozenRowCount",
                }
            }
        )
        requests.append(
            {
                "repeatCell": {
                    "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": dark,
                            "horizontalAlignment": "CENTER",
                            "textFormat": {
                                "foregroundColor": white,
                                "bold": True,
                                "fontSize": 12,
                            },
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
                }
            }
        )
        requests.append(
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sid,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 24,
                    }
                }
            }
        )

    if requests:
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()


def _populate_dashboard(service, spreadsheet_id: str, tab_name: str) -> None:
    values = [
        ["Ali Fallatah | YouTube Trend Intelligence Dashboard"],
        ["Bilingual EN/AR market intelligence control center"],
        ["Run Workflow"],
        ["1) Use n8n workflow for niche trend discovery: https://n8n.srv953562.hstgr.cloud/workflow/62MN6oqxOs3levjh"],
        ["2) Run weekly report pipeline to push data into this sheet and Slides."],
        ["3) Review tabs: WeeklyChannelSnapshot, WeeklyVideoSnapshot, WeeklyInsightsSummary, RunsAudit"],
    ]
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()


def main() -> int:
    parser = argparse.ArgumentParser(description="Organize YouTube trend Google Sheet")
    parser.add_argument("--sheet-id", required=True)
    parser.add_argument("--token", default=str(PROJECT_DIR / "token_sheets.json"))
    args = parser.parse_args()

    service = _service(Path(args.token))

    _ensure_tabs(service, args.sheet_id, TABS)

    meta = service.spreadsheets().get(spreadsheetId=args.sheet_id).execute()
    first_tab = "Dashboard"
    sheets = meta.get("sheets", [])
    if sheets:
        first_tab = str(sheets[0].get("properties", {}).get("title", "Dashboard"))
    for tab, headers in HEADERS.items():
        _ensure_headers(service, args.sheet_id, tab, headers)

    _populate_dashboard(service, args.sheet_id, first_tab)
    _style_tabs(service, args.sheet_id)

    print(f"Organized sheet: {args.sheet_id}")
    print("Tabs ready: " + ", ".join(TABS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
