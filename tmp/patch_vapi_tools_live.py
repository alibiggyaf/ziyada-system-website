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


env = read_env('.env.local')
assistant_id = env.get('VAPI_ASSISTANT_ID', '').strip()
api_key = env.get('VAPI_API_KEY', '').strip()
if not assistant_id or not api_key:
    raise SystemExit('Missing VAPI credentials')

# Canonical tool IDs in this workspace/session.
TOOL_IDS = [
    'bb7675e6-54cc-4066-9dfe-970b36eb0d3e',  # get_services_info
    '675ea618-5ade-4701-a8d5-4a7144a308c1',  # save_lead
    '585baf39-3e5e-4b66-9540-40d3e956f594',  # create_booking_request
    '45eabeed-ef94-4330-9b82-661c3966fba7',  # get_conversation_history
]

url = f'https://api.vapi.ai/assistant/{assistant_id}'
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
current = requests.get(url, headers=headers, timeout=30)
current.raise_for_status()
d = current.json()
model = d.get('model') if isinstance(d.get('model'), dict) else {'provider': 'openai', 'model': 'gpt-4o-mini'}
model['toolIds'] = TOOL_IDS
payload = {
    'name': d.get('name'),
    'firstMessage': d.get('firstMessage'),
    'maxDurationSeconds': d.get('maxDurationSeconds', 150),
    'voice': d.get('voice'),
    'transcriber': d.get('transcriber'),
    'model': model,
    'server': d.get('server'),
    'analysisPlan': d.get('analysisPlan'),
    'artifactPlan': d.get('artifactPlan'),
    'startSpeakingPlan': d.get('startSpeakingPlan'),
    'responseDelaySeconds': d.get('responseDelaySeconds', 0),
    'llmRequestDelaySeconds': d.get('llmRequestDelaySeconds', 0),
    'serverMessages': d.get('serverMessages'),
    'clientMessages': d.get('clientMessages'),
    'endCallMessage': d.get('endCallMessage'),
}
res = requests.patch(url, headers=headers, data=json.dumps(payload), timeout=40)
if not res.ok:
    print(res.text)
res.raise_for_status()
out = res.json()
out_model = out.get('model') if isinstance(out.get('model'), dict) else {}
print(json.dumps({
    'assistantId': out.get('id'),
    'modelToolCount': len(out_model.get('toolIds') or []),
    'modelToolIds': out_model.get('toolIds') or [],
}, ensure_ascii=False, indent=2))
