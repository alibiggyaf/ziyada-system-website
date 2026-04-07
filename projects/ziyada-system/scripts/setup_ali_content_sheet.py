#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def load_env() -> None:
    for env_path in (ROOT_DIR / ".env", PROJECT_DIR / ".env"):
        if not env_path.exists():
            continue
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


def get_service():
    token_path = PROJECT_DIR / "token.json"
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("token.json invalid for Sheets scope")
    return build("sheets", "v4", credentials=creds)


def ensure_tabs(service, spreadsheet_id: str, tabs: list[str]) -> None:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing = {s["properties"]["title"] for s in meta.get("sheets", [])}
    requests = []
    for t in tabs:
        if t not in existing:
            requests.append({"addSheet": {"properties": {"title": t}}})
    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
        ).execute()


def get_sheet_id(service, spreadsheet_id: str, tab: str) -> int:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        if props.get("title") == tab:
            return int(props.get("sheetId"))
    raise RuntimeError(f"Sheet tab not found: {tab}")


def put_headers(service, spreadsheet_id: str, tab: str, headers: list[str]) -> None:
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab}!A1",
        valueInputOption="RAW",
        body={"values": [headers]},
    ).execute()


def emphasize_trigger_column(service, spreadsheet_id: str, tab: str) -> None:
    sheet_id = get_sheet_id(service, spreadsheet_id, tab)
    # Column G (0-based index 6) is the mandatory trigger_status input column.
    col = 6
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": col,
                    "endColumnIndex": col + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 0.96, "blue": 0.7},
                        "textFormat": {"bold": True},
                    },
                    "note": "خانة تشغيل إلزامية: اكتب start أو continue فقط لتشغيل التريغر.",
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat.bold),note",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 2000,
                    "startColumnIndex": col,
                    "endColumnIndex": col + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 0.99, "blue": 0.86}
                    }
                },
                "fields": "userEnteredFormat.backgroundColor",
            }
        },
        {
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 2000,
                    "startColumnIndex": col,
                    "endColumnIndex": col + 1,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": "start"}, {"userEnteredValue": "continue"}],
                    },
                    "strict": True,
                    "showCustomUi": True,
                    "inputMessage": "اكتب start أو continue لتشغيل التريغر.",
                },
            }
        },
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests},
    ).execute()


def main() -> int:
    load_env()
    spreadsheet_id = os.getenv("ZIYADA_BLOG_SHEET_ID", "").strip()
    if not spreadsheet_id:
        raise RuntimeError("ZIYADA_BLOG_SHEET_ID missing")

    request_tab = os.getenv("ZIYADA_BLOG_REQUEST_SHEET_TAB", "Content Intake").strip() or "Content Intake"
    results_tab = os.getenv("ZIYADA_BLOG_RESULTS_SHEET_TAB", "resault").strip() or "resault"
    chat_state_tab = os.getenv("ZIYADA_CHAT_STATE_TAB", "Chat State").strip() or "Chat State"

    service = get_service()
    ensure_tabs(service, spreadsheet_id, [request_tab, results_tab, chat_state_tab])

    intake_headers = [
        "request_id",
        "company_name",
        "industry",
        "target_audience",
        "company_link",
        "topic",
        "trigger_status",
        "sent_status",
        "approval_status",
        "writer_task",
        "created_at",
    ]

    result_headers = [
        "request_id",
        "created_at",
        "company_name",
        "company_link",
        "topic",
        "workflow_status",
        "approval_status",
        "output",
        "workflow_name",
        "workflow_link",
        "sheet_link",
        "doc_link",
        "slides_link",
    ]

    chat_state_headers = [
        "created_at",
        "telegram_chat_id",
        "request_id",
        "requested_intent",
        "stage",
        "workflow_status",
        "approval_status",
        "user_message",
        "bot_message",
        "business_summary",
        "company_name",
        "industry",
        "target_audience",
        "company_link",
        "topic",
        "workflow_link",
        "sheet_link",
        "doc_link",
        "slides_link",
    ]

    put_headers(service, spreadsheet_id, request_tab, intake_headers)
    put_headers(service, spreadsheet_id, results_tab, result_headers)
    put_headers(service, spreadsheet_id, chat_state_tab, chat_state_headers)
    emphasize_trigger_column(service, spreadsheet_id, request_tab)

    print("Configured sheet:", spreadsheet_id)
    print("Request tab:", request_tab)
    print("Results tab:", results_tab)
    print("Chat state tab:", chat_state_tab)
    print("Mandatory trigger cell column emphasized:", f"{request_tab}!G2:G")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
