#!/usr/bin/env python3
import os
import urllib.request
import json
import time

# Use n8n API to check workflow status
N8N_BASE_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
WORKFLOW_ID = "C8JWsE3KIoxr1KgO"

if not N8N_API_KEY:
    print("Error: N8N_API_KEY not set")
    exit(1)

print(f"Checking n8n workflow status: {WORKFLOW_ID}")
print(f"N8N URL: {N8N_BASE_URL}\n")

# Get workflow details
headers = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Content-Type": "application/json"
}

try:
    # Check workflow
    req = urllib.request.Request(
        f"{N8N_BASE_URL}/workflows/{WORKFLOW_ID}",
        headers=headers,
        method="GET"
    )
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        print(f"✓ Workflow Status:")
        print(f"  ID: {data.get('id')}")
        print(f"  Name: {data.get('name')}")
        print(f"  Active: {data.get('active')}")
        print(f"  Nodes: {len(data.get('nodes', []))}")
        
        # Check for trigger nodes
        triggers = [n for n in data.get('nodes', []) if 'trigger' in n.get('type', '').lower()]
        print(f"  Schedule Triggers: {len(triggers)}")
        for t in triggers:
            print(f"    - {t.get('name')} ({t.get('type')})")
            
    # Get recent executions
    print(f"\n✓ Recent workflow executions:")
    req = urllib.request.Request(
        f"{N8N_BASE_URL}/workflows/{WORKFLOW_ID}/executions?limit=10",
        headers=headers,
        method="GET"
    )
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        executions = data.get('data', [])
        if executions:
            print(f"  Total: {len(executions)} executions")
            for i, exe in enumerate(executions[:5], 1):
                status = exe.get('status', 'unknown')
                finished_at = exe.get('finishedAt', 'N/A')
                started_at = exe.get('startedAt', 'N/A')
                print(f"  {i}. {status.upper()} | Started: {started_at[:19] if isinstance(started_at, str) else started_at} | Finished: {finished_at[:19] if isinstance(finished_at, str) else finished_at}")
        else:
            print(f"  No executions yet - workflow may not have run")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
