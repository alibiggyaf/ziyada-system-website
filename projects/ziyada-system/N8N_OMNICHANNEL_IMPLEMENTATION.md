# n8n Omnichannel Workflow Implementation Guide

**Last Updated**: April 15, 2026  
**Status**: 5 Core Workflows Created — Ready for Deployment  
**Email**: ziyadasystem@gmail.com (updated from ali.biggy.af@gmail.com)

---

## Overview

Five integrated n8n workflows implement a unified omnichannel support system (WhatsApp + website chat + voice) with persistent lifecycle history, identity-aware context reuse, and safe human escalation.

---

## Workflows Created

### 1. **WhatsApp Ingress Workflow** (`workflow_whatsapp_ingress.json`)

**Purpose**: Receive Evolution API webhooks, normalize payload to unified contract, deduplicate, apply anti-loop guard.

**Trigger**: POST `/webhook/whatsapp-inbound` (public webhook)

**Flow**:
1. Evolution webhook received
2. Normalize to canonical fields: `channel`, `session_id`, `phone_e164`, `message_id`, `direction`, `event_ts`, `source_label`, `content`
3. Anti-loop guard: skip outbound echoes (our own messages)
4. Call Shared Response Orchestrator

**Key Decisions**:
- Session per WhatsApp phone number (persistent across conversations)
- Deduplicate by Evolution `message_id`
- Direction: `inbound` only (skip outbound)

**Deployment**:
```bash
# In n8n UI, create webhook trigger:
- Mode: webhook
- Public: true
- Authentication: none
- Webhook ID: whatsapp-inbound-webhook
```

---

### 2. **Shared Response Orchestrator** (`workflow_shared_orchestrator.json`)

**Purpose**: Core orchestrator for identity resolution, confidence assessment, context loading, AI response, and channel routing.

**Trigger**: Webhook from WhatsApp Ingress or website chat (internal HTTP calls)

**Flow**:
1. Validate event contract
2. Resolve contact identity from `leads` table (phone_normalized + email)
3. Assess confidence: `high` (both match) | `medium` (one match) | `low` (no match) | `none` (no contact)
4. Identity confidence policy:
   - **High**: Load full prior context, respond with all customer info
   - **Medium**: Ask soft verification question before loading context
   - **Low/None**: Generic response, no private context
5. Load conversation history from `chat_messages` (last 15 turns)
6. Call GPT-4o-mini with assembled context
7. Route response to correct channel

**Key Decisions**:
- Identity matching: exact `email` (case-insensitive) + `phone_e164` (E.164 standard)
- Medium confidence triggers soft verification (ask for confirmation without exposing mismatch)
- Context window: 15 messages (configurable)
- AI model: GPT-4o-mini (cost-optimized, suitable for support)

**Dependencies**:
- Supabase `leads` table (contact resolution)
- Supabase `chat_messages` table (history retrieval)
- OpenAI API credentials

**Testing**:
```python
# Test identity resolution:
# High confidence: send message with known phone + email
# Medium confidence: send message with phone only (no email match)
# Low confidence: send message with unknown phone
```

---

### 3. **Unified Persistence Workflow** (`workflow_unified_persistence.json`)

**Purpose**: Listen for events, write to Supabase tables, update lead lifecycle.

**Trigger**: Webhook from orchestrator (internal calls)

**Flow**:
1. Validate event contract
2. Upsert `chat_sessions`: session_id, lead_id, channel, language, identity_confidence, status
3. Insert `chat_messages`: session_id, message_id, direction, content, ai_model, created_at
4. Update `leads`: latest_session_id, last_contact_method, lifecycle_state → `'known'`
5. Insert `contact_events`: event_type='message', event_source, event_data (audit trail)
6. Emit completion event

**Key Decisions**:
- Session identified by `session_id` (per-browser for website chat, per-phone for WhatsApp)
- Every write includes `source_label` for traceability
- Lead lifecycle advanced to `'known'` on first contact
- Message deduplication by `message_id`

