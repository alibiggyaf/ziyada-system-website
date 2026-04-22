#!/usr/bin/env python3
"""
Deploy the updated Ziyada AI Chat Agent workflow to n8n.
Uses existing webhook IDs (no new webhooks).
"""

import json
import urllib.request
import urllib.error
import pathlib
from dotenv import dotenv_values

# Load credentials from .env.local
env = dotenv_values("/Users/djbiggy/Downloads/Claude Code- File Agents/.env.local")
API_URL = env.get("N8N_API_URL", "").rstrip("/")
API_KEY = env.get("N8N_API_KEY", "").strip('"').strip("'")

if not API_URL or not API_KEY:
    raise RuntimeError("Missing N8N_API_URL or N8N_API_KEY in .env.local")

print(f"🔗 n8n API: {API_URL}")
print(f"🔑 API Key: {API_KEY[:20]}...")

# 1. Load the updated workflow JSON
workflow_path = pathlib.Path(
    "/Users/djbiggy/Downloads/Claude Code- File Agents"
    "/projects/ziyada-system/n8n for ziyada system"
    "/workflow_ziyada_ai_chat_agent_FIXED.json"
)

with open(workflow_path, encoding="utf-8") as f:
    updated_workflow = json.load(f)

print(f"\n📄 Loaded updated workflow: {updated_workflow['name']}")
print(f"   Nodes: {[n['name'] for n in updated_workflow['nodes']]}")

# 2. List all workflows in n8n to find the ID
list_url = f"{API_URL}/workflows"
req = urllib.request.Request(list_url)
req.add_header("X-N8N-API-KEY", API_KEY)
req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(req) as response:
        workflows_data = json.loads(response.read().decode('utf-8'))
    
    print(f"\n📋 Found {len(workflows_data.get('data', []))} workflows in n8n")
    
    # Find the workflow by name
    target_workflow = None
    for wf in workflows_data.get('data', []):
        if wf['name'] == updated_workflow['name']:
            target_workflow = wf
            break
    
    if not target_workflow:
        print(f"⚠️  Workflow '{updated_workflow['name']}' not found by name.")
        print("   Available workflows:")
        for wf in workflows_data.get('data', [])[:10]:
            print(f"     - {wf['name']} (ID: {wf['id']})")
        raise RuntimeError(f"Workflow '{updated_workflow['name']}' not found in n8n")
    
    workflow_id = target_workflow['id']
    print(f"✅ Found target workflow: {target_workflow['name']} (ID: {workflow_id})")
    
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"❌ HTTP Error {e.code}: {error_body}")
    raise
except Exception as e:
    print(f"❌ Error listing workflows: {e}")
    raise

# 3. Get current workflow to see exact schema
get_url = f"{API_URL}/workflows/{workflow_id}"
req = urllib.request.Request(get_url)
req.add_header("X-N8N-API-KEY", API_KEY)

current_workflow = None
try:
    with urllib.request.urlopen(req) as response:
        current_workflow = json.loads(response.read().decode('utf-8'))
    
    print(f"\n✅ Retrieved current workflow from n8n")
    
except Exception as e:
    print(f"⚠️  Could not retrieve current workflow: {e}")

# 4. Update the workflow using PUT with only essential update fields
update_url = f"{API_URL}/workflows/{workflow_id}"
req = urllib.request.Request(update_url, method='PUT')
req.add_header("X-N8N-API-KEY", API_KEY)
req.add_header("Content-Type", "application/json")

# Build minimal payload with only fields that should be updated
payload = {
    "name": updated_workflow['name'],
    "nodes": updated_workflow.get('nodes', []),
    "connections": updated_workflow.get('connections', {}),
    "settings": updated_workflow.get('settings', {})
}

payload_json = json.dumps(payload, ensure_ascii=False, indent=2)

try:
    req.data = payload_json.encode('utf-8')
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    print(f"\n✅ Workflow updated successfully!")
    print(f"   Name: {result.get('name')}")
    print(f"   ID: {result.get('id')}")
    print(f"   Nodes: {len(result.get('nodes', []))}")
    
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"❌ HTTP Error {e.code}")
    print(f"   Response: {error_body}")
    
    # If it fails, suggest manual import
    print(f"\n⚠️  API update failed. Trying alternative approach...")
    print(f"   The updated workflow JSON is ready at:")
    print(f"   {workflow_path}")
    print(f"\n   You can manually import it in n8n:")
    print(f"   1. Go to n8n dashboard")
    print(f"   2. Click Workflows")
    print(f"   3. Find 'Ziyada AI Chat Agent — Website'")
    print(f"   4. Use import/upload option with the JSON file")
    raise
except Exception as e:
    print(f"❌ Error updating workflow: {e}")
    raise

# 4. Activate the workflow
activate_url = f"{API_URL}/workflows/{workflow_id}/activate"
req = urllib.request.Request(activate_url, method='PATCH')
req.add_header("X-N8N-API-KEY", API_KEY)
req.add_header("Content-Type", "application/json")
req.data = b'{}'

try:
    with urllib.request.urlopen(req) as response:
        activate_result = json.loads(response.read().decode('utf-8'))
    
    if activate_result.get('active'):
        print(f"\n✅ Workflow activated!")
    else:
        print(f"\n⚠️  Workflow update complete, but activation status unclear")
    
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"⚠️  Activation HTTP {e.code}: {error_body}")
    print("   (Workflow may still be updated successfully)")
except Exception as e:
    print(f"⚠️  Could not activate: {e}")
    print("   (Workflow may still be updated successfully)")

print("\n🎉 Deployment complete!")
print(f"   Workflow: {updated_workflow['name']}")
print(f"   ID: {workflow_id}")
print(f"   Tools: {len([n for n in updated_workflow['nodes'] if 'tool' in n.get('name', '').lower()])}")
print(f"   Webhook: {[n.get('webhookId') for n in updated_workflow['nodes'] if 'Trigger' in n.get('name', '')]}")
