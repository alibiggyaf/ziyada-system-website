import json

with open('workflow_payload.json', 'r') as f:
    data = json.load(f)

# The API update requires 'nodes', 'connections', 'name', 'settings' at the top level
# If the previous payload was the entire workflow object, let's extract what's needed
payload = {
    "name": data.get("name", "Ziyada Content Writer"),
    "nodes": data.get("nodes", []),
    "connections": data.get("connections", {}),
    "settings": data.get("settings", {}),
    "staticData": data.get("staticData", None),
    "tags": data.get("tags", [])
}

with open('fixed_workflow_payload.json', 'w') as f:
    json.dump(payload, f)
