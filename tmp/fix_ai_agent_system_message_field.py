import json
import pathlib
import urllib.request
from dotenv import dotenv_values

WORKFLOW_PATH = pathlib.Path('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/n8n for ziyada system/workflow_ziyada_ai_chat_agent_FIXED.json')
WORKFLOW_ID = '4wO4enlPyFeNduqY'

# 1) Update local JSON file
with open(WORKFLOW_PATH, encoding='utf-8') as f:
    wf = json.load(f)

ai = next(n for n in wf['nodes'] if n.get('name') == 'Ziyada AI Agent')
params = ai.setdefault('parameters', {})
opts = params.setdefault('options', {})

system_message = params.get('systemMessage', '')
if not system_message:
    raise RuntimeError('No systemMessage found in parameters.systemMessage')

# Move system message into options where this node version expects it
opts['systemMessage'] = system_message
# Keep maxIterations intact (default 8 if absent)
opts['maxIterations'] = opts.get('maxIterations', 8)

# Remove misplaced root field to avoid confusion
params.pop('systemMessage', None)

# Keep prompt as pure user input
params['text'] = '={{ $json.chatInput }}'
params['promptType'] = 'define'

with open(WORKFLOW_PATH, 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Updated local JSON: moved systemMessage -> parameters.options.systemMessage')

# 2) Deploy same workflow ID (same webhook)
env = dotenv_values('/Users/djbiggy/Downloads/Claude Code- File Agents/.env.local')
api = (env.get('N8N_API_URL') or '').rstrip('/')
key = (env.get('N8N_API_KEY') or '').strip('"').strip("'")

payload = {
    'name': wf['name'],
    'nodes': wf.get('nodes', []),
    'connections': wf.get('connections', {}),
    'settings': wf.get('settings', {}),
}

req = urllib.request.Request(f"{api}/workflows/{WORKFLOW_ID}", method='PUT')
req.add_header('X-N8N-API-KEY', key)
req.add_header('Content-Type', 'application/json')
req.data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

with urllib.request.urlopen(req) as r:
    result = json.loads(r.read().decode('utf-8'))

print('Deployed workflow ID:', result.get('id'))

# 3) Verify live field placement
get_req = urllib.request.Request(f"{api}/workflows/{WORKFLOW_ID}")
get_req.add_header('X-N8N-API-KEY', key)
with urllib.request.urlopen(get_req) as r:
    live = json.loads(r.read().decode('utf-8'))

live_ai = next(n for n in live['nodes'] if n.get('name') == 'Ziyada AI Agent')
live_params = live_ai.get('parameters', {})
live_opts = live_params.get('options', {})

print('live options.systemMessage length:', len(str(live_opts.get('systemMessage', ''))))
print('live root systemMessage exists:', 'systemMessage' in live_params)
print('live text:', live_params.get('text'))
print('live webhook unchanged check expected id in chat trigger:')
chat = next(n for n in live['nodes'] if n.get('name') == 'Chat Trigger')
print('webhookId:', chat.get('webhookId'))
