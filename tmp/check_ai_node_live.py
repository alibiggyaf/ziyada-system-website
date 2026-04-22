import json
import urllib.request
from dotenv import dotenv_values

env = dotenv_values('.env.local')
api = (env.get('N8N_API_URL') or '').rstrip('/')
key = (env.get('N8N_API_KEY') or '').strip('"').strip("'")
wid = '4wO4enlPyFeNduqY'

req = urllib.request.Request(f"{api}/workflows/{wid}")
req.add_header('X-N8N-API-KEY', key)

with urllib.request.urlopen(req) as r:
    wf = json.loads(r.read().decode('utf-8'))

ai = next(n for n in wf['nodes'] if n.get('name') == 'Ziyada AI Agent')
p = ai.get('parameters', {})
sm = p.get('systemMessage')
print('promptType:', p.get('promptType'))
print('text:', p.get('text'))
print('systemMessage exists:', sm is not None)
print('systemMessage length:', 0 if sm is None else len(str(sm)))
print('systemMessage empty:', sm is None or str(sm).strip() == '')
