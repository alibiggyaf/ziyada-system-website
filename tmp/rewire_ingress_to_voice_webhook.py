#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

env = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/.env.local').read_text()
key = ''
for line in env.splitlines():
    if line.startswith('N8N_API_KEY='):
        key = line.split('=', 1)[1].strip().strip('"').strip("'")
        break

base = 'https://n8n.srv953562.hstgr.cloud'
headers = {'X-N8N-API-KEY': key, 'Content-Type': 'application/json'}

def api(method, path, payload=None):
    req = urllib.request.Request(base + path, method=method, headers=headers)
    if payload is not None:
        req.data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read().decode('utf-8', 'ignore')
        return json.loads(body) if body else {}

wid = 'qHAIKXEV4SW8r5Nx'
wf = api('GET', f'/api/v1/workflows/{wid}')

# Ensure normalize can consume either VAPI voice payload or generic webhook payload.
for node in wf['nodes']:
    if node.get('name') == 'Validate and Normalize Voice':
        node['parameters']['jsCode'] = (
            "const rawBody = $json.body || $json;\n"
            "const toolCallList = rawBody.message && rawBody.message.toolCallList ? rawBody.message.toolCallList : rawBody.toolCallList || null;\n"
            "if (toolCallList && toolCallList.length > 0) {\n"
            "  return [{ json: { _mode: 'tool_call', toolCallList } }];\n"
            "}\n"
            "const p = rawBody.voice || rawBody.event || rawBody;\n"
            "const transcript = String(p.transcript || p.content || (p.message && p.message.content) || rawBody.chatInput || rawBody.text || '').trim();\n"
            "if (!transcript) throw new Error('Missing transcript');\n"
            "const normalizedPhone = String(p.phone_e164 || p.phone || rawBody.phone_e164 || rawBody.phone || '').replace(/\\s+/g, '');\n"
            "const sessionId = p.session_id || rawBody.sessionId || rawBody.session_id || (normalizedPhone ? ('phone-' + normalizedPhone) : ('voice-' + Date.now()));\n"
            "const arabicRegex = /[\\u0600-\\u06ff]/g;\n"
            "const language = p.language || rawBody.language || (arabicRegex.test(transcript) ? 'ar' : 'en');\n"
            "return [{ json: { _mode: 'voice', session_id: sessionId, message_id: p.message_id || ('msg-' + Date.now()), event_ts: p.timestamp || rawBody.timestamp || new Date().toISOString(), transcript, language, provider: p.provider || 'vapi', phone_e164: normalizedPhone, call_id: p.call_id || rawBody.call_id || '' } }];\n"
        )

# Route voice path back to dedicated voice-agent webhook.
conn = wf.get('connections', {})
conn['Persist Transcript Supabase'] = {
    'main': [[{'node': 'Call AI Chat Webhook', 'type': 'main', 'index': 0}]]
}
wf['connections'] = conn

payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings') or {},
}

try:
    api('POST', f'/api/v1/workflows/{wid}/deactivate', {})
except Exception:
    pass
api('PUT', f'/api/v1/workflows/{wid}', payload)
api('POST', f'/api/v1/workflows/{wid}/activate', {})

wf2 = api('GET', f'/api/v1/workflows/{wid}')
print(json.dumps(wf2.get('connections', {}).get('Persist Transcript Supabase', {}), ensure_ascii=False))
