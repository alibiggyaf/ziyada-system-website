#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import argparse
import urllib.parse
import urllib.request

ROOT_DIR = pathlib.Path(__file__).resolve().parents[3]
PROJECT_DIR = pathlib.Path(__file__).resolve().parents[1]


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Debug n8n workflow executions")
    parser.add_argument("--workflow-id", default="", help="Override workflow id")
    args = parser.parse_args()

    load_env()
    base = os.getenv("N8N_BASE_URL", "").rstrip("/")
    key = os.getenv("N8N_API_KEY", "")
    workflow_id = args.workflow_id.strip() or os.getenv("N8N_BLOG_WORKFLOW_ID", "C8JWsE3KIoxr1KgO")

    print("workflow_id:", workflow_id)
    print("base:", base)

    wf_req = urllib.request.Request(
        f"{base}/api/v1/workflows/{urllib.parse.quote(workflow_id)}",
        headers={"X-N8N-API-KEY": key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(wf_req, timeout=30) as resp:
        wf = json.loads(resp.read().decode("utf-8", errors="replace"))
    print("workflow_name:", wf.get("name"))
    print("active:", wf.get("active"))

    exec_req = urllib.request.Request(
        f"{base}/api/v1/executions?limit=10&workflowId={urllib.parse.quote(workflow_id)}&includeData=true",
        headers={"X-N8N-API-KEY": key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(exec_req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))

    items = []
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            items = data["data"]
        elif isinstance(data.get("executions"), list):
            items = data["executions"]
    elif isinstance(data, list):
        items = data

    print("executions:", len(items))
    for it in items[:5]:
        print("---")
        print("id:", it.get("id"), "status:", it.get("status"), "finished:", it.get("finished"), "mode:", it.get("mode"))
        print("started:", it.get("startedAt"), "stopped:", it.get("stoppedAt"))
        err = it.get("error")
        if err:
            if isinstance(err, str):
                print("error:", err[:800])
            else:
                print("error:", json.dumps(err, ensure_ascii=False)[:800])

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    print("TELEGRAM_BOT_TOKEN set:", bool(token), "len:", len(token))
    print("OPENAI_API_KEY set:", bool(openai_key), "len:", len(openai_key))
    print("OPENAI_MODEL:", os.getenv("OPENAI_MODEL", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
