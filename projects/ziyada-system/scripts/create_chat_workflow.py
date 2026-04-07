# -*- coding: utf-8 -*-
"""Create the 'Ziyada System Chat Website' chatbot workflow in n8n."""
import json
import urllib.request

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"

SYSTEM_PROMPT = (
    "\u0623\u0646\u062a \u0645\u0633\u0627\u0639\u062f \u0632\u064a\u0627\u062f\u0629 \u0633\u064a\u0633\u062a\u0645 \u0627\u0644\u0630\u0643\u064a. "
    "\u0623\u0646\u062a \u0645\u0633\u062a\u0634\u0627\u0631 \u0623\u0639\u0645\u0627\u0644 \u0631\u0642\u0645\u064a \u0645\u062a\u062e\u0635\u0635 "
    "\u0641\u064a \u0645\u0633\u0627\u0639\u062f\u0629 \u0627\u0644\u0634\u0631\u0643\u0627\u062a \u0648\u0627\u0644\u0645\u0624\u0633\u0633\u0627\u062a "
    "\u0627\u0644\u0633\u0639\u0648\u062f\u064a\u0629.\n\n"
    "\u0645\u0639\u0644\u0648\u0645\u0627\u062a\u0643 \u0639\u0646 \u0632\u064a\u0627\u062f\u0629 \u0633\u064a\u0633\u062a\u0645:\n"
    "- \u0632\u064a\u0627\u062f\u0629 \u0633\u064a\u0633\u062a\u0645 \u0647\u064a \u0634\u0631\u0643\u0629 \u0633\u0639\u0648\u062f\u064a\u0629 "
    "\u0645\u062a\u062e\u0635\u0635\u0629 \u0641\u064a \u0627\u0644\u0623\u0646\u0638\u0645\u0629 \u0627\u0644\u0631\u0642\u0645\u064a\u0629 "
    "\u0627\u0644\u0645\u062a\u0643\u0627\u0645\u0644\u0629\n"
    "- \u0646\u0642\u062f\u0645 6 \u062e\u062f\u0645\u0627\u062a \u0631\u0626\u064a\u0633\u064a\u0629:\n"
    "  1. \u0623\u0646\u0638\u0645\u0629 \u0623\u062a\u0645\u062a\u0629 \u0627\u0644\u0623\u0639\u0645\u0627\u0644\n"
    "  2. \u0623\u0646\u0638\u0645\u0629 \u0625\u062f\u0627\u0631\u0629 \u0627\u0644\u0639\u0645\u0644\u0627\u0621 \u0648\u0627\u0644\u0645\u0628\u064a\u0639\u0627\u062a (CRM)\n"
    "  3. \u0623\u0646\u0638\u0645\u0629 \u0627\u0643\u062a\u0633\u0627\u0628 \u0627\u0644\u0639\u0645\u0644\u0627\u0621\n"
    "  4. \u0627\u0644\u062a\u0633\u0648\u064a\u0642 \u0627\u0644\u0623\u062f\u0627\u0626\u064a \u0648\u0627\u0644\u0638\u0647\u0648\u0631 \u0641\u064a \u0627\u0644\u0628\u062d\u062b\n"
    "  5. \u0627\u0644\u0645\u0648\u0627\u0642\u0639 \u0627\u0644\u0630\u0643\u064a\u0629 \u0648\u0627\u0644\u0645\u0646\u0635\u0627\u062a \u0627\u0644\u0631\u0642\u0645\u064a\u0629\n"
    "  6. \u0623\u0646\u0638\u0645\u0629 \u0627\u0644\u0645\u062d\u062a\u0648\u0649 \u0648\u0648\u0633\u0627\u0626\u0644 \u0627\u0644\u062a\u0648\u0627\u0635\u0644\n\n"
    "- \u0627\u0644\u0645\u0648\u0642\u0639: ziyada.sa\n"
    "- \u0644\u0644\u0627\u0633\u062a\u0634\u0627\u0631\u0629 \u0627\u0644\u0645\u062c\u0627\u0646\u064a\u0629: /BookMeeting\n"
    "- \u0644\u0637\u0644\u0628 \u0639\u0631\u0636 \u0633\u0639\u0631: /RequestProposal\n\n"
    "\u0642\u0648\u0627\u0639\u062f:\n"
    "- \u062a\u062d\u062f\u062b \u0628\u0627\u0644\u0644\u0647\u062c\u0629 \u0627\u0644\u0633\u0639\u0648\u062f\u064a\u0629 \u0627\u0644\u0628\u064a\u0636\u0627\u0621\n"
    "- \u0643\u0646 \u0648\u062f\u0648\u062f\u0627\u064b \u0648\u0645\u062d\u062a\u0631\u0641\u0627\u064b\n"
    "- \u0625\u0630\u0627 \u0633\u0623\u0644 \u0627\u0644\u0639\u0645\u064a\u0644 \u0633\u0624\u0627\u0644 \u062a\u0642\u0646\u064a \u0645\u0639\u0642\u062f\u060c "
    "\u0627\u0642\u062a\u0631\u062d \u0639\u0644\u064a\u0647 \u062d\u062c\u0632 \u0627\u0633\u062a\u0634\u0627\u0631\u0629 \u0645\u062c\u0627\u0646\u064a\u0629\n"
    "- \u0644\u0627 \u062a\u062e\u062a\u0631\u0639 \u0645\u0639\u0644\u0648\u0645\u0627\u062a\n"
    "- \u0631\u0643\u0632 \u0639\u0644\u0649 \u0627\u0644\u0642\u064a\u0645\u0629 \u0648\u0627\u0644\u0646\u062a\u0627\u0626\u062c"
)

