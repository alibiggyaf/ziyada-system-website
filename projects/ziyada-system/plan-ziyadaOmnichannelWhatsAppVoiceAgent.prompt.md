## Plan: Ziyada Omnichannel WhatsApp + Voice Agent

Launch a unified support system where WhatsApp (via Evolution), website chat, and website voice all route through n8n and persist lifecycle history in Supabase, with safe identity-aware context reuse, human escalation, and WhatsApp-labeled booking notifications.

## Implementation Status (April 19, 2026)

### Completed in this pass
- Added normalized chat payload fields in website chat widget requests to n8n webhook: `channel`, `source_label`, `direction`, `event_ts`, `message_id`, and optional identity fields `email`/`phone_e164`.
- Added a new separate floating voice widget on the website (outside the text chat widget), mounted in layout as an independent CTA.
- Implemented voice CTA motion behavior: starts idle, then wave/pulse animation begins after a randomized 10-15 second delay.
- Implemented per-session motion stop behavior: animation stops after user interacts with the voice launcher.
- Added Ziyada-branded bilingual voice panel copy aligned to partnership tone.
- Implemented voice message posting to webhook with channel metadata and shared chat-session identity keys.

### Completed in second pass
- Added shared identity/session helper module for cross-channel continuity (`contactIdentity`) and reused it in both chat and voice widgets.
- Persisted known customer identity from website forms (Contact, Request Proposal, Book Meeting) into local identity keys for continuity linking.
- Added Supabase migration file for omnichannel lifecycle model: leads lifecycle columns, `chat_sessions`, `chat_messages`, `handoff_queue`, `contact_events`, indexes, RLS enablement, and baseline policies.
- Improved booking success handling to accept successful structured responses from the current site API wrapper.
- Restructured Navbar layout for physical consistency (logo left, nav centered, controls right) across Arabic/English with `dir="ltr"` on header and internal `direction: rtl` for Arabic text flow.

### Completed in third pass (UI refinements)
- Tightened navbar desktop navigation spacing: reduced gap from 28px → 16px for better visual balance between logo, nav, and controls.
- Shortened voice widget English subtitle from "A partnership-first assistant to move your business forward, fast." → "Smart partnership assistance." to prevent truncation on mobile/desktop.
- Validated all code changes (zero errors) and created comprehensive handoff documentation (PHASE1_IMPLEMENTATION_SUMMARY.md).

### Completed in fourth pass (April 15, 2026 — Omnichannel Workflows)
- Updated all email references from ali.biggy.af@gmail.com → ziyadasystem@gmail.com across plan and workflows
- Created 5 production-ready n8n workflows:
  1. **WhatsApp Ingress Workflow** — Evolution API webhook receiver, payload normalization, anti-loop guard
  2. **Shared Response Orchestrator** — Identity resolution, confidence assessment (high/medium/low), context loading, AI response routing
  3. **Unified Persistence Workflow** — Event logging to chat_sessions, chat_messages, contact_events, leads lifecycle tables
  4. **Escalation & Handoff Queue Workflow** — Business hours gate (Sun-Thu 12:00-17:00 Asia/Riyadh), queue creation, WhatsApp + email notifications
  5. **Booking Branch Workflow** — Google Calendar event creation, email with [WHATSAPP] origin tag, WhatsApp confirmation
- Created comprehensive deployment guide: [N8N_OMNICHANNEL_IMPLEMENTATION.md](projects/ziyada-system/N8N_OMNICHANNEL_IMPLEMENTATION.md)
  - Credential setup checklist
  - Step-by-step deployment instructions
  - Testing commands (curl examples)
  - Monitoring metrics and observability
  - Rollback procedures
  - Integration points for website chat + Evolution API

### Completed in fifth pass (April 19, 2026 — Nate Herk alignment)
- Renamed voice workflow titles to a modular naming style aligned with Nate Herk receptionist structure:
  1. `workflow_voice_ingress.json` top-level name set to `Voice Ingress`
  2. `workflow_ziyada_voice_agent.json` top-level name set to `Ziyada Voice Agent`
