#!/usr/bin/env python3
from __future__ import annotations

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


def remove_key_param(node: dict) -> None:
    params = node.setdefault("parameters", {})
    q = params.setdefault("queryParameters", {}).setdefault("parameters", [])
    params["queryParameters"]["parameters"] = [p for p in q if p.get("name") != "key"]


def main() -> None:
    wf = requests.get(f"{BASE}/api/v1/workflows/{SUB}", headers=H, timeout=30).json()

    for n in wf.get("nodes", []):
        if n.get("name") == "search_youtube":
            n.setdefault("parameters", {})["url"] = "https://yt.lemnoslife.com/noKey/search"
            remove_key_param(n)
            print("patched search_youtube")
        if n.get("name") == "find_video_data1":
            n.setdefault("parameters", {})["url"] = "https://yt.lemnoslife.com/noKey/videos"
            remove_key_param(n)
            print("patched find_video_data1")

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