workflow = {
    "name": "Ziyada System Chat Website",
    "nodes": [
        {
            "parameters": {
                "options": {
                    "allowedOrigins": "*"
                }
            },
            "id": "a1b2c3d4-0001-4000-8000-000000000001",
            "name": "Chat Trigger",
            "type": "@n8n/n8n-nodes-langchain.chatTrigger",
            "typeVersion": 1.1,
            "position": [200, 300],
            "webhookId": "390b23bb-a7e4-48c4-8768-c3b89cc0ef36"
        },
        {
            "parameters": {
                "options": {
                    "systemMessage": SYSTEM_PROMPT
                },
                "promptType": "define"
            },
            "id": "a1b2c3d4-0001-4000-8000-000000000002",
            "name": "AI Agent",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 1.7,
            "position": [500, 300]
        },
        {
            "parameters": {
                "options": {
                    "temperature": 0.7
                }
            },
            "id": "a1b2c3d4-0001-4000-8000-000000000003",
            "name": "OpenAI Chat Model",
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
            "typeVersion": 1.2,
            "position": [500, 520]
        },
        {
            "parameters": {
                "contextWindowLength": 20
            },
            "id": "a1b2c3d4-0001-4000-8000-000000000004",
            "name": "Window Buffer Memory",
            "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
            "typeVersion": 1.3,
            "position": [700, 520]
        }
    ],
    "connections": {
        "Chat Trigger": {
            "main": [
                [
                    {
                        "node": "AI Agent",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "OpenAI Chat Model": {
            "ai_languageModel": [
                [
                    {
                        "node": "AI Agent",
                        "type": "ai_languageModel",
                        "index": 0
                    }
                ]
            ]
        },
        "Window Buffer Memory": {
            "ai_memory": [
                [
                    {
                        "node": "AI Agent",
                        "type": "ai_memory",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

payload = json.dumps(workflow).encode("utf-8")
req = urllib.request.Request(
    f"{N8N_URL}/workflows",
    data=payload,
    headers={
        "X-N8N-API-KEY": N8N_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"SUCCESS: Workflow created!")
        print(f"  ID: {result.get('id')}")
        print(f"  Name: {result.get('name')}")
        print(f"  Active: {result.get('active')}")
        for node in result.get('nodes', []):
            if 'chatTrigger' in node.get('type', ''):
                wh_id = node.get('webhookId', 'unknown')
                print(f"  Chat Trigger webhookId: {wh_id}")
                print(f"  Production webhook URL: https://n8n.srv953562.hstgr.cloud/webhook/{wh_id}/chat")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"ERROR {e.code}: {body}")
