#!/usr/bin/env python3
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
WF = "62MN6oqxOs3levjh"

NEW_SYSTEM_MESSAGE = (
    "You are the Niche Signal Intelligence assistant for YouTube trend discovery.\n\n"
    "1) If the user did not provide a niche/topic, ask one concise follow-up question with 3 suggestions.\n"
    "2) Use the youtube_search tool up to 3 times with varied search terms tied to the user's niche.\n"
    "3) Treat tool data as valid even when some metrics are unavailable. Do not apologize for missing view/like/comment/tag/channel fields.\n"
    "4) Always return actionable insights based on titles, repeated themes, and topic angles across returned videos.\n"
    "5) Always include video links in this format: https://www.youtube.com/watch?v={video_id}.\n"
    "6) If confidence is low, clearly label assumptions, then still provide useful next search angles and content hooks.\n\n"
    "Answer format:\n"
    "- Top signals (3-5 bullets)\n"
    "- Content angles to test (3 bullets)\n"
    "- Example titles/hooks (3 bullets)\n"
    "- Video links found"
)


def main() -> None:
    get_headers = {"X-N8N-API-KEY": KEY}
    put_headers = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}

    r = requests.get(f"{BASE}/api/v1/workflows/{WF}", headers=get_headers, timeout=30)
    r.raise_for_status()
    wf = r.json()

    updated = False
    for node in wf.get("nodes", []):
        if node.get("type") == "@n8n/n8n-nodes-langchain.agent" or node.get("name") == "AI Agent":
            opts = node.setdefault("parameters", {}).setdefault("options", {})
            opts["systemMessage"] = "=" + NEW_SYSTEM_MESSAGE
            updated = True

    if not updated:
        raise SystemExit("AI Agent node not found in workflow 62")

    payload = {k: wf.get(k) for k in ["name", "nodes", "connections", "settings"]}
    up = requests.put(f"{BASE}/api/v1/workflows/{WF}", headers=put_headers, json=payload, timeout=30)
    print("PUT", up.status_code)
    print(up.text[:300])

    act = requests.post(f"{BASE}/api/v1/workflows/{WF}/activate", headers=get_headers, timeout=30)
    print("ACT", act.status_code)


if __name__ == "__main__":
    main()
