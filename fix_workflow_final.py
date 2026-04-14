import json

# Correct original content path (double checking)
orig_path = '/Users/djbiggy/Library/Application Support/Code/User/workspaceStorage/c717fb7f2fd809c953132c1321d44824/GitHub.copilot-chat/chat-session-resources/debd2622-c4c8-41c0-9fba-9ec52531de02/call_MHxwWGlFS0IyYXBIQ1dxQTFQb2M__vscode-1776127346052/content.txt'

with open(orig_path, 'r') as f:
    wf = json.load(f)

# Define the Structured Output Schema for Ziyada Content Writer
ziyada_schema = {
    "type": "object",
    "required": ["title_ar", "title_en", "content_ar", "content_en", "excerpt_ar", "excerpt_en", "slug", "subject"],
    "properties": {
        "title_ar": {"type": "string", "description": "SEO Title in Arabic"},
        "title_en": {"type": "string", "description": "SEO Title in English"},
        "content_ar": {"type": "string", "description": "Markdown content in Arabic"},
        "content_en": {"type": "string", "description": "Markdown content in English"},
        "excerpt_ar": {"type": "string", "description": "Short summary in Arabic"},
        "excerpt_en": {"type": "string", "description": "Short summary in English"},
        "slug": {"type": "string", "description": "URL-friendly slug (e.g. ai-automation-benefits)"},
        "subject": {"type": "string", "description": "Email subject line"}
    }
}

# 1. Update 'search news topics' to handle Webhook input
for node in wf['nodes']:
    if node['name'] == 'search news topics':
        node['parameters']['query'] = "={{ $json.body.topic || 'AI adoption for businesses' }}"

# 2. Add the Structured Output Parser for Ziyada Content Writer
parser_node = {
    "parameters": {
        "schemaType": "manual",
        "inputSchema": json.dumps(ziyada_schema)
    },
    "type": "@n8n/n8n-nodes-langchain.outputParserStructured",
    "typeVersion": 1.3,
    "position": [1988, 272],
    "id": "ziyada-parser-id-final",
    "name": "Ziyada Output Parser"
}
wf['nodes'].append(parser_node)

# 3. Enable output parsing on the 'ziyada content writer' node (Agent)
for node in wf['nodes']:
    if node['name'] == 'ziyada content writer':
        node['parameters']['hasOutputParser'] = True

# 4. Map connections for the new parser
# We'll put it in connections at the same level (Ziyada Output Parser -> ziyada content writer)
wf['connections']["Ziyada Output Parser"] = {
    "ai_outputParser": [[{"node": "ziyada content writer", "type": "ai_outputParser", "index": 0}]]
}

# 5. Connect the Agent to the Supabase node ('Create a row')
for node in wf['nodes']:
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

# 6. Fix Gmail Draft Node
for node in wf['nodes']:
    if node['name'] == 'Create a draft':
        node['parameters']['subject'] = "=Ziyada: {{ $json.output.subject }}"
        node['parameters']['message'] = "={{ $json.output.content_ar }}"

# 7. REQUIRED properties for n8n API update: name, nodes, connections
# MUST NOT have extra nesting. 
payload = {
    "name": wf.get('name', 'Ziyada Blogs and Newsletter Content Writer'),
    "nodes": wf['nodes'],
    "connections": wf['connections'],
    "settings": wf.get('settings', {}),
    "staticData": wf.get('staticData', None)
}

# Dump to file
with open('final_fix_payload.json', 'w') as f:
    json.dump(payload, f)

