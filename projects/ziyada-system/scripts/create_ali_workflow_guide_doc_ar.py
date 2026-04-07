#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

FOLDER_ID = "1pW0UP5xqlvVNSIRFi8fJWxEX8aawFK_4"
DOC_TITLE = "الدليل التشغيلي الشامل - Ali Content Writer Engine 2026"
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
LATIN_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_+\-./:]*")


@dataclass
class LineSpec:
    text: str
    heading: str | None = None
    bullet: bool = False
    is_warning: bool = False
    is_portfolio_identity: bool = False
    is_rtl: bool = False


def has_arabic(text: str) -> bool:
    return bool(ARABIC_RE.search(text))


def normalize_bidi_text(text: str, is_rtl: bool) -> str:
    if not text:
        return text
    if not is_rtl:
        return text
    # Preserve Arabic flow when Latin terms appear inside RTL lines.
    return LATIN_TOKEN_RE.sub(lambda m: f"\u200e{m.group(0)}\u200e", text)


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


def get_creds() -> Credentials:
    token_path = PROJECT_DIR / "token_docs.json"
    if not token_path.exists():
        raise FileNotFoundError(f"Missing token_docs.json at {token_path}")

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("token_docs.json is invalid for Docs/Drive scopes")
    return creds


def ensure_single_doc_in_folder(drive, folder_id: str, title: str) -> str:
    q = (
        f"name = '{title}' and "
        f"'{folder_id}' in parents and "
        "mimeType = 'application/vnd.google-apps.document' and trashed = false"
    )
    result = drive.files().list(
        q=q,
        spaces="drive",
        fields="files(id,modifiedTime)",
        orderBy="modifiedTime desc",
        pageSize=200,
    ).execute()
    files = result.get("files", [])

    if not files:
        created = drive.files().create(
            body={
                "name": title,
                "mimeType": "application/vnd.google-apps.document",
                "parents": [folder_id],
            },
            fields="id",
        ).execute()
        return created["id"]

    keep_id = files[0]["id"]
    for file_obj in files[1:]:
        drive.files().delete(fileId=file_obj["id"]).execute()
    return keep_id


def clear_doc_content(docs, doc_id: str) -> None:
    doc = docs.documents().get(documentId=doc_id).execute()
    content = doc.get("body", {}).get("content", [])
    if not content:
        return
    end_index = content[-1].get("endIndex", 1)
    if end_index <= 1:
        return
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "deleteContentRange": {
                        "range": {"startIndex": 1, "endIndex": end_index - 1}
                    }
                }
            ]
        },
    ).execute()


def parse_markdown(md: str) -> list[LineSpec]:
    specs: list[LineSpec] = []

    for raw in md.splitlines():
        line = raw.rstrip()
        line_is_rtl = has_arabic(line)
        line = normalize_bidi_text(line, line_is_rtl)

        if line.startswith("### "):
            txt = line[4:]
            specs.append(LineSpec(text=txt, heading="HEADING_3", is_rtl=has_arabic(txt)))
            continue
        if line.startswith("## "):
            txt = line[3:]
            specs.append(LineSpec(text=txt, heading="HEADING_2", is_rtl=has_arabic(txt)))
            continue
        if line.startswith("# "):
            txt = line[2:]
            specs.append(LineSpec(text=txt, heading="HEADING_1", is_rtl=has_arabic(txt)))
            continue

        if line.startswith("- "):
            txt = line[2:]
            txt_is_rtl = has_arabic(txt)
            txt = normalize_bidi_text(txt, txt_is_rtl)
            specs.append(
                LineSpec(
                    text=txt,
                    bullet=True,
                    is_warning=("تنبيه" in txt or "مهم" in txt),
                    is_portfolio_identity=("هوية البورتفوليو" in txt),
                    is_rtl=txt_is_rtl,
                )
            )
            continue

        text_is_rtl = has_arabic(line)
        line = normalize_bidi_text(line, text_is_rtl)
        specs.append(
            LineSpec(
                text=line,
                is_warning=("تنبيه" in line or "مهم" in line),
                is_portfolio_identity=("هوية البورتفوليو" in line),
                is_rtl=text_is_rtl,
            )
        )

    return specs


