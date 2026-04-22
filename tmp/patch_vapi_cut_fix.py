#!/usr/bin/env python3
import json
import subprocess

API_KEY = "bb31ea26-edac-4e14-bd24-a5abbece31bc"
ASSISTANT_ID = "f3e88e06-573f-4d2d-8f8a-214edf3144a6"


def call_vapi(method, path, payload=None):
    cmd = [
        "curl", "-s", "-X", method, f"https://api.vapi.ai{path}",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
    ]
    if payload is not None:
        cmd += ["-d", json.dumps(payload, ensure_ascii=False)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError:
        return {"raw": res.stdout, "stderr": res.stderr}

assistant = call_vapi("GET", f"/assistant/{ASSISTANT_ID}")
model = assistant.get("model", {})
messages = model.get("messages", [])

stability_rules = """

قواعد منع انقطاع المكالمة:
- لا تتكلم أكثر من جملتين في كل رد.
- بعد كل رد توقف مباشرة وانتظر صوت العميل.
- لا تعدد كل الخدمات دفعة واحدة؛ اذكر 1-2 فقط ثم اسأل إذا يكمل.
- إذا صار تشويش أو ما وصل صوت العميل، قل جملة قصيرة فقط: "ثواني عن إذنك، الصوت مو واضح، ممكن تعيد؟".
"""

if messages and messages[0].get("role") == "system":
    content = messages[0].get("content", "")
    if "قواعد منع انقطاع المكالمة" not in content:
        messages[0]["content"] = content + stability_rules

# Keep same model/provider; only reduce max tokens to avoid long monologues.
if isinstance(model, dict):
    model["messages"] = messages
    model["maxTokens"] = min(int(model.get("maxTokens", 220)), 140)

payload = {
    "name": assistant.get("name"),
    "model": model,
    "voice": assistant.get("voice"),
    "transcriber": assistant.get("transcriber"),
    "firstMessage": assistant.get("firstMessage"),
    "voicemailMessage": assistant.get("voicemailMessage"),
    "endCallMessage": assistant.get("endCallMessage"),
    "clientMessages": assistant.get("clientMessages", []),
    "serverMessages": assistant.get("serverMessages", []),
    "analysisPlan": assistant.get("analysisPlan", {}),
    "artifactPlan": assistant.get("artifactPlan", {}),
    "backgroundDenoisingEnabled": False,
    "startSpeakingPlan": {"waitSeconds": 0.45}
}

updated = call_vapi("PATCH", f"/assistant/{ASSISTANT_ID}", payload)
print(json.dumps({
    "id": updated.get("id"),
    "name": updated.get("name"),
    "model": updated.get("model", {}).get("model"),
    "voiceProvider": updated.get("voice", {}).get("provider"),
    "transcriberProvider": updated.get("transcriber", {}).get("provider"),
    "maxTokens": updated.get("model", {}).get("maxTokens"),
    "backgroundDenoisingEnabled": updated.get("backgroundDenoisingEnabled"),
    "startSpeakingPlan": updated.get("startSpeakingPlan")
}, ensure_ascii=False, indent=2))