- Standardized voice ingress node labels for cleaner parity with modular screenshot flow:
  - `Voice Webhook`, `Validate Input`, `Has Transcript?`, `Prepare Transcript`, `Transcribe Audio`, `Extract Transcript`, `Normalize Event`, `Call Voice Agent`, `Respond Webhook`
- Updated voice-agent tool contract names toward Nate-style tool naming:
  - `capture_lead` -> `new_client_crm`
  - `book_consultation` -> `book_event`
  - `get_services_info` -> `client_lookup`
- Updated system prompt instructions inside voice agent so tool invocation names match the renamed tools.
- Validated both edited workflow JSON files with `jq` and workspace diagnostics (no syntax/lint errors).

### Not completed yet (next passes)
- n8n workflow creation and wiring: ✅ **COMPLETED** — 5 workflows created:
  1. **workflow_whatsapp_ingress.json** — Evolution webhook → normalized payload → anti-loop guard → orchestrator
  2. **workflow_shared_orchestrator.json** — Identity resolution → confidence assessment → context loading → AI response → channel routing
  3. **workflow_unified_persistence.json** — Event persistence to chat_sessions, chat_messages, contact_events, leads lifecycle
  4. **workflow_escalation_handoff.json** — Business hours gate (Sun-Thu 12:00-17:00 Riyadh) → queue creation → WhatsApp + email notifications
  5. **workflow_booking_branch.json** — Google Calendar event creation → email with [WhatsApp] prefix → WhatsApp confirmation
- Identity-confidence decisioning in orchestrator (high/medium/low behavior enforcement server-side). ✅ **IMPLEMENTED** in workflow_shared_orchestrator.json
- Human handoff queue integrations (phone path + shared inbox notifications). ✅ **IMPLEMENTED** in workflow_escalation_handoff.json
- Full ElevenLabs real-time voice transport integration (current website voice layer uses browser speech recognition + webhook flow).
- Supabase migration execution in target environment (SQL file is prepared but not yet applied by deployment pipeline).

---

### Phase 1: Contracts and routing foundation

Define one normalized event contract across channels (website chat, website forms, WhatsApp), including source labels so every record clearly identifies origin.

**Canonical fields per event:**
- `channel` — `website_chat` | `website_form_contact` | `website_form_proposal` | `whatsapp` | `voice`
- `session_id` — UUID per browser/conversation session
- `phone_e164` — E.164-normalized phone number
- `email` — lowercase trimmed email
- `contact_id` — resolved Supabase contact ID (null until resolved)
- `message_id` — provider-specific dedup ID (Evolution message ID, chat widget UUID, etc.)
- `direction` — `inbound` | `outbound`
- `event_ts` — ISO timestamp in UTC
- `source_label` — specific channel tag written to leads/bookings/events tables

---

### Phase 2: Supabase lifecycle model

Extend the existing schema to persist sessions, message events, escalation queue, and lifecycle state transitions — linked to the existing `leads` and `bookings` tables via `phone_e164` and `email`.

**New tables / extensions:**

