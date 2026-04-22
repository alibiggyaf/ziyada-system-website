#!/usr/bin/env python3
import subprocess

BASE = "https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/chat_messages"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

candidates = [
    "id","session_id","content","created_at","sender","role","direction","source","source_label","language","event_ts","message_id","phone","channel","type"
]

for col in candidates:
    url = f"{BASE}?select={col}&limit=1"
    cmd = ["curl","-s",url,"-H",f"apikey: {KEY}","-H",f"Authorization: Bearer {KEY}"]
    out = subprocess.run(cmd,capture_output=True,text=True).stdout.strip()
    ok = out.startswith("[")
    print(f"{col}: {'OK' if ok else 'NO'} | {out[:120]}")
