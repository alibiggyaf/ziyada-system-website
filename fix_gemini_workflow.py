#!/usr/bin/env python3
"""
Fix the Ziyada Chat Widget - Gemini Flash workflow.
Problems found:
1. "Format Response" code node has NO jsCode - causes 500 errors
2. Webhook path has leading slash "/chat" which may register as "//chat"
3. No actual Gemini AI - just hardcoded keyword responses

This script rebuilds the workflow properly using the existing 
Google Gemini credential (A87gfuB0ORA75x5R) with a chatTrigger + AI Agent pattern.
"""
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

WF_ID = "eO6LzcPrnPT3JlpA"
WEBHOOK_ID = "3c9f6cb1-a3ce-4302-8260-6748f093520d"  # keep same ID

GEMINI_CRED_ID = "A87gfuB0ORA75x5R"
GEMINI_CRED_NAME = "Google Gemini(PaLM) Api account"

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

SERVICES QUICK REFERENCE:
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

# First GET the existing workflow to preserve settings/meta
print(f"Getting existing workflow {WF_ID}...")
st, existing = n8n("GET", f"/workflows/{WF_ID}")
if st != 200:
    print(f"Failed to get workflow: {st} {existing}")
    exit(1)

print(f"  Name: {existing.get('name')}, Active: {existing.get('active')}")

# Build the new workflow body (PUT replaces the full workflow)
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
                "options": {
                    "responseMode": "lastNode"
                }
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
                "options": {
                    "systemMessage": SYSTEM_MESSAGE
                }
            }
        },
        {
            "id": "gemini-llm-node",
            "name": "Gemini Flash Model",
            "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
            "position": [400, 520],
            "typeVersion": 1,
            "parameters": {
                "modelName": "models/gemini-2.0-flash",
                "options": {
                    "temperature": 0.7,
                    "maxOutputTokens": 300
                }
            },
            "credentials": {
                "googlePalmApi": {
                    "id": GEMINI_CRED_ID,
                    "name": GEMINI_CRED_NAME
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
            "main": [
                [{"node": "Ziyada AI Agent", "type": "main", "index": 0}]
            ]
        },
        "Gemini Flash Model": {
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

print(f"\nUpdating workflow with chatTrigger + Gemini Flash AI Agent...")
st2, result = n8n("PUT", f"/workflows/{WF_ID}", new_workflow)
print(f"PUT status: {st2}")

if st2 == 200:
    print(f"  ✓ Workflow updated: {result.get('name')}")
    print(f"  Active: {result.get('active')}")
    
    # Activate - try POST /activate
    print("\nActivating workflow...")
    st3, act = n8n("POST", f"/workflows/{WF_ID}/activate")
    print(f"  Activate result: {st3} -> {act}")
    
    # The webhook URL for chatTrigger
    webhook_url = f"{N8N_BASE}/webhook/{WEBHOOK_ID}/chat"
    vite_path   = f"/n8n/webhook/{WEBHOOK_ID}/chat"
    
    print(f"\n{'='*65}")
    print(f"✓ WEBHOOK URL: {webhook_url}")
    print(f"✓ VITE variable: {vite_path}")
    print(f"{'='*65}")
    
    # Test it
    import time
    print("\nWaiting 3s for n8n to register webhook...")
    time.sleep(3)
    
    print(f"Testing: POST {webhook_url}")
    try:
        payload = json.dumps({
            "action": "sendMessage",
            "chatInput": "ما هي خدمات زيادة سيستم؟",
            "sessionId": "test-fix-001"
        }).encode()
        req = urllib.request.Request(
            webhook_url, data=payload,
            headers={"Content-Type":"application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            print(f"  ✓ Status: {r.status}")
            print(f"  ✓ Response: {body[:600]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8","ignore")
        print(f"  ✗ HTTP {e.code}: {body[:500]}")
    except Exception as ex:
        print(f"  ✗ Error: {ex}")
else:
    print(f"✗ Update failed: {json.dumps(result, indent=2)[:800]}")
