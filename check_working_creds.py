#!/usr/bin/env python3
"""Check Ali Content Writer Engine http request node for OpenAI credentials."""
import json, urllib.request, urllib.error

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

# Check y7gXaTFEyIDOz7uS - the working Ali Content Writer
print("=== Ali Content Writer (y7gXaTFEyIDOz7uS) - OpenAI node details ===")
st, wf = n8n_get("/workflows/y7gXaTFEyIDOz7uS")
if st == 200:
    for node in wf.get("nodes", []):
        name = node.get("name","")
        ntype = node.get("type","")
        if "openai" in name.lower() or "openai" in ntype.lower() or "generate" in name.lower():
            print(f"\nNode: {name} | type: {ntype}")
            params = node.get("parameters", {})
            creds = node.get("credentials", {})
            print(f"  credentials: {json.dumps(creds)}")
            # Show URL and auth method but not the key itself
            if "url" in params:
                print(f"  url: {params['url']}")
            if "sendHeaders" in params or "headerParameters" in params:
                headers_param = params.get("headerParameters", {})
                send_headers = params.get("sendHeaders", False)
                print(f"  sendHeaders: {send_headers}")
                # Show header names only (not values which might contain API key)
                if isinstance(headers_param, dict):
                    entries = headers_param.get("parameters", [])
                    for entry in entries:
                        key = entry.get("name","")
                        val = entry.get("value","")
                        # Only print if it's not obviously an API key
                        if "key" not in key.lower() and "auth" not in key.lower() and "bearer" not in val[:10].lower():
                            print(f"    header[{key}] = {val[:50]}")
                        else:
                            print(f"    header[{key}] = [HIDDEN]")
            if "authentication" in params:
                print(f"  authentication: {params['authentication']}")
            if "genericAuthType" in params:
                print(f"  genericAuthType: {params['genericAuthType']}")

# Also check C8JWsE3KIoxr1KgO
print("\n=== Ali Content Writer (C8JWsE3KIoxr1KgO) ===")
st2, wf2 = n8n_get("/workflows/C8JWsE3KIoxr1KgO")
if st2 == 200:
    print(f"  Name: {wf2.get('name')}")
    for node in wf2.get("nodes", []):
        name = node.get("name","")
        ntype = node.get("type","")
        if "openai" in name.lower() or "generate" in name.lower() or "gemini" in name.lower() or "llm" in name.lower():
            print(f"\n  Node: {name} | type: {ntype}")
            print(f"    credentials: {json.dumps(node.get('credentials',{}))}")
