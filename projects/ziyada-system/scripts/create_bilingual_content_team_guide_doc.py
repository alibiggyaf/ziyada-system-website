#!/usr/bin/env python3
"""Create a bilingual AR/EN Google Doc guide for the Ziyada content marketing team.

Outputs:
- Google Doc link
- Optional Gmail send to ziyadasystem@gmail.com if a valid gmail.send token exists
"""

from __future__ import annotations

import base64
import json
from email.mime.text import MIMEText
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PROJECT_DIR = Path(__file__).resolve().parents[1]
DOC_TOKEN = PROJECT_DIR / "token_docs.json"
GMAIL_TOKEN = PROJECT_DIR / "token_gmail_send.json"
FALLBACK_GMAIL_TOKEN = PROJECT_DIR / "token_gmail_readonly.json"

DOC_SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"

RECIPIENT = "ziyadasystem@gmail.com"
TITLE = "Ziyada System - Bilingual Content Marketing Team Guide (AR | EN)"


def _load_creds(path: Path, scopes: list[str]) -> Credentials:
    creds = Credentials.from_authorized_user_file(str(path), scopes)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError(f"Invalid token for scopes: {scopes} at {path}")
    return creds


def _guide_text() -> str:
    # Side-by-side bilingual table, Arabic right, English left, with all required details
    return """
Ziyada System - Bilingual Content Marketing Team Guide
دليل فريق التسويق بالمحتوى الثنائي اللغة - زيادة سيستم

آخر تحديث: 2026-04-01

| English (Left) | العربية (يمين) |
|----------------|-----------------|
| **What is this system?**<br>A bilingual content engine for Ziyada System. It researches Saudi competitors, discovers trends, generates content calendars, drafts blogs, and supports creative/video production with approval workflows. | **ما هو هذا النظام؟**<br>نظام متكامل لإنتاج المحتوى الثنائي اللغة لزيادة سيستم. يحلل المنافسين، يكتشف الترندات، ينشئ تقاويم المحتوى، يصيغ المدونات، ويدعم إنتاج التصاميم والفيديو مع إجراءات الموافقة. |
| **How does it work?**<br>- Brand Analyst: analyzes brand, competitors, market.<br>- Trend Scout: scans X, Instagram, TikTok, YouTube, LinkedIn.<br>- Script Writer: creates AR-first, EN-second content.<br>- Content Calendar: weekly/monthly, multi-post.<br>- Blog Studio: professional blogs, image guidance.<br>- Creative Producer: Canva (AR), Banana (images).<br>- Video Producer: publish-ready videos.<br>- Daily Reporter: sends HTML summaries by Gmail. | **كيف يعمل؟**<br>- محلل العلامة: تحليل الهوية والمنافسين والسوق.<br>- كشاف الترند: مسح X، إنستغرام، تيك توك، يوتيوب، لينكدإن.<br>- كاتب المحتوى: محتوى عربي أساسي وإنجليزي مكمل.<br>- تقويم المحتوى: تخطيط أسبوعي/شهري متعدد.<br>- استوديو المدونة: مدونات احترافية مع اقتراح الصور.<br>- منتج التصاميم: Canva للعربية، Banana للصور.<br>- منتج الفيديو: فيديوهات جاهزة للنشر.<br>- التقرير اليومي: إرسال ملخصات عبر Gmail. |
| **Where to add competitors?**<br>1. Dashboard: Add Competitor.<br>2. Google Sheet: Config > Competitor Seeds.<br>3. API: competitor import webhook. | **أين تضيف المنافسين؟**<br>١. لوحة التحكم: إضافة منافس.<br>٢. Google Sheet: تبويب Config ثم Competitor Seeds.<br>٣. API: ويبهوك رفع المنافسين. |
| **Platform priorities**<br>X > Instagram > TikTok > YouTube > LinkedIn | **أولوية المنصات**<br>X ثم إنستغرام ثم تيك توك ثم يوتيوب ثم لينكدإن |
| **Language mix**<br>70-80% Arabic, 20-30% English | **نسبة اللغات**<br>٧٠-٨٠٪ عربي، ٢٠-٣٠٪ إنجليزي |
| **Key links**<br>- Dashboard: http://localhost:5173/trend-intelligence<br>- n8n: https://n8n.srv953562.hstgr.cloud<br>- Brand Voice: projects/ziyada-system/docs/ZIYADA_VOICE_PROMPT_SYSTEM.txt<br>- Brand Guidelines: projects/ziyada-system/docs/ZIYADA_GUIDELINES.md<br>- Services Catalog: projects/ziyada-system/docs/SERVICES_CATALOG_AR_EN.md<br>- App Folder: projects/ziyada-system/app/ziyada-system-website/<br>- Blog Workflow: [Blog Intake Webhook](https://n8n.srv953562.hstgr.cloud/webhook/ziyada-blog-ingest) | **الروابط الأساسية**<br>- لوحة التحكم: http://localhost:5173/trend-intelligence<br>- n8n: https://n8n.srv953562.hstgr.cloud<br>- صوت العلامة: projects/ziyada-system/docs/ZIYADA_VOICE_PROMPT_SYSTEM.txt<br>- دليل العلامة: projects/ziyada-system/docs/ZIYADA_GUIDELINES.md<br>- كتالوج الخدمات: projects/ziyada-system/docs/SERVICES_CATALOG_AR_EN.md<br>- مجلد التطبيق: projects/ziyada-system/app/ziyada-system-website/<br>- سير عمل المدونة: [Webhook استقبال المدونة](https://n8n.srv953562.hstgr.cloud/webhook/ziyada-blog-ingest) |
| **Approve/apply actions**<br>- Approve Blog: creates publish package (Google Doc + HTML) for WordPress/Elementor.<br>- Apply Creative: sends brief to Canva workflow; Banana/Sora/Veo3 optional.<br>- Approve Video: review in outputs/ folder, then approve in dashboard.<br>- Video Storage: All videos are generated and stored in outputs/ (e.g., outputs/ziyada_sora_ad_16x9_v1.mp4).<br>- Creation Date: Each file is timestamped in its filename and in the dashboard log.<br>- Content Appearance: Content appears in the dashboard, Google Doc, and is distributed via Gmail and social media assets folders. | **إجراءات الموافقة والتطبيق**<br>- موافقة المدونة: إنشاء حزمة نشر (Google Doc + HTML) للنشر في WordPress/Elementor.<br>- تطبيق التصميم: إرسال البريف لمسار Canva، مع إمكانية Banana/Sora/Veo3.<br>- موافقة الفيديو: مراجعة الفيديو في مجلد outputs/ ثم الموافقة من لوحة التحكم.<br>- تخزين الفيديو: جميع الفيديوهات تُنتج وتُخزن في outputs/ (مثال: outputs/ziyada_sora_ad_16x9_v1.mp4).<br>- تاريخ الإنشاء: كل ملف يحمل تاريخ الإنشاء في اسمه وفي سجل لوحة التحكم.<br>- ظهور المحتوى: يظهر المحتوى في لوحة التحكم، Google Doc، ويتم توزيعه عبر Gmail ومجلدات الأصول الاجتماعية. |
| **Reporting**<br>Daily HTML summary sent by Gmail API as a normal email. | **التقارير**<br>ملخص يومي بصيغة HTML يُرسل عبر Gmail API كرسالة بريد إلكتروني. |
"""


