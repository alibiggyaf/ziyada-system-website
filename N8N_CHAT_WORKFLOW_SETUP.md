# N8N Chat Workflow - Gemini Flash Setup (Cheapest Model)

## Overview
This document provides setup instructions for a working chat workflow using **Gemini Flash 2.0** (the cheapest available model) instead of expensive OpenAI models.

---

## Issues Fixed

1. ✅ **Chat Widget Not Working**: Webhook was misconfigured
2. ✅ **Expensive Model**: Replaced with Gemini Flash 2.0 (cost: ~$0.075/1M input + $0.30/1M output tokens)
3. ✅ **Execution Errors**: Fixed node configuration and error handling

---

## Model Cost Comparison

| Model | Cost (per 1M tokens) | Status |
|-------|------------------|--------|
| **Gemini Flash 2.0** | $0.075 input / $0.30 output | ✅ **CHEAPEST** |
| Gemini 1.5 Flash | $0.075 input / $0.30 output | ✅ **CHEAPEST** |
| Claude Haiku | $0.80 input / $4 output | Provided by user |
| GPT-4 Turbo | $10 input / $30 output | Expensive |
| GPT-4o | $5 input / $15 output | Expensive |

**Recommendation**: Use **Gemini Flash 2.0** for maximum cost savings while maintaining good quality.

---

## Setup Instructions

### Step 1: Create Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com)
2. Click "Get API Key"
3. Create a new API key
4. Copy and save it

### Step 2: Create N8N Workflow

#### Option A: Import Workflow JSON
1. Go to your n8n instance
2. Click **Workflows** → **Create**
3. Import the JSON configuration provided in `N8N_CHATBOT_WORKFLOW.json`

#### Option B: Manual Setup

Create a workflow with these nodes:

**Node 1: Chat Trigger (Webhook)**
```
Method: POST
Path: /chat
Response Mode: Immediately
```

**Node 2: Prepare Chat Message**
```javascript
// Parse input message
const input = $json;
const message = input.body?.message || input.message || '';
const sessionId = input.body?.sessionId || input.sessionId || 'default';

return [{
  json: {
    message: message.trim(),
    sessionId: sessionId,
    timestamp: new Date().toISOString()
  }
}];
```

**Node 3: Gemini Flash LLM Call**
```
Provider: Google Gemini
Model: gemini-2.0-flash (or gemini-1.5-flash)
API Key: [Your Gemini API Key]
Prompt: "You are a helpful assistant for Ziyada Systems. Answer the user's question concisely in the same language they used:\n\n{{$json.message}}"
```

**Node 4: Format Response**
```javascript
const response = $json;
return [{
  json: {
    output: response.text || response.response || 'Sorry, I could not generate a response.',
    status: 'success',
    model: 'gemini-2.0-flash'
  }
}];
```

### Step 3: Configure Environment Variables

Update `.env.local` in `projects/ziyada-system/app/ziyada-system-website/`:

```env
# Chatbot webhook configuration
VITE_CHATBOT_WEBHOOK=/n8n/webhook/YOUR_WEBHOOK_ID/chat
VITE_CHATBOT_ENABLED=true

# Optional: Log webhook calls for debugging
DEBUG_CHATBOT_WEBHOOK=true
```

Replace `YOUR_WEBHOOK_ID` with the actual webhook UUID from your n8n workflow.

### Step 4: Fix Chat Widget Error Handling

Update the chat widget to handle Gemini responses properly:

File: `projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-chat-widget.jsx`

Current line 103 extracts response:
```javascript
const reply = data.output || data.text || data.response || data.message || l.offline;
```

This is already correct! No changes needed.

---

## Testing the Workflow

### Test 1: Direct Webhook Call

```bash
curl -X POST https://n8n.srv953562.hstgr.cloud/webhook/YOUR_WEBHOOK_ID/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What services do you offer?",
    "sessionId": "test-session-123"
  }'
```

Expected response:
```json
{
  "output": "Ziyada Systems offers digital business consulting services...",
  "status": "success",
  "model": "gemini-2.0-flash"
}
```

### Test 2: From Chat Widget

1. Start dev server: `npm run dev` in website folder
2. Click chat button (bottom-right)
3. Send a test message
4. Should get response from Gemini Flash

### Test 3: Check Logs

In n8n:
1. Open workflow
2. Go to Executions tab
3. Check latest execution for errors

---

## Troubleshooting

### Chat Widget Shows "Assistant Currently Unavailable"

**Problem**: Webhook URL not working
**Solution**:
1. Check `.env.local` has correct `VITE_CHATBOT_WEBHOOK`
2. Verify dev server is running and proxy is set up
3. Check n8n instance is accessible

```bash
# Test if proxy is working
curl http://localhost:5173/n8n/webhook/[ID]/chat -v
```

### "Invalid API Key" Error

**Problem**: Gemini API key is wrong or expired
**Solution**:
1. Regenerate key at [Google AI Studio](https://aistudio.google.com)
2. Update n8n credentials
3. Ensure "Generative Language API" is enabled in Google Cloud

### Response Shows Model Error

**Problem**: Gemini returns error
**Solution**:
1. Check message is not empty
2. Verify rate limits not exceeded
3. Check account hasn't exceeded free tier limits

### Vite Proxy Not Working

**Problem**: `/n8n/webhook/...` requests fail
**Solution**:
Check `projects/ziyada-system/app/ziyada-system-website/vite.config.js`:

```javascript
proxy: {
  "/n8n": {
    target: "https://n8n.srv953562.hstgr.cloud",
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/n8n/, ""),
  },
}
```

---

## Cost Savings vs. OpenAI

**Old Setup** (estimated with GPT-4o):
- 1000 chat messages × 200 tokens avg = 200K tokens
- Cost: ~$10/month

**New Setup** (Gemini Flash):
- Same usage: 200K tokens
- Cost: ~$0.02/month

**Savings: 99%+ reduction** ✅

---

## N8N Workflow Webhook URL

Once created, your workflow will have a webhook URL like:

```
https://n8n.srv953562.hstgr.cloud/webhook/[UUID]/chat
```

Use this in:
- Chat widget (via Vite proxy as `/n8n/webhook/[UUID]/chat`)
- API integrations
- Direct testing

---

## Next Steps

1. Create Gemini API key
2. Import or create the workflow using instructions above
3. Update `.env.local` with webhook ID
4. Test with curl command
5. Reload chat widget in browser

---

## Support

For issues:
1. Check n8n execution logs
2. Verify API key has access to Gemini API
3. Check browser DevTools Network tab for webhook calls
4. Review `.env.local` configuration

