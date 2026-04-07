#!/usr/bin/env python3
"""Check if successful Ali Content Writer executions actually call OpenAI, 
and check if any other AI provider credentials exist in the env files."""
import json, urllib.request, urllib.error, os, re

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
HEADERS = {"X-N8N-API-KEY": N8N_KEY, "Accept": "application/json"}

def n8n_get(path):
    req = urllib.request.Request(f"{N8N_URL}{path}", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# Check execution 232895 (successful y7gXaTFEyIDOz7uS run)
print("=== Successful execution 232895 - which nodes ran? ===")
st, exec_data = n8n_get("/executions/232895?includeData=true")
if st == 200:
    run_data = exec_data.get("data", {}).get("resultData", {}).get("runData", {})
    for node_name, runs in run_data.items():
        status = "ok" if not any(r.get("error") for r in runs) else "ERROR"
        print(f"  {status} | {node_name}")
else:
    print(f"  Error {st}: {exec_data}")

# Search env files for any API keys
print("\n=== Searching env files for API keys ===")
search_dirs = [
    "/Users/djbiggy/Downloads/Claude Code- File Agents",
    "/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system"
]
key_patterns = re.compile(r'(API_KEY|SECRET|TOKEN|OPENAI|GEMINI|GROQ|MISTRAL|ANTHROPIC|CLAUDE)\s*[=:]\s*([A-Za-z0-9_\-\.]{10,})', re.IGNORECASE)

for d in search_dirs:
    for root, dirs, files in os.walk(d):
        # Skip node_modules and .git
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', '.venv', 'dist']]
        for fname in files:
            if fname in ['.env', '.env.local', '.env.example', 'setup.sh'] or fname.endswith('.env'):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', errors='ignore') as f:
                        content = f.read()
                    matches = key_patterns.findall(content)
                    if matches:
                        print(f"\n  File: {fpath.replace('/Users/djbiggy/Downloads/Claude Code- File Agents/', '')}")
                        for key_name, key_val in matches:
                            # Show key type but hide actual value for security
                            val_preview = key_val[:8] + "..." if len(key_val) > 8 else key_val
                            print(f"    {key_name}: {val_preview}")
                except:
                    pass
