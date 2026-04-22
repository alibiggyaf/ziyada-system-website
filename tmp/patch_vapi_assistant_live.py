import json
from pathlib import Path

import requests


def read_env(path: str) -> dict:
    env = {}
    for line in Path(path).read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


env = read_env(".env.local")
assistant_id = env.get("VAPI_ASSISTANT_ID", "").strip()
api_key = env.get("VAPI_API_KEY", "").strip()
if not assistant_id or not api_key:
    raise SystemExit("Missing VAPI credentials in .env.local")

url = f"https://api.vapi.ai/assistant/{assistant_id}"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

current_resp = requests.get(url, headers=headers, timeout=30)
current_resp.raise_for_status()
current = current_resp.json()

system_prompt = (
    "أنت مساعد مبيعات زيادة سيستم (صوتي) متخصص في الأعمال فقط. "
    "إذا كان السؤال خارج نطاق الأعمال فقل: هذا خارج نطاقي، أقدر أساعدك في خدمات زيادة سيستم ونمو عملك. وش التحدي الرئيسي عندكم؟ "
    "عند جمع أي رقم: اطلبه رقم رقم، ثم أعده رقم رقم وتأكد قبل الحفظ. "
    "إذا طلب العميل الإنجليزية انطق الرقم بالإنجليزية فقط، وإذا كان بالعربية انطقه بالعربية فقط، ولا تخلط اللغتين إلا بطلب صريح. "
    "إذا كان هناك تأخير تقني استخدم عبارات مهذبة قصيرة مثل: ثواني من فضلك، عن إذنك بشيك لك بسرعة."
)

model = current.get("model") if isinstance(current.get("model"), dict) else {
    "provider": "openai",
    "model": "gpt-4o-mini",
}
model["messages"] = [{"role": "system", "content": system_prompt}]

payload = {
    "name": current.get("name") or "Ziyada system voice call",
    "firstMessage": current.get("firstMessage") or "هلا وغلا، معك مساعد زيادة سيستم. كيف أقدر أخدمك اليوم؟",
    "model": model,
    "voice": {"provider": "11labs", "voiceId": "t9akNmCDhz230CEXOYmn"},
    "transcriber": {
        "provider": "11labs",
        "language": "ar",
        "model": "scribe_v2_realtime",
    },
    "maxDurationSeconds": 150,
    "responseDelaySeconds": 0,
    "llmRequestDelaySeconds": 0,
    "server": current.get("server"),
    "startSpeakingPlan": current.get("startSpeakingPlan") or {"waitSeconds": 0.2},
    "stopSpeakingPlan": current.get("stopSpeakingPlan"),
    "analysisPlan": current.get("analysisPlan"),
    "backgroundSound": current.get("backgroundSound"),
    "clientMessages": current.get("clientMessages"),
    "serverMessages": current.get("serverMessages"),
    "endCallMessage": current.get("endCallMessage") or "تمام، أسعدنا اتصالك، وفي أمان الله.",
}

patch_resp = requests.patch(url, headers=headers, data=json.dumps(payload), timeout=40)
if not patch_resp.ok:
    print(patch_resp.text)
patch_resp.raise_for_status()
out = patch_resp.json()

summary = {
    "assistantId": out.get("id"),
    "voiceProvider": (out.get("voice") or {}).get("provider"),
    "voiceId": (out.get("voice") or {}).get("voiceId"),
    "transcriberProvider": (out.get("transcriber") or {}).get("provider"),
    "transcriberModel": (out.get("transcriber") or {}).get("model"),
    "transcriberLanguage": (out.get("transcriber") or {}).get("language"),
    "toolCount": len(out.get("toolIds") or []),
    "maxDurationSeconds": out.get("maxDurationSeconds"),
    "responseDelaySeconds": out.get("responseDelaySeconds"),
    "llmRequestDelaySeconds": out.get("llmRequestDelaySeconds"),
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
