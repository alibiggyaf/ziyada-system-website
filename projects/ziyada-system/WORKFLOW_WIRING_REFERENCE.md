# Workflow Wiring Reference

**Quick lookup for connecting n8n workflows**

## Workflow Files Created

| Workflow | File | Trigger | Purpose |
|---|---|---|---|
| **WhatsApp Ingress** | `workflow_whatsapp_ingress.json` | Evolution Webhook POST `/webhook/whatsapp-inbound` | Receive WhatsApp messages, normalize, anti-loop guard |
| **Shared Orchestrator** | `workflow_shared_orchestrator.json` | HTTP Webhook (internal) | Identity resolution, confidence assessment, AI response |
| **Unified Persistence** | `workflow_unified_persistence.json` | HTTP Webhook (internal) | Write to Supabase (sessions, messages, events, leads) |
| **Escalation Handoff** | `workflow_escalation_handoff.json` | HTTP Webhook (internal) | Business hours gate, create queue, send notifications |
| **Booking Branch** | `workflow_booking_branch.json` | HTTP Webhook (internal) | Create Google Calendar event, send confirmation emails |

---

## Connection Map

```
Evolution API WhatsApp Message
    ↓
[WhatsApp Ingress Workflow]
    ├─ Normalize payload to canonical contract
    ├─ Apply anti-loop guard
    └─ POST to Shared Orchestrator
    ↓
[Shared Orchestrator Workflow]
    ├─ Query Supabase leads table
    ├─ Assess identity confidence
    ├─ Load conversation history
    ├─ Call GPT-4o-mini
    ├─ Check if escalation needed
    │  ├─ NO: Route response
    │  │    └─ POST to Unified Persistence
    │  │
    │  └─ YES: Determine escalation type
    │       ├─ Standard escalation
    │       │  └─ POST to Escalation Handoff
    │       │
    │       └─ Booking request
    │           └─ POST to Booking Branch
    │
    ↓
[Unified Persistence Workflow]
    ├─ Insert chat_sessions row
    ├─ Insert chat_messages row
    ├─ Update leads lifecycle
    └─ Insert contact_events audit
    ↓
[Escalation Handoff Workflow]
    ├─ Check business hours (Asia/Riyadh)
    ├─ Insert handoff_queue row
    ├─ Send WhatsApp notification
    ├─ Send email to ziyadasystem@gmail.com
    └─ Insert contact_events audit
    ↓
[Booking Branch Workflow]
    ├─ Create Google Calendar event
    ├─ Send email to ziyadasystem@gmail.com (with [WHATSAPP] tag)
    ├─ Send WhatsApp confirmation
    └─ Insert contact_events audit
```

---

## Deployment Wiring Steps

### 1. Import All 5 Workflows into n8n
```
n8n UI > Workflows > Import from file
1. workflow_whatsapp_ingress.json
2. workflow_shared_orchestrator.json
3. workflow_unified_persistence.json
4. workflow_escalation_handoff.json
5. workflow_booking_branch.json
```