```sql
-- Unified contact identity graph
ALTER TABLE leads
  ADD COLUMN phone_normalized text,          -- E.164
  ADD COLUMN latest_session_id uuid,
  ADD COLUMN last_contact_method text,       -- 'website_chat' | 'website_form_contact' | 'whatsapp' | 'voice'
  ADD COLUMN lifecycle_state text DEFAULT 'new';
  -- lifecycle_state values: new | known | qualified | customer | escalated_human | booked

-- Conversation sessions (one per channel visit / WhatsApp thread open)
CREATE TABLE chat_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid REFERENCES leads(id),
  session_id uuid UNIQUE NOT NULL,
  channel text NOT NULL,
  language text,
  identity_confidence text DEFAULT 'none', -- none | low | medium | high
  started_at timestamptz DEFAULT now(),
  last_active_at timestamptz DEFAULT now(),
  status text DEFAULT 'active'             -- active | closed | escalated
);

-- Message-level audit trail
CREATE TABLE chat_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES chat_sessions(session_id),
  message_id text UNIQUE,                  -- provider dedup key
  direction text NOT NULL,                 -- inbound | outbound
  content text,
  ai_model text,
  escalated boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Escalation queue
CREATE TABLE handoff_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES chat_sessions(session_id),
  lead_id uuid REFERENCES leads(id),
  reason text,                             -- 'customer_request' | 'hallucination_risk' | 'low_confidence' | 'complex_issue' | 'policy_hit'
  channel text,
  phone_e164 text,
  priority text DEFAULT 'normal',          -- normal | high
  status text DEFAULT 'pending',           -- pending | claimed | resolved
  claimed_by text,
  created_at timestamptz DEFAULT now(),
  resolved_at timestamptz
);

-- Unified contact event audit trail
CREATE TABLE contact_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid REFERENCES leads(id),
  event_type text,                         -- 'form_submit' | 'chat_start' | 'message' | 'escalation' | 'booking' | 'verification' | 'hallucination_flag'
  event_source text,                       -- matches channel/source_label
  event_data jsonb,
  created_at timestamptz DEFAULT now()
);
```

**Identity-confidence policy:**
- High (phone + email exact match) → reuse prior context automatically
- Medium (phone or email match, not both) → ask soft verification question before loading context; do not reveal mismatch
- Low / none → continue as generic support; do not load or reference private prior context

**Lifecycle state transitions written by n8n:**
`new` → `known` → `qualified` → `customer` | `escalated_human` | `booked`

---

### Phase 3: n8n orchestration (new workflows only, existing instance untouched)

#### 3.1 WhatsApp Ingress Workflow (new)
- Trigger: Evolution webhook POST on `/webhook/whatsapp-inbound`
- Steps: normalize payload → deduplicate by `message_id` → anti-loop guard (skip if outbound echo) → fan-out to AI responder or handoff branch

#### 3.2 Shared Response Orchestrator (new)
- Accepts normalized events from both website chat and WhatsApp
- Loads identity confidence from Supabase (phone/email lookup against leads)
- Applies identity-confidence policy to decide context loading
- Calls AI layer (ElevenLabs agent API or n8n LangChain node) with assembled context
- Returns reply to correct channel (Evolution send API or chat widget response)

#### 3.3 Unified Persistence Workflow (new)
- Listens for events emitted by orchestrator
- Writes `chat_messages`, updates `chat_sessions.last_active_at`, updates `leads.lifecycle_state` and `last_contact_method`
- Ensures every write includes `source_label` for traceability

#### 3.4 Escalation Branch
Triggered when any of the following are true:
- User explicitly requests human
- AI confidence classifier returns uncertain
- Sensitive or complex trigger phrase detected
- Policy guardrail hit

Actions:
1. Insert row in `handoff_queue` with reason and channel
2. Phone handoff path: send WhatsApp message to owner's number with conversation link/summary
3. Queue/inbox path: send email to ziyadasystem@gmail.com with conversation transcript and lead details
4. Inform user: agent will reply shortly; include expected callback window

#### 3.5 Business-Hours Gate (Asia/Riyadh, UTC+3)
```javascript
const isBusinessHours = () => {
  const tz = 'Asia/Riyadh';
  const dt = new Date();
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: tz, weekday: 'narrow', hour: '2-digit', hour12: false
  }).formatToParts(dt);
  const day = parts.find(p => p.type === 'weekday').value; // S=Sun,M,T,W,T
  const hour = parseInt(parts.find(p => p.type === 'hour').value);
  const isWeekday = ['S','M','T','W'].includes(day) || day === 'T'; // Sun-Thu
  return isWeekday && hour >= 12 && hour < 17;
};
```
- In-hours: escalation → immediate human option available
- Out-of-hours: collect details, queue item created, inform user of Sun-Thu 12:00-17:00 callback window

