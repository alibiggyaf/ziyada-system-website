import json

orig_path = '/Users/djbiggy/Library/Application Support/Code/User/workspaceStorage/c717fb7f2fd809c953132c1321d44824/GitHub.copilot-chat/chat-session-resources/debd2622-c4c8-41c0-9fba-9ec52531de02/call_MHxMNjJIREtUNWlxS0lxVHhFV3c__vscode-1776127346081/content.txt'

with open(orig_path, 'r') as f:
    data = f.read()
    idx = data.rfind('}')
    wf = json.loads(data[:idx+1])

# 1. Define Parser
schema = {
    "type": "object",
    "required": ["title_ar", "title_en", "content_ar", "content_en", "excerpt_ar", "excerpt_en", "slug", "subject"],
    "properties": {
        "title_ar": {"type": "string"},
        "title_en": {"type": "string"},
        "content_ar": {"type": "string"},
        "content_en": {"type": "string"},
        "excerpt_ar": {"type": "string"},
        "excerpt_en": {"type": "string"},
        "slug": {"type": "string"},
        "subject": {"type": "string"}
    }
}

parser_node = {
    "parameters": {
        "schemaType": "manual",
        "inputSchema": json.dumps(schema)
    },
    "type": "@n8n/n8n-nodes-langchain.outputParserStructured",
    "typeVersion": 1.3,
    "position": [1988, 272],
    "id": "v12-parser-final",
    "name": "Ziyada Parser"
}

# 2. Update Nodes
wf['nodes'].append(parser_node)

for node in wf['nodes']:
    if node['name'] == 'ziyada content writer':
        node['parameters']['hasOutputParser'] = True
    if node['name'] == 'Create a row':
        node['parameters']['fieldsUi'] = {
            "fieldValues": [
                {"fieldId": "title_ar", "value": "={{ $json.output.title_ar }}"},
                {"fieldId": "title_en", "value": "={{ $json.output.title_en }}"},
                {"fieldId": "content_ar", "value": "={{ $json.output.content_ar }}"},
                {"fieldId": "content_en", "value": "={{ $json.output.content_en }}"},
                {"fieldId": "excerpt_ar", "value": "={{ $json.output.excerpt_ar }}"},
                {"fieldId": "excerpt_en", "value": "={{ $json.output.excerpt_en }}"},
                {"fieldId": "slug", "value": "={{ $json.output.slug }}"},
                {"fieldId": "status", "value": "draft"},
                {"fieldId": "author_id", "value": "e159d4f4-7111-4850-8d98-2ac5355287ee"}
            ]
        }
    if node['name'] == 'Create a draft':
        node['parameters']['subject'] = "=Ziyada: {{ $json.output.subject }}"
        node['parameters']['message'] = "={{ $json.output.content_ar }}"

# 3. Connections
wf['connections']["Ziyada Parser"] = {
    "ai_outputParser": [[{"node": "ziyada content writer", "type": "ai_outputParser", "index": 0}]]
}

# 4. Final Payload
payload = {
    "name": wf.get('name', 'Ziyada Content Writer'),
    "nodes": wf['nodes'],
    "connections": wf['connections'],
    "active": True,
    "settings": {}
}

with open('v12_final.json', 'w') as f:
    json.dump(payload, f)
