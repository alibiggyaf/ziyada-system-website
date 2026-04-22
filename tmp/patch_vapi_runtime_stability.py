#!/usr/bin/env python3
import json
import subprocess

API_KEY = "bb31ea26-edac-4e14-bd24-a5abbece31bc"
ASSISTANT_ID = "f3e88e06-573f-4d2d-8f8a-214edf3144a6"


def call_vapi(method, path, payload=None):
    cmd = [
        "curl",
        "-s",
        "-X",
        method,
        f"https://api.vapi.ai{path}",
        "-H",
        f"Authorization: Bearer {API_KEY}",
        "-H",
        "Content-Type: application/json",
    ]
    if payload is not None:
        cmd += ["-d", json.dumps(payload, ensure_ascii=False)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout, "stderr": result.stderr}

assistant = call_vapi("GET", f"/assistant/{ASSISTANT_ID}")

# Keep model/voice/transcriber unchanged exactly; only adjust runtime stability and prompt behavior.
model = assistant.get("model", {})
messages = model.get("messages", [])
if messages and messages[0].get("role") == "system":
    content = messages[0].get("content", "")
    stability_block = """

قواعد الاستقرار أثناء المكالمة (مهم جداً):
- لا تعطِ ردود طويلة متواصلة. كل رد يكون قصير جداً (جملتين كحد أقصى غالباً) ثم توقف.
- عند شرح الخدمات، اذكر خدمتين فقط ثم اسأل إذا العميل يريد تكمل.
- إذا ما وصل صوت العميل بوضوح، لا تكرر كلام طويل؛ استخدم جملة قصيرة: "ثواني عن إذنك، الصوت مو واضح، ممكن تعيد؟".
- لا تبقى تتكلم بدون انتظار رد العميل.
- إذا صار أي تأخير تقني، استخدم عبارة لبقة قصيرة فقط ثم ارجع لسؤال العميل.
"""
    if "قواعد الاستقرار أثناء المكالمة" not in content:
        messages[0]["content"] = content + stability_block

# Keep same model id/provider; only lower max tokens to reduce long rambles that trigger mid-call instability.
if isinstance(model, dict):
    model["messages"] = messages
    # keep within safe concise band; do not alter model name/provider
    current_max = model.get("maxTokens", 260)
    model["maxTokens"] = min(current_max, 180)

server_url = "https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook"

payload = {
    "name": assistant.get("name", "Ziyada system voice call"),
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
    # Runtime stability knobs (non-model, non-voice, non-transcriber)
    "backgroundDenoisingEnabled": False,
    "startSpeakingPlan": {
        "waitSeconds": 0.4,
        "timeoutSeconds": 45
    },
    "server": {
        "url": server_url,
        "timeoutSeconds": 45
    },
    "maxDurationSeconds": 1800,
    "silenceTimeoutSeconds": 90
}

updated = call_vapi("PATCH", f"/assistant/{ASSISTANT_ID}", payload)

print("assistant:", updated.get("id"), updated.get("name"))
print("model:", updated.get("model", {}).get("model"))
print("voice provider:", updated.get("voice", {}).get("provider"))
print("transcriber provider:", updated.get("transcriber", {}).get("provider"))
print("maxTokens:", updated.get("model", {}).get("maxTokens"))
print("backgroundDenoisingEnabled:", updated.get("backgroundDenoisingEnabled"))
print("startSpeakingPlan:", updated.get("startSpeakingPlan"))
print("server:", updated.get("server"))
print("maxDurationSeconds:", updated.get("maxDurationSeconds"))
print("silenceTimeoutSeconds:", updated.get("silenceTimeoutSeconds"))
