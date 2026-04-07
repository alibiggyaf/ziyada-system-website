#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]

for env_path in (ROOT / ".env", PROJECT / ".env"):
    if not env_path.exists():
        continue
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() and key.strip() not in os.environ:
            os.environ[key.strip()] = value.strip().strip('"').strip("'")

base = (os.getenv("N8N_BASE_URL") or os.getenv("N8N_API_URL") or "").strip()
for marker in ("/api/", "/rest/"):
    if marker in base:
        base = base.split(marker, 1)[0]
base = base.rstrip("/")
api_key = os.getenv("N8N_API_KEY", "").strip().strip('"').strip("'")

if not base or not api_key:
    print("Missing n8n config", {"base": bool(base), "api_key": bool(api_key)})
    raise SystemExit(1)


def api_get(path: str) -> dict:
    req = urllib.request.Request(
        f"{base}{path}",
        headers={"X-N8N-API-KEY": api_key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


workflows = api_get("/api/v1/workflows")
items = workflows.get("data", workflows if isinstance(workflows, list) else [])
wf = next((x for x in items if x.get("name") == "Ali Content Writer"), None)
if not wf:
    print("workflow_not_found")
    raise SystemExit(1)

wf_id = str(wf.get("id"))
print("workflow", {"id": wf_id, "active": wf.get("active")})

wf_full = api_get(f"/api/v1/workflows/{urllib.parse.quote(wf_id)}")
node_names = {node.get("name") for node in wf_full.get("nodes", [])}
print("has_draft_route", {"Draft Email Gate": "Draft Email Gate" in node_names, "Build Organized Draft Email": "Build Organized Draft Email" in node_names})
for node in wf_full.get("nodes", []):
    if node.get("name") == "Webhook In":
        print("webhook_path", node.get("parameters", {}).get("path"))
        print("webhook_disabled", bool(node.get("disabled", False)))
        print("webhook_id", node.get("webhookId"))
    if node.get("name") == "Draft Email Gate":
        print("draft_gate", node.get("parameters", {}).get("conditions", {}))
    if node.get("name") == "Append Approved Row To Sheet":
        params = node.get("parameters", {})
        print("sheet_target", json.dumps({
            "documentId": params.get("documentId"),
            "sheetName": params.get("sheetName"),
        }, ensure_ascii=False))

executions = api_get(f"/api/v1/executions?workflowId={urllib.parse.quote(wf_id)}&limit=5")
exec_items = executions.get("data", executions if isinstance(executions, list) else [])
print("recent_executions", len(exec_items))
for ex in exec_items[:5]:
    ex_id = str(ex.get("id"))
    print("execution", {"id": ex_id, "status": ex.get("status")})
    detail = api_get(f"/api/v1/executions/{urllib.parse.quote(ex_id)}?includeData=true")
    run_data = detail.get("data", {}).get("resultData", {}).get("runData", {})
    print(
        "node_ran",
        {
            "Read Intake Rows": "Read Intake Rows" in run_data,
            "Append Request Registry Row": "Append Request Registry Row" in run_data,
            "Append Approved Row To Sheet": "Append Approved Row To Sheet" in run_data,
            "Append Draft Email Row To Sheet": "Append Draft Email Row To Sheet" in run_data,
            "Append Pending Row To Sheet": "Append Pending Row To Sheet" in run_data,
        },
    )
    for node_name, runs in run_data.items():
        if not runs:
            continue
        first = runs[0]
        if node_name == "Normalize Blog Metadata":
            try:
                sample = first.get("data", {}).get("main", [[{}]])[0][0].get("json", {})
                print("normalized_flags", {
                    "request_email_draft": sample.get("request_email_draft"),
                    "approval_status": sample.get("approval_status"),
                    "approval": sample.get("approval", {}),
                    "source": sample.get("source"),
                })
            except Exception:
                pass
        if "error" in first:
            print("node_error", node_name, json.dumps(first.get("error"), ensure_ascii=False))