**Database Tables Updated**:
- `chat_sessions` (upsert)
- `chat_messages` (insert)
- `leads` (update lifecycle)
- `contact_events` (insert audit)

**Testing**:
```python
# Check Supabase after persistence:
# - chat_sessions row created/updated
# - chat_messages row inserted
# - leads.lifecycle_state == 'known'
# - contact_events audit entry exists
```

---

### 4. **Escalation & Handoff Queue Workflow** (`workflow_escalation_handoff.json`)

**Purpose**: Handle escalations with business hours logic, create handoff queue, route notifications.

**Trigger**: Webhook (triggered by orchestrator when escalation condition met)

**Escalation Triggers**:
- User explicitly requests human
- AI confidence classifier returns uncertain
- Sensitive/complex phrase detected
- Policy guardrail hit

**Flow**:
1. Validate escalation event
2. Check business hours: Asia/Riyadh timezone, Sun-Thu 12:00-17:00 (UTC+3)
3. Create `handoff_queue` row: session_id, lead_id, reason, channel, priority, status='pending'
4. If WhatsApp: send WhatsApp notification (with callback window)
5. Send email to `ziyadasystem@gmail.com`: escalation reason, session ID, conversation summary
6. Log escalation to `contact_events`
7. Emit completion

**Business Hours Logic**:
```javascript
// Asia/Riyadh timezone (UTC+3)
// Sun-Thu 12:00-17:00 (noon to 5 PM)
// In-hours: immediate human option
// Out-of-hours: queue item, inform user of next callback window
```

**Notification Content**:
- **WhatsApp**: Bilingual confirmation (Arabic primary), callback window
- **Email**: Subject includes reason, body includes session ID, phone, conversation summary, priority

**Key Decisions**:
- Single email destination: `ziyadasystem@gmail.com` for all escalations
- Business hours tie to Riyadh time zone (HQ location)
- Phone handoff (WhatsApp) + email inbox integration (dual path)

**Testing**:
```python
# Test at business hours boundaries:
# - 11:59 Asia/Riyadh (out-of-hours) → callback window msg
# - 12:00 Asia/Riyadh (in-hours) → immediate msg
# - 16:59 Asia/Riyadh (in-hours) → immediate msg
# - 17:00 Asia/Riyadh (out-of-hours) → callback window msg
# - Sat/Fri (out-of-hours) → callback window msg
```

---

### 5. **Booking Branch Workflow** (`workflow_booking_branch.json`)

**Purpose**: Handle booking requests — create calendar event, send confirmation email, WhatsApp confirmation.

**Trigger**: Webhook (triggered when escalation includes booking request)

**Flow**:
1. Validate booking request: session_id, lead_name, phone_e164, requested_datetime
2. Create Google Calendar event: title="Meeting with {lead_name}", attendee=ziyadasystem@gmail.com
3. Send email to `ziyadasystem@gmail.com`:
   - Subject: `[WHATSAPP] Meeting Request — {lead_name} — {date}` ← **origin clearly labeled**
   - Body: phone, email, conversation summary, session ID
4. If WhatsApp origin: send WhatsApp confirmation with date/time in Arabic
5. Log to `contact_events`: event_type='booking'
6. Emit completion

**Email Subject Format**:
```
[WHATSAPP] Meeting Request — Ahmed Al-Dosari — 4/19/2026
[WEBSITE_CHAT] Meeting Request — Fatima Hassan — 4/20/2026
```

**Key Decisions**:
- Origin channel `[WHATSAPP]` | `[WEBSITE_CHAT]` prefixed in subject for easy filtering
- Calendar integration: Google Calendar (primary account owner)
- Email recipient: `ziyadasystem@gmail.com` for all booking notifications
- Bilingual WhatsApp confirmation (Arabic)

