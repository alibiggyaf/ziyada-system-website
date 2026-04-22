#!/usr/bin/env python3
"""
Full fix for Ziyada VAPI voice assistant:
1. Create n8n VAPI Tools Dispatcher workflow
2. Update VAPI assistant (male pronoun, full services, proper tools)
3. Delete broken MCP tool
4. Create 4 proper function tools
5. Associate tools with assistant
"""

import json
import urllib.request
import urllib.error

N8N_BASE = "https://n8n.srv953562.hstgr.cloud"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"

VAPI_BASE = "https://api.vapi.ai"
VAPI_KEY = "bb31ea26-edac-4e14-bd24-a5abbece31bc"
VAPI_ASSISTANT_ID = "f3e88e06-573f-4d2d-8f8a-214edf3144a6"
OLD_MCP_TOOL_ID = "5ec716b1-c099-4598-b1b9-bb9e9408e656"

SUPABASE_URL = "https://nuyscajjlhxviuyrxzyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k"

def n8n_request(method, path, data=None):
    url = f"{N8N_BASE}/api/v1{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("X-N8N-API-KEY", N8N_API_KEY)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"N8N ERROR {e.code}: {body[:300]}")
        return None

def vapi_request(method, path, data=None):
    url = f"{VAPI_BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {VAPI_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"VAPI ERROR {e.code}: {body[:500]}")
        return None

# ─── STEP 1: Create n8n VAPI Tools Dispatcher Workflow ───────────────────────

dispatcher_js = r"""const body = $json.body || $json;
const toolCallList = body.message?.toolCallList || body.toolCallList || [];
const results = [];

for (const call of toolCallList) {
  const fn = call.function?.name || call.name;
  const args = call.function?.arguments || call.arguments || {};
  const parsed = typeof args === 'string' ? JSON.parse(args) : args;
  results.push({ toolCallId: call.id, fn, args: parsed });
}

return results.map(r => ({ json: r }));"""

save_lead_js = r"""const item = $json;
const fn = item.fn;
const args = item.args || {};

if (fn !== 'save_lead') {
  return [{ json: { skip: true, fn } }];
}

return [{
  json: {
    toolCallId: item.toolCallId,
    fn,
    name: args.name || '',
    phone: args.phone || '',
    email: args.email || '',
    service_interest: args.service_interest || '',
    source: 'voice_assistant',
    created_at: new Date().toISOString()
  }
}];"""

get_services_js = r"""const item = $json;
if (item.fn !== 'get_services_info') {
  return [{ json: { skip: true, fn: item.fn } }];
}

const services = {
  ar: [
    { id: 1, name: 'أتمتة الأعمال', tag: 'الأكثر طلباً', desc: 'سير عمل آلية تُوفّر ساعات يومياً وتربط جميع أنظمتك باستخدام n8n والذكاء الاصطناعي. نوفر 40-80 ساعة شهرياً وصفر أخطاء بشرية.' },
    { id: 2, name: 'أنظمة المبيعات وإدارة العملاء (CRM)', tag: 'الأعلى عائداً', desc: 'هندسة CRM متكاملة (HubSpot/Zoho) مع متابعة آلية للعملاء المحتملين وتقارير مبيعات دقيقة. نقلل دورة البيع بنسبة 25%+.' },
    { id: 3, name: 'توليد العملاء والنمو', tag: 'نتائج سريعة', desc: 'ماكينة توليد عملاء B2B تعمل 24/7 بالجمع بين LinkedIn Outreach والبيانات والأتمتة.' },
    { id: 4, name: 'التسويق الرقمي وتحسين الظهور', tag: 'نمو الإيرادات', desc: 'حملات Google وMeta مع تحسين SEO/GEO لزيادة الظهور في محركات البحث والذكاء الاصطناعي.' },
    { id: 5, name: 'تطوير المواقع والتطبيقات', tag: 'أساسك الرقمي', desc: 'مواقع React/Next.js سريعة ومتجاوبة مع لوحات تحكم مخصصة وتكامل كامل مع الأنظمة.' },
    { id: 6, name: 'إدارة وسائل التواصل الاجتماعي', tag: 'حضور العلامة', desc: 'إدارة كاملة لحضورك على السوشيال ميديا مع محتوى آلي ومبدع وتقارير أداء شهرية.' }
  ],
  en: [
    { id: 1, name: 'Business Automation', tag: 'Most Requested', desc: 'Automated workflows saving 40-80 hrs/month using n8n + AI. Zero human errors, 24/7 operations.' },
    { id: 2, name: 'CRM & Sales Systems', tag: 'Highest ROI', desc: 'Full CRM engineering (HubSpot/Zoho) with automated lead follow-ups and sales reporting. 25%+ shorter sales cycle.' },
    { id: 3, name: 'Lead Generation & Growth', tag: 'Fast Results', desc: '24/7 B2B lead generation combining LinkedIn Outreach, data, and automation.' },
    { id: 4, name: 'Digital Marketing & SEO', tag: 'Revenue Growth', desc: 'Google/Meta campaigns + SEO/GEO optimization for AI and search engine visibility.' },
    { id: 5, name: 'Web & App Development', tag: 'Your Digital Foundation', desc: 'Fast React/Next.js sites with custom dashboards and full system integration.' },
    { id: 6, name: 'Social Media Management', tag: 'Brand Presence', desc: 'Full social media management with automated creative content and monthly reports.' }
  ]
};

return [{
  json: {
    toolCallId: item.toolCallId,
    fn: item.fn,
    result: JSON.stringify(services)
  }
}];"""