def build_content_and_requests(specs: list[LineSpec], start_index: int = 1) -> tuple[str, list[dict]]:
    content = "\n".join(s.text for s in specs).rstrip() + "\n"

    requests: list[dict] = []
    idx = start_index
    bullet_ranges: list[tuple[int, int]] = []

    for s in specs:
        ln = len(s.text) + 1

        if s.heading:
            requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + ln},
                        "paragraphStyle": {"namedStyleType": s.heading},
                        "fields": "namedStyleType",
                    }
                }
            )

        if s.text.strip():
            requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + ln},
                        "paragraphStyle": {
                            "alignment": "END" if s.is_rtl else "START",
                            "direction": "RIGHT_TO_LEFT" if s.is_rtl else "LEFT_TO_RIGHT",
                        },
                        "fields": "alignment,direction",
                    }
                }
            )

        style_fields = ["foregroundColor"]
        style_payload: dict = {
            "foregroundColor": {
                "color": {"rgbColor": {"red": 0.06, "green": 0.09, "blue": 0.18}}
            }
        }

        if s.heading == "HEADING_1":
            style_payload.update(
                {
                    "bold": True,
                    "fontSize": {"magnitude": 24, "unit": "PT"},
                    "foregroundColor": {
                        "color": {"rgbColor": {"red": 0.23, "green": 0.51, "blue": 0.96}}
                    },
                }
            )
            style_fields.extend(["bold", "fontSize"])
        elif s.heading == "HEADING_2":
            style_payload.update(
                {
                    "bold": True,
                    "fontSize": {"magnitude": 16, "unit": "PT"},
                    "foregroundColor": {
                        "color": {"rgbColor": {"red": 0.23, "green": 0.51, "blue": 0.96}}
                    },
                }
            )
            style_fields.extend(["bold", "fontSize"])
        elif s.heading == "HEADING_3":
            style_payload.update(
                {
                    "bold": True,
                    "fontSize": {"magnitude": 13, "unit": "PT"},
                    "foregroundColor": {
                        "color": {"rgbColor": {"red": 0.55, "green": 0.36, "blue": 0.96}}
                    },
                }
            )
            style_fields.extend(["bold", "fontSize"])

        if s.is_warning and not s.heading:
            style_payload.update(
                {
                    "bold": True,
                    "foregroundColor": {
                        "color": {"rgbColor": {"red": 0.73, "green": 0.11, "blue": 0.11}}
                    },
                }
            )
            if "bold" not in style_fields:
                style_fields.append("bold")

        if s.is_portfolio_identity and not s.heading:
            style_payload.update(
                {
                    "bold": True,
                    "foregroundColor": {
                        "color": {"rgbColor": {"red": 0.55, "green": 0.36, "blue": 0.96}}
                    },
                }
            )
            if "bold" not in style_fields:
                style_fields.append("bold")

        if s.text.strip():
            requests.append(
                {
                    "updateTextStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + ln - 1},
                        "textStyle": style_payload,
                        "fields": ",".join(style_fields),
                    }
                }
            )

        if s.bullet and s.text.strip():
            bullet_ranges.append((idx, idx + ln))

        idx += ln

    for st, en in bullet_ranges:
        requests.append(
            {
                "createParagraphBullets": {
                    "range": {"startIndex": st, "endIndex": en},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                }
            }
        )

    return content, requests


