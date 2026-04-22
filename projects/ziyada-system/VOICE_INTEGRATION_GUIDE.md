# ElevenLabs Voice Integration Guide — Phase 4

**Last Updated**: April 15, 2026  
**Status**: Voice Widget + Ingress Workflow Complete  
**Email**: ziyadasystem@gmail.com

---

## Overview

Phase 4 implements **real-time voice integration** using ElevenLabs for transcription and text-to-speech synthesis. Voice sessions are treated as separate omnichannel threads linked to the same lead/contact via identity resolution, following the same unified event contract as WhatsApp and website chat.

---

## Components

### 1. **Voice Widget** (`floating-voice-widget.jsx`)

**Location**: `projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-voice-widget.jsx`

**Features**:
- Floating action button (bottom-right, separate from text chat)
- Browser Speech Recognition API for local transcription (fallback to ElevenLabs)
- Real-time waveform visualization while recording
- Automatic language detection (Arabic/English)
- Auto-play text-to-speech responses via ElevenLabs
- Session tracking per voice conversation thread
- Identity-aware context loading (same contact as text/WhatsApp)

**Key Props**:
```javascript
<FloatingVoiceWidget 
  lang="ar"                    // Initial language: 'ar' or 'en'
  theme="dark"                 // UI theme (dark/light)
/>
```

**Environment Variables** (add to `.env`):
```
VITE_N8N_VOICE_INGRESS_WEBHOOK=https://[n8n-instance]/webhook/voice-ingress
VITE_ELEVENLABS_API_KEY=[your-elevenlabs-api-key]
```

**Behavior**:
1. User clicks voice button → panel opens
2. User clicks "Start Talking" → microphone activates
3. Browser speech API transcribes in real-time
4. User stops recording → transcript sent to Voice Ingress workflow
5. Voice Ingress routes through Shared Orchestrator
6. Response received → synthesized to speech and played automatically

---

### 2. **Voice Ingress Workflow** (`workflow_voice_ingress.json`)

**Purpose**: Receive voice messages from website, transcribe via ElevenLabs, normalize to unified contract, route to Shared Orchestrator.

**Trigger**: POST `/webhook/voice-ingress` (public webhook)

**Flow**:
1. Validate voice input (audio_base64 or audio_url required)
2. Store audio file in S3 (optional, for audit trail)
3. Call ElevenLabs transcription API
4. Extract transcript and verify confidence
5. Detect language (Arabic/English)
6. Normalize to unified event contract:
   ```json
   {
     "channel": "voice",
     "session_id": "uuid-voice-session",
     "phone_e164": "E.164 number",
     "email": "contact email",
     "contact_id": "resolved from leads",
     "message_id": "voice-{session_id}-{timestamp}",
     "direction": "inbound",
     "event_ts": "ISO timestamp",
     "source_label": "voice",
     "content": "transcribed text",
     "language": "ar" | "en",
     "_metadata": {
       "transcription_provider": "elevenlabs",
       "transcription_confidence": 0.95,
       "detected_language": "ar" | "en"
     }
   }
   ```
7. Call Shared Orchestrator workflow

**Success Response**:
```json
{
  "success": true,
  "message": "Voice message received and processed",
  "session_id": "uuid",
  "response": "AI agent reply"
}
```

**Error Handling**:
- Transcription fails → 400 error with message
- Identity resolution fails → Continue as anonymous (generic responses)
- Orchestrator timeout → Return empty response, log to contact_events

---

## Omnichannel Session Model

Voice sessions are **separate from text sessions** but **linked to the same contact**:

```
Contact (leads table)
├── Session A (website_chat)
│   ├── Message 1: "What's your pricing?"
│   ├── Message 2: "Can I try free?"
│   └── Contact migrated to text
│
├── Session B (voice)
│   ├── Message 1: "[transcribed audio: 'Hello, I'd like to know more']"
│   ├── Message 2: "[transcribed audio: 'Do you have Arabic support?']"
│   └── Separate voice thread, same contact context
│
└── Session C (whatsapp)
    ├── Message 1: "[via WhatsApp]"
    └── Continuation with full contact history available
```

### Identity Matching for Voice
- **High confidence**: Phone + email both match → load all prior context
- **Medium confidence**: Phone or email matches, not both → ask verification
- **Low confidence**: No match → generic response, no private context

### Context Window
Voice sessions load the last **10 messages** from any channel (website chat, WhatsApp, voice) to provide continuity without overwhelming token limits.

---

## Deployment Steps

