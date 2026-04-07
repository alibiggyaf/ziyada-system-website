#!/usr/bin/env python3
"""Activate an n8n workflow by ID using compatible API endpoints."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Tuple


ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]


def load_env_files() -> None:
    for env_path in (ROOT_DIR / ".env", PROJECT_DIR / ".env"):
        if not env_path.exists():
            continue
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


def normalize_base_url() -> str:
    base = (os.getenv("N8N_BASE_URL") or os.getenv("N8N_API_URL") or "").strip().strip('"').strip("'")
    for marker in ("/api/", "/rest/"):
        if marker in base:
            base = base.split(marker, 1)[0]
            break
    return base.rstrip("/")


def api_request(method: str, base_url: str, api_key: str, path: str, payload: Dict[str, Any] | None = None) -> Tuple[int, Any]:
    url = f"{base_url}{path}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url=url,
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-N8N-API-KEY": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw


def set_active(base_url: str, api_key: str, workflow_id: str) -> None:
    wf_id = urllib.parse.quote(str(workflow_id), safe="")
    candidates = [
        ("POST", f"/api/v1/workflows/{wf_id}/activate"),
        ("POST", f"/api/v1/workflows/{wf_id}/active"),
        ("PATCH", f"/api/v1/workflows/{wf_id}", {"active": True}),
    ]
    last_status = None
    last_data = None
    for item in candidates:
        if len(item) == 2:
            method, path = item
            payload = None
        else:
            method, path, payload = item
        status, data = api_request(method, base_url, api_key, path, payload)
        last_status, last_data = status, data
        if status in (200, 201, 204):
            return
        if status in (404, 405):
            continue
    raise RuntimeError(f"Unable to activate workflow. HTTP {last_status}: {last_data}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Activate n8n workflow")
    parser.add_argument("--workflow-id", required=True)
    args = parser.parse_args()

    load_env_files()
    base_url = normalize_base_url()
    api_key = (os.getenv("N8N_API_KEY") or "").strip()

    if not base_url or not api_key:
        raise RuntimeError("Missing N8N_BASE_URL/N8N_API_URL or N8N_API_KEY")

    set_active(base_url, api_key, args.workflow_id)
    status, wf = api_request("GET", base_url, api_key, f"/api/v1/workflows/{urllib.parse.quote(args.workflow_id, safe='')}")
    if status != 200:
        raise RuntimeError(f"Activation check failed. HTTP {status}: {wf}")

    print(f"Workflow: {wf.get('name')}")
    print(f"ID: {wf.get('id')}")
    print(f"Active: {wf.get('active')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
