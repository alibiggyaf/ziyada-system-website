#!/usr/bin/env python3
"""Configure Telegram bot webhook to trigger n8n workflow webhook."""

from __future__ import annotations

import json
import os
import pathlib
import urllib.parse
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


def call_telegram_api(token: str, method: str, params: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def main() -> int:
    load_env_files()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip().strip('"').strip("'")
    trigger_path = os.getenv("N8N_BLOG_TRIGGER_PATH", "ziyada-blog-ingest").strip().strip('"').strip("'")

    if not token:
        print("Missing TELEGRAM_BOT_TOKEN")
        return 1

    base_url = normalize_base_url()
    webhook_url = f"{base_url}/webhook/{trigger_path}"

    set_resp = call_telegram_api(token, "setWebhook", {"url": webhook_url})
    me_resp = call_telegram_api(token, "getMe")
    info_resp = call_telegram_api(token, "getWebhookInfo")

    print("setWebhook:", json.dumps(set_resp, ensure_ascii=False))
    print("getMe:", json.dumps(me_resp, ensure_ascii=False))
    print("getWebhookInfo:", json.dumps(info_resp, ensure_ascii=False))

    ok = bool(set_resp.get("ok")) and bool(info_resp.get("ok"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
