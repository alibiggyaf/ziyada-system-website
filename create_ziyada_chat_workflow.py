#!/usr/bin/env python3
"""
Create dedicated Ziyada Website Chat Assistant workflow on n8n.
Uses chatTrigger + AI Agent + OpenAI LLM + Memory.
Then prints the webhook URL to update .env.local.
"""
import json, urllib.request, urllib.error, sys

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

# Existing credentials
OPENAI_CRED_ID   = "naOv6TxHmS3zuuvm"
OPENAI_CRED_NAME = "OpenAi account"
GEMINI_CRED_ID   = "A87gfuB0ORA75x5R"
GEMINI_CRED_NAME = "Google Gemini(PaLM) Api account"

WEBHOOK_ID = "ziyada-web-chat-2026"

def n8n(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, {"raw": raw.decode("utf-8","ignore")[:800]}

SYSTEM_MESSAGE = """You are the AI Assistant for Ziyada System (زيادة سيستم), a premium digital marketing and business automation agency.

ABOUT ZIYADA SYSTEM:
- We help businesses grow through digital marketing, content creation, and intelligent automation
- Services: Digital Marketing, Content Creation, Business Automation, AI Workflows, SEO & GEO, Social Media Management
- Languages: Arabic (primary) and English
- Values: Partnership (الشراكة), Excellence, Innovation

INSTRUCTIONS:
- Always respond in the SAME LANGUAGE the user writes in (Arabic or English)
- Be professional, concise, and helpful
- For service inquiries: briefly describe the relevant service and suggest booking a consultation
- For consultations/pricing: direct users to book a free consultation at /BookMeeting
- Keep responses under 150 words unless the user asks for detail
- Never make up prices or guarantees
- If unsure, offer to connect them with the team

QUICK LINKS:
- Book consultation: /BookMeeting
- Services: /Services
- Contact: /contact"""

workflow = {
    "name": "Ziyada Website Chat Assistant",
    "settings": {
        "executionOrder": "v1"
    },
    "nodes": [
        {
            "id": "node-chat-trigger",
            "name": "Chat Message Received",
            "type": "@n8n/n8n-nodes-langchain.chatTrigger",
            "position": [240, 300],
            "typeVersion": 1.1,
            "webhookId": WEBHOOK_ID,
            "parameters": {
                "public": True,
                "mode": "webhook",
                "authentication": "none",
                "options": {
                    "responseMode": "lastNode"
                }
            }
        },
        {
            "id": "node-agent",
            "name": "Ziyada AI Agent",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "position": [500, 300],
            "typeVersion": 1.7,
            "parameters": {
                "text": "={{ $json.chatInput }}",
                "promptType": "define",
                "options": {
                    "systemMessage": SYSTEM_MESSAGE
                }
            }
        },
        {
            "id": "node-openai",
            "name": "OpenAI Chat Model",
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
            "position": [400, 500],
            "typeVersion": 1,
            "parameters": {
                "model": "gpt-4o-mini",
                "options": {
                    "temperature": 0.7,
                    "maxTokens": 300
                }
            },
            "credentials": {
                "openAiApi": {
                    "id": OPENAI_CRED_ID,
                    "name": OPENAI_CRED_NAME
                }
            }
        },
        {
            "id": "node-memory",
            "name": "Session Memory",
            "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
            "position": [620, 500],
            "typeVersion": 1.3,
            "parameters": {
                "sessionIdType": "fromInput",
                "sessionKey": "={{ $('Chat Message Received').item.json.sessionId || 'default' }}",
                "contextWindowLength": 10
            }
        }
    ],
    "connections": {
        "Chat Message Received": {
            "main": [
                [{"node": "Ziyada AI Agent", "type": "main", "index": 0}]
            ]
        },
        "OpenAI Chat Model": {
            "ai_languageModel": [
                [{"node": "Ziyada AI Agent", "type": "ai_languageModel", "index": 0}]
            ]
        },
        "Session Memory": {
            "ai_memory": [
                [{"node": "Ziyada AI Agent", "type": "ai_memory", "index": 0}]
            ]
        }
    }
}

print("Creating Ziyada Website Chat Assistant workflow...")
st, result = n8n("POST", "/workflows", workflow)
print(f"Status: {st}")

if st in (200, 201):
    wf_id = result.get("id")
    print(f"✓ Workflow created: ID={wf_id}, Name={result.get('name')}")
    print(f"  Active: {result.get('active')}")

    # The chatTrigger webhook URL
    webhook_url = f"{N8N_BASE}/webhook/{WEBHOOK_ID}/chat"
    vite_path = f"/n8n/webhook/{WEBHOOK_ID}/chat"

    print(f"\n✓ WEBHOOK URL: {webhook_url}")
    print(f"✓ VITE_CHATBOT_WEBHOOK (for .env.local): {vite_path}")

    # Activate it
    print("\nActivating workflow...")
    st2, act = n8n("PATCH", f"/workflows/{wf_id}", {"active": True})
    print(f"  Activate status: {st2}")

    # Test the webhook
    print(f"\nTesting webhook: POST {webhook_url}")
    try:
        payload = json.dumps({
            "action": "sendMessage",
            "chatInput": "Hello, what services does Ziyada System offer?",
            "sessionId": "test-setup-001"
        }).encode()
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            print(f"  ✓ Status: {r.status}")
            print(f"  ✓ Response: {body[:400]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        print(f"  ✗ HTTP {e.code}: {body[:400]}")
    except Exception as ex:
        print(f"  ✗ Error: {ex}")

    print(f"\n{'='*60}")
    print(f"UPDATE .env.local with:")
    print(f"  VITE_CHATBOT_WEBHOOK={vite_path}")
    print(f"  VITE_CHATBOT_ENABLED=true")
    print(f"{'='*60}")
else:
    print(f"✗ Failed: {json.dumps(result, indent=2)}")
    sys.exit(1)
