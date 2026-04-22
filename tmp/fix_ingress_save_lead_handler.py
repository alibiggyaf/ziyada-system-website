#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

env = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/.env.local').read_text()
n8n_key = ''
for line in env.splitlines():
    if line.startswith('N8N_API_KEY='):
        n8n_key = line.split('=', 1)[1].strip().strip('"').strip("'")
        break

base = 'https://n8n.srv953562.hstgr.cloud'
wid = 'qHAIKXEV4SW8r5Nx'
headers = {'X-N8N-API-KEY': n8n_key, 'Content-Type': 'application/json'}
old = """    } else if (fn === 'save_lead') {\n      await sbPost('/rest/v1/voice_assistant_leads', { name: args.name||'', phone: args.phone||'', email: args.email||'', service_interest: args.service_interest||'', source: 'voice_assistant', created_at: new Date().toISOString() });\n      result = 'تم تسجيل بياناتك يا ' + (args.name||'أخوي') + '. سيتواصل معك الفريق قريباً إن شاء الله.';\n"""
new = """    } else if (fn === 'save_lead') {\n      await sbPost('/rest/v1/leads', { name: args.name||'', email: args.email||'', phone: args.phone||callerPhone||'', company: args.company||'', industry: args.sector||args.industry||'', challenge: args.challenge||'', services_requested: args.service_interest||'', source: 'voice_assistant', language: 'ar', status: 'new' });\n      result = 'تم تسجيل بياناتك يا ' + (args.name||'أخوي') + '. سيتواصل معك الفريق قريباً إن شاء الله.';\n"""

def api(method, path, payload=None):
    req = urllib.request.Request(base + path, method=method, headers=headers)
    if payload is not None:
        req.data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read().decode('utf-8', 'ignore')
        return json.loads(body) if body else {}

wf = api('GET', f'/api/v1/workflows/{wid}')
for node in wf['nodes']:
    if node.get('name') == 'Handle Tool Calls':
        code = node.get('parameters', {}).get('jsCode', '')
        if old not in code:
            raise SystemExit('save_lead block not found in live code')
        node['parameters']['jsCode'] = code.replace(old, new)
        break
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
for node in wf2['nodes']:
    if node.get('name') == 'Handle Tool Calls':
        code = node.get('parameters', {}).get('jsCode', '')
        print('/rest/v1/leads' in code, '/rest/v1/voice_assistant_leads' in code)
        break
