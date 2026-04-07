#!/usr/bin/env python3
"""
Test the local OPENAI_API_KEY from .env and inject into chat workflow.
Never prints the actual key.
"""
import json, urllib.request, urllib.error, os, time, re

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json", "Content-Type": "application/json"}

WF_ID      = "eO6LzcPrnPT3JlpA"
WEBHOOK_ID = "3c9f6cb1-a3ce-4302-8260-6748f093520d"

ENV_PATH = "/Users/djbiggy/Downloads/Claude Code- File Agents/.env"

# Read .env
openai_key = None
with open(ENV_PATH, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('OPENAI_API_KEY=') and 'your_key' not in line and not line.startswith('#'):
            openai_key = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

if not openai_key:
    print("No OPENAI_API_KEY found in .env")
    exit(1)

print(f"Found OPENAI_API_KEY: {openai_key[:8]}... (hidden)")

# Test the key
print("\nTesting key with a quick API call...")
test_body = json.dumps({
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say 'OK' only"}],
    "max_tokens": 5
}).encode()

test_req = urllib.request.Request(
    "https://api.openai.com/v1/chat/completions",
    data=test_body,
    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
    method="POST"
)
try:
    with urllib.request.urlopen(test_req, timeout=15) as r:
        resp = json.loads(r.read())
        reply = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"  ✓ Key is VALID! API response: '{reply}'")
        key_works = True
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", "ignore")
    print(f"  ✗ HTTP {e.code}: {body[:300]}")
    key_works = False
except Exception as ex:
    print(f"  ✗ Error: {ex}")
    key_works = False

if not key_works:
    print("\nKey does not work. Cannot proceed.")
    exit(1)

SYSTEM_MESSAGE = """You are the AI Assistant for Ziyada System (زيادة سيستم), a premium digital marketing and AI automation agency based in Saudi Arabia.

ABOUT ZIYADA SYSTEM:
- Premium digital marketing, content creation, and business automation
- Services: Digital Marketing, AI Content Creation, Business Automation, YouTube Niche Intelligence, SEO & GEO, Social Media
- Languages: Arabic (primary) and English
- Values: Partnership (الشراكة), Excellence, Innovation

RULES:
- Respond in the SAME LANGUAGE the user writes in (Arabic → Arabic, English → English)
- Be professional, friendly, and concise (under 120 words unless more detail asked)
- For service/pricing questions: briefly explain and suggest /BookMeeting for a free consultation
- Never fabricate prices or guarantees

SERVICES:
- Niche Signal Intelligence: AI-powered YouTube niche & trend research
- Content Creation: AI blogs, social media posts, video scripts  
- Digital Marketing: Google Ads, Meta Ads, Snapchat Ads
- Business Automation: n8n workflows, AI agents
- SEO/GEO: Search + AI engine optimization"""

# n8n helper
def n8n(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=N8N_HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, {"raw": raw.decode("utf-8","ignore")[:500]}

# Build workflow with local key
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
return [{{
  json: {{
    model: 'gpt-4o-mini',
    messages: [
      {{ role: 'system', content: {json.dumps(SYSTEM_MESSAGE)} }},
      {{ role: 'user', content: chatInput }}
    ],
    temperature: 0.7,
    max_tokens: 300
  }}
}}];"""
            }
        },
        {
            "id": "openai-http-node",
            "name": "Call OpenAI API",
            "type": "n8n-nodes-base.httpRequest",
            "position": [720, 280],
            "typeVersion": 4.2,
            "parameters": {
                "method": "POST",
                "url": "https://api.openai.com/v1/chat/completions",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Authorization", "value": f"Bearer {openai_key}"},
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
const text = data?.choices?.[0]?.message?.content 
  || 'عذرًا، لم أتمكن من توليد رد. يرجى المحاولة مرة أخرى.';
return [{ json: { output: text.trim(), status: 'success', model: 'gpt-4o-mini' } }];"""
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

print(f"\nDeploying workflow with local OPENAI_API_KEY...")
st, result = n8n("PUT", f"/workflows/{WF_ID}", new_workflow)
print(f"PUT: {st}")
if st != 200:
    print(f"Failed: {json.dumps(result)[:400]}")
    exit(1)

print(f"  ✓ Updated: {result.get('name')}")
st2, _ = n8n("POST", f"/workflows/{WF_ID}/activate")
print(f"  Activate: {st2}")

webhook_url = f"{N8N_BASE}/webhook/{WEBHOOK_ID}/chat"
vite_path   = f"/n8n/webhook/{WEBHOOK_ID}/chat"

print("\nWaiting 3s for n8n to register...")
time.sleep(3)

# Live test
for msg, sid in [("ما هي خدمات زيادة سيستم؟", "test-ar"), ("What services do you offer?", "test-en")]:
    print(f"\nTest: {msg[:50]}")
    payload = json.dumps({"action": "sendMessage", "chatInput": msg, "sessionId": sid}).encode()
    try:
        req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            data = json.loads(body)
            print(f"  ✓ output: {data.get('output','')[:300]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8","ignore")
        print(f"  ✗ HTTP {e.code}: {body[:300]}")
    except Exception as ex:
        print(f"  ✗ {ex}")

print(f"\n{'='*65}")
print(f"NOW UPDATE .env.local:")
print(f"  VITE_CHATBOT_WEBHOOK={vite_path}")
print(f"  VITE_CHATBOT_ENABLED=true")
print(f"{'='*65}")
