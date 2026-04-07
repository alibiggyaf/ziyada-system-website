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
WF = "62MN6oqxOs3levjh"
SUB = "INHDUWqaC4WMae1R"
WEBHOOK = "ff9622a4-a6ec-4396-b9de-c95bd834c23c"
WORKFLOW_NAME = "Niche Signal Intelligence Workflow"
SUBWORKFLOW_NAME = "Niche Signal Search Tool"

H = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}


def main() -> None:
    wf = requests.get(f"{BASE}/api/v1/workflows/{WF}", headers=H, timeout=30).json()

    for n in wf.get("nodes", []):
        if n.get("name") == "youtube_search":
            n.setdefault("parameters", {})["workflowId"] = {
                "__rl": True,
                "mode": "list",
                "value": SUB,
                "cachedResultName": SUBWORKFLOW_NAME,
            }
        if n.get("name") == "chat_message_received":
            n["webhookId"] = WEBHOOK
            params = n.setdefault("parameters", {})
            params["public"] = True
            params["mode"] = "webhook"
            params["authentication"] = "none"
            options = params.setdefault("options", {})
            options["responseMode"] = "lastNode"

    put_body = {
        "name": WORKFLOW_NAME,
        "nodes": wf.get("nodes", []),
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings", {}),
    }

    r = requests.put(f"{BASE}/api/v1/workflows/{WF}", headers=H, json=put_body, timeout=30)
    print("PUT", r.status_code)
    if r.status_code >= 300:
        print(r.text[:800])
        raise SystemExit(1)

    a = requests.post(f"{BASE}/api/v1/workflows/{WF}/activate", headers=H, timeout=30)
    print("ACT", a.status_code)

    check = requests.get(f"{BASE}/api/v1/workflows/{WF}", headers=H, timeout=30).json()
    for n in check.get("nodes", []):
        if n.get("name") == "chat_message_received":
            print("chat webhookId", n.get("webhookId"))
        if n.get("name") == "youtube_search":
            ref = n.get("parameters", {}).get("workflowId", {})
            print("tool subworkflow", ref.get("value"))


if __name__ == "__main__":
    main()