Note workflow IDs after import (you'll need these).

### 2. Update Workflow References in WhatsApp Ingress

**In `workflow_whatsapp_ingress.json`:**
- Find node: "Call Shared Orchestrator"
- Update `workflowId` field to match deployed Shared Orchestrator workflow ID

```json
{
  "id": "call-orchestrator",
  "name": "Call Shared Orchestrator",
  "type": "n8n-nodes-base.executeWorkflow",
  "parameters": {
    "workflowId": "YOUR_ORCHESTRATOR_WORKFLOW_ID_HERE"
  }
}
```

### 3. Link Shared Orchestrator to Downstream Workflows

**In `workflow_shared_orchestrator.json`:**

After the AI response node, add conditional branching:
- If escalation needed: POST to Escalation Handoff webhook
- If booking: POST to Booking Branch webhook  
- Otherwise: POST to Unified Persistence webhook

**Each HTTP call would look like:**
```json
{
  "node": "HTTP Request",
  "parameters": {
    "url": "https://[n8n-instance]/webhook/persistence",
    "method": "POST",
    "bodyParametersJson": {
      "event": "$json full event object"
    }
  }
}
```

### 4. Register Credentials in n8n

```
n8n UI > Settings > Credentials > New
```

| Credential | Type | Uses | Required Fields |
|---|---|---|---|
| `openAiApi` | OpenAI | Shared Orchestrator (AI model) | API Key |
| `supabase_postgres` | Postgres | Shared Orchestrator (identity query), Persistence, Escalation | Host, Port, Username, Password, Database |
| `google_oauth2` | Google OAuth2 | Booking Branch (Calendar, Gmail) | Client ID, Client Secret |
| `evolution_api` | HTTP | Escalation, Booking (WhatsApp send) | API Key, Instance URL |
| `smtp_credentials` | SMTP | Escalation, Booking (email send) | Host, Port, Username, Password |

### 5. Configure Evolution Webhook

**In Evolution API Dashboard:**
```
Webhooks > Add New

URL: https://[n8n-instance-domain]/webhook/whatsapp-inbound
Method: POST
Events: 
  - message.create
  - message.update
Headers: (if required by your n8n setup)
  - Authorization: Bearer [API_KEY]
Active: true
```

### 6. Test WhatsApp Flow End-to-End

```bash
# Option A: Send actual WhatsApp message through Evolution
# Message should trigger webhook → ingress → orchestrator → persistence

# Option B: Manually trigger Ingress workflow webhook
curl -X POST https://[n8n-instance]/webhook/whatsapp-inbound \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "from": "+966533123456",
      "message": {
        "id": "msg-test-001",
        "body": "Hello Ziyada System",
        "fromMe": false,
        "timestamp": '$(date +%s)'
      }
    }
  }'

# Verify in n8n:
# - Ingress execution completed successfully
# - Shared Orchestrator called
# - Persistence called
# - Check Supabase: chat_sessions, chat_messages rows created
```

---

## Webhook URLs After Deployment

Once all workflows deployed, you'll have these active webhook endpoints:

| Workflow | Webhook URL | Auth | Public |
|---|---|---|---|
| WhatsApp Ingress | `/webhook/whatsapp-inbound` | none | ✅ Yes (Evolution API calls this) |
| Shared Orchestrator | `/webhook/shared-orchestrator` | none | ❌ Internal (called by ingress) |
| Unified Persistence | `/webhook/persistence` | none | ❌ Internal (called by orchestrator) |
| Escalation Handoff | `/webhook/escalation` | none | ❌ Internal (called by orchestrator) |
| Booking Branch | `/webhook/booking` | none | ❌ Internal (called by orchestrator) |

---

## Website Chat Widget Integration

Update [floating-chat-widget.jsx](projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-chat-widget.jsx):

**Old**: Posts to individual lead capture workflow  
**New**: Post directly to Shared Orchestrator webhook

```javascript
// OLD (before):
const response = await fetch('https://[n8n]/webhook/chat-lead-capture', {
  // ...
});

// NEW (after):
const response = await fetch('https://[n8n]/webhook/shared-orchestrator', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event: {
      channel: 'website_chat',
      session_id: sessionId,
      phone_e164: phoneE164,
      email: email,
      message_id: uuid(),
      direction: 'inbound',
      event_ts: new Date().toISOString(),
      source_label: 'website_chat',
      content: message
    }
  })
});
```

---

## Credential IDs Reference

When you create credentials in n8n, note their credential IDs:

```json
{
  "credentials": {
    "openAiApi": {
      "id": "YOUR_OPENAI_CRED_ID",
      "name": "OpenAI API"
    },
    "supabase_postgres": {
      "id": "YOUR_SUPABASE_CRED_ID",
      "name": "Supabase Postgres"
    },
    "google_oauth2": {
      "id": "YOUR_GOOGLE_CRED_ID",
      "name": "Google OAuth2"
    },
    "evolution_api": {
      "id": "YOUR_EVOLUTION_CRED_ID",
      "name": "Evolution API"
    },
    "smtp_credentials": {
      "id": "YOUR_SMTP_CRED_ID",
      "name": "SMTP"
    }
  }
}
```

Update credential IDs in each workflow's nodes that reference them.

---

## Deployment Validation Checklist

- [ ] All 5 workflows imported into n8n
- [ ] Workflow IDs captured (WhatsApp Ingress → Orchestrator reference updated)
- [ ] All credentials created and tested
- [ ] Evolution webhook registered and verified
- [ ] Website chat widget code updated (if deploying website integration phase)
- [ ] Test WhatsApp message sent through Evolution → n8n flow
- [ ] Check Supabase tables populated with test data
- [ ] Email notifications received at ziyadasystem@gmail.com
- [ ] Google Calendar event created for booking request
- [ ] WhatsApp confirmation message received

---

## Troubleshooting Reference

| Issue | Cause | Solution |
|---|---|---|
| WhatsApp webhook not triggering | Evolution webhook URL wrong | Verify URL in Evolution dashboard matches n8n webhook URL |
| `ORCHESTRATOR_WORKFLOW_ID` not found | Workflow ID not updated in ingress | Update executeWorkflow node with correct workflow ID |
| Supabase queries failing | Credentials misconfigured | Test Supabase credential in n8n with simple SELECT query |
| Email not sent | SMTP credentials wrong | Verify SMTP host, port, username, password |
| Google Calendar event not created | OAuth2 token expired | Re-authenticate Google OAuth2 credential |
| Identity confidence always "none" | leads table empty | Insert test lead rows into Supabase first |

---

## File Locations (Quick Reference)

```
projects/ziyada-system/
├── n8n for ziyada system/
│   ├── workflow_whatsapp_ingress.json ← START HERE
│   ├── workflow_shared_orchestrator.json
│   ├── workflow_unified_persistence.json
│   ├── workflow_escalation_handoff.json
│   └── workflow_booking_branch.json
├── app/ziyada-system-website/
│   └── src/components/ui/
│       └── floating-chat-widget.jsx ← UPDATE THIS (website integration)
└── plan-ziyadaOmnichannelWhatsAppVoiceAgent.prompt.md

supabase-schema.sql ← CREATE TABLES (if not already applied)
N8N_OMNICHANNEL_IMPLEMENTATION.md ← FULL DEPLOYMENT GUIDE
```

