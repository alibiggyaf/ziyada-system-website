#!/usr/bin/env python3
"""Send a sample payload to the Ziyada blog ingest webhook for end-to-end testing."""

from __future__ import annotations

import json
import os
import pathlib
import urllib.error
import urllib.request

ROOT_DIR = pathlib.Path(__file__).resolve().parents[3]
PROJECT_DIR = pathlib.Path(__file__).resolve().parents[1]


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
            if key and key not in os.environ:
                os.environ[key] = value


def normalize_base_url() -> str:
    base = os.getenv("N8N_BASE_URL", "").strip().strip('"').strip("'")
    api_url = os.getenv("N8N_API_URL", "").strip().strip('"').strip("'")
    candidate = base or api_url
    if not candidate:
        raise RuntimeError("Missing N8N_BASE_URL or N8N_API_URL")

    for marker in ("/api/", "/rest/"):
        if marker in candidate:
            candidate = candidate.split(marker, 1)[0]
            break
    return candidate.rstrip("/")


def get_payload(approval_status: str) -> dict:
    return {
        "request_id": "",
        "topic": "أتمتة متابعة العملاء في العيادات",
        "company_name": "عيادات نبض الحياة",
        "industry": "الرعاية الصحية",
        "target_audience": "أصحاب العيادات ومدراء التشغيل",
        "company_link": "https://example.com",
        "brand_context": "العلامة تركّز على سرعة الحجز وسلاسة تجربة المريض من أول رسالة حتى الزيارة.",
        "approval_status": approval_status,
        "hooks": [
            "عميلك يرسل ومحد يرد بسرعة؟",
            "تأخير المتابعة يضيّع مواعيد ومراجعين",
            "هنا يجي دور النظام حقنا في ترتيب الردود تلقائياً",
        ],
        "seo": {
            "seo_title": "أتمتة متابعة العملاء للعيادات في السعودية",
            "seo_description": "كيف تقلل ضياع العملاء وتسريع الردود باستخدام CRM والأتمتة.",
            "seo_keywords": "أتمتة, CRM, عيادات, متابعة العملاء",
            "target_keyword": "أتمتة متابعة العملاء",
        },
        "cta": "تواصل معنا على الواتساب ونرتب لك عرض بسيط للنظام",
        "audience": "أصحاب العيادات ومدراء التشغيل",
        "tags": ["عيادات", "crm", "automation"],
        "author": "Ziyada System",
    }


def post_json(url: str, payload: dict) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def main() -> int:
    load_env_files()
    base_url = normalize_base_url()
    trigger_path = os.getenv("N8N_BLOG_TRIGGER_PATH", "ziyada-blog-ingest").strip().strip('"').strip("'")
    approval_status = os.getenv("ZIYADA_TEST_APPROVAL_STATUS", "pending").strip().lower()

    webhook_url = f"{base_url}/webhook/{trigger_path}"
    webhook_test_url = f"{base_url}/webhook-test/{trigger_path}"
    payload = get_payload(approval_status)

    status, body = post_json(webhook_url, payload)
    print(f"Webhook URL: {webhook_url}")
    print(f"HTTP {status}")
    print(body)

    if status == 404:
        print("Production webhook not registered. Retrying test webhook URL...")
        status, body = post_json(webhook_test_url, payload)
        print(f"Webhook Test URL: {webhook_test_url}")
        print(f"HTTP {status}")
        print(body)

    return 0 if status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
