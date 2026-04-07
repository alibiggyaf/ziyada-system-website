from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
TAB = "Content Intake"
EXPECTED = [
    "request_id",
    "company_name",
    "industry",
    "target_audience",
    "company_link",
    "topic",
    "send_status",
    "approval_status",
    "writer_task",
]

creds = Credentials.from_authorized_user_file(
    "projects/ziyada-system/token.json",
    ["https://www.googleapis.com/auth/spreadsheets"],
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

svc = build("sheets", "v4", credentials=creds)
vals = svc.spreadsheets().values().get(
    spreadsheetId=SHEET_ID,
    range=f"{TAB}!A1:I500",
).execute().get("values", [])

if not vals:
    raise SystemExit("No intake values found")

rows = vals[1:]
out = [EXPECTED]

for row in rows:
    while len(row) < 9:
        row.append("")

    # Existing variants seen in sheet:
    # G: trigger_status, H: sent_status, I: approval_status
    trigger_status = str(row[6]).strip().lower()
    sent_status = str(row[7]).strip().lower()
    approval_status = str(row[8]).strip()

    send_status = trigger_status or sent_status or "pending"
    if send_status not in {"start", "continue", "pending", "done", "stop"}:
        send_status = "pending"

    new_row = [
        row[0],  # request_id
        row[1],  # company_name
        row[2],  # industry
        row[3],  # target_audience
        row[4],  # company_link
        row[5],  # topic
        send_status,
        approval_status or "pending",
        "",  # writer_task
    ]
    out.append(new_row)

svc.spreadsheets().values().clear(
    spreadsheetId=SHEET_ID,
    range=f"{TAB}!A:I",
).execute()

svc.spreadsheets().values().update(
    spreadsheetId=SHEET_ID,
    range=f"{TAB}!A1:I{len(out)}",
    valueInputOption="RAW",
    body={"values": out},
).execute()

print("INTAKE_SCHEMA_NORMALIZED", len(out)-1)