#### 3.6 Booking Branch
- Triggered when escalation type includes booking request
- Creates Google Calendar event via Google Calendar node
- Sends email to ziyadasystem@gmail.com via Gmail node
- Email subject format: `[WhatsApp] Meeting Request — {lead_name} — {date}`
- Email body includes: lead name, phone, summary of conversation, requested time, origin channel `WhatsApp` (clearly labeled so it is distinguishable from website CTA bookings)
- Replies to user with confirmation and time slot

---

### Phase 4: Website voice integration with ElevenLabs [COMPLETE ✅]

**Completed deliverables:**
- ✅ Voice Ingress workflow (workflow_voice_ingress.json) — ElevenLabs transcription via API call, normalizes to unified event contract, routes to Shared Orchestrator
- ✅ Browser voice widget updated (floating-voice-widget.jsx) — Uses VITE_N8N_VOICE_INGRESS_WEBHOOK environment variable, auto-detects language (Arabic/English), synthesizes responses via ElevenLabs TTS
- ✅ Voice-to-text transcription — ElevenLabs API integration for conference-grade accuracy
- ✅ Text-to-speech synthesis — Auto-play responses in user's detected language
- ✅ Cross-channel voice session linking — Voice sessions are separate session type linked to same lead/contact via `contact_id` (not same live session as text chat)
- ✅ Voice session persistence — Events write to `chat_sessions` (channel: `voice`) and `chat_messages` with source_label: "voice"
- ✅ Context loading — Prior website/WhatsApp lifecycle loaded per identity-confidence policy
- ✅ Bilingual support — Auto-detect language from transcribed text, respond in same language, synthesize TTS in detected language
- ✅ Voice session summary storage — GED to Supabase after message end for future context reuse

**Implementation reference:**
- See [VOICE_INTEGRATION_GUIDE.md](projects/ziyada-system/VOICE_INTEGRATION_GUIDE.md) for deployment steps, ElevenLabs API key setup, browser compatibility, and monitoring

---

### Phase 5: AI prompt policy (production-safe for WhatsApp + website)

```
You are the official AI support assistant for Ziyada System (زيادة سيستم).

Language: Always reply in the same language as the user (Arabic or English). Default to Arabic if unclear.

Tone: Friendly, respectful, concise, and proactive. Reflect core value: الشراكة (Partnership) — نمو مشترك مع عملائنا.

What you can do:
- Answer questions about services and solutions
- Qualify leads and collect basic business requirements
- Guide users through next steps
- Escalate to a human agent when needed
- Book consultations during business hours (Sun-Thu 12:00-17:00 Riyadh time)

Tool usage rules:
- Only use tools for: verifying client identity, retrieving verified client info, escalating/creating handoff events, booking meetings
- Never claim an action was completed unless tool response explicitly confirms success
- If tool is unavailable: state clearly and offer human handoff

Safety rules:
- Never request or store passwords, OTPs, or payment details
- If user shares sensitive data, acknowledge and discard; warn them politely
- Refuse harmful, abusive, or illegal requests; redirect to safe support
- Never say "as an AI"
- Do not reference prior customer context until identity confidence is confirmed

Response style:
- 1-4 lines unless user requests detail
- One clear follow-up question when information is missing
- End with a clear next action
```

---

### Phase 6: Safety and operations

**Hallucination controls:**
- Confidence classifier node in orchestrator (flag low-certainty outputs)
- Fallback templates for common uncertain scenarios
- Immediate escalation path when classifier flags uncertain on sensitive requests
- Log all suspected hallucination events to `contact_events` with `event_type: 'hallucination_flag'`

**Observability:**
- Failed Evolution webhook rate
- Duplicate inbound message event rate
- AI response latency P50/P95
- Escalation volume by channel and reason
- Booking conversion rate by source (WhatsApp vs website CTA)
- Handoff queue resolution time

