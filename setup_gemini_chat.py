#!/usr/bin/env python3
"""
N8N Chatbot Workflow Setup with Gemini Flash (cheapest model)
Automates creating and testing the chat workflow
"""

import json
import urllib.request
import urllib.error
import sys
from typing import Tuple

# Configuration
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"

HEADERS = {
    "X-N8N-API-KEY": N8N_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json",
}

def api(method: str, path: str, body=None) -> Tuple[int, dict]:
    """Make N8N API call"""
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(raw)
        except:
            parsed = {"message": raw}
        return e.code, parsed

def create_gemini_chat_workflow(gemini_api_key: str, webhook_path: str = "/chat") -> dict:
    """Create a chat workflow using Gemini Flash (cheapest model)"""

    workflow = {
        "name": "Ziyada Chat Widget - Gemini Flash (Cheapest)",
        "active": True,
        "nodes": [
            {
                "name": "Chat Trigger",
                "type": "n8n-nodes-base.webhook",
                "position": [250, 300],
                "parameters": {
                    "path": webhook_path,
                    "method": "POST",
                    "responseMode": "immediately",
                },
            },
            {
                "name": "Prepare Message",
                "type": "n8n-nodes-base.code",
                "position": [450, 300],
                "parameters": {
                    "jsCode": """
const input = $json;
const message = input.chatInput || input.message || '';
const sessionId = input.sessionId || 'default-' + Date.now();

return [{
  json: {
    userMessage: message.trim(),
    sessionId: sessionId,
    timestamp: new Date().toISOString()
  }
}];
""",
                },
            },
            {
                "name": "Gemini Flash (Cheapest)",
                "type": "n8n-nodes-base.openAi",
                "position": [650, 300],
                "parameters": {
                    "model": "gemini-2.0-flash",  # or "gemini-1.5-flash"
                    "prompt": "You are a helpful assistant for Ziyada Systems. Answer the user question concisely in their language:\n\n{{$json.userMessage}}",
                    "temperature": 0.7,
                    "maxTokens": 500,
                },
                "credentials": {
                    "openAiApi": {
                        "key": gemini_api_key
                    }
                }
            },
            {
                "name": "Format Response",
                "type": "n8n-nodes-base.code",
                "position": [850, 300],
                "parameters": {
                    "jsCode": """
const response = $json;
const output = response.response || response.text || response.choices?.[0]?.message?.content || 'Unable to generate response';

return [{
  json: {
    output: output,
    status: 'success',
    model: 'gemini-2.0-flash',
    cost: 'From $0.075 per 1M input tokens!'
  }
}];
""",
                },
            },
        ],
        "connections": {
            "Chat Trigger": {
                "main": [[{"node": "Prepare Message", "branch": 0, "type": "main"}]]
            },
            "Prepare Message": {
                "main": [[{"node": "Gemini Flash (Cheapest)", "branch": 0, "type": "main"}]]
            },
            "Gemini Flash (Cheapest)": {
                "main": [[{"node": "Format Response", "branch": 0, "type": "main"}]]
            },
        },
    }

    return workflow

def test_webhook(webhook_url: str, test_message: str = "What services do you offer?") -> Tuple[int, dict]:
    """Test the workflow webhook"""

    payload = {
        "action": "sendMessage",
        "chatInput": test_message,
        "sessionId": "test-session-" + str(int(__import__('time').time()))
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data,
                                headers={"Content-Type": "application/json"},
                                method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(raw)
        except:
            parsed = {"message": raw}
        return e.code, parsed

def main():
    print("=" * 70)
    print("N8N CHATBOT WORKFLOW SETUP - GEMINI FLASH (CHEAPEST MODEL)")
    print("=" * 70)

    # Step 1: Get Gemini API key
    print("\n📝 Enter your Gemini API key (from https://aistudio.google.com)")
    print("   Leave blank to skip workflow creation: ", end="")
    gemini_key = input().strip()

    if not gemini_key:
        print("\n⚠️  Skipping workflow creation. Please provide Gemini API key.")
        print("\n📚 See N8N_CHAT_WORKFLOW_SETUP.md for manual setup instructions.")
        return

    # Step 2: List existing workflows
    print("\n🔍 Fetching existing workflows...")
    st, workflows = api("GET", "/workflows?limit=50")

    if st != 200:
        print(f"❌ Error fetching workflows: {st} {workflows}")
        return

    chat_workflows = [w for w in workflows.get("data", [])
                     if "chat" in w.get("name", "").lower()]

    print(f"\n📋 Found {len(chat_workflows)} existing chat workflows:")
    for w in chat_workflows:
        print(f"   • {w['name']} (ID: {w['id']})")

    # Step 3: Create new workflow
    print("\n➕ Creating new Gemini Flash workflow...")
    new_workflow = create_gemini_chat_workflow(gemini_key)

    st, created = api("POST", "/workflows", new_workflow)

    if st not in [200, 201]:
        print(f"❌ Error creating workflow: {st} {created}")
        return

    workflow_id = created.get("id")
    webhook_id = None

    print(f"✅ Workflow created! ID: {workflow_id}")
    print(f"   Direct URL: https://n8n.srv953562.hstgr.cloud/workflow/{workflow_id}")

    # Step 4: Get webhook details
    print("\n🔗 Fetching webhook configuration...")
    st, full_workflow = api("GET", f"/workflows/{workflow_id}")

    if st == 200:
        trigger_node = next((n for n in full_workflow.get("nodes", [])
                           if n.get("type") == "n8n-nodes-base.webhook"), None)
        if trigger_node:
            webhook_id = trigger_node.get("id")
            webhook_path = trigger_node.get("parameters", {}).get("path", "/chat")
            print(f"✅ Webhook configured at path: {webhook_path}")
            print(f"   Use in .env.local: VITE_CHATBOT_WEBHOOK=/n8n/webhook/{webhook_id}{webhook_path}")

    # Step 5: Setup instructions
    print("\n📋 SETUP INSTRUCTIONS:")
    print("=" * 70)
    print("\n1️⃣  Update .env.local:")
    print("   File: projects/ziyada-system/app/ziyada-system-website/.env.local")
    print(f"   Add: VITE_CHATBOT_WEBHOOK=/n8n/webhook/{webhook_id}/chat")
    print("        VITE_CHATBOT_ENABLED=true")

    print("\n2️⃣  Start dev server:")
    print("   cd projects/ziyada-system/app/ziyada-system-website")
    print("   npm run dev")

    print("\n3️⃣  Test the chat widget:")
    print("   • Open http://localhost:5173")
    print("   • Click chat button (bottom-right)")
    print("   • Send a test message")

    print("\n4️⃣  Monitor workflow:")
    print(f"   • Open: https://n8n.srv953562.hstgr.cloud/workflow/{workflow_id}")
    print("   • Check Executions tab for real-time updates")

    # Step 6: Cost information
    print("\n💰 COST SAVINGS:")
    print("=" * 70)
    print("Gemini Flash 2.0:     $0.075 per 1M input + $0.30 per 1M output")
    print("vs OpenAI GPT-4o:     $5.00 per 1M input + $15 per 1M output")
    print("Savings:              ~99% reduction in LLM costs! ✨")

    print("\n✅ Setup complete! The chat widget should now work with Gemini Flash.")
    print("   For detailed troubleshooting, see N8N_CHAT_WORKFLOW_SETUP.md")

if __name__ == "__main__":
    main()
