#!/usr/bin/env python3
from pathlib import Path
import json, requests

def read_env(path):
    env = {}
    if not Path(path).exists():
        return env
    for line in Path(path).read_text().splitlines():
        s = line.strip()
        if not s or s.startswith('#') or '=' not in s:
            continue
        k, v = s.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ROOT_ENV = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/.env.local')
APP_ENV = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/.env.local')

root_env = read_env(ROOT_ENV)
app_env = read_env(APP_ENV)

api_key = root_env.get('VAPI_API_KEY') or app_env.get('VAPI_API_KEY')
assistant_id = app_env.get('VAPI_ASSISTANT_ID') or app_env.get('VITE_VAPI_ASSISTANT_ID')
pub_key = app_env.get('VITE_VAPI_PUBLIC_KEY') or app_env.get('VAPI_PUBLIC_KEY')

print('pub_key_present:', bool(pub_key))
print('assistant_id:', assistant_id)

headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
d = requests.get(f'https://api.vapi.ai/assistant/{assistant_id}', headers=headers, timeout=30).json()
model = d.get('model') or {}
voice = d.get('voice') or {}
trans = d.get('transcriber') or {}
server = d.get('server') or {}

print('=== VAPI ASSISTANT SUMMARY ===')
print('id:', d.get('id'))
print('name:', d.get('name'))
print('modelProvider:', model.get('provider'))
print('modelName:', model.get('model'))
print('voiceProvider:', voice.get('provider'), '| voiceId:', voice.get('voiceId') or voice.get('id'))
print('transcriberProvider:', trans.get('provider'), '| transcriberModel:', trans.get('model'))
print('maxDurationSeconds:', d.get('maxDurationSeconds'))
print('firstMessage:', d.get('firstMessage'))
print('server.url:', server.get('url'))
print('\n=== SYSTEM PROMPT (first 3000 chars) ===')
sys_prompt = model.get('systemPrompt') or (model.get('messages') or [{}])[0].get('content') or '(not set)'
print(str(sys_prompt)[:3000])
print('\nmaxDurationSeconds:', d.get('maxDurationSeconds'))
