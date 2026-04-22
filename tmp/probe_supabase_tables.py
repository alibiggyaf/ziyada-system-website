#!/usr/bin/env python3
import json
import subprocess

BASE = "https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

headers = [
    "-H", f"apikey: {KEY}",
    "-H", f"Authorization: Bearer {KEY}",
    "-H", "Content-Type: application/json",
    "-H", "Prefer: return=representation",
]

def req(method, path, body=None):
    cmd = ["curl", "-s", "-X", method, f"{BASE}/{path}"] + headers
    if body is not None:
        cmd += ["-d", json.dumps(body, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip()

print("chat_messages select:")
print(req("GET", "chat_messages?select=*&limit=1"))
print()

print("voice_assistant_leads insert:")
print(req("POST", "voice_assistant_leads", {"name": "probe", "phone": "0551"}))
print()

print("voice_booking_requests insert:")
print(req("POST", "voice_booking_requests", {"name": "probe", "phone": "0551", "service": "test"}))
print()

print("chat_messages insert (minimal):")
print(req("POST", "chat_messages", {"content": "probe only"}))

print()
print("chat_messages insert (session_id+sender+content):")
print(req("POST", "chat_messages", {"session_id": "phone-0559991110", "sender": "voice_assistant", "content": "probe insert ok"}))

print()
print("leads insert probe:")
print(req("POST", "leads", {"email": "voice-probe@ziyada.local", "name": "Voice Probe", "source": "voice_assistant", "status": "new"}))

print()
print("bookings insert probe:")
print(req("POST", "bookings", {"lead_email": "voice-probe@ziyada.local", "lead_name": "Voice Probe", "lead_phone": "0550001112", "company": "Voice Test Co", "booking_date": "2026-04-18", "booking_time": "10:00", "status": "pending"}))