### 1. Configure ElevenLabs Credentials

```
n8n UI > Settings > Credentials > New

Name: ElevenLabs API
Type: HTTP Header Auth
xi-api-key: [your-elevenlabs-api-key]
```

**Get API Key**:
1. Go to https://elevenlabs.io/app/speech-synthesis
2. Sign up or log in
3. Copy API key from Settings > API Keys
4. Add to n8n credentials

### 2. Import Voice Ingress Workflow

```
n8n UI > Workflows > Import from file

workflow_voice_ingress.json
```

Note workflow ID after import.

### 3. Wire Workflow References

**In `workflow_voice_ingress.json`**:
- Node "Call Shared Orchestrator" → Update workflowId to match deployed Shared Orchestrator workflow

### 4. Deploy Voice Widget to Website

**Option A: React Component (Recommended)**
```javascript
// In your main layout component
import FloatingVoiceWidget from '@/components/ui/floating-voice-widget';

export default function Layout() {
  return (
    <>
      <main>{/* page content */}</main>
      <FloatingVoiceWidget lang="ar" theme="dark" />
    </>
  );
}
```

**Option B: Direct Script (CDN)**
```html
<script src="https://[your-domain]/voice-widget.min.js"></script>
<script>
  VoiceWidget.mount({ 
    containerId: 'voice-container',
    webhookUrl: 'https://[n8n]/webhook/voice-ingress'
  });
</script>
```

### 5. Environment Configuration

Create `.env` file in React app:
```
VITE_N8N_VOICE_INGRESS_WEBHOOK=https://[n8n-instance-domain]/webhook/voice-ingress
VITE_ELEVENLABS_API_KEY=[your-elevenlabs-api-key]
VITE_ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # English voice
VITE_ELEVENLABS_VOICE_ID_AR=[arabic-voice-id]   # Arabic voice
```

**Find Voice IDs**:
```bash
curl -X GET "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: [your-api-key]"
```

### 6. Test Voice Flow

```bash
# Test voice ingress webhook
curl -X POST https://[n8n]/webhook/voice-ingress \
  -H "Content-Type: application/json" \
  -d '{
    "voice": {
      "session_id": "test-voice-123",
      "phone_e164": "+966533123456",
      "email": "test@example.com",
      "message_id": "msg-voice-001",
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
      "transcript": "السلام عليكم، أود أن أتعرف على خدماتكم",
      "language": "ar",
      "transcription_confidence": 0.95,
      "channel": "voice",
      "source_label": "voice",
      "direction": "inbound"
    }
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Voice message received and processed",
  "session_id": "test-voice-123",
  "response": "وعليكم السلام ورحمة الله وبركاته. أهلا وسهرا بك في زيادة سيستم..."
}
```

---

## Browser Compatibility

| Browser | Support | Transcription |
|---------|---------|---------------|
| Chrome | ✅ Full | Web Speech API (local) |
| Firefox | ✅ Full | Web Speech API (local) |
| Safari | ✅ Full | Web Speech API (local) |
| Edge | ✅ Full | Web Speech API (local) |
| Mobile Safari | ⚠️ Limited | Web Speech API (iOS 14.5+) |
| Mobile Chrome | ✅ Full | Web Speech API (local) |

**Fallback**: If Web Speech API unavailable, show text chat option.

---

## Voice Message Flow Diagram

```
User speaks → Browser Speech API → Transcript sent to Voice Ingress
     ↓
Voice Ingress Workflow:
  1. Validate audio/transcript
  2. (Optional) transcribe via ElevenLabs if needed
  3. Normalize to unified event contract
  4. POST to Shared Orchestrator
     ↓
Shared Orchestrator:
  1. Resolve identity from leads table
  2. Assess confidence (high/medium/low)
  3. Load context from chat_messages (last 10 messages across all channels)
  4. Call GPT-4o-mini with context
  5. Return response
     ↓
Voice Ingress Response:
  1. Receive AI response
  2. Call text-to-speech (ElevenLabs)
  3. Auto-play audio in browser
  4. POST message + response to Persistence workflow
     ↓
Unified Persistence:
  1. Write chat_sessions row (channel: 'voice')
  2. Insert chat_messages (direction: inbound + outbound)
  3. Update leads.lifecycle_state and last_contact_method
  4. Insert contact_events audit trail
```

---

## Advanced Configuration

### Custom Voice Personas

