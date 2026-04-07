#!/usr/bin/env python3
"""
Debug workflow trigger - check sheet, verify polling, manually test
"""
import urllib.request
import json
import os
import time

SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WORKFLOW_ID = "C8JWsE3KIoxr1KgO"

print("="*70)
print("WORKFLOW TRIGGER DEBUG")
print("="*70)

# Step 1: Check workflow status via n8n API
print("\n1. Checking workflow status in n8n...")
N8N_API_KEY = os.getenv("N8N_API_KEY", "").strip()

if not N8N_API_KEY:
    print("   ✗ N8N_API_KEY not set - skipping API check")
    print("   (This is OK, we can still test via Telegram webhook)")
else:
    try:
        headers = {
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json"
        }
        
        req = urllib.request.Request(
            f"{N8N_URL}/workflows/{WORKFLOW_ID}",
            headers=headers,
            method="GET"
        )
        
        with urllib.request.urlopen(req) as response:
            workflow = json.loads(response.read())
            print(f"   ✓ Workflow ID: {workflow.get('id')}")
            print(f"     Name: {workflow.get('name')}")
            print(f"     Active: {workflow.get('active')}")
            print(f"     Nodes: {len(workflow.get('nodes', []))}")
            
            # Check for trigger nodes
            triggers = [n['name'] for n in workflow.get('nodes', []) if 'trigger' in n.get('type', '').lower()]
            print(f"     Triggers found: {triggers}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")

# Step 2: Manual trigger via webhook
print("\n2. Testing webhook trigger (like Telegram would)...")

webhook_url = "https://n8n.srv953562.hstgr.cloud/webhook/ziyada-blog-ingest"

test_data = {
    "update_id": 999999,
    "message": {
        "message_id": 1,
        "date": int(time.time()),
        "chat": {
            "id": -1001234567890,
            "type": "group"
        },
        "text": """اسم الشركة: Ziyada System
المجال: Software/AI
الجمهور: Business Leaders
الرابط: https://ziyada.com
الموضوع: AI workflow automation

ابدأ التنفيذ"""
    }
}

try:
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(test_data).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        print(f"   ✓ Webhook triggered!")
        print(f"     Status: {response.status}")
        print(f"     Response: {result}")
        print(f"     → Check ContentResults tab in 30 seconds")
        
except urllib.error.HTTPError as e:
    print(f"   ✗ Webhook error: {e.code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Step 3: Sheet diagnostic
print("\n3. Sheet structure check...")
print("""
   Your sheet should have columns:
   A: request_id
   B: company_name
   C: industry
   D: target_audience
   E: company_link
   F: topic (or writer_task)
   G: send_status  ← This is your TRIGGER column
   H: approval_status
   I: writer_task (or other)

   CRITICAL: The send_status column MUST contain:
   ✓ "start" or "continue" (exactly, lowercase)
   ✗ NOT "done", "done", empty, or other values
""")

print("\n" + "="*70)
print("NEXT: Check your ContentResults tab in 30 seconds")
print("="*70)