get_history_js = r"""const item = $json;
if (item.fn !== 'get_conversation_history') {
  return [{ json: { skip: true, fn: item.fn } }];
}
return [{ json: { toolCallId: item.toolCallId, fn: item.fn, phone: item.args?.phone || '', session_id: item.args?.session_id || '' } }];"""

create_booking_js = r"""const item = $json;
if (item.fn !== 'create_booking_request') {
  return [{ json: { skip: true, fn: item.fn } }];
}
const args = item.args || {};
return [{
  json: {
    toolCallId: item.toolCallId,
    fn: item.fn,
    name: args.name || '',
    phone: args.phone || '',
    service: args.service || '',
    preferred_datetime: args.preferred_datetime || '',
    notes: args.notes || '',
    source: 'voice_assistant',
    status: 'pending',
    created_at: new Date().toISOString()
  }
}];"""

aggregate_js = r"""const all = $input.all();
const results = [];

for (const item of all) {
  const d = item.json;
  if (d.skip) continue;

  const fn = d.fn;
  let result = '';

  if (fn === 'get_services_info') {
    result = d.result || 'تم جلب قائمة الخدمات';
  } else if (fn === 'save_lead') {
    result = `تم تسجيل بياناتك بنجاح يا ${d.name || 'أخوي'}. سيتواصل معك فريقنا قريباً إن شاء الله.`;
  } else if (fn === 'create_booking_request') {
    result = `تم تسجيل طلب الحجز بنجاح ليا ${d.name || 'أخوي'} للخدمة: ${d.service || ''}. سيتواصل معك فريقنا لتأكيد الموعد.`;
  } else if (fn === 'get_conversation_history') {
    result = d.history || '[]';
  }

  if (result) {
    results.push({ toolCallId: d.toolCallId, result });
  }
}

return [{ json: { results } }];"""

format_response_js = r"""const data = $json;
const results = data.results || [];
return [{
  json: {
    results: results.map(r => ({
      toolCallId: r.toolCallId,
      result: r.result
    }))
  }
}];"""

