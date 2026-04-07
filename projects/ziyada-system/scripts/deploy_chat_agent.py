#!/usr/bin/env python3
"""
Deploy Ziyada AI Chat Agent to N8N
-----------------------------------
This script:
1. Imports the lead capture sub-workflow
2. Imports the AI Agent chat workflow (with lead capture tool wired in)
3. Sets the OpenAI credential
4. Activates both workflows

Usage:
  python deploy_chat_agent.py

Requirements:
  pip install requests
"""

import os
import json
import sys
import requests

# ─── Config ─────────────────────────────────────────────────────────────────
N8N_BASE = os.getenv("N8N_BASE_URL", "https://n8n.srv953562.hstgr.cloud")
N8N_API_KEY = os.getenv("N8N_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOWS_DIR = os.path.join(SCRIPT_DIR, "..", "n8n for ziyada systen")

LEAD_CAPTURE_FILE = os.path.join(WORKFLOWS_DIR, "workflow_chat_lead_capture.json")
CHAT_AGENT_FILE   = os.path.join(WORKFLOWS_DIR, "workflow_ziyada_ai_chat_agent.json")

HEADERS = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Content-Type": "application/json",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def api(method, path, **kwargs):
    url = f"{N8N_BASE}/api/v1{path}"
    resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
    if resp.status_code not in (200, 201):
        print(f"  [ERROR] {method} {path} → {resp.status_code}: {resp.text[:300]}")
        return None
    return resp.json()

def import_workflow(filepath, workflow_dict=None):
    if workflow_dict is None:
        with open(filepath) as f:
            workflow_dict = json.load(f)
    # N8N API v1 only accepts these fields on POST /workflows
    allowed = {"name", "nodes", "connections", "settings"}
    payload = {k: v for k, v in workflow_dict.items() if k in allowed}
    result = api("POST", "/workflows", json=payload)
    if result:
        wf_id = result.get("id")
        name  = result.get("name")
        print(f"  ✓ Imported: {name} (id={wf_id})")
        return wf_id
    return None

def activate_workflow(wf_id):
    # N8N API uses PUT for workflow activation
    result = api("PUT", f"/workflows/{wf_id}/activate", json={})
    if result:
        print(f"  ✓ Activated workflow {wf_id}")
        return True
    # Try alternate endpoint
    result2 = api("POST", f"/workflows/{wf_id}/activate", json={})
    if result2:
        print(f"  ✓ Activated workflow {wf_id}")
        return True
    print(f"  ⚠ Could not auto-activate {wf_id} — activate manually in N8N UI")
    return False

def list_credentials():
    # N8N credentials list endpoint
    result = api("GET", "/credentials?includeData=false&limit=100")
    if result is None:
        return []
    # Handle both list and paginated response
    if isinstance(result, list):
        return result
    return result.get("data", [])

def find_credential(creds, name_or_type):
    for c in creds:
        if name_or_type.lower() in c.get("name","").lower() or name_or_type.lower() in c.get("type","").lower():
            return c
    return None

def patch_workflow_credential(wf_id, node_name, cred_type, cred_id, cred_name):
    """Patch a specific node's credential in an existing workflow."""
    wf = api("GET", f"/workflows/{wf_id}")
    if not wf:
        return False
    nodes = wf.get("nodes", [])
    patched = False
    for node in nodes:
        if node.get("name") == node_name:
            node.setdefault("credentials", {})[cred_type] = {
                "id": cred_id,
                "name": cred_name,
            }
            patched = True
            break
    if patched:
        result = api("PUT", f"/workflows/{wf_id}", json=wf)
        if result:
            print(f"  ✓ Patched credential on node '{node_name}'")
            return True
    return False

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n=== Ziyada AI Chat Agent Deployment ===\n")

    # 1. Check connectivity
    print("1. Checking N8N connection...")
    r = requests.get(f"{N8N_BASE}/healthz", timeout=10)
    if r.status_code != 200:
        print("  [ERROR] Cannot reach N8N. Check the URL and network.")
        sys.exit(1)
    print("  ✓ N8N is reachable")

    # 2. Print credential setup instructions
    print("\n2. Credentials checklist (N8N API doesn't expose credential list):")
    print("  Make sure these credentials exist in N8N UI before testing:")
    print()
    print("  [A] OpenAI API credential:")
    print("      N8N → Credentials → New → OpenAI API")
    print("      Name: openAiApi")
    print(f"      API Key: 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")
    print()
    print("  [B] Supabase Service Role credential:")
    print("      N8N → Credentials → New → HTTP Header Auth")
    print("      Name: supabaseServiceRole")
    print("      Header Name: apikey")
    print("      Header Value: <get from https://supabase.com/dashboard → Project Settings → API → service_role key>")
    print()
    print("  [C] HubSpot API credential (add later after getting HubSpot Private App key):")
    print("      N8N → Credentials → New → HTTP Header Auth")
    print("      Name: hubspotApi")
    print("      Header Name: Authorization")
    print("      Header Value: Bearer <your-hubspot-private-app-token>")
    print()

    # 3. Import lead capture sub-workflow
    print("\n3. Importing Chat Lead Capture sub-workflow...")
    lead_wf_id = import_workflow(LEAD_CAPTURE_FILE, workflow_dict=None)
    if not lead_wf_id:
        print("  [ERROR] Failed to import lead capture workflow")
        sys.exit(1)

    # 4. Patch the chat agent workflow with the lead capture workflow ID
    print("\n4. Updating AI Agent workflow with lead capture ID...")
    with open(CHAT_AGENT_FILE) as f:
        agent_workflow = json.load(f)

    for node in agent_workflow.get("nodes", []):
        if node.get("name") == "capture_lead":
            node["parameters"]["workflowId"]["value"] = lead_wf_id
            print(f"  ✓ Linked lead_capture tool → workflow {lead_wf_id}")
            break

    # 5. Import the AI Agent chat workflow (pass dict directly)
    print("\n5. Importing Ziyada AI Chat Agent workflow...")
    chat_wf_id = import_workflow(None, workflow_dict=agent_workflow)
    if not chat_wf_id:
        print("  [ERROR] Failed to import chat agent workflow")
        sys.exit(1)

    # 6. Activate both workflows
    print("\n6. Activating workflows...")
    activate_workflow(lead_wf_id)
    activate_workflow(chat_wf_id)

    # 7. Summary
    print("\n=== DEPLOYMENT COMPLETE ===\n")
    print(f"  Lead Capture Sub-Workflow ID : {lead_wf_id}")
    print(f"  AI Chat Agent Workflow ID    : {chat_wf_id}")
    print(f"  Chat Webhook URL             : {N8N_BASE}/webhook/3c9f6cb1-a3ce-4302-8260-6748f093520d/chat")
    print()
    print("  IMPORTANT — Manual steps still needed:")
    print("  1. Add OpenAI API credential in N8N UI (see above)")
    print("  2. Add Supabase Service Role credential in N8N UI (see above)")
    print("  3. Get HubSpot API key → update workflow_hubspot_sync and import it")
    print()
    print("  Test the chat agent:")
    print(f"  curl -X POST {N8N_BASE}/webhook/3c9f6cb1-a3ce-4302-8260-6748f093520d/chat \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"action":"sendMessage","chatInput":"السلام عليكم، وش خدماتكم؟","sessionId":"test-001"}\'')
    print()

if __name__ == "__main__":
    main()
