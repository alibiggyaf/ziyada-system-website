#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

url = "https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/chat_sessions"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

body = json.dumps({"id": "00000000-0000-4000-8000-000000000001"}).encode()
req = urllib.request.Request(url, data=body, method="POST")
req.add_header("apikey", key)
req.add_header("Authorization", f"Bearer {key}")
req.add_header("Content-Type", "application/json")
req.add_header("Prefer", "return=representation")

try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print(r.status)
        print(r.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    print(e.read().decode())
except Exception as e:
    print("ERR", type(e).__name__, str(e))
