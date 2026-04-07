from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

sid = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
creds = Credentials.from_authorized_user_file(
    "projects/ziyada-system/token.json",
    ["https://www.googleapis.com/auth/spreadsheets"],
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

svc = build("sheets", "v4", credentials=creds)
meta = svc.spreadsheets().get(spreadsheetId=sid).execute()
tabs = [s["properties"]["title"] for s in meta.get("sheets", [])]

if "ContentResults" not in tabs:
    svc.spreadsheets().batchUpdate(
        spreadsheetId=sid,
        body={"requests": [{"addSheet": {"properties": {"title": "ContentResults"}}}]},
    ).execute()

header = (
    svc.spreadsheets()
    .values()
    .get(spreadsheetId=sid, range="resault!A1:Q1")
    .execute()
    .get("values", [[]])[0]
)
if not header:
    header = [
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
        "SUBJECT",
        "TITLE",
        "hook_1",
        "hook_2",
    ]

svc.spreadsheets().values().update(
    spreadsheetId=sid,
    range="ContentResults!A1:Q1",
    valueInputOption="RAW",
    body={"values": [header]},
).execute()

print("CONTENTRESULTS_READY")
