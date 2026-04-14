# N8N Chat Workflow — Supabase Memory & Logging Setup

## What This Does
- **Logs every message** (user + assistant) to Supabase `chat_messages`
- **AI has memory** — on each new message, the workflow fetches the last 10 messages
  for that session and includes them as conversation history for the LLM
- **Admin can see all conversations** at `/admin/chat`

---

## Step 1 — Add Supabase Credentials in N8N

1. Go to N8N → Credentials → New
2. Choose **Supabase**
3. Fill in:
   - **Host**: `https://nuyscajjlhxviuyrxzyq.supabase.co`
   - **Service Role Key**: your `service_role` key from Supabase → Settings → API
4. Save as `supabase-ziyada`

---

## Step 2 — Update Your Chat Workflow

Open your existing chat workflow. The current flow is:

```
Webhook → Prepare Message → Gemini LLM → Format Response → Respond to Webhook
```

Replace it with this new flow:

```
Webhook
  ↓
Prepare Message (Code)
  ↓
Fetch Chat History (Supabase)
  ↓
Save User Message (Supabase)
  ↓
Gemini LLM (with history)
  ↓
Save Assistant Message (Supabase)
  ↓
Format Response (Code)
  ↓
Respond to Webhook
```

---

## Step 3 — Node Configurations

### Node: "Fetch Chat History" (Supabase node)
- **Operation**: Get Many
- **Table**: `chat_messages`
- **Filter**: `session_id = {{ $json.sessionId }}`
- **Sort**: `created_at` ascending
- **Limit**: 10

### Node: "Save User Message" (Supabase node)
- **Operation**: Create
- **Table**: `chat_messages`
- **Fields**:
  ```json
  {
    "session_id": "{{ $('Prepare Message').item.json.sessionId }}",
    "role": "user",
    "content": "{{ $('Prepare Message').item.json.chatInput }}"
  }
  ```

### Node: "Save Assistant Message" (Supabase node)
- **Operation**: Create
- **Table**: `chat_messages`
- **Fields**:
  ```json
  {
    "session_id": "{{ $('Prepare Message').item.json.sessionId }}",
    "role": "assistant",
    "content": "{{ $json.text }}"
  }
  ```
  *(adjust `$json.text` to match your Gemini node's output field)*

---

## Step 4 — Update "Prepare Message" Code Node

Replace your current code with:

```javascript
const body = $input.first().json.body || $input.first().json;

const chatInput = body.chatInput || body.message || body.text || '';
const sessionId = body.sessionId || 'unknown';
const action = body.action || 'sendMessage';

return [{
  json: {
    chatInput,
    sessionId,
    action,
  }
}];
```

---

## Step 5 — Update Gemini LLM Node to Use History

In the Gemini (or OpenAI) node, change the **Messages** input to include history.

Add a **Code** node before the LLM called "Build Messages with History":

```javascript
const userMessage = $('Prepare Message').item.json.chatInput;
const history = $('Fetch Chat History').all();

// Build conversation history array
const messages = history.map(item => ({
  role: item.json.role,      // 'user' or 'assistant'
  content: item.json.content
}));

// Add the new user message
messages.push({ role: 'user', content: userMessage });

return [{ json: { messages, userMessage } }];
```

Then in your LLM node, set **Messages** to `{{ $json.messages }}` (array input mode).

**System Prompt** (add to your LLM node):
```
أنت مساعد زيادة سيستم الذكي. تساعد أصحاب الأعمال السعوديين على تحسين أعمالهم بالحلول الرقمية.
شركة زيادة سيستم متخصصة في: أتمتة الأعمال، CRM، توليد العملاء المحتملين، التسويق الرقمي، تطوير المواقع.
أجب بالعربية السعودية، بأسلوب ودي ومهني. إذا أراد العميل حجز استشارة، وجّهه إلى: https://ziyadasystem.com/BookMeeting
---
You are the Ziyada Systems AI assistant. Answer in the same language as the user (Arabic or English).
```

---

## Step 6 — Test

1. Open your website chat widget
2. Send a message
3. Send a second message — the AI should remember the first one
4. Go to `/admin/chat` in your admin panel
5. You should see the session and both messages logged

---

## How the session_id works

The chat widget already sends a `sessionId` with every request (stored in `sessionStorage`).
The N8N workflow uses this to group messages by conversation.
The Supabase trigger automatically creates/updates the `chat_sessions` row.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Messages not saving | Check Supabase service role key in N8N credentials |
| History not loading | Make sure "Fetch Chat History" runs before LLM node |
| AI not remembering | Check "Build Messages with History" output includes all turns |
| `session_id` is null | Confirm widget sends `sessionId` field (it does by default) |