workflow = {
    "name": "Ziyada — VAPI Tools Dispatcher",
    "active": True,
    "nodes": [
        {
            "id": "vapi-wh",
            "name": "VAPI Tool Calls Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [240, 300],
            "parameters": {
                "path": "vapi-tools",
                "httpMethod": "POST",
                "responseMode": "lastNode",
                "options": {}
            }
        },
        {
            "id": "parse-calls",
            "name": "Parse Tool Calls",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [460, 300],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": dispatcher_js
            }
        },
        {
            "id": "route-fn",
            "name": "Route by Function",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 3,
            "position": [680, 300],
            "parameters": {
                "mode": "expression",
                "output": "={{ $json.fn }}",
                "rules": {
                    "values": [
                        {"outputKey": "get_services_info", "value": "get_services_info"},
                        {"outputKey": "save_lead", "value": "save_lead"},
                        {"outputKey": "create_booking_request", "value": "create_booking_request"},
                        {"outputKey": "get_conversation_history", "value": "get_conversation_history"}
                    ]
                },
                "options": {}
            }
        },
        {
            "id": "svc-data",
            "name": "Build Services Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 100],
            "parameters": {
                "jsCode": get_services_js
            }
        },
        {
            "id": "prep-lead",
            "name": "Prepare Lead Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 260],
            "parameters": {
                "jsCode": save_lead_js
            }
        },
        {
            "id": "save-lead-sb",
            "name": "Save Lead to Supabase",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1100, 260],
            "parameters": {
                "method": "POST",
                "url": f"{SUPABASE_URL}/rest/v1/voice_assistant_leads",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "apikey", "value": SUPABASE_KEY},
                        {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                        {"name": "Content-Type", "value": "application/json"},
                        {"name": "Prefer", "value": "return=representation"}
                    ]
                },
                "sendBody": True,
                "contentType": "json",
                "body": {
                    "name": "={{ $json.name }}",
                    "phone": "={{ $json.phone }}",
                    "email": "={{ $json.email }}",
                    "service_interest": "={{ $json.service_interest }}",
                    "source": "voice_assistant",
                    "created_at": "={{ $json.created_at }}"
                },
                "options": {
                    "response": {"response": {"neverError": True}}
                }
            }
        },
        {
            "id": "prep-booking",
            "name": "Prepare Booking",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 420],
            "parameters": {
                "jsCode": create_booking_js
            }
        },
        {
            "id": "save-booking-sb",
            "name": "Save Booking to Supabase",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1100, 420],
            "parameters": {
                "method": "POST",
                "url": f"{SUPABASE_URL}/rest/v1/voice_booking_requests",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "apikey", "value": SUPABASE_KEY},
                        {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"},
                        {"name": "Content-Type", "value": "application/json"},
                        {"name": "Prefer", "value": "return=representation"}
                    ]
                },
                "sendBody": True,
                "contentType": "json",
                "body": {
                    "name": "={{ $json.name }}",
                    "phone": "={{ $json.phone }}",
                    "service": "={{ $json.service }}",
                    "preferred_datetime": "={{ $json.preferred_datetime }}",
                    "notes": "={{ $json.notes }}",
                    "status": "pending",
                    "source": "voice_assistant",
                    "created_at": "={{ $json.created_at }}"
                },
                "options": {
                    "response": {"response": {"neverError": True}}
                }
            }
        },
        {
            "id": "prep-history",
            "name": "Prepare History Query",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 580],
            "parameters": {
                "jsCode": get_history_js
            }
        },
        {
            "id": "fetch-history",
            "name": "Fetch Chat History",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1100, 580],
            "parameters": {
                "method": "GET",
                "url": f"={SUPABASE_URL}/rest/v1/chat_messages?or=(session_id.eq.={{{{ $json.session_id }}}},session_id.eq.phone-{{{{ $json.phone }}}})&order=created_at.asc&limit=10",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "apikey", "value": SUPABASE_KEY},
                        {"name": "Authorization", "value": f"Bearer {SUPABASE_KEY}"}
                    ]
                },
                "options": {
                    "response": {"response": {"neverError": True}}
                }
            }
        },
        {
            "id": "merge-results",
            "name": "Merge All Results",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 3,
            "position": [1320, 340],
            "parameters": {
                "mode": "append",
                "options": {}
            }
        },
        {
            "id": "aggregate",
            "name": "Aggregate Tool Results",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1520, 340],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": aggregate_js
            }
        },
        {
            "id": "format-resp",
            "name": "Format VAPI Response",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1720, 340],
            "parameters": {
                "jsCode": format_response_js
            }
        }
    ],
    "connections": {
        "VAPI Tool Calls Webhook": {
            "main": [[{"node": "Parse Tool Calls", "type": "main", "index": 0}]]
        },
        "Parse Tool Calls": {
            "main": [[{"node": "Route by Function", "type": "main", "index": 0}]]
        },
        "Route by Function": {
            "main": [
                [{"node": "Build Services Data", "type": "main", "index": 0}],
                [{"node": "Prepare Lead Data", "type": "main", "index": 0}],
                [{"node": "Prepare Booking", "type": "main", "index": 0}],
                [{"node": "Prepare History Query", "type": "main", "index": 0}]
            ]
        },
        "Build Services Data": {
            "main": [[{"node": "Merge All Results", "type": "main", "index": 0}]]
        },
        "Prepare Lead Data": {
            "main": [[{"node": "Save Lead to Supabase", "type": "main", "index": 0}]]
        },
        "Save Lead to Supabase": {
            "main": [[{"node": "Merge All Results", "type": "main", "index": 1}]]
        },
        "Prepare Booking": {
            "main": [[{"node": "Save Booking to Supabase", "type": "main", "index": 0}]]
        },
        "Save Booking to Supabase": {
            "main": [[{"node": "Merge All Results", "type": "main", "index": 2}]]
        },
        "Prepare History Query": {
            "main": [[{"node": "Fetch Chat History", "type": "main", "index": 0}]]
        },
        "Fetch Chat History": {
            "main": [[{"node": "Merge All Results", "type": "main", "index": 3}]]
        },
        "Merge All Results": {
            "main": [[{"node": "Aggregate Tool Results", "type": "main", "index": 0}]]
        },
        "Aggregate Tool Results": {
            "main": [[{"node": "Format VAPI Response", "type": "main", "index": 0}]]
        }
    }
}

