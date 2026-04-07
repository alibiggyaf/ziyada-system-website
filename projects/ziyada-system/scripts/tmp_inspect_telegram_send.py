#!/usr/bin/env python3
import json
import os
import pathlib
import urllib.request


def load_env() -> None:
    root = pathlib.Path(__file__).resolve().parents[3]
    project = pathlib.Path(__file__).resolve().parents[1]
    for env_path in (root / ".env", project / ".env"):
        if not env_path.exists():
            continue
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


def get_json(url: str, key: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"X-N8N-API-KEY": key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main() -> int:
    load_env()
    base = os.getenv("N8N_BASE_URL", "").strip().rstrip("/")
    if not base:
        base = os.getenv("N8N_API_URL", "").strip().split("/api/")[0].rstrip("/")
    key = os.getenv("N8N_API_KEY", "").strip()
    wf = os.getenv("N8N_BLOG_WORKFLOW_ID", "").strip() or "y7gXaTFEyIDOz7uS"

    execs = get_json(f"{base}/api/v1/executions?workflowId={wf}&limit=25", key).get("data", [])
    print("recent_execution_ids", [e.get("id") for e in execs])

    webhooks = [e for e in execs if e.get("mode") == "webhook"]
    triggers = [e for e in execs if e.get("mode") != "webhook"]
    ordered = webhooks[:6] + triggers[:2]
    for e in ordered:
        ex_id = e.get("id")
        ex = get_json(f"{base}/api/v1/executions/{ex_id}?includeData=true", key)
        rd = ((ex.get("data") or {}).get("resultData") or {}).get("runData") or {}
        print("\nexecution", ex_id, "status", ex.get("status"), "mode", ex.get("mode"))
        print("  nodes", list(rd.keys()))

        def first_json(entry: dict) -> dict:
            main = ((entry.get("data") or {}).get("main") or [])
            if not main or not main[0]:
                return {}
            first = main[0][0] if len(main[0]) > 0 else {}
            return (first or {}).get("json", {}) if isinstance(first, dict) else {}

        prep = (rd.get("Prepare Content Writer Input") or [])
        if prep:
            out = first_json(prep[-1])
            print("  prepare.source", out.get("source"), "chat_id", out.get("telegram_chat_id"), "text", out.get("telegram_text"))
            interview = out.get("interview_state") or {}
            print(
                "  prepare.ready",
                out.get("is_generation_ready"),
                "missing",
                interview.get("missing_fields"),
                "next",
                interview.get("next_question"),
            )

        build = (rd.get("Build Telegram Run Summary") or [])
        if build:
            entry = build[-1]
            if entry.get("error"):
                print("  build.error", entry.get("error"))
            out = first_json(entry)
            payload = out.get("telegram_send_payload") or {}
            print("  build.payload.chat_id", payload.get("chat_id"), "text_len", len(str(payload.get("text", ""))))
            print("  build.payload.text_preview", str(payload.get("text", ""))[:220].replace("\n", " | "))
        else:
            print("  build: no data")

        send = (rd.get("Send Telegram Run Summary") or [])
        if send:
            entry = send[-1]
            if entry.get("error"):
                print("  send.error", entry.get("error"))
            out = first_json(entry)
            print("  send.response.ok", out.get("ok"), "keys", list(out.keys())[:8])
        else:
            print("  send: no data")

        parsed_agent = (rd.get("Parse Telegram Agent Reply") or [])
        if parsed_agent:
            out = first_json(parsed_agent[-1])
            intake = out.get("intake") or {}
            print(
                "  ai.intent",
                out.get("ai_requested_intent"),
                "ai.trigger",
                out.get("ai_should_trigger_generation"),
                "ai.reply",
                str(out.get("ai_reply_text", ""))[:120],
            )
            print(
                "  ai.intake",
                {
                    "company_name": intake.get("company_name", ""),
                    "industry": intake.get("industry", ""),
                    "target_audience": intake.get("target_audience", ""),
                    "company_link": intake.get("company_link", ""),
                },
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
