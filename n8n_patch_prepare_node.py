#!/usr/bin/env python3
import json, urllib.request, urllib.error

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_URL = "https://n8n.srv953562.hstgr.cloud/api/v1"
WF_ID = "C8JWsE3KIoxr1KgO"

HEADERS = {
    "X-N8N-API-KEY": N8N_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json",
}

def api(method, path, body=None):
    url = f"{N8N_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"message": raw}
        return e.code, parsed

new_js = """const input = $json || {};
const raw = (input.body && typeof input.body === 'object') ? input.body : input;

const telegramText = String(raw.message?.text || raw.edited_message?.text || raw.text || '').trim();
const telegramChatId = raw.message?.chat?.id || raw.edited_message?.chat?.id || raw.chat?.id || input.telegram_chat_id || '';
const isTelegram = Object.prototype.hasOwnProperty.call(raw, 'update_id') || !!telegramChatId;

const now = new Date();
const pad = (n) => String(n).padStart(2, '0');
const generatedRequestId = `REQ-${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}-${Math.random().toString(36).slice(2,6).toUpperCase()}`;

const requestId = String(raw.request_id || input.request_id || raw.id || generatedRequestId).trim();
const companyName = String(raw.company_name || raw.company || input.company_name || '').trim();
const industry = String(raw.industry || input.industry || '').trim();
const targetAudience = String(raw.target_audience || raw.audience || input.target_audience || '').trim();
const companyLink = String(raw.company_link || raw.website || raw.url || input.company_link || '').trim();
const writerTask = String(raw.writer_task || raw.prompt || input.writer_task || input.prompt || '').trim();

const statusSource = raw.trigger_status || raw['trigger status'] || raw.send_status || raw['send status'] || raw.workflow_status || raw.status || input.trigger_status || input.send_status || 'start';
const triggerStatus = String(statusSource || 'start').trim().toLowerCase() || 'start';
const sentStatus = String(raw.sent_status || raw['sent status'] || input.sent_status || 'pending').trim().toLowerCase() || 'pending';

const source = isTelegram ? 'telegram' : (input.source || 'sheet_intake');
const approvalStatus = String(raw.approval_status || input.approval_status || 'approved').trim() || 'approved';

const topicFromTelegram = telegramText.replace(/^\/(start|blog|write)\b/i, '').trim();
const topic = String(raw.topic || raw.title_ar || raw.title_en || input.topic || topicFromTelegram || writerTask || companyName || 'موضوع جديد').trim();

const systemPrompt = String((input.content_writer && input.content_writer.system_prompt) || raw.system_prompt || '').trim();
const userPrompt = writerTask || `اكتب محتوى تسويقي احترافي باللغة العربية عن ${companyName || 'الشركة'}.\nالقطاع: ${industry || 'غير محدد'}\nالجمهور المستهدف: ${targetAudience || 'غير محدد'}\nالرابط: ${companyLink || 'غير متوفر'}\nالموضوع: ${topic}.`;

const intake = {
  request_id: requestId,
  row_number: raw.row_number || raw.rowNumber || input.row_number || '',
  created_at: raw.created_at || raw['created at'] || input.created_at || '',
  company_name: companyName,
  industry,
  target_audience: targetAudience,
  company_link: companyLink,
  writer_task: writerTask,
};

const out = {
  ...input,
  secret: String(raw.secret || input.secret || 'ziyada-n8n-2026'),
  request_id: requestId,
  topic,
  intake,
  post: {
    topic,
    language: 'ar-SA',
  },
  content_writer: {
    system_prompt: systemPrompt,
    user_prompt: userPrompt,
    language: 'ar-SA',
    prompt_version: 'intake-company-tone-v2026-03-20',
  },
  company_name: companyName,
  industry,
  target_audience: targetAudience,
  company_link: companyLink,
  writer_task: writerTask,
  trigger_status: triggerStatus,
  sent_status: sentStatus,
  source,
  approval_status: approvalStatus,
  telegram_chat_id: telegramChatId,
  request_email_draft: Boolean(raw.request_email_draft || input.request_email_draft),
  budget_mode: String(raw.budget_mode || input.budget_mode || 'balanced'),
    generation_ready_flag: 1,
    interview_state: {
        missing_fields: [],
        next_question: '',
        prompt: ''
    },
};

return [{ json: out }];
"""

# Load workflow
st, wf = api("GET", f"/workflows/{WF_ID}")
if st != 200:
    print(f"Failed to load workflow: {st} {wf}")
    raise SystemExit(1)

changed = False
for node in wf.get("nodes", []):
    if node.get("name") == "Prepare Content Writer Input":
        node.setdefault("parameters", {})["jsCode"] = new_js
        changed = True
        break

if not changed:
    print("Prepare Content Writer Input node not found")
    raise SystemExit(1)

# Save workflow with minimal allowed payload
payload = {
    "name": wf.get("name", "Ali Content Writer Engine 2026"),
    "settings": wf.get("settings", {}),
    "nodes": wf.get("nodes", []),
    "connections": wf.get("connections", {}),
}

st2, out = api("PUT", f"/workflows/{WF_ID}", payload)
print(f"PUT status: {st2}")
if st2 != 200:
    print(out)
    raise SystemExit(1)

print("Patched Prepare Content Writer Input successfully")
