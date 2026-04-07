#!/usr/bin/env python3
"""
Switch Gemini quota-exceeded workflow to use OpenAI gpt-4o-mini.
OpenAI credentials (naOv6TxHmS3zuuvm) are confirmed working.
"""
import json, urllib.request, urllib.error, time

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

WF_ID = "eO6LzcPrnPT3JlpA"
WEBHOOK_ID = "3c9f6cb1-a3ce-4302-8260-6748f093520d"

OPENAI_CRED_ID   = "naOv6TxHmS3zuuvm"
OPENAI_CRED_NAME = "OpenAi account"

SYSTEM_MESSAGE = """You are the AI Assistant for Ziyada System (زيادة سيستم), a premium digital marketing and AI automation agency based in Saudi Arabia.

ABOUT ZIYADA SYSTEM:
- Premium digital marketing, content creation, and business automation services
- Services: Digital Marketing, AI Content Creation, Business Automation, YouTube Niche Intelligence, SEO & GEO, Social Media Management
- Languages: Arabic (primary) and English
- Values: Partnership (الشراكة), Excellence, Innovation

RULES:
- Respond in the SAME LANGUAGE the user writes in (Arabic → Arabic, English → English)
- Be professional, friendly, and concise (under 120 words unless more detail is asked)
- For service questions: briefly explain and suggest booking a consultation
- For consultation/pricing: direct to /BookMeeting for a free 30-min session
- Never fabricate prices or guarantees
- If asked about contact: email or /BookMeeting page

SERVICES:
- Niche Signal Intelligence: AI-powered YouTube niche research
- Content Creation: AI-assisted blogs, social media, video scripts
- Digital Marketing: Google Ads, Meta Ads, Snapchat
- Business Automation: n8n workflows, AI agents
- SEO/GEO: Search + AI engine optimization"""

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
            return e.code, {"raw": raw.decode("utf-8","ignore")[:1000]}

new_workflow = {
    "name": "🚀 Ziyada Chat Widget - Gemini Flash (Cheapest)",
    "settings": {"executionOrder": "v1"},
    "staticData": None,
    "nodes": [
        {
            "id": "chat-trigger-node",
            "name": "Chat Message Received",
            "type": "@n8n/n8n-nodes-langchain.chatTrigger",
            "position": [240, 300],
            "typeVersion": 1.1,
            "webhookId": WEBHOOK_ID,
            "parameters": {
                "public": True,
                "mode": "webhook",
                "authentication": "none",
                "options": {"responseMode": "lastNode"}
            }
        },
        {
            "id": "ai-agent-node",
            "name": "Ziyada AI Agent",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "position": [520, 300],
            "typeVersion": 1.7,
            "parameters": {
                "text": "={{ $json.chatInput }}",
                "promptType": "define",
                "options": {"systemMessage": SYSTEM_MESSAGE}
            }
        },
        {
            "id": "openai-llm-node",
            "name": "OpenAI Chat Model",
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
            "position": [400, 520],
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
            "id": "memory-node",
            "name": "Session Memory",
            "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
            "position": [660, 520],
            "typeVersion": 1.3,
            "parameters": {
                "sessionIdType": "fromInput",
                "sessionKey": "={{ $('Chat Message Received').item.json.sessionId || 'default' }}",
                "contextWindowLength": 8
            }
        }
    ],
    "connections": {
        "Chat Message Received": {
            "main": [[{"node": "Ziyada AI Agent", "type": "main", "index": 0}]]
        },
        "OpenAI Chat Model": {
            "ai_languageModel": [[{"node": "Ziyada AI Agent", "type": "ai_languageModel", "index": 0}]]
        },
        "Session Memory": {
            "ai_memory": [[{"node": "Ziyada AI Agent", "type": "ai_memory", "index": 0}]]
        }
    }
}

print(f"Updating workflow to use OpenAI gpt-4o-mini (Gemini quota exceeded)...")
st, result = n8n("PUT", f"/workflows/{WF_ID}", new_workflow)
print(f"PUT: {st}")

if st == 200:
    print(f"  ✓ Updated: {result.get('name')}")

    st2, act = n8n("POST", f"/workflows/{WF_ID}/activate")
    print(f"  Activate: {st2}")

    webhook_url = f"{N8N_BASE}/webhook/{WEBHOOK_ID}/chat"
    vite_path   = f"/n8n/webhook/{WEBHOOK_ID}/chat"

    print(f"\n  Webhook URL : {webhook_url}")
    print(f"  VITE path   : {vite_path}")

    print("\nWaiting 3s for n8n to register webhook...")
    time.sleep(3)

    print("Testing Arabic message...")
    payload = json.dumps({
        "action": "sendMessage",
        "chatInput": "ما هي خدمات زيادة سيستم؟",
        "sessionId": "test-ar-001"
    }).encode()
    try:
        req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            print(f"  ✓ {r.status}: {body[:600]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8","ignore")
        print(f"  ✗ HTTP {e.code}: {body[:400]}")
    except Exception as ex:
        print(f"  ✗ {ex}")

    print("\nTesting English message...")
    payload2 = json.dumps({
        "action": "sendMessage",
        "chatInput": "What services do you offer?",
        "sessionId": "test-en-001"
    }).encode()
    try:
        req2 = urllib.request.Request(webhook_url, data=payload2, headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req2, timeout=30) as r2:
            body2 = r2.read().decode()
            print(f"  ✓ {r2.status}: {body2[:600]}")
    except urllib.error.HTTPError as e:
        body2 = e.read().decode("utf-8","ignore")
        print(f"  ✗ HTTP {e.code}: {body2[:400]}")
    except Exception as ex:
        print(f"  ✗ {ex}")
else:
    print(f"  ✗ Failed: {json.dumps(result, indent=2)[:600]}")
