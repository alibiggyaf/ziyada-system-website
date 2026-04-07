#!/usr/bin/env python3
"""Initialize Ziyada blog workflow and validate prompt wiring."""

from __future__ import annotations

import json
import pathlib
import sys

from deploy_n8n_blog_workflow import (
    PROJECT_DIR,
    build_workflow_payload,
    create_or_update_workflow,
    load_writer_system_prompt,
)


def build_test_payload() -> dict:
    """Create a local sample payload used to verify prompt insertion."""
    system_prompt = load_writer_system_prompt()
    return build_workflow_payload(
        name="Ali Content Writer",
        trigger_path="ziyada-blog-ingest",
        request_sheet_gid="2094549117",
        target_url="https://example.com/functions/n8nWebhook",
        secret="ziyada-n8n-2026",
        system_prompt=system_prompt,
        sheet_id="TEST_SHEET_ID",
        request_sheet_tab="ContentRequests",
        results_sheet_tab="ContentResults",
    )


def run_prompt_test() -> int:
    """Validate workflow contains content writer, approval, and sheet logging fields."""
    payload = build_test_payload()
    nodes = payload.get("nodes", [])

    code_nodes = [node for node in nodes if node.get("name") == "Prepare Content Writer Input"]
    if not code_nodes:
        print("[FAIL] Missing 'Prepare Content Writer Input' node")
        return 1

    js_code = code_nodes[0].get("parameters", {}).get("jsCode", "")
    required_markers = [
        "content_writer",
        "system_prompt",
        "user_prompt",
        "prompt_version",
        "request_id",
        "company_name",
    ]

    missing = [marker for marker in required_markers if marker not in js_code]
    if missing:
        print(f"[FAIL] Missing markers in content writer node: {', '.join(missing)}")
        return 1

    node_names = {node.get("name") for node in nodes}
    required_nodes = {
        "Normalize Blog Metadata",
        "Build Request Registry Row",
        "Append Request Registry Row",
        "Approval Gate",
        "Build Sheet Row (Approved)",
        "Build Sheet Row (Pending)",
        "Append Approved Row To Sheet",
        "Append Pending Row To Sheet",
    }
    missing_nodes = sorted(required_nodes - node_names)
    if missing_nodes:
        print(f"[FAIL] Missing workflow nodes: {', '.join(missing_nodes)}")
        return 1

    output_path = pathlib.Path(PROJECT_DIR) / "outputs" / "ziyada_blog_workflow_init_preview.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[PASS] Content writer, approval gate, and sheet logging wiring are valid.")
    print(f"[INFO] Preview workflow payload saved to: {output_path}")
    return 0


def main() -> int:
    test_status = run_prompt_test()
    if test_status != 0:
        return test_status

    deploy_status = create_or_update_workflow()
    if deploy_status != 0:
        print("[WARN] Prompt wiring test passed, but n8n deployment failed. Check N8N env vars.")
        return deploy_status

    print("[PASS] Ziyada blog workflow initialized and deployed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