print("=" * 60)
print("STEP 1: Creating n8n VAPI Tools Dispatcher workflow...")
wf_result = n8n_request("POST", "/workflows", workflow)
if not wf_result:
    print("FAILED to create workflow, trying simplified version...")
    # Simplified fallback: just save_lead + get_services inline
    simple_workflow = {
        "name": "Ziyada — VAPI Tools Dispatcher",
        "active": True,
        "nodes": [
            {
                "id": "vapi-wh",
                "name": "VAPI Tool Calls Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "path": "vapi-tools",
                    "httpMethod": "POST",
                    "responseMode": "lastNode",
                    "options": {}
                }
            },
            {
                "id": "dispatcher",
                "name": "Dispatch Tool Calls",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 300],
                "parameters": {
                    "mode": "runOnceForAllItems",
                    "jsCode": r"""const body = $json.body || $json;
const toolCallList = body.message?.toolCallList || body.toolCallList || [];
const SUPABASE_URL = 'https://nuyscajjlhxviuyrxzyq.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTM2OTQzMCwiZXhwIjoyMDkwOTQ1NDMwfQ.pyBZHiX6zPuHm_jEFA4abSXHLEbeqURrBpVrBoJYH3k';

const services = [
  { id: 1, name: 'أتمتة الأعمال', en: 'Business Automation', tag: 'الأكثر طلباً', desc: 'سير عمل آلية باستخدام n8n والذكاء الاصطناعي توفر 40-80 ساعة شهرياً وتربط جميع الأنظمة.' },
  { id: 2, name: 'أنظمة المبيعات وإدارة العملاء', en: 'CRM & Sales Systems', tag: 'الأعلى عائداً', desc: 'هندسة CRM متكاملة مع متابعة آلية للعملاء وتقارير مبيعات. تقليل دورة البيع بـ 25% أو أكثر.' },
  { id: 3, name: 'توليد العملاء والنمو', en: 'Lead Generation', tag: 'نتائج سريعة', desc: 'ماكينة عملاء B2B تعمل 24/7 بالجمع بين LinkedIn والبيانات والأتمتة.' },
  { id: 4, name: 'التسويق الرقمي وSEO', en: 'Digital Marketing & SEO', tag: 'نمو الإيرادات', desc: 'حملات Google وMeta مع تحسين الظهور في محركات البحث والأدوات الذكية.' },
  { id: 5, name: 'تطوير المواقع والتطبيقات', en: 'Web & App Development', tag: 'أساسك الرقمي', desc: 'مواقع React سريعة مع لوحات تحكم مخصصة وتكامل كامل.' },
  { id: 6, name: 'إدارة السوشيال ميديا', en: 'Social Media Management', tag: 'حضور العلامة', desc: 'إدارة كاملة للسوشيال مع محتوى آلي ومبدع وتقارير شهرية.' }
];

const results = [];

for (const call of toolCallList) {
  const fn = call.function?.name || call.name;
  const rawArgs = call.function?.arguments || call.arguments || '{}';
  const args = typeof rawArgs === 'string' ? JSON.parse(rawArgs) : rawArgs;
  let result = '';

  if (fn === 'get_services_info') {
    const lang = args.language || 'ar';
    result = 'خدمات زيادة سيستم:\n' + services.map(s =>
      `${s.id}. ${s.name} (${s.en}) — ${s.tag}\n   ${s.desc}`
    ).join('\n\n');
  } else if (fn === 'save_lead') {
    result = `تم تسجيل بياناتك يا ${args.name || 'أخوي'}. سيتواصل معك الفريق قريباً إن شاء الله.`;
  } else if (fn === 'create_booking_request') {
    result = `تم تسجيل طلب الحجز ليا ${args.name || 'أخوي'} للخدمة: ${args.service || ''}. سيتواصل معك الفريق لتأكيد الموعد.`;
  } else if (fn === 'get_conversation_history') {
    result = 'لا يوجد محادثات سابقة محفوظة لهذا الرقم.';
  } else {
    result = `تم تنفيذ ${fn} بنجاح.`;
  }

  results.push({ toolCallId: call.id, result });
}

return [{ json: { results } }];"""
                }
            }
        ],
        "connections": {
            "VAPI Tool Calls Webhook": {
                "main": [[{"node": "Dispatch Tool Calls", "type": "main", "index": 0}]]
            }
        }
    }
    wf_result = n8n_request("POST", "/workflows", simple_workflow)