def guide_markdown() -> str:
    workflow_url = os.getenv(
        "N8N_BLOG_WORKFLOW_PUBLIC_URL",
        "https://n8n.srv953562.hstgr.cloud/workflow/C8JWsE3KIoxr1KgO",
    )
    sheet_url = os.getenv(
        "ZIYADA_CONTENT_SHEET_URL",
        "https://docs.google.com/spreadsheets/d/1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s/edit",
    )
    doc_url = os.getenv(
        "ZIYADA_CONTENT_DOC_URL",
        "https://docs.google.com/document/d/1AP4rdSfnpc72CJsJVj7uXhNZLp5myPK5Q295ecYvh7U/edit",
    )
    slides_url = os.getenv(
        "ZIYADA_CONTENT_SLIDES_URL",
        "https://docs.google.com/presentation/d/1A9yC_kjVJXSx3OVcP31st4gdGgo2qiMQzH2Pgm9OmHs/edit",
    )

    return f"""
# الدليل التشغيلي الشامل
### Ali Content Writer Engine 2026

## هوية البورتفوليو
- يعتمد هذا الدليل على هوية بصرية واضحة: #0f172a و #3b82f6 و #8b5cf6 مع عرض احترافي بسيط.
- اللغة الأساسية عربية مع دعم إنجليزي مختصر داخل كل قسم.
### Portfolio Identity
- Visual identity follows #0f172a, #3b82f6, and #8b5cf6 in a clean professional layout.

## نبذة عن النظام
هذا النظام يجمع ويحلل بيانات السوق والمنافسين تلقائيا عبر منصة ابيفاي (Apify)، ثم ينتج محتوى اصيلا مخصصا لمنصات الشركة.
### System Overview
This system automatically analyzes market and competitor signals via Apify, then generates tailored content for company channels.

## أدوار ابيفاي في الوركفلو
- استخراج وتحليل محتوى مواقع الشركة والمنافسين (Website Content Crawler).
- تحليل ترندات السوشال والمحتوى الاكثر تفاعلا (Social Media Scraper).
- جمع مؤشرات السوق الداعمة لقرارات المحتوى (Market Intel Actor).
- اقتراح زوايا محتوى مبنية على اهتمامات الجمهور (Trending Topics Actor).
### Apify Actors
- Website Content Crawler
- Social Media Scraper
- Market Intel Actor
- Trending Topics Actor

## تقدير التكلفة لكل تشغيل
- الحد الادنى المتوقع: 3 ريال سعودي.
- الحد الاعلى المتوقع: 7 ريال سعودي.
- التكلفة تتغير حسب حجم السحب وعدد مهام ابيفاي (Apify) لكل تنفيذ.
### Cost per Run
- Estimated range: 3 to 7 SAR depending on run volume.

## خطوات التشغيل
1. ادخال نشاط العميل في الشيت او عبر تيليجرام.
2. التحقق من اكتمال الحقول الالزامية قبل التنفيذ.
3. تشغيل التحليل التلقائي للسوق والمنافسين عبر ابيفاي (Apify).
4. توليد المحتوى النهائي بناء على التحليل.
5. حفظ النتائج والروابط في جوجل شيتس (Google Sheets).
6. ارسال ملخص التنفيذ في تيليجرام.
### Runbook
- Intake -> Validation -> Market Analysis -> Content Generation -> Delivery.

## الروابط الرسمية
- Workflow URL: {workflow_url}
- Google Sheet: {sheet_url}
- Content Doc: {doc_url}
- Slides Deck: {slides_url}
- Telegram Bot: https://t.me/Aliabadi_Ai_Agent_bot

## ملاحظة مهمة
تنبيه: لا يتم نشر اي مخرج قبل مراجعة الاتساق مع هوية البورتفوليو وسياق نشاط العميل.
### Important Note
Always validate tone, brand consistency, and business context before publishing.
""".strip()


def main() -> int:
    load_env()
    creds = get_creds()

    drive = build("drive", "v3", credentials=creds)
    docs = build("docs", "v1", credentials=creds)

    doc_id = ensure_single_doc_in_folder(drive, FOLDER_ID, DOC_TITLE)
    clear_doc_content(docs, doc_id)

    specs = parse_markdown(guide_markdown())
    content, fmt_requests = build_content_and_requests(specs, start_index=1)

    docs.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {"insertText": {"location": {"index": 1}, "text": content}},
                *fmt_requests,
            ]
        },
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print("doc_id:", doc_id)
    print("doc_url:", url)
    print("folder_url:", f"https://drive.google.com/drive/folders/{FOLDER_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
