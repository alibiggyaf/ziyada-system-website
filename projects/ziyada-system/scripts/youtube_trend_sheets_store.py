#!/usr/bin/env python3
"""Store weekly channel/video/insight snapshots in Google Sheets."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _sheet_service():
    token_path = PROJECT_DIR / "token.json"
    if not token_path.exists():
        raise RuntimeError("token.json missing in projects/ziyada-system")
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("token.json is invalid for Sheets scope")
    return build("sheets", "v4", credentials=creds)


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


def _append_rows(service, spreadsheet_id: str, tab: str, rows: List[List]) -> None:
    if not rows:
        return
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def _get_sheet_meta(service, spreadsheet_id: str) -> Dict:
    return service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()


def _sheet_id_map(meta: Dict) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        mapping[props.get("title", "")] = props.get("sheetId", 0)
    return mapping


def _header_exists(service, spreadsheet_id: str, tab: str) -> bool:
    values = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{tab}!A1:ZZ1")
        .execute()
        .get("values", [])
    )
    return bool(values and any(values[0]))


def _ensure_header(service, spreadsheet_id: str, tab: str, headers: List[str]) -> None:
    if _header_exists(service, spreadsheet_id, tab):
        return
    _append_rows(service, spreadsheet_id, tab, [headers])


def _style_tabs(service, spreadsheet_id: str, tabs: List[str]) -> None:
    meta = _get_sheet_meta(service, spreadsheet_id)
    mapping = _sheet_id_map(meta)
    requests = []

    # Ali brand colors: black + violet.
    violet = {"red": 112 / 255, "green": 0 / 255, "blue": 1.0}
    dark = {"red": 5 / 255, "green": 1 / 255, "blue": 10 / 255}
    white = {"red": 1, "green": 1, "blue": 1}

    for tab in tabs:
        sheet_id = mapping.get(tab)
        if sheet_id is None:
            continue

        requests.append(
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
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
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": dark,
                            "horizontalAlignment": "CENTER",
                            "textFormat": {
                                "foregroundColor": white,
                                "bold": True,
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
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 20,
                    }
                }
            }
        )

    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
        ).execute()


def _create_spreadsheet(service, title: str) -> str:
    created = service.spreadsheets().create(body={"properties": {"title": title}}).execute()
    return created["spreadsheetId"]


def store_weekly_snapshots(scored: Dict, insights: Dict, mode: str, run_cost_usd: float) -> str:
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()

    tab_channels = os.getenv("GOOGLE_SHEET_TAB_CHANNELS", "WeeklyChannelSnapshot")
    tab_videos = os.getenv("GOOGLE_SHEET_TAB_VIDEOS", "WeeklyVideoSnapshot")
    tab_insights = os.getenv("GOOGLE_SHEET_TAB_INSIGHTS", "WeeklyInsightsSummary")
    tab_runs = os.getenv("GOOGLE_SHEET_TAB_RUNS", "RunsAudit")

    service = _sheet_service()
    if not spreadsheet_id:
        new_title = f"YouTube Trend History {scored.get('run_id', '')}"
        spreadsheet_id = _create_spreadsheet(service, new_title)

    _ensure_tabs(service, spreadsheet_id, [tab_channels, tab_videos, tab_insights, tab_runs])

    _ensure_header(
        service,
        spreadsheet_id,
        tab_channels,
        [
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
    )

    _ensure_header(
        service,
        spreadsheet_id,
        tab_videos,
        [
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
    )

    _ensure_header(
        service,
        spreadsheet_id,
        tab_insights,
        [
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
    )

    _ensure_header(
        service,
        spreadsheet_id,
        tab_runs,
        [
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
    )

    channel_rows = []
    for row in scored.get("channels", []):
        channel_rows.append(
            [
                row.get("run_id", ""),
                row.get("week_start", ""),
                row.get("week_end", ""),
                scored.get("timezone", ""),
                row.get("channel_id", ""),
                row.get("channel_title", ""),
                row.get("subscriber_count", 0),
                row.get("category_label", ""),
                row.get("relevance_score", 0),
                row.get("region_score", 0),
                row.get("final_channel_score", 0),
                f"{run_cost_usd:.2f}",
                row.get("data_source", "youtube_api"),
            ]
        )

    video_rows = []
    for row in scored.get("videos", []):
        video_rows.append(
            [
                row.get("run_id", ""),
                row.get("week_start", ""),
                row.get("week_end", ""),
                row.get("video_id", ""),
                row.get("video_url", f"https://www.youtube.com/watch?v={row.get('video_id', '')}"),
                row.get("channel_id", ""),
                row.get("title", ""),
                row.get("published_at", ""),
                row.get("views", 0),
                row.get("likes", 0),
                row.get("comments", 0),
                row.get("duration", ""),
                row.get("language_hint", ""),
                row.get("trend_score", 0),
                "mixed",
                f"{run_cost_usd:.2f}",
                row.get("data_source", "youtube_api"),
            ]
        )

    insights_rows = [
        [
            insights.get("run_id", ""),
            insights.get("week_start", ""),
            insights.get("week_end", ""),
            len(scored.get("channels", [])),
            len(scored.get("videos", [])),
            insights.get("insights_en", ""),
            insights.get("insights_ar", ""),
            "AI automation-heavy strategy",
            "تركيز أعلى على أتمتة الذكاء الاصطناعي",
            f"{run_cost_usd:.2f}",
        ]
    ]

    run_rows = [
        [
            scored.get("run_id", ""),
            scored.get("week_end", ""),
            mode,
            scored.get("week_start", ""),
            scored.get("week_end", ""),
            scored.get("timezone", ""),
            "estimate",
            0,
            len(scored.get("channels", [])),
            len(scored.get("videos", [])),
            f"{run_cost_usd:.2f}",
            "success",
            "",
        ]
    ]

    _append_rows(service, spreadsheet_id, tab_channels, channel_rows)
    _append_rows(service, spreadsheet_id, tab_videos, video_rows)
    _append_rows(service, spreadsheet_id, tab_insights, insights_rows)
    _append_rows(service, spreadsheet_id, tab_runs, run_rows)
    _style_tabs(service, spreadsheet_id, [tab_channels, tab_videos, tab_insights, tab_runs])
    return spreadsheet_id
