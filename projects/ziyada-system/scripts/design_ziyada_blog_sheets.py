#!/usr/bin/env python3
"""Design and organize Ziyada intake/result sheets with formatting and status controls."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]

DEFAULT_SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
DEFAULT_INTAKE_TAB = "Content Intake"
DEFAULT_RESULTS_TAB = "resault"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Ziyada palette (brand-aligned)
HEADER_BG = {"red": 8 / 255, "green": 10 / 255, "blue": 18 / 255}
HEADER_TEXT = {"red": 1.0, "green": 1.0, "blue": 1.0}
STATUS_HEADER_BG = {"red": 112 / 255, "green": 0 / 255, "blue": 1.0}
GRID_BG = {"red": 243 / 255, "green": 244 / 255, "blue": 246 / 255}


INTAKE_STATUS_RULES: Dict[str, List[str]] = {
    "trigger_status": ["start", "pause", "continue", "done"],
    "sent_status": ["pending", "done"],
    "workflow_status": ["pending", "in_progress", "completed", "failed"],
    "approval_status": ["approved", "pending", "draft_email", "rejected"],
}

RESULT_STATUS_RULES: Dict[str, List[str]] = {
    "trigger_status": ["start", "pause", "continue", "done"],
    "sent_status": ["pending", "done"],
    "workflow_status": ["pending", "in_progress", "completed", "failed", "waiting_approval"],
    "approval_status": ["approved", "pending", "draft_email", "rejected"],
}


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
    if col_index < 0:
        raise ValueError("Column index must be non-negative")
    n = col_index + 1
    letters: List[str] = []
    while n:
        n, rem = divmod(n - 1, 26)
        letters.append(chr(ord("A") + rem))
    return "".join(reversed(letters))


def load_credentials(token_path: Path) -> Credentials:
    if not token_path.exists():
        raise RuntimeError(
            "Missing token.json. Run enforce_intake_status_dropdowns.py with --interactive once first."
        )

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.valid:
        return creds

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    raise RuntimeError("token.json is invalid for Sheets scope. Re-auth is required.")


def get_sheet_meta(service, spreadsheet_id: str, tab_name: str) -> Tuple[int, int, int, Dict]:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        if props.get("title") == tab_name:
            grid = props.get("gridProperties", {})
            return (
                int(props["sheetId"]),
                int(grid.get("rowCount", 1000)),
                int(grid.get("columnCount", 26)),
                sheet,
            )
    raise RuntimeError(f"Tab '{tab_name}' not found.")


def get_headers(service, spreadsheet_id: str, tab_name: str, col_count: int) -> List[str]:
    end_col = col_index_to_a1(max(0, col_count - 1))
    rng = f"{tab_name}!A1:{end_col}1"
    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=rng).execute().get("values", [])
    if not values:
        return []
    return [str(v) for v in values[0]]


def status_conditional_rules(sheet_id: int, row_count: int, col_idx: int) -> List[Dict]:
    col_a1 = col_index_to_a1(col_idx)
    base_range = {
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "endRowIndex": row_count,
        "startColumnIndex": col_idx,
        "endColumnIndex": col_idx + 1,
    }
    return [
        {
            "addConditionalFormatRule": {
                "index": 0,
                "rule": {
                    "ranges": [base_range],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": f"=LOWER(${col_a1}2)=\"start\""}],
                        },
                        "format": {
                            "backgroundColor": {"red": 219 / 255, "green": 234 / 255, "blue": 254 / 255},
                            "textFormat": {"foregroundColor": {"red": 30 / 255, "green": 64 / 255, "blue": 175 / 255}, "bold": True},
                        },
                    },
                },
            }
        },
        {
            "addConditionalFormatRule": {
                "index": 1,
                "rule": {
                    "ranges": [base_range],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": f"=LOWER(${col_a1}2)=\"pending\""}],
                        },
                        "format": {
                            "backgroundColor": {"red": 254 / 255, "green": 249 / 255, "blue": 195 / 255},
                            "textFormat": {"foregroundColor": {"red": 146 / 255, "green": 64 / 255, "blue": 14 / 255}, "bold": True},
                        },
                    },
                },
            }
        },
        {
            "addConditionalFormatRule": {
                "index": 2,
                "rule": {
                    "ranges": [base_range],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": f"=LOWER(${col_a1}2)=\"continue\""}],
                        },
                        "format": {
                            "backgroundColor": {"red": 224 / 255, "green": 231 / 255, "blue": 255 / 255},
                            "textFormat": {"foregroundColor": {"red": 55 / 255, "green": 48 / 255, "blue": 163 / 255}, "bold": True},
                        },
                    },
                },
            }
        },
        {
            "addConditionalFormatRule": {
                "index": 3,
                "rule": {
                    "ranges": [base_range],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": f"=LOWER(${col_a1}2)=\"pause\""}],
                        },
                        "format": {
                            "backgroundColor": {"red": 254 / 255, "green": 243 / 255, "blue": 199 / 255},
                            "textFormat": {"foregroundColor": {"red": 146 / 255, "green": 64 / 255, "blue": 14 / 255}, "bold": True},
                        },
                    },
                },
            }
        },
        {
            "addConditionalFormatRule": {
                "index": 4,
                "rule": {
                    "ranges": [base_range],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": f"=OR(LOWER(${col_a1}2)=\"done\",LOWER(${col_a1}2)=\"finish\",LOWER(${col_a1}2)=\"completed\",LOWER(${col_a1}2)=\"approved\")"}],
                        },
                        "format": {
                            "backgroundColor": {"red": 220 / 255, "green": 252 / 255, "blue": 231 / 255},
                            "textFormat": {"foregroundColor": {"red": 22 / 255, "green": 101 / 255, "blue": 52 / 255}, "bold": True},
                        },
                    },
                },
            }
        },
    ]


def build_sheet_requests(
    sheet_id: int,
    row_count: int,
    col_count: int,
    headers: List[str],
    status_rules: Dict[str, List[str]],
) -> List[Dict]:
    active_cols = max(1, len(headers))
    header_map = {normalize_header(h): idx for idx, h in enumerate(headers) if h.strip()}

    requests: List[Dict] = []

    # Freeze header row and apply filter bar.
    requests.append(
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        }
    )
    requests.append(
        {
            "setBasicFilter": {
                "filter": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": row_count,
                        "startColumnIndex": 0,
                        "endColumnIndex": active_cols,
                    }
                }
            }
        }
    )

    # Header styling.
    requests.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": active_cols,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": HEADER_BG,
                        "horizontalAlignment": "CENTER",
                        "textFormat": {"foregroundColor": HEADER_TEXT, "bold": True, "fontSize": 13},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }
        }
    )

    requests.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": 0,
                    "endIndex": 1,
                },
                "properties": {"pixelSize": 42},
                "fields": "pixelSize",
            }
        }
    )

    # Subtle table background for body rows.
    requests.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": active_cols,
                },
                "cell": {"userEnteredFormat": {"backgroundColor": GRID_BG}},
                "fields": "userEnteredFormat.backgroundColor",
            }
        }
    )

    # Status columns: dropdown validation + highlighted headers + center aligned cells + conditional colors.
    for field, allowed in status_rules.items():
        idx = header_map.get(field)
        if idx is None:
            continue

        requests.append(
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": row_count,
                        "startColumnIndex": idx,
                        "endColumnIndex": idx + 1,
                    },
                    "rule": {
                        "condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in allowed]},
                        "strict": True,
                        "showCustomUi": True,
                        "inputMessage": "Select status from the dropdown.",
                    },
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
                        "startColumnIndex": idx,
                        "endColumnIndex": idx + 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": STATUS_HEADER_BG,
                            "horizontalAlignment": "CENTER",
                            "textFormat": {"foregroundColor": HEADER_TEXT, "bold": True, "fontSize": 12},
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
                }
            }
        )

        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": row_count,
                        "startColumnIndex": idx,
                        "endColumnIndex": idx + 1,
                    },
                    "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER", "textFormat": {"bold": True}}},
                    "fields": "userEnteredFormat(horizontalAlignment,textFormat.bold)",
                }
            }
        )

        requests.extend(status_conditional_rules(sheet_id, row_count, idx))

    trigger_idx = header_map.get("trigger_status")
    if trigger_idx is not None:
        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": trigger_idx,
                        "endColumnIndex": trigger_idx + 1,
                    },
                    "cell": {
                        "note": "Trigger control: set to 'start' to run now, 'pause' to stop queue, 'continue' to resume queue."
                    },
                    "fields": "note",
                }
            }
        )

    sent_idx = header_map.get("sent_status")
    if sent_idx is not None:
        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": sent_idx,
                        "endColumnIndex": sent_idx + 1,
                    },
                    "cell": {
                        "note": "Auto status: this becomes 'done' after workflow completes and draft is prepared/sent."
                    },
                    "fields": "note",
                }
            }
        )

    # Auto resize all active columns.
    requests.append(
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": max(1, min(active_cols, col_count)),
                }
            }
        }
    )

    return requests


def apply_sheet_design(service, spreadsheet_id: str, tab_name: str, status_rules: Dict[str, List[str]]) -> Tuple[List[str], int]:
    sheet_id, row_count, col_count, sheet_payload = get_sheet_meta(service, spreadsheet_id, tab_name)
    headers = get_headers(service, spreadsheet_id, tab_name, col_count)
    if not headers:
        raise RuntimeError(f"Header row is empty in '{tab_name}'.")

    existing_cf_count = len(sheet_payload.get("conditionalFormats", []))
    requests = build_sheet_requests(sheet_id, row_count, col_count, headers, status_rules)
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()

    return headers, existing_cf_count


def main() -> int:
    load_env_files()

    parser = argparse.ArgumentParser(description="Design intake/results tabs and enforce status controls.")
    parser.add_argument("--sheet-id", default=os.getenv("ZIYADA_BLOG_SHEET_ID", DEFAULT_SHEET_ID))
    parser.add_argument("--intake-tab", default=os.getenv("ZIYADA_BLOG_REQUEST_SHEET_TAB", DEFAULT_INTAKE_TAB))
    parser.add_argument("--results-tab", default=os.getenv("ZIYADA_BLOG_RESULTS_SHEET_TAB", DEFAULT_RESULTS_TAB))
    parser.add_argument("--token", default=str(PROJECT_DIR / "token.json"))
    args = parser.parse_args()

    creds = load_credentials(Path(args.token))
    service = build("sheets", "v4", credentials=creds)

    intake_headers, _ = apply_sheet_design(service, args.sheet_id, args.intake_tab, INTAKE_STATUS_RULES)
    results_headers, _ = apply_sheet_design(service, args.sheet_id, args.results_tab, RESULT_STATUS_RULES)

    print(f"Designed tab '{args.intake_tab}' with {len(intake_headers)} headers and mandatory status dropdowns.")
    print(f"Designed tab '{args.results_tab}' with {len(results_headers)} headers and mandatory status dropdowns.")
    print("Applied header colors, filter bars, frozen top row, auto-resize, and status conditional colors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