def create_doc() -> tuple[str, str]:
    creds = _load_creds(DOC_TOKEN, DOC_SCOPES)
    docs = build("docs", "v1", credentials=creds)

    doc = docs.documents().create(body={"title": TITLE}).execute()
    doc_id = doc["documentId"]

    docs.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": _guide_text(),
                    }
                }
            ]
        },
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_id, url


def send_email_with_link(doc_url: str) -> str:
    token_path = GMAIL_TOKEN if GMAIL_TOKEN.exists() else FALLBACK_GMAIL_TOKEN
    if not token_path.exists():
        return "SKIPPED: no Gmail token file found"

    raw = json.loads(token_path.read_text(encoding="utf-8"))
    scopes = set(raw.get("scopes", []))
    if GMAIL_SEND_SCOPE not in scopes:
        return f"SKIPPED: token missing {GMAIL_SEND_SCOPE} scope"

    creds = _load_creds(token_path, [GMAIL_SEND_SCOPE])
    gmail = build("gmail", "v1", credentials=creds)

    subject = "Ziyada System - Bilingual Content Marketing Team Guide"
    body = f"""Hello,

Your bilingual AR/EN guide document is ready:
{doc_url}

This includes:
- What the system is
- How it works
- Competitor seed entry points
- Platform priorities
- Dashboard and workflow links

Regards,
Ziyada Automation
"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["to"] = RECIPIENT
    msg["subject"] = subject
    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    gmail.users().messages().send(userId="me", body={"raw": encoded}).execute()
    return "SENT"


def main() -> None:
    doc_id, doc_url = create_doc()
    email_status = send_email_with_link(doc_url)

    print("\n=== BILINGUAL GUIDE CREATED ===")
    print(f"DOC_ID: {doc_id}")
    print(f"DOC_URL: {doc_url}")
    print(f"EMAIL_STATUS: {email_status}")


if __name__ == "__main__":
    main()
