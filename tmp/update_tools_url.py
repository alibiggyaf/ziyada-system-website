#!/usr/bin/env python3
import json, subprocess

VAPI_KEY = "bb31ea26-edac-4e14-bd24-a5abbece31bc"
DISPATCHER = "https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook"
TOOL_IDS = [
    "17d7c276-72cb-4037-b91a-431bfd78eda1",
    "d23f0a11-e437-4b28-82e7-fadb152fc0f4",
    "585baf39-3e5e-4b66-9540-40d3e956f594",
    "45ea8eed-ef94-4330-9b82-661c3966fba7"
]

for tid in TOOL_IDS:
    cmd = ["curl", "-s", "-X", "PATCH", "https://api.vapi.ai/tool/" + tid,
           "-H", "Authorization: Bearer " + VAPI_KEY,
           "-H", "Content-Type: application/json",
           "-d", json.dumps({"server": {"url": DISPATCHER}})]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        name = d.get("function", {}).get("name", "?")
        url = d.get("server", {}).get("url", "?")
        print(tid[:8], "->", name, "| url:", url[:60])
    except:
        print(tid[:8], "raw:", r.stdout[:100])
