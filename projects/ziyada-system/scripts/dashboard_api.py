#!/usr/bin/env python3
"""Local-owned API server for the Ziyada website.

This server replaces the previous managed-backend dependency with:
- local JSON-backed storage for website content and submissions
- local function endpoints for contact, newsletter, booking, and admin reset
- optional SMTP delivery for notifications and reset emails
- the existing draft-send endpoint used by the intelligence dashboard

Port:
  5175 (Vite proxies /api -> this server)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
WEBSITE_DIR = PROJECT_DIR / "app" / "ziyada-system-website"
DATA_DIR = WEBSITE_DIR / "local-data"
OUTPUTS_DIR = PROJECT_DIR / "outputs" / "market_intel" / "youtube"

sys.path.insert(0, str(SCRIPT_DIR))

try:
    from send_youtube_trend_report import send_draft  # noqa: E402
except Exception:
    send_draft = None

load_dotenv(WEBSITE_DIR / ".env.local", override=False)
load_dotenv(WEBSITE_DIR / ".env.server.local", override=True)

ENTITY_FILES = {
    "Lead": DATA_DIR / "leads.json",
    "Booking": DATA_DIR / "bookings.json",
    "BlogPost": DATA_DIR / "blog-posts.json",
    "CaseStudy": DATA_DIR / "case-studies.json",
    "Subscriber": DATA_DIR / "subscribers.json",
}

RESET_TOKENS_FILE = DATA_DIR / "reset-tokens.json"
OUTBOX_FILE = DATA_DIR / "outbox.json"
DEFAULT_TIMES = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]

ADMIN_RECOVERY_EMAIL = os.environ.get("ADMIN_RECOVERY_EMAIL", "ali.biggy.af@gmail.com")
ADMIN_NOTIFICATION_EMAIL = os.environ.get("ADMIN_NOTIFICATION_EMAIL", ADMIN_RECOVERY_EMAIL)
RESET_SECRET = os.environ.get("ADMIN_RESET_SECRET", "change-this-secret")
RESET_TTL_MINUTES = int(os.environ.get("ADMIN_RESET_TTL_MINUTES", "15"))
MAX_VERIFY_ATTEMPTS = int(os.environ.get("ADMIN_RESET_MAX_VERIFY_ATTEMPTS", "5"))
MAIL_FROM = os.environ.get("MAIL_FROM", f"Ziyada Systems <{ADMIN_NOTIFICATION_EMAIL}>")
N8N_WEBHOOK_SECRET = os.environ.get("N8N_WEBHOOK_SECRET", "change-this-secret-too")


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path in [*ENTITY_FILES.values(), RESET_TOKENS_FILE, OUTBOX_FILE]:
        if not path.exists():
            path.write_text("[]\n", encoding="utf-8")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().isoformat()


def read_json(path: Path, default: Any) -> Any:
    ensure_storage()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    ensure_storage()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def b64url_decode(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def sign_value(value: str) -> str:
    digest = hmac.new(RESET_SECRET.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).digest()
    return b64url_encode(digest)


def secure_hash_code(code: str, nonce: str) -> str:
    return hashlib.sha256(f"{code}:{nonce}:{RESET_SECRET}".encode("utf-8")).hexdigest()


def create_reset_token(nonce: str, expires_at_ms: int) -> str:
    payload = {"nonce": nonce, "exp": expires_at_ms}
    payload_encoded = b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return f"{payload_encoded}.{sign_value(payload_encoded)}"


def parse_reset_token(token: str) -> dict[str, Any] | None:
    try:
        payload_encoded, signature = token.split(".", 1)
    except ValueError:
        return None

    if not hmac.compare_digest(sign_value(payload_encoded), signature):
        return None

    try:
        payload = json.loads(b64url_decode(payload_encoded).decode("utf-8"))
    except Exception:
        return None

    if payload.get("exp", 0) < int(now_utc().timestamp() * 1000):
        return None

    if not payload.get("nonce"):
        return None

    return payload


def slugify(value: str) -> str:
    simplified = re.sub(r"[^a-zA-Z0-9\s-]", "", value or "").strip().lower()
    return re.sub(r"[\s_-]+", "-", simplified).strip("-")


def parse_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def sort_records(records: list[dict[str, Any]], sort_key: str | None) -> list[dict[str, Any]]:
    if not sort_key:
        return records
    reverse = sort_key.startswith("-")
    field = sort_key[1:] if reverse else sort_key
    return sorted(records, key=lambda item: item.get(field) or "", reverse=reverse)


def apply_filter(records: list[dict[str, Any]], criteria: dict[str, Any]) -> list[dict[str, Any]]:
    if not criteria:
        return records

    def matches(item: dict[str, Any]) -> bool:
        for key, expected in criteria.items():
            if item.get(key) != expected:
                return False
        return True

    return [item for item in records if matches(item)]


def paginate(records: list[dict[str, Any]], limit: int | None, skip: int | None) -> list[dict[str, Any]]:
    start = max(skip or 0, 0)
    if limit is None:
        return records[start:]
    return records[start:start + max(limit, 0)]


def read_entity(entity_name: str) -> list[dict[str, Any]]:
    return read_json(ENTITY_FILES[entity_name], [])


def write_entity(entity_name: str, records: list[dict[str, Any]]) -> None:
    write_json(ENTITY_FILES[entity_name], records)


def append_outbox(message: dict[str, Any]) -> dict[str, Any]:
    outbox = read_json(OUTBOX_FILE, [])
    record = {"id": str(uuid4()), "created_date": iso_now(), **message}
    outbox.insert(0, record)
    write_json(OUTBOX_FILE, outbox)
    return record


def send_email(recipient: str, subject: str, body: str) -> dict[str, Any]:
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_secure = os.environ.get("SMTP_SECURE", "false").lower() == "true"
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")

    if not smtp_host:
        record = append_outbox({
            "to": recipient,
            "subject": subject,
            "body": body,
            "delivery": "outbox",
        })
        return {"ok": False, "delivery": "outbox", "record_id": record["id"]}

    message = EmailMessage()
    message["From"] = MAIL_FROM
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    try:
        if smtp_secure:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                if smtp_user:
                    server.login(smtp_user, smtp_pass)
                server.send_message(message)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                if os.environ.get("SMTP_STARTTLS", "true").lower() == "true":
                    server.starttls()
                    server.ehlo()
                if smtp_user:
                    server.login(smtp_user, smtp_pass)
                server.send_message(message)
        return {"ok": True, "delivery": "smtp"}
    except Exception as exc:
        record = append_outbox({
            "to": recipient,
            "subject": subject,
            "body": body,
            "delivery": "outbox",
            "smtp_error": str(exc),
        })
        return {"ok": False, "delivery": "outbox", "record_id": record["id"], "error": str(exc)}


def normalize_record(entity_name: str, record: dict[str, Any], existing: dict[str, Any] | None = None) -> dict[str, Any]:
    existing = existing or {}
    normalized = {**existing, **record}

    if entity_name == "Lead":
        normalized.setdefault("status", "new")
        source = normalized.get("source") or normalized.get("type") or "contact"
        normalized["source"] = source
        normalized["type"] = source
        normalized.setdefault("services", normalized.get("services_requested") or [])

    if entity_name == "Booking":
        normalized.setdefault("status", "pending")

    if entity_name == "Subscriber":
        normalized.setdefault("status", "active")
        normalized.setdefault("welcome_email_sent", False)

    if entity_name == "CaseStudy":
        normalized.setdefault("published", True)
        normalized.setdefault("order", 0)

    if entity_name == "BlogPost":
        if normalized.get("status") == "published":
            normalized["published"] = True
        elif normalized.get("status") == "draft":
            normalized["published"] = False
        if "published" in normalized:
            normalized["status"] = "published" if normalized.get("published") else "draft"
        normalized.setdefault("published", normalized.get("status") == "published")
        normalized.setdefault("status", "published" if normalized.get("published") else "draft")
        normalized.setdefault("tags", [])
        if not normalized.get("slug") and normalized.get("title_en"):
            normalized["slug"] = slugify(normalized.get("title_en", "")) or str(uuid4())[:8]
        if normalized.get("published") and not normalized.get("published_date"):
            normalized["published_date"] = now_utc().date().isoformat()

    return normalized


def create_entity_record(entity_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    records = read_entity(entity_name)
    record = normalize_record(entity_name, payload)
    record.setdefault("id", str(uuid4()))
    record.setdefault("created_date", iso_now())
    record["updated_date"] = iso_now()
    records.insert(0, record)
    write_entity(entity_name, records)
    return record


def update_entity_record(entity_name: str, record_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    records = read_entity(entity_name)
    for index, current in enumerate(records):
        if current.get("id") != record_id:
            continue
        updated = normalize_record(entity_name, payload, existing=current)
        updated["id"] = current.get("id")
        updated.setdefault("created_date", current.get("created_date", iso_now()))
        updated["updated_date"] = iso_now()
        records[index] = updated
        write_entity(entity_name, records)
        return updated
    return None


def delete_entity_record(entity_name: str, record_id: str) -> bool:
    records = read_entity(entity_name)
    filtered = [record for record in records if record.get("id") != record_id]
    if len(filtered) == len(records):
        return False
    write_entity(entity_name, filtered)
    return True


def read_reset_records() -> list[dict[str, Any]]:
    records = read_json(RESET_TOKENS_FILE, [])
    now_ms = int(now_utc().timestamp() * 1000)
    filtered = [record for record in records if record.get("expires_at", 0) >= now_ms or not record.get("used")]
    if len(filtered) != len(records):
        write_json(RESET_TOKENS_FILE, filtered)
    return filtered


def save_reset_record(record: dict[str, Any]) -> None:
    records = read_reset_records()
    next_records = [item for item in records if item.get("nonce") != record.get("nonce")]
    next_records.insert(0, record)
    write_json(RESET_TOKENS_FILE, next_records)


def get_reset_record(nonce: str) -> dict[str, Any] | None:
    for record in read_reset_records():
        if record.get("nonce") == nonce:
            return record
    return None


def latest_draft_id() -> str:
    runs = sorted(OUTPUTS_DIR.glob("*/run_summary.json"), key=os.path.getmtime, reverse=True)
    for summary_path in runs:
        try:
            data = json.loads(summary_path.read_text(encoding="utf-8"))
            draft_id = data.get("gmail_draft_id", "")
            if draft_id:
                return draft_id
        except Exception:
            continue
    return ""


def handle_send_draft(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    if send_draft is None:
        return 500, {"ok": False, "error": "Draft sending is not available in this environment."}

    draft_id = payload.get("draft_id") or latest_draft_id()
    if not draft_id:
        return 400, {"ok": False, "error": "No draft found. Run the pipeline first."}

    try:
        message_id = send_draft(draft_id)
        return 200, {"ok": True, "message_id": message_id}
    except Exception as exc:
        return 500, {"ok": False, "error": str(exc)}


def handle_submit_lead(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    lead = create_entity_record("Lead", {
        "name": payload.get("name", ""),
        "email": payload.get("email", ""),
        "phone": payload.get("phone", payload.get("lead_phone", "")),
        "company": payload.get("company", ""),
        "industry": payload.get("industry", ""),
        "company_size": payload.get("company_size", ""),
        "challenge": payload.get("challenge", ""),
        "source": payload.get("source", "contact"),
        "budget": payload.get("budget", ""),
        "timeline": payload.get("timeline", ""),
        "services": payload.get("services_requested", []),
        "language": payload.get("language", "ar"),
    })

    summary = [
        "New lead from the website.",
        "",
        f"Name: {lead.get('name')}",
        f"Email: {lead.get('email')}",
        f"Company: {lead.get('company')}",
        f"Source: {lead.get('source')}",
        f"Challenge: {lead.get('challenge')}",
    ]
    mail_result = send_email(ADMIN_NOTIFICATION_EMAIL, "Ziyada Website Lead", "\n".join(summary))
    return 200, {"success": True, "lead_id": lead["id"], "delivery": mail_result}


def handle_subscribe_email(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    email = (payload.get("email") or "").strip().lower()
    if not email:
        return 400, {"success": False, "error": "Email is required."}

    subscribers = read_entity("Subscriber")
    existing = next((item for item in subscribers if item.get("email", "").lower() == email), None)
    if existing:
        updated = update_entity_record("Subscriber", existing["id"], {
            "status": "active",
            "language": payload.get("language", existing.get("language", "ar")),
        })
        return 200, {"success": True, "subscriber_id": updated["id"], "existing": True}

    subscriber = create_entity_record("Subscriber", {
        "email": email,
        "name": payload.get("name", ""),
        "language": payload.get("language", "ar"),
        "status": "active",
        "welcome_email_sent": False,
    })

    mail_result = send_email(email, "Welcome to Ziyada Systems", "Thank you for subscribing to Ziyada Systems updates.")
    update_entity_record("Subscriber", subscriber["id"], {"welcome_email_sent": mail_result.get("ok", False)})
    return 200, {"success": True, "subscriber_id": subscriber["id"], "delivery": mail_result}


def handle_get_available_slots(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    date = payload.get("date", "")
    bookings = read_entity("Booking")
    booked = {
        booking.get("booking_time")
        for booking in bookings
        if booking.get("booking_date") == date and booking.get("status") in {"pending", "confirmed"}
    }
    available = [time for time in DEFAULT_TIMES if time not in booked]
    return 200, {"available_slots": available}


def handle_book_meeting(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    lead_email = (payload.get("lead_email") or "").strip().lower()
    leads = read_entity("Lead")
    existing = next((lead for lead in leads if lead.get("email", "").lower() == lead_email), None)
    if existing is None and lead_email:
        create_entity_record("Lead", {
            "name": payload.get("lead_name", ""),
            "email": lead_email,
            "phone": payload.get("lead_phone", ""),
            "company": payload.get("company", ""),
            "industry": payload.get("industry", ""),
            "company_size": payload.get("company_size", ""),
            "challenge": payload.get("challenge", ""),
            "source": "meeting",
            "language": payload.get("language", "ar"),
        })

    booking = create_entity_record("Booking", {
        **payload,
        "lead_email": lead_email,
        "status": payload.get("status", "pending"),
        "google_meet_link": payload.get("google_meet_link", ""),
    })

    summary = [
        "New booking request from the website.",
        "",
        f"Name: {booking.get('lead_name')}",
        f"Email: {booking.get('lead_email')}",
        f"Date: {booking.get('booking_date')}",
        f"Time: {booking.get('booking_time')}",
        f"Company: {booking.get('company')}",
    ]
    mail_result = send_email(ADMIN_NOTIFICATION_EMAIL, "Ziyada Meeting Request", "\n".join(summary))
    return 200, {"success": True, "booking": booking, "delivery": mail_result}


def handle_admin_credential_reset(payload: dict[str, Any], origin: str) -> tuple[int, dict[str, Any]]:
    action = payload.get("action")

    if action == "request":
        nonce = str(uuid4())
        expires_at = int((now_utc() + timedelta(minutes=RESET_TTL_MINUTES)).timestamp() * 1000)
        code = str(secrets.randbelow(900000) + 100000)
        token = create_reset_token(nonce, expires_at)
        save_reset_record({
            "nonce": nonce,
            "code_hash": secure_hash_code(code, nonce),
            "expires_at": expires_at,
            "attempts": 0,
            "used": False,
            "created_date": iso_now(),
        })

        reset_url = f"{origin}/AdminDashboard?resetToken={token}"
        message = "\n".join([
            "A credential reset was requested for your local Ziyada admin area.",
            "",
            f"Reset code: {code}",
            f"Reset link: {reset_url}",
            "",
            f"This code expires in {RESET_TTL_MINUTES} minutes and can only be used once.",
        ])
        mail_result = send_email(ADMIN_RECOVERY_EMAIL, "Ziyada Admin Credential Reset", message)
        return 200, {
            "ok": True,
            "token": token,
            "message": "If your local email delivery is configured, a reset email has been sent.",
            "delivery": mail_result,
        }

    if action == "verify":
        token = str(payload.get("token", ""))
        code = str(payload.get("code", "")).strip()
        token_payload = parse_reset_token(token)
        if not token_payload or not code:
            return 400, {"ok": False, "error": "invalid_or_expired_token"}

        record = get_reset_record(token_payload["nonce"])
        if not record or record.get("used"):
            return 400, {"ok": False, "error": "invalid_or_expired_token"}
        if record.get("expires_at", 0) < int(now_utc().timestamp() * 1000):
            return 400, {"ok": False, "error": "invalid_or_expired_token"}
        if int(record.get("attempts", 0)) >= MAX_VERIFY_ATTEMPTS:
            return 429, {"ok": False, "error": "too_many_attempts"}

        incoming_hash = secure_hash_code(code, token_payload["nonce"])
        if not hmac.compare_digest(incoming_hash, record.get("code_hash", "")):
            record["attempts"] = int(record.get("attempts", 0)) + 1
            save_reset_record(record)
            return 400, {"ok": False, "error": "invalid_code"}

        record["attempts"] = int(record.get("attempts", 0)) + 1
        record["used"] = True
        save_reset_record(record)
        return 200, {"ok": True, "message": "Code verified."}

    return 400, {"ok": False, "error": "unsupported_action"}


def handle_n8n_webhook(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    if payload.get("secret") != N8N_WEBHOOK_SECRET:
        return 401, {"ok": False, "error": "unauthorized"}

    post_payload = payload.get("post", {})
    post = create_entity_record("BlogPost", {
        "title_ar": post_payload.get("title_ar", ""),
        "title_en": post_payload.get("title_en", ""),
        "slug": post_payload.get("slug") or slugify(post_payload.get("title_en", "")) or str(uuid4())[:8],
        "excerpt_ar": post_payload.get("excerpt_ar", ""),
        "excerpt_en": post_payload.get("excerpt_en", ""),
        "content_ar": post_payload.get("content_ar", ""),
        "content_en": post_payload.get("content_en", ""),
        "cover_image": post_payload.get("cover_image", ""),
        "tags": post_payload.get("tags", []),
        "author": post_payload.get("author", "Ziyada Systems"),
        "status": post_payload.get("status", "published"),
        "published": post_payload.get("status", "published") == "published",
    })
    return 200, {"success": True, "post_id": post["id"], "slug": post["slug"]}


FUNCTION_HANDLERS = {
    "submitLead": handle_submit_lead,
    "subscribeEmail": handle_subscribe_email,
    "getAvailableSlots": handle_get_available_slots,
    "bookMeeting": handle_book_meeting,
    "n8nWebhook": handle_n8n_webhook,
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[ziyada-api] {fmt % args}")

    def cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def json_response(self, status: int, payload: dict[str, Any] | list[Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self.json_response(200, {"ok": True, "storage": str(DATA_DIR)})
            return
        if parsed.path.startswith("/api/entities/"):
            self.handle_entity_get(parsed.path, parse_qs(parsed.query))
            return
        self.json_response(404, {"ok": False, "error": "Not found."})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        payload = parse_json_body(self)
        if parsed.path == "/api/send-draft":
            status, body = handle_send_draft(payload)
            self.json_response(status, body)
            return
        if parsed.path.startswith("/api/entities/"):
            self.handle_entity_create(parsed.path, payload)
            return
        if parsed.path.startswith("/api/functions/"):
            self.handle_function(parsed.path, payload)
            return
        self.json_response(404, {"ok": False, "error": "Not found."})

    def do_PUT(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        payload = parse_json_body(self)
        if parsed.path.startswith("/api/entities/"):
            self.handle_entity_update(parsed.path, payload)
            return
        self.json_response(404, {"ok": False, "error": "Not found."})

    def do_DELETE(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/entities/"):
            self.handle_entity_delete(parsed.path)
            return
        self.json_response(404, {"ok": False, "error": "Not found."})

    def handle_entity_get(self, path: str, query: dict[str, list[str]]) -> None:
        parts = [part for part in path.split("/") if part]
        if len(parts) < 3:
            self.json_response(404, {"ok": False, "error": "Invalid entity path."})
            return
        entity_name = parts[2]
        if entity_name not in ENTITY_FILES:
            self.json_response(404, {"ok": False, "error": "Unknown entity."})
            return

        records = read_entity(entity_name)
        if len(parts) == 4 and parts[3] != "filter":
            record = next((item for item in records if item.get("id") == parts[3]), None)
            if record is None:
                self.json_response(404, {"ok": False, "error": "Record not found."})
                return
            self.json_response(200, record)
            return

        if len(parts) == 4 and parts[3] == "filter":
            criteria = {}
            if query.get("q"):
                criteria = json.loads(query["q"][0])
            records = apply_filter(records, criteria)

        sort = query.get("sort", [None])[0]
        limit = int(query["limit"][0]) if query.get("limit") else None
        skip = int(query["skip"][0]) if query.get("skip") else None
        self.json_response(200, paginate(sort_records(records, sort), limit, skip))

    def handle_entity_create(self, path: str, payload: dict[str, Any]) -> None:
        parts = [part for part in path.split("/") if part]
        if len(parts) != 3 or parts[2] not in ENTITY_FILES:
            self.json_response(404, {"ok": False, "error": "Unknown entity."})
            return
        created = create_entity_record(parts[2], payload)
        self.json_response(200, created)

    def handle_entity_update(self, path: str, payload: dict[str, Any]) -> None:
        parts = [part for part in path.split("/") if part]
        if len(parts) != 4 or parts[2] not in ENTITY_FILES:
            self.json_response(404, {"ok": False, "error": "Unknown entity."})
            return
        updated = update_entity_record(parts[2], parts[3], payload)
        if updated is None:
            self.json_response(404, {"ok": False, "error": "Record not found."})
            return
        self.json_response(200, updated)

    def handle_entity_delete(self, path: str) -> None:
        parts = [part for part in path.split("/") if part]
        if len(parts) != 4 or parts[2] not in ENTITY_FILES:
            self.json_response(404, {"ok": False, "error": "Unknown entity."})
            return
        deleted = delete_entity_record(parts[2], parts[3])
        if not deleted:
            self.json_response(404, {"ok": False, "error": "Record not found."})
            return
        self.json_response(200, {"success": True})

    def handle_function(self, path: str, payload: dict[str, Any]) -> None:
        parts = [part for part in path.split("/") if part]
        if len(parts) != 3:
            self.json_response(404, {"ok": False, "error": "Invalid function path."})
            return
        name = parts[2]
        if name == "adminCredentialReset":
            host = self.headers.get("Host", "127.0.0.1:5173")
            status, body = handle_admin_credential_reset(payload, f"http://{host}")
            self.json_response(status, body)
            return
        handler = FUNCTION_HANDLERS.get(name)
        if handler is None:
            self.json_response(404, {"ok": False, "error": "Unknown function."})
            return
        status, body = handler(payload)
        self.json_response(status, body)


if __name__ == "__main__":
    ensure_storage()
    port = int(os.environ.get("DASHBOARD_API_PORT", "5175"))
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"[ziyada-api] Listening on http://127.0.0.1:{port}")
    server.serve_forever()
