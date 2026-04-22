#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
ROOT_ENV = ROOT / ".env.local"
APP_ENV = ROOT / "projects" / "ziyada-system" / "app" / "ziyada-system-website" / ".env.local"


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> None:
    root_env = read_env(ROOT_ENV)
    app_env = read_env(APP_ENV)
    api_key = root_env.get("VAPI_API_KEY") or app_env.get("VAPI_API_KEY")
    assistant_id = app_env.get("VAPI_ASSISTANT_ID") or app_env.get("VITE_VAPI_ASSISTANT_ID")
    if not api_key or not assistant_id:
        raise SystemExit("Missing VAPI_API_KEY or assistant id in env files")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"https://api.vapi.ai/assistant/{assistant_id}"
    current = requests.get(url, headers=headers, timeout=30)
    current.raise_for_status()
    assistant = current.json()

    model = assistant.get("model") if isinstance(assistant.get("model"), dict) else {}
    model["provider"] = "openrouter"
    model["model"] = "openai/gpt-4.1-mini"

    payload = {
        "name": assistant.get("name"),
        "firstMessage": assistant.get("firstMessage"),
        "maxDurationSeconds": assistant.get("maxDurationSeconds", 150),
        "voice": assistant.get("voice"),
        "transcriber": assistant.get("transcriber"),
        "model": model,
        "analysisPlan": assistant.get("analysisPlan"),
        "artifactPlan": assistant.get("artifactPlan"),
        "startSpeakingPlan": assistant.get("startSpeakingPlan"),
        "responseDelaySeconds": assistant.get("responseDelaySeconds", 0),
        "llmRequestDelaySeconds": assistant.get("llmRequestDelaySeconds", 0),
        "serverMessages": assistant.get("serverMessages"),
        "clientMessages": assistant.get("clientMessages"),
        "endCallMessage": assistant.get("endCallMessage"),
        "voicemailMessage": assistant.get("voicemailMessage"),
        "backgroundDenoisingEnabled": assistant.get("backgroundDenoisingEnabled", False),
    }

    patched = requests.patch(url, headers=headers, data=json.dumps(payload), timeout=40)
    patched.raise_for_status()
    out = patched.json()
    out_model = out.get("model") if isinstance(out.get("model"), dict) else {}
    out_voice = out.get("voice") if isinstance(out.get("voice"), dict) else {}
    out_transcriber = out.get("transcriber") if isinstance(out.get("transcriber"), dict) else {}

    print(
        json.dumps(
            {
                "assistantId": out.get("id"),
                "modelProvider": out_model.get("provider"),
                "modelName": out_model.get("model"),
                "voiceProvider": out_voice.get("provider"),
                "voiceId": out_voice.get("voiceId") or out_voice.get("model") or out_voice.get("id"),
                "transcriberProvider": out_transcriber.get("provider"),
                "transcriberModel": out_transcriber.get("model"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()