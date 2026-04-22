#!/usr/bin/env python3
import subprocess

BASE = "https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1/chat_sessions"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"
cols = ["id","created_at","updated_at","phone","user_id","title","status","source","channel","metadata"]
for c in cols:
    u = f"{BASE}?select={c}&limit=1"
    cmd=["curl","-s",u,"-H",f"apikey: {KEY}","-H",f"Authorization: Bearer {KEY}"]
    out=subprocess.run(cmd,capture_output=True,text=True).stdout.strip()
    ok = out.startswith("[")
    print(f"{c}: {'OK' if ok else 'NO'} | {out[:120]}")
