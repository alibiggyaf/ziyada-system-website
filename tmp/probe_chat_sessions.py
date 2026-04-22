#!/usr/bin/env python3
import json, subprocess

BASE = "https://nuyscajjlhxviuyrxzyq.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

def req(method, path, body=None):
    cmd=["curl","-s","-X",method,f"{BASE}/{path}","-H",f"apikey: {KEY}","-H",f"Authorization: Bearer {KEY}","-H","Content-Type: application/json","-H","Prefer: return=representation"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    return subprocess.run(cmd,capture_output=True,text=True).stdout

print('chat_sessions select:')
print(req('GET','chat_sessions?select=*&limit=1'))
print('\ninsert chat_sessions minimal:')
out1 = req('POST','chat_sessions',{'id':'phone-0551230099'})
print(out1)
print('len:', len(out1))
print('\ninsert chat_sessions name field:')
out2 = req('POST','chat_sessions',{'id':'phone-0551230099','name':'Voice Session'})
print(out2)
print('len:', len(out2))

print('\ninsert chat_sessions uuid id only:')
out3 = req('POST','chat_sessions',{'id':'00000000-0000-4000-8000-000000000001'})
print(out3)
print('len:', len(out3))
