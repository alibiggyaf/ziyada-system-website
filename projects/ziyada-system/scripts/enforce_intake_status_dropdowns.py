#!/usr/bin/env python3
"""Enforce status dropdown data validation in the Ziyada intake sheet."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]

DEFAULT_SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
DEFAULT_TAB = "Content Intake"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

STATUS_VALIDATIONS: Dict[str, List[str]] = {
    "trigger_status": ["start", "pending", "done"],
    "sent_status": ["pending", "done"],
    "workflow_status": ["pending", "done", "waiting_approval", "failed"],
    "budget_mode": ["lite", "balanced", "deep"],
}

MANDATORY_INPUT_COLUMNS: List[str] = [
    "company_name",
    "company_link",
    "industry",
    "target_audience",
    "topic",
    "trigger_status",
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
            # Last assignment wins to avoid duplicate-key drift in .env files.
            if key:
                os.environ[key] = value


def find_client_secret() -> Path:
    candidates = [
        PROJECT_DIR / "client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json",
        PROJECT_DIR / "credentials.json",
        PROJECT_DIR / "client_secret_724758724688-5qkibhju55ov0h27c6glmpl33mchlb0j.apps.googleusercontent.com.json",
    ]
    for path in candidates:
        if path.exists() and path.stat().st_size > 0:
            return path
    raise RuntimeError("No OAuth client secret file found in project root.")


def load_client_config(path: Path) -> Dict:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise RuntimeError(f"OAuth client secret file is empty: {path}")

    # Some credential exports in this workspace include trailing garbage after JSON.
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError(f"OAuth client secret JSON is malformed: {path}")

    data = json.loads(raw[start : end + 1])
    if "installed" in data and isinstance(data["installed"], dict):
        return {"installed": data["installed"]}
    if "web" in data and isinstance(data["web"], dict):
        return {"web": data["web"]}
    raise RuntimeError(f"OAuth client config missing 'installed' or 'web' section: {path}")


def get_client_config_for_interactive() -> Dict:
    """Prefer desktop installed OAuth config for localhost callback flows."""
    candidates = [
        PROJECT_DIR / "client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json",
        PROJECT_DIR / "credentials.json",
    ]
    for path in candidates:
        if not path.exists() or path.stat().st_size == 0:
            continue
        data = load_client_config(path)
        if "installed" in data and data["installed"].get("client_id"):
            return data
    # Fallback: any valid config from general lookup.
    return load_client_config(find_client_secret())


def pick_redirect_uri(redirect_uris: List[str]) -> str:
    preferred = ["http://localhost:8080/", "http://localhost:8080", "http://localhost/", "http://localhost"]
    for target in preferred:
        if target in redirect_uris:
            return target
    if redirect_uris:
        return redirect_uris[0]
    return "http://localhost:8080/"


def get_client_details() -> Tuple[str, str, str]:
    """Return (client_id, client_secret, redirect_uri) from env or credential files."""
    env_client_id = (os.getenv("GOOGLE_OAUTH_CLIENT_ID") or "").strip().strip('"').strip("'")
    env_client_secret = (os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") or "").strip().strip('"').strip("'")
    env_redirect = (os.getenv("GOOGLE_OAUTH_REDIRECT_URI") or "").strip().strip('"').strip("'")

    if env_client_id.endswith(".apps.googleusercontent.com") and env_client_secret:
        return env_client_id, env_client_secret, (env_redirect or "http://localhost:8080/")

    client_secret_file = find_client_secret()
    client_config = load_client_config(client_secret_file)
    block = client_config.get("installed") or client_config.get("web") or {}
    client_id = str(block.get("client_id") or "").strip()
    client_secret = str(block.get("client_secret") or "").strip()
    redirect_uris = block.get("redirect_uris") or []
    redirect_uri = pick_redirect_uri([str(x) for x in redirect_uris if str(x).strip()])

    if not client_id or not client_secret:
        raise RuntimeError("OAuth client ID/secret not found.")
    return client_id, client_secret, redirect_uri


def extract_auth_code(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    if text.startswith("http://") or text.startswith("https://"):
        parsed = urlparse(text)
        code_vals = parse_qs(parsed.query).get("code", [])
        if code_vals:
            return code_vals[0]
    return text


def build_auth_url(client_id: str, redirect_uri: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    return "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)


def exchange_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> Dict:
    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    data = urlencode(payload).encode("utf-8")
    with urlopen("https://oauth2.googleapis.com/token", data=data) as response:
        return json.loads(response.read().decode("utf-8"))


def load_credentials(token_path: Path, auth_code: Optional[str] = None, interactive: bool = False) -> Credentials:
    client_id, client_secret, redirect_uri = get_client_details()
    creds: Optional[Credentials] = None

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            creds = None

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token_path.write_text(creds.to_json(), encoding="utf-8")
            return creds
        except Exception:
            # Refresh can fail with invalid_scope if token was minted without spreadsheets scope.
            creds = None

    if interactive:
        client_config = get_client_config_for_interactive()
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(
            host="localhost",
            port=8080,
            open_browser=False,
            authorization_prompt_message="Open this URL in your browser:\n{url}\n",
        )
        token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    code = extract_auth_code(auth_code or "")
    if not code:
        auth_url = build_auth_url(client_id, redirect_uri)
        raise RuntimeError(
            "Sheets OAuth authorization is required.\n"
            f"Open this URL, approve access, then re-run with --auth-code:\n{auth_url}\n"
        )

    token = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
    if "access_token" not in token:
        raise RuntimeError(f"Failed to exchange OAuth code. Response: {token}")

    creds = Credentials(
        token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def normalize_header(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def col_index_to_a1(col_index: int) -> str:
    if col_index < 0:
        raise ValueError("col_index must be non-negative")
    value = col_index + 1
    letters: List[str] = []
    while value > 0:
        value, rem = divmod(value - 1, 26)
        letters.append(chr(ord("A") + rem))
    return "".join(reversed(letters))


def fetch_sheet_meta(service, spreadsheet_id: str, tab_name: str) -> Tuple[int, int, int]:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        if props.get("title") == tab_name:
            grid = props.get("gridProperties", {})
            return int(props["sheetId"]), int(grid.get("rowCount", 2000)), int(grid.get("columnCount", 26))
    raise RuntimeError(f"Tab '{tab_name}' not found in spreadsheet.")


def fetch_header_row(service, spreadsheet_id: str, tab_name: str, max_columns: int) -> List[str]:
    end_col = col_index_to_a1(max(0, max_columns - 1))
    rng = f"{tab_name}!A1:{end_col}1"
    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=rng).execute().get("values", [])
    if not values:
        return []
    return [str(v) for v in values[0]]


def ensure_required_headers(
    service,
    spreadsheet_id: str,
    tab_name: str,
    headers: List[str],
    required_headers: Iterable[str],
) -> List[str]:
    existing_norm = {normalize_header(h) for h in headers if str(h).strip()}
    missing = [h for h in required_headers if h not in existing_norm]
    if not missing:
        return headers

    start_idx = len(headers)
    start_col = col_index_to_a1(start_idx)
    end_col = col_index_to_a1(start_idx + len(missing) - 1)
    rng = f"{tab_name}!{start_col}1:{end_col}1"

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=rng,
        valueInputOption="RAW",
        body={"values": [missing]},
    ).execute()

    return headers + missing


def build_validation_request(sheet_id: int, column_index: int, row_count: int, allowed_values: Iterable[str]) -> Dict:
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,
                "endRowIndex": row_count,
                "startColumnIndex": column_index,
                "endColumnIndex": column_index + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in allowed_values],
                },
                "strict": True,
                "showCustomUi": True,
                "inputMessage": "Select a valid status from the dropdown.",
            },
        }
    }


def build_header_highlight_request(sheet_id: int, column_index: int) -> Dict:
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": column_index,
                "endColumnIndex": column_index + 1,
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.95, "green": 0.77, "blue": 0.77},
                    "textFormat": {"bold": True},
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat.bold)",
        }
    }


def build_blank_required_rule(sheet_id: int, column_index: int, row_count: int) -> Dict:
    col_letter = col_index_to_a1(column_index)
    return {
        "addConditionalFormatRule": {
            "index": 0,
            "rule": {
                "ranges": [
                    {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": row_count,
                        "startColumnIndex": column_index,
                        "endColumnIndex": column_index + 1,
                    }
                ],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": f"=LEN(TRIM(${col_letter}2))=0"}],
                    },
                    "format": {
                        "backgroundColor": {"red": 0.99, "green": 0.89, "blue": 0.89},
                    },
                },
            },
        }
    }


def build_start_status_rule(sheet_id: int, trigger_col_index: int, row_count: int) -> Dict:
    col_letter = col_index_to_a1(trigger_col_index)
    return {
        "addConditionalFormatRule": {
            "index": 0,
            "rule": {
                "ranges": [
                    {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": row_count,
                        "startColumnIndex": trigger_col_index,
                        "endColumnIndex": trigger_col_index + 1,
                    }
                ],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": f"=LOWER(TRIM(${col_letter}2))=\"start\""}],
                    },
                    "format": {
                        "backgroundColor": {"red": 0.90, "green": 0.55, "blue": 0.55},
                        "textFormat": {"bold": True},
                    },
                },
            },
        }
    }


def apply_manual_guidance_formatting(
    service,
    spreadsheet_id: str,
    tab_name: str,
    sheet_id: int,
    row_count: int,
    header_to_index: Dict[str, int],
) -> Tuple[int, int]:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing_rules = 0
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        if int(props.get("sheetId", -1)) == int(sheet_id):
            existing_rules = len(sheet.get("conditionalFormats", []))
            break

    requests: List[Dict] = []
    for idx in reversed(range(existing_rules)):
        requests.append({"deleteConditionalFormatRule": {"sheetId": sheet_id, "index": idx}})

    highlighted = 0
    for name in MANDATORY_INPUT_COLUMNS:
        col_index = header_to_index.get(name)
        if col_index is None:
            continue
        requests.append(build_header_highlight_request(sheet_id, col_index))
        requests.append(build_blank_required_rule(sheet_id, col_index, row_count))
        highlighted += 1

    trigger_col = header_to_index.get("trigger_status")
    if trigger_col is not None:
        requests.append(build_start_status_rule(sheet_id, trigger_col, row_count))

    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
        ).execute()

    return highlighted, existing_rules


def dedupe_intake_rows(
    service,
    spreadsheet_id: str,
    tab_name: str,
    header_to_index: Dict[str, int],
    row_count: int,
    column_count: int,
) -> int:
    end_col = col_index_to_a1(max(0, column_count - 1))
    source_range = f"{tab_name}!A2:{end_col}{row_count}"
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=source_range).execute().get("values", [])
    if not rows:
        return 0

    req_i = header_to_index.get("request_id")
    company_i = header_to_index.get("company_name")
    link_i = header_to_index.get("company_link")
    topic_i = header_to_index.get("topic")

    seen = set()
    kept_reversed: List[List[str]] = []
    removed = 0

    for row in reversed(rows):
        request_id = row[req_i].strip().lower() if req_i is not None and req_i < len(row) else ""
        company = row[company_i].strip().lower() if company_i is not None and company_i < len(row) else ""
        link = row[link_i].strip().lower() if link_i is not None and link_i < len(row) else ""
        topic = row[topic_i].strip().lower() if topic_i is not None and topic_i < len(row) else ""

        if request_id:
            key = ("request", request_id)
        elif company or link or topic:
            key = ("company_topic", company, link, topic)
        else:
            key = ("row", len(kept_reversed), "")

        if key in seen:
            removed += 1
            continue
        seen.add(key)
        kept_reversed.append(row)

    kept = list(reversed(kept_reversed))
    clear_range = f"{tab_name}!A2:{end_col}{row_count}"
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=clear_range,
        body={},
    ).execute()

    if kept:
        write_end_row = len(kept) + 1
        write_range = f"{tab_name}!A2:{end_col}{write_end_row}"
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=write_range,
            valueInputOption="RAW",
            body={"values": kept},
        ).execute()

    return removed


def fill_missing_status_values(service, spreadsheet_id: str, tab_name: str, header_to_index: Dict[str, int], row_count: int) -> int:
    trigger_col = header_to_index.get("trigger_status")
    if trigger_col is None:
        return 0

    col_letter = col_index_to_a1(trigger_col)
    rng = f"{tab_name}!{col_letter}2:{col_letter}{row_count}"
    existing = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=rng).execute().get("values", [])

    if not existing:
        return 0

    updates: List[List[str]] = []
    changed = 0
    for row in existing:
        current = row[0].strip().lower() if row else ""
        if not current:
            updates.append(["pending"])
            changed += 1
        else:
            updates.append([current])

    if changed == 0:
        return 0

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=rng,
        valueInputOption="RAW",
        body={"values": updates},
    ).execute()
    return changed


def fill_missing_budget_mode(service, spreadsheet_id: str, tab_name: str, header_to_index: Dict[str, int], row_count: int) -> int:
    budget_col = header_to_index.get("budget_mode")
    if budget_col is None:
        return 0

    col_letter = col_index_to_a1(budget_col)
    rng = f"{tab_name}!{col_letter}2:{col_letter}{row_count}"
    existing = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=rng).execute().get("values", [])

    if not existing:
        return 0

    updates: List[List[str]] = []
    changed = 0
    for row in existing:
        current = row[0].strip().lower() if row else ""
        if not current:
            updates.append(["balanced"])
            changed += 1
        elif current not in {"lite", "balanced", "deep"}:
            updates.append(["balanced"])
            changed += 1
        else:
            updates.append([current])

    if changed == 0:
        return 0

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=rng,
        valueInputOption="RAW",
        body={"values": updates},
    ).execute()
    return changed


def main() -> int:
    load_env_files()

    parser = argparse.ArgumentParser(description="Apply status dropdowns on intake tab.")
    parser.add_argument("--sheet-id", default=os.getenv("ZIYADA_BLOG_SHEET_ID", DEFAULT_SHEET_ID))
    parser.add_argument("--tab", default=os.getenv("ZIYADA_BLOG_REQUEST_SHEET_TAB", DEFAULT_TAB))
    parser.add_argument("--token", default=str(PROJECT_DIR / "token_sheets.json"))
    parser.add_argument("--auth-code", default="", help="OAuth code or full callback URL")
    parser.add_argument("--interactive", action="store_true", help="Run local OAuth callback flow")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-formatting", action="store_true", help="Skip red mandatory-cell guidance formatting")
    parser.add_argument("--skip-dedupe", action="store_true", help="Skip duplicate intake row cleanup")
    args = parser.parse_args()

    creds = load_credentials(Path(args.token), auth_code=args.auth_code, interactive=args.interactive)
    service = build("sheets", "v4", credentials=creds)

    sheet_id, row_count, column_count = fetch_sheet_meta(service, args.sheet_id, args.tab)
    headers = fetch_header_row(service, args.sheet_id, args.tab, column_count)
    if not headers:
        raise RuntimeError("Header row is empty. Cannot apply dropdowns.")

    headers = ensure_required_headers(
        service,
        args.sheet_id,
        args.tab,
        headers,
        STATUS_VALIDATIONS.keys(),
    )

    header_to_index = {normalize_header(h): idx for idx, h in enumerate(headers) if str(h).strip()}

    requests: List[Dict] = []
    applied_columns: List[str] = []
    for header, allowed in STATUS_VALIDATIONS.items():
        idx = header_to_index.get(header)
        if idx is None:
            continue
        requests.append(build_validation_request(sheet_id, idx, row_count, allowed))
        applied_columns.append(header)

    if not requests:
        print("No matching status columns found. Expected headers include:")
        print(json.dumps(list(STATUS_VALIDATIONS.keys()), ensure_ascii=True))
        return 1

    if args.dry_run:
        print("Dry run enabled. Validation requests prepared for columns:")
        print(json.dumps(applied_columns, ensure_ascii=True))
        return 0

    service.spreadsheets().batchUpdate(
        spreadsheetId=args.sheet_id,
        body={"requests": requests},
    ).execute()

    filled = fill_missing_status_values(service, args.sheet_id, args.tab, header_to_index, row_count)
    filled_budget = fill_missing_budget_mode(service, args.sheet_id, args.tab, header_to_index, row_count)
    highlighted_cols = 0
    cleared_rules = 0
    removed_duplicates = 0

    if not args.skip_formatting:
        highlighted_cols, cleared_rules = apply_manual_guidance_formatting(
            service,
            args.sheet_id,
            args.tab,
            sheet_id,
            row_count,
            header_to_index,
        )

    if not args.skip_dedupe:
        removed_duplicates = dedupe_intake_rows(
            service,
            args.sheet_id,
            args.tab,
            header_to_index,
            row_count,
            column_count,
        )

    print(f"Applied dropdown validation on tab '{args.tab}' for columns: {', '.join(applied_columns)}")
    print(f"Backfilled blank trigger_status cells with 'pending': {filled}")
    print(f"Backfilled/normalized budget_mode cells with 'balanced': {filled_budget}")
    print(f"Applied red manual-guidance formatting on mandatory columns: {highlighted_cols}")
    print(f"Replaced existing conditional rules on this tab: {cleared_rules}")
    print(f"Removed duplicate intake rows: {removed_duplicates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
