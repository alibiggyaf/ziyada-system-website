#!/usr/bin/env python3
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"

r = requests.get(
    f"{BASE}/api/v1/workflows/62MN6oqxOs3levjh",
    headers={"X-N8N-API-KEY": KEY},
    timeout=30,
)
r.raise_for_status()
wf = r.json()

print("name", wf.get("name"), "nodes", len(wf.get("nodes", [])))
for node in wf.get("nodes", []):
    t = node.get("type", "")
    if "langchain" in t or node.get("name") in {"AI Agent", "ai_agent", "youtube_search", "chat_model", "memory", "System Message"}:
        print("\nNODE", node.get("name"), "|", t)
        p = node.get("parameters", {})
        for k in ["text", "prompt", "systemMessage", "options", "inputText", "messages", "description", "toolDescription"]:
            if k in p:
                print(k, str(p[k])[:1200])
