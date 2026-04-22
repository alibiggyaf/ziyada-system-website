#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

BASE = "https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

def post(path, payload):
    req = urllib.request.Request(f"{BASE}/{path}", data=json.dumps(payload).encode(), method="POST")
    req.add_header("apikey", KEY)
    req.add_header("Authorization", f"Bearer {KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

print('insert chat_session by session_id')
status, out = post('chat_sessions', {'session_id': 'phone-0551230099'})
print(status, out)

print('insert chat_message using same session_id')
status2, out2 = post('chat_messages', {'session_id': 'phone-0551230099', 'role': 'user', 'content': 'history test'})
print(status2, out2)