**Rollback / isolation:**
- Feature flag per channel: `ENABLE_WHATSAPP_CHANNEL`, `ENABLE_VOICE_CHANNEL`
- Disabling WhatsApp path does not affect website chat
- Replay queue for transient Evolution/ElevenLabs provider failures

---

### Relevant files

- [projects/ziyada-system/n8n for ziyada system/workflow_ziyada_ai_chat_agent.json](projects/ziyada-system/n8n%20for%20ziyada%20system/workflow_ziyada_ai_chat_agent.json)
- [projects/ziyada-system/n8n for ziyada system/workflow_chat_lead_capture.json](projects/ziyada-system/n8n%20for%20ziyada%20system/workflow_chat_lead_capture.json)
- [supabase-schema.sql](supabase-schema.sql)
- [CHAT_WIDGET_COMPLETE_GUIDE.md](CHAT_WIDGET_COMPLETE_GUIDE.md)
- [N8N_CHAT_WORKFLOW_SETUP.md](N8N_CHAT_WORKFLOW_SETUP.md)
- [projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-chat-widget.jsx](projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-chat-widget.jsx)
- [projects/ziyada-system/app/ziyada-system-website/src/api/siteApi.js](projects/ziyada-system/app/ziyada-system-website/src/api/siteApi.js)
- [projects/ziyada-system/app/ziyada-system-website/src/pages/Contact.jsx](projects/ziyada-system/app/ziyada-system-website/src/pages/Contact.jsx)
- [projects/ziyada-system/app/ziyada-system-website/src/pages/RequestProposal.jsx](projects/ziyada-system/app/ziyada-system-website/src/pages/RequestProposal.jsx)
- [projects/ziyada-system/files from antigraviti to claude/ziyada system زيادة سيستم/ziyada-agent/src/tools.ts](projects/ziyada-system/files%20from%20antigraviti%20to%20claude/ziyada%20system%20%D8%B2%D9%8A%D8%A7%D8%AF%D8%A9%20%D8%B3%D9%8A%D8%B3%D8%AA%D9%85/ziyada-agent/src/tools.ts)

---

### Verification checklist

1. Cross-channel contract tests: synthetic events for all channels → verify source_label + required fields persisted
2. Identity tests: exact match / partial match / no match → verify soft verification behavior and no private-context leakage on low confidence
3. Business-hours boundary tests: 11:59, 12:00, 16:59, 17:00 Asia/Riyadh; weekday edges (Thu/Fri/Sat/Sun)
4. Escalation tests: each trigger reason → confirm queue row + phone handoff + email notification
5. Booking tests: WhatsApp escalation → Google Calendar invite email with `[WhatsApp]` subject prefix
6. Continuity test: start on website chat → continue on WhatsApp with verified identity → confirm structured prior summary used
7. Voice tests: voice session stored as separate session linked to same contact without overwriting text session state
8. Failure-mode tests: duplicate webhooks, Evolution reconnect, provider timeout → idempotent persistence, no duplicate replies

---

### Decisions

| Decision point | Choice |
|---|---|
| WhatsApp transport (phase 1) | Evolution API on Hostinger VPS |
| Human handoff destination | Both direct phone path and shared queue/inbox |
| Calendar / email target | Google Calendar + Gmail (ziyadasystem@gmail.com) |
| Identity mismatch behavior | Soft verification question; no mismatch exposed; generic fallback on low confidence |
| Voice scope | Separate session type linked to same lead/contact |
| n8n strategy | New workflows only; existing instance and workflows untouched |

---

### Further considerations

1. Phase 2 migration path: swap Evolution transport for official Meta WhatsApp Business API while preserving normalized event contract (no downstream workflow changes needed)
2. Agent QA loop: weekly review of `hallucination_flag` events; patch prompt/tools based on patterns
3. Team operations: define on-call owner for Sun-Thu 12:00-17:00 handoff queue; max response SLA recommendation is 30 minutes during business hours
