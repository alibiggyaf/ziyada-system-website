#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJu"
    "OG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcy"
    "MDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
)
SUB = "INHDUWqaC4WMae1R"
H = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}


def load_env() -> None:
    root = Path(__file__).resolve().parents[3]
    project = Path(__file__).resolve().parents[1]
    for p in (root / ".env", project / ".env"):
        if not p.exists():
            continue
        for raw in p.read_text(encoding="utf-8").splitlines():
            s = raw.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k = k.strip()
            if k and k not in os.environ:
                os.environ[k] = v.strip().strip('"').strip("'")


def patch_key_param(node: dict, api_key: str) -> bool:
    params = node.get("parameters", {})
    qp = params.get("queryParameters", {})
    plist = qp.get("parameters", [])
    changed = False
    for p in plist:
        if p.get("name") == "key" and p.get("value") != api_key:
            p["value"] = api_key
            changed = True
    return changed


def main() -> None:
    load_env()
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing YOUTUBE_API_KEY/GOOGLE_API_KEY in env")

    wf = requests.get(f"{BASE}/api/v1/workflows/{SUB}", headers=H, timeout=30).json()
    changed = False
    for n in wf.get("nodes", []):
        if n.get("name") in {"search_youtube", "find_video_data1"}:
            if patch_key_param(n, api_key):
                print("patched", n.get("name"))
                changed = True

    if not changed:
        print("No changes needed")

    put_body = {
        "name": wf.get("name", ""),
        "nodes": wf.get("nodes", []),
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings", {}),
    }
    r = requests.put(f"{BASE}/api/v1/workflows/{SUB}", headers=H, json=put_body, timeout=30)
    print("PUT", r.status_code)
    if r.status_code >= 300:
        print(r.text[:800])
        raise SystemExit(1)

    a = requests.post(f"{BASE}/api/v1/workflows/{SUB}/activate", headers=H, timeout=30)
    print("ACT", a.status_code)


if __name__ == "__main__":
    main()