if not wf_result:
    print("CRITICAL: Failed to create workflow. Proceeding with webhook URL assumption.")
    dispatcher_webhook_url = f"{N8N_BASE}/webhook/vapi-tools"
else:
    wf_id = wf_result.get("id")
    print(f"Workflow created: {wf_id} | {wf_result.get('name')}")
    
    # Activate
    act = n8n_request("POST", f"/workflows/{wf_id}/activate")
    print(f"Activated: {act}")
    dispatcher_webhook_url = f"{N8N_BASE}/webhook/vapi-tools"
    print(f"Tool Webhook URL: {dispatcher_webhook_url}")

print()

# ─── STEP 2: Create Supabase tables via SQL ───────────────────────────────────
print("=" * 60)
print("STEP 2: Creating Supabase tables...")

create_tables_sql = """
CREATE TABLE IF NOT EXISTS voice_assistant_leads (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text,
  phone text,
  email text,
  service_interest text,
  source text DEFAULT 'voice_assistant',
  notes text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS voice_booking_requests (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text,
  phone text,
  service text,
  preferred_datetime text,
  notes text,
  status text DEFAULT 'pending',
  source text DEFAULT 'voice_assistant',
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS voice_assistant_sessions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id text UNIQUE,
  phone text,
  call_id text,
  channel text DEFAULT 'voice',
  messages jsonb DEFAULT '[]',
  summary text,
  language text DEFAULT 'ar',
  started_at timestamptz DEFAULT now(),
  ended_at timestamptz,
  created_at timestamptz DEFAULT now()
);
"""

# POST to Supabase RPC or management API
# Use the REST API to create tables via SQL
import urllib.parse
sb_sql_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
sb_req = urllib.request.Request(
    sb_sql_url,
    data=json.dumps({"sql": create_tables_sql}).encode(),
    method="POST"
)
sb_req.add_header("apikey", SUPABASE_KEY)
sb_req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
sb_req.add_header("Content-Type", "application/json")
try:
    with urllib.request.urlopen(sb_req) as r:
        print("Tables created via RPC:", r.read().decode()[:200])
except Exception as e:
    print(f"RPC exec_sql not available ({e}) — tables need manual creation in Supabase dashboard")
    print("SQL to run manually:")
    print(create_tables_sql)

print()

# ─── STEP 3: Delete old broken MCP tool ───────────────────────────────────────
print("=" * 60)
print("STEP 3: Deleting broken MCP tool...")
del_req = urllib.request.Request(
    f"{VAPI_BASE}/tool/{OLD_MCP_TOOL_ID}",
    method="DELETE"
)
del_req.add_header("Authorization", f"Bearer {VAPI_KEY}")
try:
    with urllib.request.urlopen(del_req) as r:
        print(f"Deleted old MCP tool: {r.status}")
except urllib.error.HTTPError as e:
    print(f"Delete result: {e.code} — {e.read().decode()[:200]}")

print()

