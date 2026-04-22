# Ziyada System Backend Webhook Guide (AR/EN)

Last updated: 2026-04-19
Scope: Website backend routing through n8n webhooks (no API keys in this document)

---

## العربية

### 1) كيف الباكند يشتغل باختصار

واجهة الموقع (Frontend) ترسل طلبات POST إلى Webhook داخل n8n.
كل Workflow في n8n يبدأ من Trigger node (Chat Trigger أو Webhook).

المبدأ:
- Frontend env var -> Webhook path -> n8n workflow trigger -> response يعود للواجهة.

---

### 2) Webhookات الأساسية المستخدمة

1. Chat Widget
- Env var: VITE_CHATBOT_WEBHOOK
- Path: /webhook/0f30c293-c375-45a2-9cf6-d55208de387b
- Workflow URL:
  https://n8n.srv953562.hstgr.cloud/workflow/Y6WTad9ORgiyYEmc
- Workflow name:
  Ziyada AI Chat Agent —  Chat widget.

2. Niche Signal Intelligence (YouTube/NSI)
- Env var: VITE_N8N_NSI_WEBHOOK
- Path: /webhook/ff9622a4-a6ec-4396-b9de-c95bd834c23c/chat
- Workflow URL:
  https://n8n.srv953562.hstgr.cloud/workflow/62MN6oqxOs3levjh
- Workflow name:
  Niche Signal Intelligence Workflow

3. Voice
- Env var (preferred): VITE_VOICE_AGENT_WEBHOOK
- Fallback in UI: VITE_CHATBOT_WEBHOOK
- Current voice workflow URL:
  https://n8n.srv953562.hstgr.cloud/workflow/qHAIKXEV4SW8r5Nx
- Workflow name:
  Ziyada system voice chat

---

### 3) شرح سؤال: ليش أشوف Chat Trigger فقط؟

هذا طبيعي.
بعض Workflows تعتمد فقط على Chat Trigger كبوابة دخول.
إذا ما فيه HTTP Request nodes إضافية، فهذا يعني الرد يرجع مباشرة للمستخدم من نفس workflow.

---

### 4) Workflows الظاهرة كـ Active: هل كلها مستخدمة من الموقع؟

ليست كلها بالضرورة مستخدمة مباشرة من الواجهة.

Used now (confirmed from frontend routing):
- Y6WTad9ORgiyYEmc (chat via VITE_CHATBOT_WEBHOOK)
- 62MN6oqxOs3levjh (NSI via VITE_N8N_NSI_WEBHOOK)

Potentially used depending on env:
- qHAIKXEV4SW8r5Nx (voice, if VITE_VOICE_AGENT_WEBHOOK configured)

Not a direct website entry trigger:
- ImrkLJa5mO7TvJmk (Chat Lead Capture — Supabase + HubSpot) has no public webhook trigger; used as processing flow.

Legacy/inactive candidate:
- eO6LzcPrnPT3JlpA (Gemini Flash) should stay inactive unless intentionally re-enabled.

---

### 5) Safe cleanup policy before delete

1. Deactivate candidate workflow first (do not delete immediately).
2. Keep 24h monitoring window.
3. Validate website chat + voice + NSI dashboard.
4. If no regressions, then delete.
5. Keep exported JSON backup before final delete.

---

## English

### 1) Backend flow in one view

The website frontend sends POST requests to n8n webhooks.
Each n8n workflow starts from a trigger node (Chat Trigger or Webhook).

Pattern:
- Frontend env var -> webhook path -> n8n trigger -> response back to frontend.

---

### 2) Primary webhooks currently mapped

1. Chat Widget
- Env var: VITE_CHATBOT_WEBHOOK
- Path: /webhook/0f30c293-c375-45a2-9cf6-d55208de387b
- Workflow URL:
  https://n8n.srv953562.hstgr.cloud/workflow/Y6WTad9ORgiyYEmc
- Workflow name:
  Ziyada AI Chat Agent —  Chat widget.

2. Niche Signal Intelligence (YouTube/NSI)
- Env var: VITE_N8N_NSI_WEBHOOK
- Path: /webhook/ff9622a4-a6ec-4396-b9de-c95bd834c23c/chat
- Workflow URL:
  https://n8n.srv953562.hstgr.cloud/workflow/62MN6oqxOs3levjh
- Workflow name:
  Niche Signal Intelligence Workflow

3. Voice
- Env var (preferred): VITE_VOICE_AGENT_WEBHOOK
- UI fallback: VITE_CHATBOT_WEBHOOK
- Current voice workflow URL:
  https://n8n.srv953562.hstgr.cloud/workflow/qHAIKXEV4SW8r5Nx
- Workflow name:
  Ziyada system voice chat

---

### 3) Why you may only see a Chat Trigger

That is expected.
Some workflows are intentionally trigger-first and return directly from internal nodes.
If no extra HTTP Request nodes are present, the workflow still works as an input->process->reply chain.

---

### 4) Are all active chat workflows used by the deployed website?

Not always.

Confirmed website-entry workflows:
- Y6WTad9ORgiyYEmc (chat)
- 62MN6oqxOs3levjh (NSI)

Conditionally used:
- qHAIKXEV4SW8r5Nx (voice, depends on VITE_VOICE_AGENT_WEBHOOK)

Not a direct public website trigger:
- ImrkLJa5mO7TvJmk (processing/capture workflow)

Legacy/inactive candidate:
- eO6LzcPrnPT3JlpA

---

### 5) Deletion safety checklist

1. Deactivate first.
2. Observe for 24 hours.
3. Test chat, voice, NSI dashboard.
4. Delete only after stable verification.
5. Keep JSON export backup.
