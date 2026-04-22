#!/usr/bin/env python3
import json
import subprocess

API = "bb31ea26-edac-4e14-bd24-a5abbece31bc"
AID = "f3e88e06-573f-4d2d-8f8a-214edf3144a6"

get_cmd = ["curl", "-s", f"https://api.vapi.ai/assistant/{AID}", "-H", f"Authorization: Bearer {API}"]
res = subprocess.run(get_cmd, capture_output=True, text=True).stdout
print("GET length:", len(res))
obj = json.loads(res)

payload = {
    "name": obj["name"],
    "model": obj["model"],
    "voice": obj["voice"],
    "transcriber": obj["transcriber"],
    "startSpeakingPlan": {"waitSeconds": 0.4, "timeoutSeconds": 45},
    "server": {"url": "https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook", "timeoutSeconds": 45},
}

patch_cmd = [
    "curl", "-s", "-X", "PATCH", f"https://api.vapi.ai/assistant/{AID}",
    "-H", f"Authorization: Bearer {API}",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload, ensure_ascii=False),
]
out = subprocess.run(patch_cmd, capture_output=True, text=True).stdout
print("PATCH response:")
print(out[:4000])