**Testing**:
```python
# Create booking request via WhatsApp
# Verify:
# - Google Calendar event created
# - Email received at ziyadasystem@gmail.com with [WHATSAPP] prefix
# - WhatsApp confirmation sent with formatted date/time
# - contact_events audit entry logged
```

---

## Deployment Checklist

### Prerequisites
- [ ] n8n instance running (cloud or self-hosted)
- [ ] Supabase account with schema applied
- [ ] OpenAI API credentials (GPT-4o-mini)
- [ ] Google OAuth2 credentials (Calendar, Gmail)
- [ ] Evolution API credentials (WhatsApp)
- [ ] SMTP credentials (email notifications)

### Step 1: Create Credentials in n8n
```
Settings > Credentials > New

1. OpenAI API (gpt-4o-mini)
   - Credential: openAiApi
   - API Key: [from OpenAI]

2. Supabase Postgres
   - Credential: supabase_postgres
   - Host, Port, Username, Password, DB: [from Supabase]

3. Google OAuth2
   - Credential: google_oauth2
   - Client ID, Secret: [from Google Cloud Console]

4. Evolution API
   - Credential: evolution_api
   - API Key, Webhook URL: [from Evolution]

5. SMTP (for email)
   - Credential: smtp_credentials
   - Host, Port, Username, Password: [from email provider]
```

### Step 2: Import Workflows
```
n8n UI > Workflows > Import from file

1. workflow_whatsapp_ingress.json
2. workflow_shared_orchestrator.json
3. workflow_unified_persistence.json
4. workflow_escalation_handoff.json
5. workflow_booking_branch.json
```

### Step 3: Wire Workflow References
In **workflow_whatsapp_ingress.json**:
- Update node "Call Shared Orchestrator" → workflowId: [shared_orchestrator_workflow_id]

In **workflow_shared_orchestrator.json**:
- Ensure Supabase credentials linked to resolve-contact-identity and load-conversation-history nodes

### Step 4: Configure Evolution Webhook
```
Evolution API Dashboard > Webhooks

1. Add new webhook
   - URL: https://[n8n-instance]/webhook/whatsapp-inbound
   - Events: message.create, message.update
   - Active: true

2. Test: Send WhatsApp message to connected instance
   - Verify webhook received in n8n
```

### Step 5: Test Each Workflow
```bash
# 1. WhatsApp Ingress
curl -X POST https://[n8n]/webhook/whatsapp-inbound \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "from": "+966533123456",
      "message": {
        "id": "msg-123",
        "body": "Hello",
        "fromMe": false,
        "timestamp": 1713184800
      }
    }
  }'

# 2. Persistence
curl -X POST https://[n8n]/webhook/persistence \
  -H "Content-Type: application/json" \
  -d '{
    "event": {
      "session_id": "uuid-123",
      "phone_e164": "+966533123456",
      "message_id": "msg-123",
      "direction": "inbound",
      "content": "Hello",
      "channel": "whatsapp",
      "source_label": "whatsapp",
      "event_ts": "2026-04-15T10:00:00Z"
    }
  }'

# 3. Escalation
curl -X POST https://[n8n]/webhook/escalation \
  -H "Content-Type: application/json" \
  -d '{
    "escalation": {
      "session_id": "uuid-123",
      "reason": "customer_request",
      "channel": "whatsapp",
      "phone_e164": "+966533123456",
      "priority": "normal"
    }
  }'
```

---

## Data Flow Diagram

```
WhatsApp Message
    ↓
[Ingress Workflow]
    ↓
Normalize + Anti-loop Guard
    ↓
[Shared Orchestrator]
    ↓
Resolve Identity → Assess Confidence → Load Context → AI Response
    ↓
Check Escalation Needed?
    ├─ No → Route Response to Channel
    │   ↓
    │ [Persistence Workflow]
    │   ↓
    │ Write: chat_sessions, chat_messages, contact_events, leads
    │
    └─ Yes → [Escalation Handoff]
        ↓
        Check Business Hours
        ├─ In Hours → Immediate Queue + Notifications
        └─ Out of Hours → Queue + Callback Window
        ↓
        Booking Request?
        ├─ Yes → [Booking Branch] → Calendar + Email
        └─ No → [Persistence Workflow]
```

