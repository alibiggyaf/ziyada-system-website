# Ziyada AI Chat Agent — Deployment Complete

**Date:** April 20, 2026  
**Workflow ID:** `4wO4enlPyFeNduqY`  
**Webhook ID:** `3c9f6cb1-a3ce-4302-8260-6748f093520d` (unchanged)

---

## ✅ What Was Deployed

### 1. **System Prompt Rewrite** (AI Agent Node)
- **Expression-based**: Prefix `=` enables live n8n variable resolution
- **Live Riyadh DateTime Injection**: `{{ $now.setZone('Asia/Riyadh').toFormat('cccc, d MMMM yyyy - HH:mm') }}`
- **Full Brand Voice Embedded**:
  - Saudi "white" Najdi dialect rules
  - VIP persona (Jeddah HQ mindset)
  - Approved emoji list (😊 🤝 🚀 ✅ 💡 🎉 etc.)
  - Empathy phrases (فاهم عليك، هذا تحدي نسمعه كثير)
  - Preferred expressions (يا هلا، حياك، أبشر، ولا يهمك)
  - Text formatting rules (short sentences, blank lines, no markdown)
- **Relative Time Awareness**:
  - "tomorrow" → next calendar day
  - "after 2pm" → 14:00 in next valid business day
  - "Sunday" → next Sunday
  - Converts to ISO 8601 with +03:00 before booking
- **Working Hours**: 12:00–18:00 Sun–Thu only; no bookings within next 6 hours
- **Tool Usage Policy**: All 6 tools documented with explicit triggers

### 2. **Tool Updates**

#### capture_lead (Updated Description)
- **OLD**: "after collecting ALL THREE: full name, phone, AND email"
- **NEW**: "after confirming full_name AND at least one of: phone OR email (either alone is sufficient)"
- **Threshold**: `full_name` + `phone` alone is enough, OR `full_name` + `email` alone is enough

#### create_booking_request (Updated Description)
- **NEW**: Explicit rules for ISO 8601 datetime format, Riyadh +03:00 offset, 6-hour buffer, working hours enforcement
- **Requirement**: All 3 contacts + valid preferred_time must be confirmed before tool execution

### 3. **New Tools Added** (3 new nodes)

#### get_website_info (Code Tool)
- **Type**: Embedded static knowledge
- **Content**: All website sections (Home, Services, Success Stories, About, Blog, Contact, Pricing)
- **Usage**: When visitor asks "wain" (where), "how do I find", "where is X"
- **Rule**: Never send URLs; guide verbally only

#### brand_tone_guide (HTTP Tool → Google Doc 1)
- **Source**: Google Docs export `https://docs.google.com/document/d/1o9vnMOJYqIte1zqGOWbW3OzfRAFmIPBqUHzLm2H9Y0E/export?format=txt`
- **Usage**: Mandatory at conversation start + identity/tone questions
- **Content**: Saudi dialect, emoji rules, persona, empathy phrases, voice guidelines

#### services_reference_guide (HTTP Tool → Google Doc 2)
- **Source**: Google Docs export `https://docs.google.com/document/d/14rIWpFZHv1uQzUsdcYibI77abOSnCWZwJIp7p6aaFB4/export?format=txt`
- **Usage**: Company background, policies, reference only (not for service questions)
- **Note**: get_services_info is called FIRST for service questions

### 4. **Connections Wired**
All 6 tools connected to "Ziyada AI Agent" node:
1. ✅ capture_lead
2. ✅ get_services_info
3. ✅ create_booking_request
4. ✅ get_website_info
5. ✅ brand_tone_guide
6. ✅ services_reference_guide

---

## 🎯 How It Works Now

### Lead Capture Flow
```
User: "I'm Ahmed from a restaurant, my number is +966501234567"
  ↓
Agent: "تمام! احتاج إيميلك عشان أسجلك"
  ↓
User: "ahmed@restaurant.sa"
  ↓
Agent: "خلني أتأكد: اسمك Ahmed، جوالك +966501234567، إيميلك ahmed@restaurant.sa. صحيح؟"
  ↓
User: "يا، صحيح"
  ↓
[capture_lead fires immediately with name + phone + email]
```

### Booking Flow
```
User: "I want to book tomorrow after 2 p.m."
  ↓
Agent: [Resolves "tomorrow after 2pm" against current Riyadh time to ISO 8601]
Agent: "احتاج إيميلك كمان عشان أحجز لك"
  ↓
User: "ah...email@example.com"
  ↓
Agent: "تمام! سجّلت: الاسم، الجوال، الإيميل، الوقت [التاريخ والوقت]. صحيح؟"
  ↓
User: "نعم"
  ↓
[create_booking_request fires with all required fields + ISO datetime]
```

### Relative Time Resolution
- Current Riyadh time injected at conversation start
- Agent understands: "غداً، بعد الغد، الأحد، الأسبوع القادم، بعد الساعة 2"
- Converts to: `2026-04-22T14:00:00+03:00` before sending to webhook

---

## 📋 Nodes (12 Total)
1. **Chat Trigger** — webhook entry (unchanged webhook ID)
2. **Ziyada AI Agent** — LLM (new system prompt)
3. **GPT-4o-mini** — OpenAI model
4. **Window Buffer Memory** — session context (15-message window)
5. **capture_lead** — lead registration (updated description)
6. **get_services_info** — service details
7. **create_booking_request** — appointment booking (updated description)
8. **Output Sanitizer** — strips URLs/markdown
9. **Respond to Chat** — sends response to user
10. **get_website_info** ⭐ — website navigation (NEW)
11. **brand_tone_guide** ⭐ — brand voice reference (NEW)
12. **services_reference_guide** ⭐ — company background (NEW)

---

## ✨ Key Features Live Now

✅ **Live Datetime Injection** — Riyadh timezone, updates every conversation  
✅ **Relative Time Understanding** — "tomorrow", "after 2pm", day names all work  
✅ **Relaxed Lead Capture** — phone OR email, not both required  
✅ **Full Brand Voice** — Saudi white dialect, VIP treatment, approved emojis  
✅ **Website Knowledge** — embedded static site sections, no URL exposure  
✅ **Google Doc Tools** — live brand tone + services reference fetches  
✅ **ISO 8601 Booking** — correct timezone offset for Saudi Arabia  
✅ **Same Webhook** — no frontend changes needed; chat widget still works  

---

## 🚀 Ready to Test

1. **Visit**: https://ziyadasystem.com (chat widget on homepage)
2. **Test Lead Capture**: Name + phone only → should fire `capture_lead`
3. **Test Booking**: "I want to book Sunday at 3pm" → agent resolves datetime, asks for email
4. **Test Website Info**: "Where are the services?" → agent guides verbally
5. **Test Brand Voice**: Agent responds in Saudi white dialect with friendly tone

---

## 📁 Files
- **JSON Updated**: `projects/ziyada-system/n8n for ziyada system/workflow_ziyada_ai_chat_agent_FIXED.json`
- **Deployed To**: n8n.srv953562.hstgr.cloud (ID: 4wO4enlPyFeNduqY)
- **Webhook**: `https://n8n.srv953562.hstgr.cloud/webhook/...` (ID: 3c9f6cb1-a3ce-4302-8260-6748f093520d)

---

**Status:** ✅ LIVE  
**Deployed:** April 20, 2026  
**Chat Widget:** Ready for production
