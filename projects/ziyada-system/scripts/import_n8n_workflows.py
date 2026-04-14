"""
Import Ziyada N8N workflows via REST API.
Fixes: hardcodes HUBSPOT_TOKEN, replaces Supabase nodes with HTTP Request,
       reconstructs corrupted notifications workflow, fixes column names.
"""

import json
import requests

N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
HUBSPOT_TOKEN = "REDACTED"
SUPABASE_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

HEADERS = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Content-Type": "application/json"
}

def supabase_http_node(node_id, name, method, path_suffix, body_expr, position):
    """Returns an HTTP Request node targeting Supabase REST API."""
    return {
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": position,
        "parameters": {
            "method": method,
            "url": f"{SUPABASE_URL}/rest/v1/{path_suffix}",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "apikey", "value": SUPABASE_KEY},
                {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                {"name": "Content-Type", "value": "application/json"},
                {"name": "Prefer", "value": "return=minimal"}
            ]},
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": body_expr,
            "options": {}
        }
    }

# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW 1: HubSpot Sync
# ─────────────────────────────────────────────────────────────────────────────

hubspot_sync = {
    "name": "Ziyada - HubSpot Sync",
    "nodes": [
        {
            "id": "hs-001", "name": "Webhook",
            "type": "n8n-nodes-base.webhook", "typeVersion": 2,
            "position": [240, 300],
            "parameters": {"httpMethod": "POST", "path": "hubspot-sync", "responseMode": "onReceived", "responseData": "noData", "options": {}}
        },
        {
            "id": "hs-002", "name": "Route by Type",
            "type": "n8n-nodes-base.switch", "typeVersion": 3,
            "position": [460, 300],
            "parameters": {
                "rules": {"values": [
                    {"conditions": {"combinator": "and", "conditions": [{"leftValue": "={{ $json.body.type }}", "rightValue": "lead", "operator": {"type": "string", "operation": "equals"}}]}, "renameOutput": True, "outputKey": "lead"},
                    {"conditions": {"combinator": "and", "conditions": [{"leftValue": "={{ $json.body.type }}", "rightValue": "booking", "operator": {"type": "string", "operation": "equals"}}]}, "renameOutput": True, "outputKey": "booking"}
                ]},
                "options": {}
            }
        },
        {
            "id": "hs-003", "name": "Search HubSpot Contact",
            "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [680, 180],
            "parameters": {
                "method": "POST",
                "url": "https://api.hubapi.com/crm/v3/objects/contacts/search",
                "sendHeaders": True,
                "headerParameters": {"parameters": [{"name": "Authorization", "value": f"Bearer {HUBSPOT_TOKEN}"}]},
                "sendBody": True, "specifyBody": "json",
                "jsonBody": "={ \"filterGroups\": [{ \"filters\": [{ \"propertyName\": \"email\", \"operator\": \"EQ\", \"value\": \"{{ $('Webhook').item.json.body.record.email || $('Webhook').item.json.body.record.lead_email }}\" }] }], \"properties\": [\"email\",\"firstname\",\"lastname\"], \"limit\": 1 }",
                "options": {}
            }
        },
        {
            "id": "hs-004", "name": "Contact Exists?",
            "type": "n8n-nodes-base.if", "typeVersion": 2,
            "position": [900, 180],
            "parameters": {
                "conditions": {"combinator": "and", "conditions": [{"leftValue": "={{ $json.total }}", "rightValue": 0, "operator": {"type": "number", "operation": "gt"}}]}
            }
        },
        {
            "id": "hs-005", "name": "Update Contact",
            "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [1120, 100],
            "parameters": {
                "method": "PATCH",
                "url": "=https://api.hubapi.com/crm/v3/objects/contacts/{{ $('Search HubSpot Contact').item.json.results[0].id }}",
                "sendHeaders": True,
                "headerParameters": {"parameters": [{"name": "Authorization", "value": f"Bearer {HUBSPOT_TOKEN}"}]},
                "sendBody": True, "specifyBody": "json",
                "jsonBody": "={ \"properties\": { \"firstname\": \"{{ ($('Webhook').item.json.body.record.name || $('Webhook').item.json.body.record.lead_name || '').split(' ')[0] }}\", \"phone\": \"{{ $('Webhook').item.json.body.record.phone || $('Webhook').item.json.body.record.lead_phone || '' }}\", \"company\": \"{{ $('Webhook').item.json.body.record.company || '' }}\" } }",
                "options": {}
            }
        },
        {
            "id": "hs-006", "name": "Create Contact",
            "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [1120, 280],
            "parameters": {
                "method": "POST",
                "url": "https://api.hubapi.com/crm/v3/objects/contacts",
                "sendHeaders": True,
                "headerParameters": {"parameters": [{"name": "Authorization", "value": f"Bearer {HUBSPOT_TOKEN}"}]},
                "sendBody": True, "specifyBody": "json",
                "jsonBody": "={ \"properties\": { \"email\": \"{{ $('Webhook').item.json.body.record.email || $('Webhook').item.json.body.record.lead_email }}\", \"firstname\": \"{{ ($('Webhook').item.json.body.record.name || $('Webhook').item.json.body.record.lead_name || '').split(' ')[0] }}\", \"lastname\": \"{{ ($('Webhook').item.json.body.record.name || $('Webhook').item.json.body.record.lead_name || '').split(' ').slice(1).join(' ') }}\", \"phone\": \"{{ $('Webhook').item.json.body.record.phone || $('Webhook').item.json.body.record.lead_phone || '' }}\", \"company\": \"{{ $('Webhook').item.json.body.record.company || '' }}\" } }",
                "options": {}
            }
        },
        {
            "id": "hs-007", "name": "Create Deal",
            "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [680, 420],
            "parameters": {
                "method": "POST",
                "url": "https://api.hubapi.com/crm/v3/objects/deals",
                "sendHeaders": True,
                "headerParameters": {"parameters": [{"name": "Authorization", "value": f"Bearer {HUBSPOT_TOKEN}"}]},
                "sendBody": True, "specifyBody": "json",
                "jsonBody": "={ \"properties\": { \"dealname\": \"زيادة - اجتماع مع {{ $('Webhook').item.json.body.record.lead_name }}\", \"pipeline\": \"default\", \"dealstage\": \"appointmentscheduled\", \"closedate\": \"{{ $('Webhook').item.json.body.record.booking_date }}\" } }",
                "options": {}
            }
        },
        supabase_http_node(
            "hs-008", "Log to Supabase", "POST", "integration_logs",
            "={ \"type\": \"{{ $('Webhook').item.json.body.type }}\", \"source\": \"hubspot-sync\", \"status\": \"success\", \"record_email\": \"{{ $('Webhook').item.json.body.record.email || $('Webhook').item.json.body.record.lead_email }}\", \"payload\": {{ JSON.stringify($('Webhook').item.json.body) }} }",
            [1340, 280]
        ),
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "Route by Type", "type": "main", "index": 0}]]},
        "Route by Type": {
            "lead": [[{"node": "Search HubSpot Contact", "type": "main", "index": 0}]],
            "booking": [[{"node": "Search HubSpot Contact", "type": "main", "index": 0}], [{"node": "Create Deal", "type": "main", "index": 0}]]
        },
        "Search HubSpot Contact": {"main": [[{"node": "Contact Exists?", "type": "main", "index": 0}]]},
        "Contact Exists?": {"main": [[{"node": "Update Contact", "type": "main", "index": 0}], [{"node": "Create Contact", "type": "main", "index": 0}]]},
        "Update Contact": {"main": [[{"node": "Log to Supabase", "type": "main", "index": 0}]]},
        "Create Contact": {"main": [[{"node": "Log to Supabase", "type": "main", "index": 0}]]},
        "Create Deal": {"main": [[{"node": "Log to Supabase", "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"}
}

# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW 2: Admin Notify + Auto-Reply (reconstructed)
# ─────────────────────────────────────────────────────────────────────────────

notifications = {
    "name": "Ziyada - Admin Notify + Auto-Reply",
    "nodes": [
        {
            "id": "n-001", "name": "Webhook",
            "type": "n8n-nodes-base.webhook", "typeVersion": 2,
            "position": [240, 300],
            "parameters": {"httpMethod": "POST", "path": "notify", "responseMode": "onReceived", "responseData": "noData", "options": {}}
        },
        {
            "id": "n-002", "name": "Prepare Email Data",
            "type": "n8n-nodes-base.code", "typeVersion": 2,
            "position": [460, 300],
            "parameters": {
                "language": "javaScript",
                "jsCode": """const body = $input.item.json.body;
const type = body.type || 'unknown';
const record = body.record || {};
const sourcePage = body.source_page || record.source_page || '/';
const timestamp = body.timestamp || new Date().toISOString();
const name = record.name || record.lead_name || 'غير محدد';
const email = record.email || record.lead_email || '';
const phone = record.phone || record.lead_phone || '';
const company = record.company || '';
const challenge = record.challenge || '';
const utmSource = record.utm_source || '';
const bookingDate = record.booking_date || '';
const bookingTime = record.booking_time || '';

const typeLabel = { contact: 'Contact', lead: 'Lead', booking: 'Booking', newsletter: 'Newsletter', proposal: 'Proposal' }[type] || type;
const adminSubject = `[Ziyada] New ${typeLabel} from ${name} — ${sourcePage}`;

const adminBody = `<div dir="rtl" style="font-family:Arial,sans-serif;color:#1e293b;max-width:600px"><div style="background:#2563eb;padding:24px;border-radius:12px 12px 0 0"><h2 style="color:white;margin:0">🔔 إشعار جديد — زيادة سيستم</h2></div><div style="background:#f8fafc;padding:24px;border-radius:0 0 12px 12px;border:1px solid #e2e8f0"><table style="width:100%;border-collapse:collapse"><tr><td style="padding:8px;font-weight:600;color:#64748b">النوع</td><td>${typeLabel}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">الاسم</td><td>${name}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">البريد</td><td>${email}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">الهاتف</td><td>${phone}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">الشركة</td><td>${company}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">التحدي</td><td>${challenge}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">الاجتماع</td><td>${bookingDate} ${bookingTime}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">الصفحة</td><td>${sourcePage}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">المصدر</td><td>${utmSource}</td></tr><tr><td style="padding:8px;font-weight:600;color:#64748b">الوقت</td><td>${timestamp}</td></tr></table></div></div>`;

const replyContent = {
  contact: { ar: 'شكراً لتواصلك معنا — سنرد خلال 24 ساعة', en: "Thank you for reaching out — we'll reply within 24 hours" },
  proposal: { ar: 'شكراً لتواصلك معنا — سنرد خلال 24 ساعة', en: "Thank you for reaching out — we'll reply within 24 hours" },
  lead: { ar: 'شكراً لتواصلك معنا — سنرد خلال 24 ساعة', en: "Thank you for reaching out — we'll reply within 24 hours" },
  newsletter: { ar: 'مرحباً بك في مجتمع زيادة!', en: 'Welcome to the Ziyada community!' },
  booking: { ar: 'تم تأكيد طلب اجتماعك — سنرسل لك رابط Google Meet قريباً', en: "Your meeting request is confirmed — we'll send you the Google Meet link soon" }
}[type] || { ar: 'شكراً لتواصلك معنا', en: 'Thank you for reaching out' };

const autoReplySubject = `زيادة سيستم | ${replyContent.ar}`;
const autoReplyBody = `<div dir="rtl" style="font-family:Arial,sans-serif;color:#1e293b;max-width:600px"><div style="background:#2563eb;padding:32px;border-radius:12px 12px 0 0;text-align:center"><h1 style="color:white;margin:0">زيادة سيستم</h1><p style="color:#bfdbfe;margin:8px 0 0">Ziyada System</p></div><div style="background:#fff;padding:32px;border:1px solid #e2e8f0"><h2 style="color:#2563eb">${replyContent.ar}</h2><p style="color:#475569">${replyContent.en}</p><hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0"><p style="color:#94a3b8;font-size:14px">مرحباً ${name}، تم استلام رسالتك وسيتواصل معك فريقنا قريباً.</p><p style="color:#94a3b8;font-size:13px">Hello ${name}, your message has been received. Our team will be in touch soon.</p></div><div style="background:#f8fafc;padding:16px;border-radius:0 0 12px 12px;text-align:center;border:1px solid #e2e8f0;border-top:none"><p style="color:#94a3b8;font-size:12px;margin:0">info@ziyadasystem.com | ziyadasystem.com</p></div></div>`;

return [{ json: { type, name, email, adminSubject, adminBody, autoReplySubject, autoReplyBody, sourcePage, timestamp } }];"""
            }
        },
        {
            "id": "n-003", "name": "Send Admin Email",
            "type": "n8n-nodes-base.gmail", "typeVersion": 2.1,
            "position": [680, 180],
            "credentials": {"gmailOAuth2": {"id": "gmail-ziyada", "name": "Gmail Ziyada"}},
            "parameters": {
                "operation": "send",
                "toList": "info@ziyadasystem.com",
                "subject": "={{ $json.adminSubject }}",
                "message": "={{ $json.adminBody }}",
                "options": {"appendAttribution": False}
            }
        },
        {
            "id": "n-004", "name": "Has Submitter Email?",
            "type": "n8n-nodes-base.if", "typeVersion": 2,
            "position": [680, 420],
            "parameters": {
                "conditions": {
                    "combinator": "and",
                    "conditions": [{"leftValue": "={{ $json.email }}", "rightValue": "", "operator": {"type": "string", "operation": "notEquals"}}]
                }
            }
        },
        {
            "id": "n-005", "name": "Send Auto-Reply",
            "type": "n8n-nodes-base.gmail", "typeVersion": 2.1,
            "position": [900, 420],
            "credentials": {"gmailOAuth2": {"id": "gmail-ziyada", "name": "Gmail Ziyada"}},
            "parameters": {
                "operation": "send",
                "toList": "={{ $json.email }}",
                "subject": "={{ $json.autoReplySubject }}",
                "message": "={{ $json.autoReplyBody }}",
                "options": {"appendAttribution": False}
            }
        },
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "Prepare Email Data", "type": "main", "index": 0}]]},
        "Prepare Email Data": {"main": [[
            {"node": "Send Admin Email", "type": "main", "index": 0},
            {"node": "Has Submitter Email?", "type": "main", "index": 0}
        ]]},
        "Has Submitter Email?": {"main": [
            [{"node": "Send Auto-Reply", "type": "main", "index": 0}],
            []
        ]}
    },
    "settings": {"executionOrder": "v1"}
}

# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW 3: Google Meet Booking (column name fixed)
# ─────────────────────────────────────────────────────────────────────────────

google_meet = {
    "name": "Ziyada - Google Meet Booking",
    "nodes": [
        {
            "id": "gm-001", "name": "Webhook",
            "type": "n8n-nodes-base.webhook", "typeVersion": 2,
            "position": [240, 300],
            "parameters": {"httpMethod": "POST", "path": "google-meet", "responseMode": "onReceived", "responseData": "noData", "options": {}}
        },
        {
            "id": "gm-002", "name": "Only Bookings",
            "type": "n8n-nodes-base.if", "typeVersion": 2,
            "position": [460, 300],
            "parameters": {
                "conditions": {"combinator": "and", "conditions": [{"leftValue": "={{ $json.body.type }}", "rightValue": "booking", "operator": {"type": "string", "operation": "equals"}}]}
            }
        },
        {
            "id": "gm-003", "name": "Build Event Data",
            "type": "n8n-nodes-base.code", "typeVersion": 2,
            "position": [680, 240],
            "parameters": {
                "language": "javaScript",
                "jsCode": """const record = $input.item.json.body.record;
const bookingDate = record.booking_date;
const bookingTime = record.booking_time || '09:00';
const leadName = record.lead_name || record.name || 'عميل زيادة';
const leadEmail = record.lead_email || record.email || '';
const bookingId = record.id || null;

const startISO = `${bookingDate}T${bookingTime}:00+03:00`;
const endDate = new Date(`${bookingDate}T${bookingTime}:00+03:00`);
endDate.setMinutes(endDate.getMinutes() + 30);
const endISO = endDate.toISOString().replace('Z', '+03:00');

const calendarEvent = {
  summary: `اجتماع زيادة — ${leadName}`,
  description: `اجتماع مع ${leadName}\\nالشركة: ${record.company || ''}\\nالتحدي: ${record.challenge || ''}`,
  start: { dateTime: startISO, timeZone: 'Asia/Riyadh' },
  end: { dateTime: endISO, timeZone: 'Asia/Riyadh' },
  attendees: [{ email: leadEmail }, { email: 'info@ziyadasystem.com' }],
  conferenceData: {
    createRequest: {
      requestId: `ziyada-${bookingId || Date.now()}`,
      conferenceSolutionKey: { type: 'hangoutsMeet' }
    }
  },
  reminders: { useDefault: false, overrides: [{ method: 'email', minutes: 60 }, { method: 'popup', minutes: 15 }] }
};

return [{ json: { record, leadName, leadEmail, bookingId, bookingDate, bookingTime, calendarEvent } }];"""
            }
        },
        {
            "id": "gm-004", "name": "Create Google Calendar Event",
            "type": "n8n-nodes-base.googleCalendar", "typeVersion": 1.1,
            "position": [900, 240],
            "credentials": {"googleCalendarOAuth2Api": {"id": "google-cal-ziyada", "name": "Google Calendar Ziyada"}},
            "parameters": {
                "operation": "create",
                "calendar": {"__rl": True, "mode": "list", "value": "primary"},
                "start": "={{ $json.calendarEvent.start.dateTime }}",
                "end": "={{ $json.calendarEvent.end.dateTime }}",
                "additionalFields": {
                    "summary": "={{ $json.calendarEvent.summary }}",
                    "description": "={{ $json.calendarEvent.description }}",
                    "attendees": "={{ $json.calendarEvent.attendees }}",
                    "conferenceDataSend": "createRequest",
                    "timeZone": "Asia/Riyadh"
                }
            }
        },
        {
            "id": "gm-005", "name": "Extract Meet Link",
            "type": "n8n-nodes-base.code", "typeVersion": 2,
            "position": [1120, 240],
            "parameters": {
                "language": "javaScript",
                "jsCode": """const event = $input.item.json;
const prev = $('Build Event Data').item.json;
const meetLink = event.hangoutLink || (event.conferenceData && event.conferenceData.entryPoints && event.conferenceData.entryPoints.find(e => e.entryPointType === 'video')?.uri) || '';
return [{ json: { ...prev, meetLink, calendarEventId: event.id } }];"""
            }
        },
        {
            "id": "gm-006", "name": "Update Supabase Booking",
            "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [1340, 240],
            "parameters": {
                "method": "PATCH",
                "url": f"={SUPABASE_URL}/rest/v1/bookings?id=eq.{{{{ $json.bookingId }}}}",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "apikey", "value": SUPABASE_KEY},
                    {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "Prefer", "value": "return=minimal"}
                ]},
                "sendBody": True, "specifyBody": "json",
                "jsonBody": "={ \"google_meet_link\": \"{{ $json.meetLink }}\", \"status\": \"confirmed\" }",
                "options": {}
            }
        },
        {
            "id": "gm-007", "name": "Send Meet Link Email",
            "type": "n8n-nodes-base.gmail", "typeVersion": 2.1,
            "position": [1560, 240],
            "credentials": {"gmailOAuth2": {"id": "gmail-ziyada", "name": "Gmail Ziyada"}},
            "parameters": {
                "operation": "send",
                "toList": "={{ $json.leadEmail }}",
                "subject": "={{ 'زيادة سيستم | رابط اجتماعك — ' + $json.bookingDate + ' ' + $json.bookingTime }}",
                "message": "=<div dir=\"rtl\" style=\"font-family:Arial,sans-serif;color:#1e293b;max-width:600px\"><div style=\"background:#2563eb;padding:32px;border-radius:12px 12px 0 0;text-align:center\"><h1 style=\"color:white;margin:0\">زيادة سيستم</h1></div><div style=\"background:#fff;padding:32px;border:1px solid #e2e8f0\"><h2 style=\"color:#2563eb\">✅ تم تأكيد اجتماعك!</h2><p>مرحباً {{ $json.leadName }}،</p><table style=\"width:100%;border-collapse:collapse;margin:16px 0\"><tr><td style=\"padding:8px;color:#64748b;font-weight:600\">التاريخ</td><td>{{ $json.bookingDate }}</td></tr><tr><td style=\"padding:8px;color:#64748b;font-weight:600\">الوقت</td><td>{{ $json.bookingTime }} (بتوقيت السعودية)</td></tr><tr><td style=\"padding:8px;color:#64748b;font-weight:600\">رابط الاجتماع</td><td><a href=\"{{ $json.meetLink }}\" style=\"color:#2563eb;font-weight:700\">{{ $json.meetLink }}</a></td></tr></table><p style=\"color:#64748b;font-size:14px\">Hello {{ $json.leadName }}, your meeting is confirmed.<br>Link: <a href=\"{{ $json.meetLink }}\">{{ $json.meetLink }}</a></p></div><div style=\"background:#f8fafc;padding:16px;text-align:center;border-radius:0 0 12px 12px;border:1px solid #e2e8f0;border-top:none\"><p style=\"color:#94a3b8;font-size:12px;margin:0\">info@ziyadasystem.com | ziyadasystem.com</p></div></div>",
                "options": {"appendAttribution": False}
            }
        },
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "Only Bookings", "type": "main", "index": 0}]]},
        "Only Bookings": {"main": [
            [{"node": "Build Event Data", "type": "main", "index": 0}],
            []
        ]},
        "Build Event Data": {"main": [[{"node": "Create Google Calendar Event", "type": "main", "index": 0}]]},
        "Create Google Calendar Event": {"main": [[{"node": "Extract Meet Link", "type": "main", "index": 0}]]},
        "Extract Meet Link": {"main": [[{"node": "Update Supabase Booking", "type": "main", "index": 0}]]},
        "Update Supabase Booking": {"main": [[{"node": "Send Meet Link Email", "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"}
}

# ─────────────────────────────────────────────────────────────────────────────
# IMPORT ALL WORKFLOWS
# ─────────────────────────────────────────────────────────────────────────────

workflows = [
    ("HubSpot Sync", hubspot_sync),
    ("Admin Notify + Auto-Reply", notifications),
    ("Google Meet Booking", google_meet),
]

results = {}

for label, wf in workflows:
    resp = requests.post(
        f"{N8N_BASE}/api/v1/workflows",
        headers=HEADERS,
        json=wf
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        wf_id = data.get("id")
        results[label] = wf_id
        print(f"✅ {label}: imported (ID: {wf_id})")

        # Activate the workflow
        act = requests.patch(
            f"{N8N_BASE}/api/v1/workflows/{wf_id}",
            headers=HEADERS,
            json={"active": True}
        )
        if act.status_code in (200, 201):
            print(f"   ✅ Activated")
        else:
            print(f"   ⚠️  Activate failed: {act.status_code} {act.text[:200]}")
    else:
        print(f"❌ {label}: {resp.status_code} — {resp.text[:300]}")

print("\n─── WEBHOOK URLS ───")
for label, wf_id in results.items():
    path_map = {
        "HubSpot Sync": "hubspot-sync",
        "Admin Notify + Auto-Reply": "notify",
        "Google Meet Booking": "google-meet",
    }
    path = path_map.get(label, "unknown")
    print(f"{label}: https://n8n.srv953562.hstgr.cloud/webhook/{path}")

print("\nAdd to .env.local:")
print(f"VITE_N8N_HUBSPOT_SYNC_WEBHOOK=https://n8n.srv953562.hstgr.cloud/webhook/hubspot-sync")
print(f"VITE_N8N_NOTIFY_WEBHOOK=https://n8n.srv953562.hstgr.cloud/webhook/notify")