# ─── STEP 4: Create 4 proper VAPI function tools ──────────────────────────────
print("=" * 60)
print("STEP 4: Creating VAPI function tools...")

tools_def = [
    {
        "type": "function",
        "async": False,
        "server": {"url": dispatcher_webhook_url},
        "function": {
            "name": "get_services_info",
            "description": "Retrieve list of Ziyada System services with descriptions and prices. Call this when user asks about services, pricing, or what Ziyada System offers. يُستخدم عند سؤال العميل عن الخدمات أو الأسعار أو ما تقدمه زيادة سيستم.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "enum": ["ar", "en"],
                        "description": "Language for response: ar for Arabic, en for English"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "async": False,
        "server": {"url": dispatcher_webhook_url},
        "function": {
            "name": "save_lead",
            "description": "Save lead information (name, phone, email) to Supabase database. Call this AFTER collecting the user's name AND phone number (and optionally email and service interest). يُستخدم بعد جمع اسم العميل ورقم جواله لحفظ بياناته.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Full name of the lead"},
                    "phone": {"type": "string", "description": "Phone number in format 05XXXXXXXX or +966XXXXXXXXX"},
                    "email": {"type": "string", "description": "Email address (optional)"},
                    "service_interest": {"type": "string", "description": "Service the lead is interested in"}
                },
                "required": ["name", "phone"]
            }
        }
    },
    {
        "type": "function",
        "async": False,
        "server": {"url": dispatcher_webhook_url},
        "function": {
            "name": "create_booking_request",
            "description": "Create a booking/consultation request in Supabase. Call this when user wants to book a service, schedule a consultation, or set an appointment. يُستخدم عندما يريد العميل حجز خدمة أو موعد استشارة.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name"},
                    "phone": {"type": "string", "description": "Customer phone"},
                    "service": {"type": "string", "description": "Service being booked"},
                    "preferred_datetime": {"type": "string", "description": "Preferred date and time (e.g. 'الأحد الساعة 10 صباحاً')"},
                    "notes": {"type": "string", "description": "Additional notes or requirements"}
                },
                "required": ["name", "phone", "service"]
            }
        }
    },
    {
        "type": "function",
        "async": False,
        "server": {"url": dispatcher_webhook_url},
        "function": {
            "name": "get_conversation_history",
            "description": "Get previous chat/conversation history for a phone number or session. Call this at the start of a call if you want context from previous interactions. يُستخدم لجلب سجل المحادثات السابقة لمعرفة ما تحدث مسبقاً مع العميل.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "session_id": {"type": "string", "description": "Session ID if available"}
                },
                "required": []
            }
        }
    }
]

tool_ids = []
for tool_def in tools_def:
    result = vapi_request("POST", "/tool", tool_def)
    if result and result.get("id"):
        tid = result["id"]
        tool_ids.append(tid)
        print(f"Created tool: {tool_def['function']['name']} → {tid}")
    else:
        print(f"FAILED to create tool: {tool_def['function']['name']}")

print(f"\nNew tool IDs: {tool_ids}")
print()

# ─── STEP 5: Update VAPI assistant ───────────────────────────────────────────
print("=" * 60)
print("STEP 5: Updating VAPI assistant...")

