#!/usr/bin/env python3
import json
import subprocess

API_KEY = "bb31ea26-edac-4e14-bd24-a5abbece31bc"
ASSISTANT_ID = "f3e88e06-573f-4d2d-8f8a-214edf3144a6"

cmd = [
    "curl",
    "-s",
    f"https://api.vapi.ai/call?assistantId={ASSISTANT_ID}&limit=50",
    "-H",
    f"Authorization: Bearer {API_KEY}",
]

res = subprocess.run(cmd, capture_output=True, text=True)
try:
    data = json.loads(res.stdout)
except json.JSONDecodeError:
    print("parse-error", res.stdout[:500])
    raise SystemExit(0)

if isinstance(data, dict):
    if "results" in data and isinstance(data["results"], list):
        calls = data["results"]
    elif "data" in data and isinstance(data["data"], list):
        calls = data["data"]
    elif "id" in data:
        calls = [data]
    else:
        calls = []
else:
    calls = data

print("count:", len(calls))
for c in calls:
    cid = c.get("id")
    created = c.get("createdAt")
    status = c.get("status")
    ended = c.get("endedReason") or c.get("ended_reason")
    ended2 = c.get("analysis", {}).get("summary", {}).get("result")
    err = c.get("error")
    tr = c.get("transcriber") or c.get("assistant", {}).get("transcriber")
    print(f"{cid} | {created} | status={status} | ended={ended} | summary={ended2} | transcriber={tr} | error={err}")
