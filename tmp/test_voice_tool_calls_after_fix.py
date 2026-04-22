#!/usr/bin/env python3
import json
import subprocess

url = 'https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook'

def post(payload):
    cmd = ['curl', '-sS', '--max-time', '35', '-X', 'POST', url, '-H', 'Content-Type: application/json', '-d', json.dumps(payload, ensure_ascii=False)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout or result.stderr

cases = [
    {
        'name': 'save_lead',
        'payload': {
            'message': {
                'toolCallList': [
                    {
                        'id': 'tc-save-1',
                        'function': {
                            'name': 'save_lead',
                            'arguments': json.dumps({
                                'name': 'Ali Test',
                                'phone': '0501234567',
                                'email': 'ali.biggy.af@gmail.com',
                                'service_interest': 'CRM'
                            }, ensure_ascii=False)
                        }
                    }
                ]
            }
        }
    },
    {
        'name': 'create_booking_request',
        'payload': {
            'message': {
                'toolCallList': [
                    {
                        'id': 'tc-book-1',
                        'function': {
                            'name': 'create_booking_request',
                            'arguments': json.dumps({
                                'name': 'Ali Test',
                                'phone': '0501234567',
                                'service': 'CRM',
                                'preferred_datetime': '2026-04-21 17:00',
                                'notes': 'voice test'
                            }, ensure_ascii=False)
                        }
                    }
                ]
            }
        }
    }
]

for case in cases:
    print('===', case['name'], '===')
    print(post(case['payload'])[:1500])