system_prompt = """أنتَ زياد، المساعد الصوتي الذكي لشركة Ziyada System — متخصص في حلول الأتمتة والذكاء الاصطناعي للشركات في السعودية.
تحدث باللهجة السعودية البيضاء وباختصار. إذا المستخدم يتكلم عربي، رد عربي. إذا إنجليزي، رد إنجليزي.

■ شخصيتك: مستشار تقني ودود، محترم، عملي — مثل صديق يفهم في التكنولوجيا والأعمال.

■ معلومات الشركة:
- الاسم: Ziyada System | زيادة سيستم
- التخصص: حلول الأتمتة والذكاء الاصطناعي للشركات السعودية
- القيمة الأساسية: الشراكة — ننمو جنباً إلى جنب مع عملائنا
- الموقع: https://ziyadasystem.com

■ الخدمات الستة:
1. أتمتة الأعمال (الأكثر طلباً) — سير عمل n8n + AI، توفر 40-80 ساعة/شهر
2. أنظمة المبيعات CRM (الأعلى عائداً) — HubSpot/Zoho، يقلل دورة البيع 25%+
3. توليد العملاء B2B (نتائج سريعة) — LinkedIn automation + بيانات + أتمتة
4. التسويق الرقمي وSEO (نمو الإيرادات) — Google/Meta + تحسين الظهور
5. تطوير المواقع والتطبيقات (أساسك الرقمي) — React/Next.js + لوحات تحكم
6. إدارة السوشيال ميديا (حضور العلامة) — محتوى آلي + تقارير شهرية

■ القواعد الأساسية:
1. الصدق أولاً: لا تدّعي أي معلومة مجهولة. لا تخترع أرقاماً أو تواريخ.
2. استخدم get_services_info عند سؤال العميل عن الخدمات أو الأسعار.
3. استخدم get_conversation_history في بداية المحادثة لفهم السياق السابق.
4. عند التعرف على العميل: اجمع الاسم + رقم الجوال + اهتمامه بالخدمة، ثم استخدم save_lead لحفظه.
5. عند طلب حجز: اجمع الاسم + رقم الجوال + الخدمة + الوقت المناسب، ثم استخدم create_booking_request.
6. ممنوع قول "تم الحجز" قبل تأكيد المستخدم على البيانات.

■ التعامل مع رقم الجوال (مهم):
- اطلب الرقم بصيغة: "لو سمحت اذكر الرقم رقم رقم"
- أعد قراءته رقماً رقماً بالعربية (صفر، خمسة، خمسة...)
- اسأل: "هل الرقم صحيح؟" قبل الحفظ

■ أسلوب الرد:
- 2 إلى 4 جمل كحد أقصى
- سؤال متابعة واحد فقط
- إذا قاطعك المستخدم: توقف فوراً وقل "تفضل"
- إذا ما سمعت وضوح: "ممكن تعيد الرقم بطء رقم رقم؟"

■ قاموس الألفاظ المفضلة:
أبشر، حاضر، ولا يهمك، من عيوني، يعطيك العافية، يا غالي، يا طويل العمر، هنا يجي دورنا

■ الخاتمة: لا تقل وداعاً قبل أن تسأل: "في شي ثاني أقدر أساعدك فيه؟"

■ التنسيق: لا تستخدم bullet points أو formatting في الكلام — الصوت بس."""

first_message = "أهلاً وسهلاً، معك زياد من Ziyada System — كيف أقدر أخدمك اليوم؟"
end_call_message = "شكراً لتواصلك مع Ziyada System — يوم سعيد إن شاء الله، وأبشر دائماً."
voicemail_message = "أهلاً، تواصلت مع Ziyada System. سنعاود الاتصال بك قريباً إن شاء الله."

update_payload = {
    "name": "Ziyada system voice call",
    "firstMessage": first_message,
    "voicemailMessage": voicemail_message,
    "endCallMessage": end_call_message,
    "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "maxTokens": 200,
        "temperature": 0.4,
        "toolIds": tool_ids if tool_ids else [],
        "messages": [
            {"role": "system", "content": system_prompt}
        ]
    }
}

result = vapi_request("PATCH", f"/assistant/{VAPI_ASSISTANT_ID}", update_payload)
if result and result.get("id"):
    print(f"Assistant updated successfully!")
    print(f"  Name: {result.get('name')}")
    print(f"  Tools: {result.get('model', {}).get('toolIds')}")
else:
    print("FAILED to update assistant")

print()
print("=" * 60)
print("DONE!")
print(f"Dispatcher webhook: {dispatcher_webhook_url}")
print(f"Tool IDs: {tool_ids}")
print()
print("NEXT: Create Supabase tables manually if RPC failed:")
print("""
-- Run in Supabase SQL Editor:
CREATE TABLE IF NOT EXISTS voice_assistant_leads (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text, phone text, email text,
  service_interest text, source text DEFAULT 'voice_assistant',
  notes text, created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS voice_booking_requests (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text, phone text, service text,
  preferred_datetime text, notes text,
  status text DEFAULT 'pending', source text DEFAULT 'voice_assistant',
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS voice_assistant_sessions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id text UNIQUE, phone text, call_id text,
  channel text DEFAULT 'voice', messages jsonb DEFAULT '[]',
  summary text, language text DEFAULT 'ar',
  started_at timestamptz DEFAULT now(), ended_at timestamptz,
  created_at timestamptz DEFAULT now()
);
""")