Override default voice IDs for Arabic/English:
```javascript
// In Voice Ingress workflow, add node:
const voiceMap = {
  ar: 'nPczCjzI2devNBz1zQrH',  // Arabic voice
  en: '21m00Tcm4TlvDq8ikWAM'    // English voice (Rachel)
};
const voiceId = voiceMap[$json.language];
```

### Sentiment Analysis in Responses

Add sentiment classifier node before Persistence:
```javascript
// Optional: flag escalations based on sentiment
if (response_sentiment === 'angry' || confidence < 0.7) {
  // Trigger escalation workflow
}
```

### Recording Audio for Compliance

Store all voice messages in S3:
```
AWS S3 > voiceMessages/{date}/{session_id}/{message_id}.wav
```

Enable in production:
```javascript
// In Voice Ingress > Store Audio File node
// Set S3 credentials and bucket
```

---

## Rate Limiting & Quotas

**ElevenLabs Limits** (depends on plan):
- Free tier: 10,000 characters/month
- Starter: 100,000 characters/month
- Pro: 1,000,000 characters/month

**Monitor Usage**:
```
ElevenLabs Dashboard > Usage
```

Add rate limit check in Voice Ingress:
```javascript
// Query ElevenLabs usage endpoint
const usage = await getElevenLabsUsage();
if (usage.character_count > usage.character_limit * 0.8) {
  // Log warning to contact_events
  // Consider escalation to human
}
```

---

## Monitoring & Observability

### Key Metrics
- **Voice session initiation rate**: chatSessions with channel='voice'
- **Transcription confidence**: avg(_metadata.transcription_confidence)
- **Language distribution**: count by language (ar vs en)
- **Escalations from voice**: contact_events where event_source='voice' AND event_type='escalation'
- **Voice-to-text conversion**: avg message length from voice vs chat

### Sample Monitoring Query

```sql
-- Voice metrics last 7 days
SELECT 
  DATE(created_at) as date,
  language,
  COUNT(*) as message_count,
  AVG((event_data->>'transcription_confidence')::float) as avg_confidence,
  SUM(CASE WHEN (event_data->>'detected_language') != language THEN 1 ELSE 0 END) as language_mismatches
FROM contact_events
WHERE event_source = 'voice' AND created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at), language
ORDER BY date DESC;
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Voice not supported" error | Browser lacks Web Speech API | Update browser or use fallback |
| Transcription blank | Microphone permission denied | Check browser mic settings |
| No response from orchestrator | Orchestrator workflow ID wrong | Update workflowId in Voice Ingress node |
| Text-to-speech not playing | ElevenLabs API key invalid | Verify API key in n8n credentials |
| Audio distorted | Encoding/decoding error | Check audio bitrate (16kHz mono recommended) |
| High latency (>3s) | Network or ElevenLabs timeout | Check n8n execution logs |

---

## Integration with Existing Channels

### Website Chat + Voice (Same Widget Container)
```javascript
// Both widgets share identity context
const identity = getKnownIdentity();

// Chat Widget finds voice messages in same session
const messages = getMessagesBySessionId(sessionId);
// Returns both text and voice messages, chronologically ordered
```

### WhatsApp + Voice (Cross-channel Continuity)
```
Lead contacts via:
1. WhatsApp (messages text-based)
2. Website chat (start conversation)
3. Voice widget (ask complex question)
4. Back to WhatsApp (confirm order)

All 4 interactions visible in leads.contact_events with source_label:
['whatsapp', 'website_chat', 'voice', 'whatsapp']
```

---

## Files Reference

- **Widget**: [floating-voice-widget.jsx](projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-voice-widget.jsx)
- **Workflow**: [workflow_voice_ingress.json](projects/ziyada-system/n8n for ziyada system/workflow_voice_ingress.json)
- **Implementation Plan**: [plan-ziyadaOmnichannelWhatsAppVoiceAgent.prompt.md](projects/ziyada-system/plan-ziyadaOmnichannelWhatsAppVoiceAgent.prompt.md)
- **Database Schema**: [supabase-schema.sql](supabase-schema.sql) — includes `chat_sessions`, `chat_messages`, `contact_events`

---

## Next Steps

1. **Deploy Voice Ingress workflow** to n8n instance
2. **Configure ElevenLabs API key** in n8n credentials
3. **Update website** with voice widget component
4. **Test voice flow** end-to-end (record → transcribe → response → synthesis)
5. **Monitor metrics** for 7 days and optimize
6. **Train team** on voice interaction patterns
7. **Phase 5**: Add voice-based escalation triggers (anger detection, complexity scoring)

