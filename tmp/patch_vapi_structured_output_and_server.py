#!/usr/bin/env python3
"""Patch live VAPI assistant without changing voice/transcriber/model settings.

Changes:
- Set assistant.server.url to n8n callback webhook.
- Enable analysisPlan.structuredDataPlan with booking/lead extraction schema.
"""

from pathlib import Path
import json
import requests

ROOT_ENV = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/.env.local')
APP_ENV = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/.env.local')
VOICE_WEBHOOK_URL = 'https://n8n.srv953562.hstgr.cloud/webhook/ziyada-voice-agent'


def read_env(path: Path) -> dict:
    if not path.exists():
        return {}
    env = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main() -> None:
    root_env = read_env(ROOT_ENV)
    app_env = read_env(APP_ENV)

    api_key = root_env.get('VAPI_API_KEY') or app_env.get('VAPI_API_KEY')
    assistant_id = app_env.get('VAPI_ASSISTANT_ID') or app_env.get('VITE_VAPI_ASSISTANT_ID')
    if not api_key or not assistant_id:
        raise SystemExit('Missing VAPI_API_KEY or assistant ID')

    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    url = f'https://api.vapi.ai/assistant/{assistant_id}'

    current_resp = requests.get(url, headers=headers, timeout=30)
    current_resp.raise_for_status()
    current = current_resp.json()

    analysis_plan = dict(current.get('analysisPlan') or {})
    analysis_plan['structuredDataPlan'] = {
        'enabled': True,
        'timeoutSeconds': 12,
        'schema': {
            'type': 'object',
            'title': 'ZiyadaVoiceStructuredOutput',
            'description': 'Extract lead and booking signals from the completed call transcript.',
            'properties': {
                'intent': {
                    'type': 'string',
                    'enum': ['book_meeting', 'request_pricing', 'request_demo', 'ask_general_info', 'support', 'other'],
                    'description': 'Primary user intent by end of call.'
                },
                'language': {
                    'type': 'string',
                    'enum': ['ar', 'en', 'mixed'],
                    'description': 'Dominant language used in call.'
                },
                'lead': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'phone': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                        'company': {'type': 'string'},
                        'industry': {'type': 'string'}
                    },
                    'required': []
                },
                'booking': {
                    'type': 'object',
                    'properties': {
                        'requested': {'type': 'boolean'},
                        'date': {'type': 'string', 'format': 'date'},
                        'time': {'type': 'string'},
                        'timezone': {'type': 'string'},
                        'status': {
                            'type': 'string',
                            'enum': ['none', 'pending', 'confirmed', 'failed']
                        }
                    },
                    'required': ['requested', 'status']
                },
                'qualification': {
                    'type': 'object',
                    'properties': {
                        'budget_signal': {'type': 'string'},
                        'urgency': {'type': 'string', 'enum': ['high', 'medium', 'low', 'unknown']},
                        'decision_maker': {'type': 'string', 'enum': ['yes', 'no', 'unknown']},
                        'need_summary': {'type': 'string'}
                    },
                    'required': ['urgency', 'decision_maker']
                },
                'follow_up_channel': {
                    'type': 'string',
                    'enum': ['website_chat', 'whatsapp', 'email', 'phone', 'none']
                },
                'summary': {'type': 'string'},
                'next_action': {'type': 'string'}
            },
            'required': ['intent', 'language', 'booking', 'follow_up_channel', 'summary', 'next_action']
        }
    }

    payload = {
        'name': current.get('name'),
        'firstMessage': current.get('firstMessage'),
        'maxDurationSeconds': current.get('maxDurationSeconds', 480),
        'voice': current.get('voice'),
        'transcriber': current.get('transcriber'),
        'model': current.get('model'),
        'analysisPlan': analysis_plan,
        'artifactPlan': current.get('artifactPlan'),
        'startSpeakingPlan': current.get('startSpeakingPlan'),
        'responseDelaySeconds': current.get('responseDelaySeconds', 0),
        'llmRequestDelaySeconds': current.get('llmRequestDelaySeconds', 0),
        'serverMessages': current.get('serverMessages'),
        'clientMessages': current.get('clientMessages'),
        'endCallMessage': current.get('endCallMessage'),
        'voicemailMessage': current.get('voicemailMessage'),
        'backgroundDenoisingEnabled': current.get('backgroundDenoisingEnabled', False),
        'server': {
            'url': VOICE_WEBHOOK_URL
        }
    }

    patch_resp = requests.patch(url, headers=headers, data=json.dumps(payload), timeout=45)
    patch_resp.raise_for_status()
    out = patch_resp.json()
    out_analysis = out.get('analysisPlan') or {}
    sdp = out_analysis.get('structuredDataPlan') or {}

    print(json.dumps({
        'assistantId': out.get('id'),
        'serverUrl': (out.get('server') or {}).get('url'),
        'maxDurationSeconds': out.get('maxDurationSeconds'),
        'structuredDataEnabled': sdp.get('enabled', False),
        'structuredDataSchemaTitle': ((sdp.get('schema') or {}).get('title')),
        'voiceProvider': (out.get('voice') or {}).get('provider'),
        'transcriberProvider': (out.get('transcriber') or {}).get('provider')
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
