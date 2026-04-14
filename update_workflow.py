import json

with open('/Users/djbiggy/Library/Application Support/Code/User/workspaceStorage/c717fb7f2fd809c953132c1321d44824/GitHub.copilot-chat/chat-session-resources/debd2622-c4c8-41c0-9fba-9ec52531de02/call_MHxwWGlFS0IyYXBIQ1dxQTFQb2M__vscode-1776127346052/content.txt', 'r') as f:
    wf = json.load(f)

# Define the Structured Output Schema for Ziyada Content Writer
# Matches the blog_posts table columns
ziyada_schema = {
    "type": "object",
    "required": ["title_ar", "title_en", "content_ar", "content_en", "excerpt_ar", "excerpt_en", "slug"],
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

# 1. Update 'search news topics' to use Webhook input if available
for node in wf['nodes']:
    if node['name'] == 'search news topics':
        node['parameters']['query'] = "={{ $json.body.topic || 'AI adoption for businesses' }}"

# 2. Add a Structured Output Parser for Ziyada Content Writer
parser_node = {
    "parameters": {
        "schemaType": "manual",
        "inputSchema": json.dumps(ziyada_schema)
    },
    "type": "@n8n/n8n-nodes-langchain.outputParserStructured",
    "typeVersion": 1.3,
    "position": [1988, 272],
    "id": "ziyada-parser-id",
    "name": "Ziyada Output Parser"
}
wf['nodes'].append(parser_node)

# 3. Connect the Parser to the Ziyada Content Writer
wf['connections']['Ziyada Output Parser'] = {
    "ai_outputParser": [[{"node": "ziyada content writer", "type": "ai_outputParser", "index": 0}]]
}

# 4. Enable Output Parser on Ziyada Content Writer
for node in wf['nodes']:
    if node['name'] == 'ziyada content writer':
        node['parameters']['hasOutputParser'] = True

# 5. Fix the Supabase Node ('Create a row')
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

# Output the modified JSON
print(json.dumps(wf))
