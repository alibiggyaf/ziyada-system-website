#!/usr/bin/env python3
"""
Extract the working OpenAI Authorization header from Ali Content Writer
and build the Ziyada chat workflow using httpRequest (same approach).
Never prints the API key - only injects it directly into n8n.
"""
import json, urllib.request, urllib.error, time

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

WF_ID     = "eO6LzcPrnPT3JlpA"
WEBHOOK_ID = "3c9f6cb1-a3ce-4302-8260-6748f093520d"
SOURCE_WF  = "y7gXaTFEyIDOz7uS"  # Has working OpenAI httpRequest calls

SYSTEM_MESSAGE = """You are the AI Assistant for Ziyada System (زيادة سيستم), a premium digital marketing and AI automation agency based in Saudi Arabia.

ABOUT ZIYADA SYSTEM:
- Premium digital marketing, content creation, and business automation services
- Services: Digital Marketing, AI Content Creation, Business Automation, YouTube Niche Intelligence, SEO & GEO, Social Media Management
- Languages: Arabic (primary) and English
- Values: Partnership (الشراكة), Excellence, Innovation

RULES:
- Respond in the SAME LANGUAGE the user writes in (Arabic → Arabic, English → English)
- Be professional, friendly, and concise (under 120 words unless more detail asked)
- For service questions: briefly explain and suggest booking a free consultation
- For consultation/pricing: direct to /BookMeeting for a free 30-min session
- Never fabricate prices or guarantees

SERVICES:
- Niche Signal Intelligence: AI-powered YouTube niche & trend research
- Content Creation: AI blogs, social media posts, video scripts
- Digital Marketing: Google Ads, Meta Ads, Snapchat Ads
- Business Automation: n8n workflows, AI agents, CRM integration
- SEO/GEO: Search engine + AI engine optimization"""

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
            return e.code, {"raw": raw.decode("utf-8","ignore")[:500]}

# Step 1: Extract the Authorization header from the working workflow
print(f"Extracting auth from working workflow {SOURCE_WF}...")
st, source = n8n("GET", f"/workflows/{SOURCE_WF}")
if st != 200:
    print(f"Cannot get source workflow: {st}")
    exit(1)

auth_header_value = None
for node in source.get("nodes", []):
    if node.get("name") == "Generate Content With OpenAI":
        params = node.get("parameters", {})
        header_params = params.get("headerParameters", {})
        entries = header_params.get("parameters", [])
        for entry in entries:
            if entry.get("name","").lower() == "authorization":
                auth_header_value = entry.get("value", "")
                print("  ✓ Found Authorization header (value hidden)")
                break
        if auth_header_value:
            break

if not auth_header_value:
    print("  ✗ Could not find Authorization header")
    exit(1)

# Step 2: Build the new workflow with httpRequest to OpenAI
OPENAI_MESSAGES_URL = "https://api.openai.com/v1/chat/completions"

new_workflow = {
    "name": "🚀 Ziyada Chat Widget - Gemini Flash (Cheapest)",
    "settings": {"executionOrder": "v1"},
    "staticData": None,
    "nodes": [
        {
            "id": "chat-trigger-node",
            "name": "Chat Message Received",
            "type": "@n8n/n8n-nodes-langchain.chatTrigger",
            "position": [240, 280],
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
            "id": "prepare-node",
            "name": "Prepare OpenAI Request",
            "type": "n8n-nodes-base.code",
            "position": [480, 280],
            "typeVersion": 2,
            "parameters": {
                "jsCode": f"""const chatInput = $input.first().json.chatInput || '';
const sessionId = $input.first().json.sessionId || 'default';

return [{{
  json: {{
    model: 'gpt-4o-mini',
    messages: [
      {{
        role: 'system',
        content: {json.dumps(SYSTEM_MESSAGE)}
      }},
      {{
        role: 'user',
        content: chatInput
      }}
    ],
    temperature: 0.7,
    max_tokens: 300,
    _sessionId: sessionId,
    _userMessage: chatInput
  }}
}}];"""
            }
        },
        {
            "id": "openai-request-node",
            "name": "Call OpenAI API",
            "type": "n8n-nodes-base.httpRequest",
            "position": [720, 280],
            "typeVersion": 4.2,
            "parameters": {
                "method": "POST",
                "url": OPENAI_MESSAGES_URL,
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Authorization", "value": auth_header_value},
                        {"name": "Content-Type", "value": "application/json"}
                    ]
                },
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ model: $json.model, messages: $json.messages, temperature: $json.temperature, max_tokens: $json.max_tokens }) }}",
                "options": {}
            }
        },
        {
            "id": "format-node",
            "name": "Format Response",
            "type": "n8n-nodes-base.code",
            "position": [960, 280],
            "typeVersion": 2,
            "parameters": {
                "jsCode": """const data = $input.first().json;
const text = data?.choices?.[0]?.message?.content || 'عذرًا، لم أتمكن من توليد رد. يرجى المحاولة مرة أخرى.';

return [{
  json: {
    output: text.trim(),
    status: 'success',
    model: 'gpt-4o-mini'
  }
}];"""
            }
        }
    ],
    "connections": {
        "Chat Message Received": {
            "main": [[{"node": "Prepare OpenAI Request", "type": "main", "index": 0}]]
        },
        "Prepare OpenAI Request": {
            "main": [[{"node": "Call OpenAI API", "type": "main", "index": 0}]]
        },
        "Call OpenAI API": {
            "main": [[{"node": "Format Response", "type": "main", "index": 0}]]
        }
    }
}

print(f"\nUpdating chat workflow with working httpRequest + OpenAI approach...")
st2, result = n8n("PUT", f"/workflows/{WF_ID}", new_workflow)
print(f"PUT: {st2}")

if st2 == 200:
    print(f"  ✓ Updated: {result.get('name')}")
    st3, _ = n8n("POST", f"/workflows/{WF_ID}/activate")
    print(f"  Activate: {st3}")

    webhook_url = f"{N8N_BASE}/webhook/{WEBHOOK_ID}/chat"
    vite_path   = f"/n8n/webhook/{WEBHOOK_ID}/chat"

    print(f"\n  Webhook: {webhook_url}")
    print(f"  VITE:    {vite_path}")

    print("\nWaiting 3s...")
    time.sleep(3)

    for msg, sid in [("ما هي خدمات زيادة سيستم؟", "test-ar-01"), ("What services do you offer?", "test-en-01")]:
        print(f"\nTesting: {msg[:40]}")
        try:
            payload = json.dumps({"action": "sendMessage", "chatInput": msg, "sessionId": sid}).encode()
            req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type":"application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode()
                print(f"  ✓ {r.status}: {body[:400]}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8","ignore")
            print(f"  ✗ HTTP {e.code}: {body[:300]}")
        except Exception as ex:
            print(f"  ✗ {ex}")

    print(f"\n{'='*65}")
    print(f"UPDATE .env.local:")
    print(f"  VITE_CHATBOT_WEBHOOK={vite_path}")
    print(f"  VITE_CHATBOT_ENABLED=true")
    print(f"{'='*65}")
else:
    print(f"  ✗ Failed: {json.dumps(result,indent=2)[:500]}")
