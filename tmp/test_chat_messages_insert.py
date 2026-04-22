#!/usr/bin/env python3
import json, subprocess

BASE = "https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/chat_messages"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

headers = ["-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}", "-H", "Content-Type: application/json", "-H", "Prefer: return=representation"]

def post(body):
    cmd=["curl","-s","-X","POST",BASE]+headers+["-d",json.dumps(body)]
    return subprocess.run(cmd,capture_output=True,text=True).stdout

def get(url):
    cmd=["curl","-s",url,"-H",f"apikey: {KEY}","-H",f"Authorization: Bearer {KEY}"]
    return subprocess.run(cmd,capture_output=True,text=True).stdout

print('insert with role:')
print(post({"session_id":"phone-0551230099","role":"user","content":"hello from probe"}))
print('query same session:')
print(get(BASE + "?select=session_id,role,content,created_at&session_id=eq.phone-0551230099&order=created_at.desc&limit=3"))
