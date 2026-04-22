#!/usr/bin/env python3
import json
import subprocess
import time

URL = 'https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook'

cases = [
    ('off_topic', 'مين فاز في مباراة الهلال امس؟'),
    ('services', 'وش خدمات زيادة سيستم؟'),
    ('number_readback', 'رقمي 0501234567 اعده رقم رقم للتأكيد'),
    ('booking', 'ابغى احجز استشارة يوم الاثنين الساعة 5 مساء'),
    ('lead_capture', 'اسمي علي بيجي ورقمي 0501234567 وبريدي ali.biggy.af@gmail.com وسجلني كعميل مهتم بخدمة CRM'),
    ('website_faq', 'وين الاقي صفحة الخدمات او FAQ في موقعكم؟'),
]

for case, text in cases:
    sid = f'accept-{case}-{int(time.time()*1000)}'
    payload = {'voice': {'session_id': sid, 'transcript': text, 'language': 'ar', 'provider': 'vapi'}}
    cmd = ['curl', '-s', '-X', 'POST', URL, '-H', 'Content-Type: application/json', '-d', json.dumps(payload, ensure_ascii=False)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    print(f'=== {case} ===')
    print(out[:1600])
    print()
