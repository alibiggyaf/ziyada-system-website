#!/usr/bin/env python3
"""Send Gmail draft for the weekly YouTube trend report."""

from __future__ import annotations

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def _gmail_service():
    token_path = PROJECT_DIR / "token.json"
    if not token_path.exists():
        raise RuntimeError("token.json missing in projects/ziyada-system")
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid:
        raise RuntimeError("token.json is invalid for Gmail scope")
    return build("gmail", "v1", credentials=creds)


def create_report_draft(recipient: str, subject: str, html_body: str, text_body: str) -> str:
    service = _gmail_service()
    message = MIMEMultipart("alternative")
    message["to"] = recipient
    message["subject"] = subject
    message.attach(MIMEText(text_body, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    draft = service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft.get("id", "")


def send_draft(draft_id: str) -> str:
    """Send an existing Gmail draft by its draft ID. Returns the sent message ID."""
    service = _gmail_service()
    result = service.users().drafts().send(userId="me", body={"id": draft_id}).execute()
    return result.get("id", "")