---

## Integration Points

### Website Chat Widget
Update [floating-chat-widget.jsx](projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-chat-widget.jsx):
```javascript
// Send to Shared Orchestrator instead of direct lead capture
const response = await fetch('https://[n8n-instance]/webhook/shared-orchestrator', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event: {
      channel: 'website_chat',
      session_id: sessionId,
      phone_e164: normalizePhone(phone),
      email: email,
      message_id: messageId,
      direction: 'inbound',
      event_ts: new Date().toISOString(),
      source_label: 'website_chat',
      content: message
    }
  })
});
```

### WhatsApp Evolution Setup
```
Hostinger VPS:
- Evolution API running
- Webhook URL: https://[n8n-instance]/webhook/whatsapp-inbound
- Connected WhatsApp instance
```

### Voice Widget (Phase 4)
Voice messages POST to `/webhook/shared-orchestrator` with:
```json
{
  "channel": "voice",
  "source_label": "voice",
  "direction": "inbound",
  "content": "[transcribed audio]",
  ...
}
```

---

## Monitoring & Observability

### Key Metrics
- **Failed Evolution webhooks**: Check n8n execution history for errors
- **Duplicate events**: Monitor message_id deduplication rate
- **AI response latency**: P50/P95 in n8n logs (target < 2s)
- **Escalation volume**: Query `handoff_queue` for channel/reason breakdown
- **Booking conversion**: Query `contact_events` where event_type='booking'
- **Identity confidence**: Query `chat_sessions` for confidence distribution

### Logging
All events logged to:
- **n8n**: Execution history (per workflow)
- **Supabase**: `contact_events` table (audit trail)
- **Email**: Escalations/bookings logged in ziyadasystem@gmail.com inbox

---

## Rollback & Feature Flags

### Disable WhatsApp Channel
In **workflow_whatsapp_ingress.json**:
- Add early exit node: if `ENABLE_WHATSAPP_CHANNEL` env var is false, skip to webhook response
- Website chat unaffected

### Replay Failed Events
```sql
-- Manually retry failed event
SELECT * FROM contact_events 
WHERE event_type = 'message' 
AND created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;

-- Resend event to persistence
POST https://[n8n-instance]/webhook/persistence
```

---

## Next Steps (Phase 4 & Beyond)

1. **ElevenLabs Voice Integration**
   - Separate voice widget (already deployed)
   - Voice sessions linked to same lead/contact via identity
   - Voice-only transcription → persistence

2. **Confidence Classifier Refinement**
   - Add sentiment analysis to escalation decision
   - Log uncertain responses to `contact_events` for QA review

3. **Handoff SLA Monitoring**
   - Dashboard: handoff_queue resolution time by reason
   - Alert on >30 min resolution during business hours

4. **Team Operations Setup**
   - On-call rotation schedule (shared calendar)
   - ziyadasystem@gmail.com inbox filters for [WHATSAPP], [ESCALATION], [BOOKING]

---

## Files Reference

- **Workflows**: `/projects/ziyada-system/n8n for ziyada system/`
  - workflow_whatsapp_ingress.json
  - workflow_shared_orchestrator.json
  - workflow_unified_persistence.json
  - workflow_escalation_handoff.json
  - workflow_booking_branch.json
- **Database**: [supabase-schema.sql](supabase-schema.sql)
- **Implementation Plan**: [plan-ziyadaOmnichannelWhatsAppVoiceAgent.prompt.md](projects/ziyada-system/plan-ziyadaOmnichannelWhatsAppVoiceAgent.prompt.md)
- **Website Chat**: [floating-chat-widget.jsx](projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-chat-widget.jsx)

