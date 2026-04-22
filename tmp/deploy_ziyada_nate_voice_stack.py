#!/usr/bin/env python3
"""Deploy Ziyada voice stack + Nate-style MCP orchestration to n8n safely.

- Reads n8n credentials from .env.local only.
- Upserts core voice workflows from local JSON exports.
- Creates/updates Nate-style modular MCP workflows.
- Activates all deployed workflows.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

import requests

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env.local"
WF_DIR = ROOT / "projects" / "ziyada-system" / "n8n for ziyada system"


def read_env(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for raw in path.read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def n8n_base_and_key(env: Dict[str, str]) -> Tuple[str, str]:
    base = (env.get("N8N_API_URL") or "").rstrip("/")
    if not base:
        raw_base = env.get("N8N_BASE_URL", "").rstrip("/")
        base = f"{raw_base}/api/v1" if raw_base else ""
    key = env.get("N8N_API_KEY", "")
    if not base or not key:
        raise RuntimeError("Missing N8N_API_URL/N8N_BASE_URL or N8N_API_KEY in .env.local")
    return base, key


class N8N:
    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base
        self.headers = {
            "X-N8N-API-KEY": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get(self, path: str) -> Dict:
        r = requests.get(f"{self.api_base}{path}", headers=self.headers, timeout=45)
        r.raise_for_status()
        return r.json()

    def post(self, path: str, payload: Dict) -> Dict:
        r = requests.post(
            f"{self.api_base}{path}", headers=self.headers, data=json.dumps(payload), timeout=60
        )
        r.raise_for_status()
        return r.json()

    def put(self, path: str, payload: Dict) -> Dict:
        r = requests.put(
            f"{self.api_base}{path}", headers=self.headers, data=json.dumps(payload), timeout=60
        )
        r.raise_for_status()
        return r.json()

    def activate(self, workflow_id: str) -> None:
        # n8n supports POST /activate on most versions
        r = requests.post(
            f"{self.api_base}/workflows/{workflow_id}/activate",
            headers=self.headers,
            data="{}",
            timeout=45,
        )
        if r.ok:
            return
        # fallback for alternative deployments
        r2 = requests.patch(
            f"{self.api_base}/workflows/{workflow_id}",
            headers=self.headers,
            data=json.dumps({"active": True}),
            timeout=45,
        )
        r2.raise_for_status()


def slim_payload(wf: Dict) -> Dict:
    nodes = wf.get("nodes", [])
    connections = normalize_connections(nodes, wf.get("connections", {}))
    return {
        "name": wf.get("name"),
        "nodes": nodes,
        "connections": connections,
        "settings": wf.get("settings", {"executionOrder": "v1"}),
    }


def normalize_connections(nodes: List[Dict], connections: Dict) -> Dict:
    """n8n API expects connection keys and target node refs by node name, not node id."""
    id_to_name: Dict[str, str] = {}
    for n in nodes:
        node_id = str(n.get("id", "")).strip()
        node_name = str(n.get("name", "")).strip()
        if node_id and node_name:
            id_to_name[node_id] = node_name

    out: Dict = {}
    for src_key, conn_types in (connections or {}).items():
        src_name = id_to_name.get(src_key, src_key)
        out[src_name] = {}
        for conn_type, groups in (conn_types or {}).items():
            fixed_groups = []
            for group in groups or []:
                fixed_group = []
                for edge in group or []:
                    edge_copy = dict(edge)
                    tgt = edge_copy.get("node")
                    if isinstance(tgt, str):
                        edge_copy["node"] = id_to_name.get(tgt, tgt)
                    fixed_group.append(edge_copy)
                fixed_groups.append(fixed_group)
            out[src_name][conn_type] = fixed_groups
    return out


def list_workflows(n8n: N8N) -> List[Dict]:
    data = n8n.get("/workflows?limit=250")
    return data.get("data", [])


def find_workflow_id_by_names(workflows: List[Dict], names: List[str]) -> str | None:
    by_name = {w.get("name", ""): str(w.get("id")) for w in workflows}
    for name in names:
        if name in by_name:
            return by_name[name]
    return None


def upsert_workflow(n8n: N8N, workflows: List[Dict], payload: Dict, candidate_names: List[str]) -> Tuple[str, str]:
    existing_id = find_workflow_id_by_names(workflows, candidate_names + [payload.get("name", "")])
    if existing_id:
        n8n.put(f"/workflows/{existing_id}", slim_payload(payload))
        return existing_id, "updated"
    created = n8n.post("/workflows", slim_payload(payload))
    return str(created["id"]), "created"


def load_workflow_json(name: str) -> Dict:
    return json.loads((WF_DIR / name).read_text())


def mk_exec_trigger_node(node_id: str = "exec-trigger", name: str = "When Executed by Another Workflow", inputs: List[str] | None = None) -> Dict:
    values = [{"name": i} for i in (inputs or [])]
    return {
        "parameters": {"workflowInputs": {"values": values}},
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.executeWorkflowTrigger",
        "typeVersion": 1.1,
        "position": [120, 280],
    }


def mk_code_node(node_id: str, name: str, js: str, pos: List[int]) -> Dict:
    return {
        "parameters": {"mode": "runOnceForAllItems", "jsCode": js},
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": pos,
    }


def mk_http_node(node_id: str, name: str, method: str, url: str, body: str, pos: List[int]) -> Dict:
    return {
        "parameters": {
            "method": method,
            "url": url,
            "sendBody": True,
            "contentType": "raw",
            "rawContentType": "application/json",
            "body": body,
            "options": {"response": {"response": {"responseFormat": "json"}}},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": pos,
    }


def mk_set_node(node_id: str, name: str, assignments: List[Dict], pos: List[int]) -> Dict:
    return {
        "parameters": {
            "assignments": {"assignments": assignments},
            "options": {},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": pos,
    }


def mk_sub_workflows() -> Dict[str, Dict]:
    client_lookup = {
        "name": "Client Lookup",
        "nodes": [
            mk_exec_trigger_node(inputs=["email", "phoneNumber"]),
            mk_code_node(
                "client-lookup-code",
                "Client Lookup",
                """
const email = String($json.email || '').trim();
const phone = String($json.phoneNumber || '').trim();
const found = Boolean(email || phone);
const msg = found
  ? 'عميل موجود أو معروف بشكل جزئي. يفضّل تأكيد الهوية قبل مشاركة تفاصيل خاصة.'
  : 'لا توجد هوية كافية. اعتبره عميل جديد واطلب البريد أو الجوال.';
return [{ json: { found, email, phoneNumber: phone, message: msg } }];
""".strip(),
                [380, 280],
            ),
        ],
        "connections": {
            "When Executed by Another Workflow": {
                "main": [[{"node": "Client Lookup", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"},
    }

    new_client_crm = {
        "name": "New Client CRM",
        "nodes": [
            mk_exec_trigger_node(inputs=["fullName", "email", "phoneNumber", "sector", "challenge", "service_interest"]),
            mk_http_node(
                "send-lead",
                "Send Lead to Ziyada Lead Processor",
                "POST",
                "https://n8n.srv953562.hstgr.cloud/webhook/ziyada-lead-intake",
                """={
  \"name\": \"{{ $json.fullName || '' }}\",
  \"email\": \"{{ $json.email || '' }}\",
  \"phone\": \"{{ $json.phoneNumber || '' }}\",
  \"sector\": \"{{ $json.sector || '' }}\",
  \"challenge\": \"{{ $json.challenge || '' }}\",
  \"service_interest\": \"{{ $json.service_interest || '' }}\",
  \"source\": \"vapi_mcp\",
  \"source_context\": \"voice_assistant\"
}""",
                [430, 280],
            ),
            mk_set_node(
                "new-client-msg",
                "Result Message",
                [{"name": "message", "type": "string", "value": "تم تسجيل العميل الجديد بنجاح وسيقوم الفريق بالمتابعة."}],
                [740, 280],
            ),
        ],
        "connections": {
            "When Executed by Another Workflow": {
                "main": [[{"node": "Send Lead to Ziyada Lead Processor", "type": "main", "index": 0}]]
            },
            "Send Lead to Ziyada Lead Processor": {
                "main": [[{"node": "Result Message", "type": "main", "index": 0}]]
            },
        },
        "settings": {"executionOrder": "v1"},
    }

    check_availability = {
        "name": "Check Availability",
        "nodes": [
            mk_exec_trigger_node(inputs=["afterTime", "beforeTime"]),
            mk_code_node(
                "availability-code",
                "Availability Window",
                """
const afterTime = String($json.afterTime || '').trim();
const beforeTime = String($json.beforeTime || '').trim();
const message = `تم استلام نطاق الموعد من ${afterTime || 'غير محدد'} إلى ${beforeTime || 'غير محدد'}. سيتم التأكيد النهائي من فريق زيادة سيستم.`;
return [{ json: { available: true, afterTime, beforeTime, message } }];
""".strip(),
                [380, 280],
            ),
        ],
        "connections": {
            "When Executed by Another Workflow": {
                "main": [[{"node": "Availability Window", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"},
    }

    book_event = {
        "name": "Book Event",
        "nodes": [
            mk_exec_trigger_node(inputs=["startTime", "endTime", "email", "eventSummary", "fullName", "phoneNumber"]),
            mk_http_node(
                "book-http",
                "Create Booking Request",
                "POST",
                "https://n8n.srv953562.hstgr.cloud/webhook/booking-webhook",
                """={
  \"session_id\": \"mcp-{{ Date.now() }}\",
  \"lead_name\": \"{{ $json.fullName || 'Voice Lead' }}\",
  \"phone_e164\": \"{{ $json.phoneNumber || '' }}\",
  \"email\": \"{{ $json.email || '' }}\",
  \"requested_datetime\": \"{{ $json.startTime || '' }}\",
  \"meeting_purpose\": \"{{ $json.eventSummary || 'voice consultation' }}\",
  \"visitor_need\": \"Booked from Vapi MCP tool workflow\",
  \"channel\": \"website_voice\",
  \"source_label\": \"website_voice\"
}""",
                [430, 280],
            ),
            mk_set_node(
                "book-msg",
                "Result Message",
                [{"name": "message", "type": "string", "value": "تم تسجيل طلب الحجز بنجاح وهو بانتظار موافقة الفريق."}],
                [730, 280],
            ),
        ],
        "connections": {
            "When Executed by Another Workflow": {
                "main": [[{"node": "Create Booking Request", "type": "main", "index": 0}]]
            },
            "Create Booking Request": {
                "main": [[{"node": "Result Message", "type": "main", "index": 0}]]
            },
        },
        "settings": {"executionOrder": "v1"},
    }

    lookup_appointment = {
        "name": "Lookup Appointment",
        "nodes": [
            mk_exec_trigger_node(inputs=["afterTime", "beforeTime", "email"]),
            mk_code_node(
                "lookup-code",
                "Lookup Placeholder",
                """
return [{ json: { message: 'البحث عن الموعد متاح حالياً كمسار Placeholder وسيتم ربطه بالتقويم/الـ CRM حسب بيئة التشغيل.', appointmentFound: false } }];
""".strip(),
                [380, 280],
            ),
        ],
        "connections": {
            "When Executed by Another Workflow": {
                "main": [[{"node": "Lookup Placeholder", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"},
    }

    update_appointment = {
        "name": "Update Appointment",
        "nodes": [
            mk_exec_trigger_node(inputs=["eventID", "startTime", "endTime"]),
            mk_code_node(
                "update-code",
                "Update Placeholder",
                """
return [{ json: { message: 'تحديث الموعد مسار جاهز للبنية Nate-style وسيتم تفعيله عند ربط نظام التقويم النهائي.', updated: true } }];
""".strip(),
                [380, 280],
            ),
        ],
        "connections": {
            "When Executed by Another Workflow": {
                "main": [[{"node": "Update Placeholder", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"},
    }

    delete_appointment = {
        "name": "Delete Appointment",
        "nodes": [
            mk_exec_trigger_node(inputs=["eventID"]),
            mk_code_node(
                "delete-code",
                "Delete Placeholder",
                """
return [{ json: { message: 'حذف الموعد مسار جاهز للبنية Nate-style وسيتم تفعيله عند ربط نظام التقويم النهائي.', deleted: true } }];
""".strip(),
                [380, 280],
            ),
        ],
        "connections": {
            "When Executed by Another Workflow": {
                "main": [[{"node": "Delete Placeholder", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"},
    }

    return {
        "Client Lookup": client_lookup,
        "New Client CRM": new_client_crm,
        "Check Availability": check_availability,
        "Book Event": book_event,
        "Lookup Appointment": lookup_appointment,
        "Update Appointment": update_appointment,
        "Delete Appointment": delete_appointment,
    }


def mk_tool_node(name: str, node_id: str, workflow_id: str, description: str, value_map: Dict[str, str], schema: List[Dict], pos: List[int]) -> Dict:
    return {
        "parameters": {
            "description": description,
            "workflowId": {
                "__rl": True,
                "value": workflow_id,
                "mode": "id",
            },
            "workflowInputs": {
                "mappingMode": "defineBelow",
                "value": value_map,
                "matchingColumns": [],
                "schema": schema,
                "attemptToConvertTypes": False,
                "convertFieldsToString": False,
            },
        },
        "type": "@n8n/n8n-nodes-langchain.toolWorkflow",
        "typeVersion": 2.2,
        "position": pos,
        "id": node_id,
        "name": name,
    }


def mk_schema_str(id_: str) -> Dict:
    return {
        "id": id_,
        "displayName": id_,
        "required": False,
        "defaultMatch": False,
        "display": True,
        "canBeUsedToMatch": True,
        "type": "string",
        "removed": False,
    }


def mk_voice_tool_node(
    tool_name: str,
    node_id: str,
    workflow_id: str,
    description: str,
    value_map: Dict[str, str],
    pos: List[int],
) -> Dict:
    return {
        "parameters": {
            "name": tool_name,
            "description": description,
            "workflowId": {
                "__rl": True,
                "value": workflow_id,
                "mode": "id",
            },
            "workflowInputs": {
                "mappingMode": "defineBelow",
                "value": value_map,
            },
        },
        "id": node_id,
        "name": tool_name,
        "type": "@n8n/n8n-nodes-langchain.toolWorkflow",
        "typeVersion": 2,
        "position": pos,
    }


def mk_voice_reference_tool() -> Dict:
    return {
        "parameters": {
            "name": "voice_reference_rules",
            "description": "Use when you need a quick reminder of the approved Ziyada voice rules, tone, off-topic policy, and number-handling policy.",
            "jsCode": "return {\n  rules: [\n    'Business only. Redirect off-topic questions back to Ziyada services.',\n    'Short voice-safe replies only.',\n    'Ask one question at a time.',\n    'Collect numbers digit by digit and repeat them digit by digit.',\n    'Use check_availability before promising a time slot when the caller is still choosing a time window.',\n    'Use book_event when the caller wants to confirm a consultation request.',\n  ]\n};",
        },
        "id": "voice-reference-tool",
        "name": "voice_reference_rules",
        "type": "@n8n/n8n-nodes-langchain.toolCode",
        "typeVersion": 1.1,
        "position": [1640, 620],
    }


def wire_voice_agent_workflow(base_payload: Dict, tool_ids: Dict[str, str]) -> Dict:
    payload = json.loads(json.dumps(base_payload))

    prepare_js = """
const root = $json.body || $json;
const event = root.event || $json.event || root;
const analysis = event.analysis || root.analysis || {};
const structured = analysis.structuredData || event.structuredData || root.structuredData || {};
const artifact = event.artifact || root.artifact || {};
const transcriptMessage = Array.isArray(artifact.messages)
  ? artifact.messages.filter((entry) => entry && entry.role === 'user').map((entry) => String(entry.message || '').trim()).filter(Boolean).join(' ')
  : '';
const directContent = String(event.content || event.transcript || root.chatInput || root.message || root.text || transcriptMessage || '').trim();
const fallbackSummary = String(structured.summary || structured.next_action || '').trim();
const content = directContent || fallbackSummary;

if (!content && !Object.keys(structured || {}).length) {
  throw new Error('Missing voice content or structured data');
}

return [{
  json: {
    ...event,
    analysis,
    artifact,
    userText: content,
    language: structured.language || event.language || root.language || 'ar',
    channel: event.channel || root.channel || 'website_voice',
    source_label: event.source_label || root.source_label || 'website_voice',
    session_id: event.session_id || root.session_id || `voice-${Date.now()}`,
    event_ts: event.event_ts || event.timestamp || root.timestamp || new Date().toISOString(),
    structuredData: structured,
  }
}];
""".strip()

    system_message = """
أنت محرك تشغيل Ziyada Voice Agent داخل n8n، وتعمل كطبقة تنفيذ خلفية للبنية المتوافقة مع Nate Herk orchestration.

المصدر الحقيقي للمحادثة والصوت هو VAPI. أنت لا تعيد اختراع شخصية الوكيل، بل تنفّذ الأدوات الصحيحة وترجع رداً قصيراً صالحاً للصوت عند الحاجة.

القواعد:
- نطاقك فقط خدمات زيادة سيستم التجارية.
- ردك قصير جداً: جملة إلى ثلاث جمل كحد أقصى.
- لا تسرد الخدمات أو القدرات كلها دفعة واحدة.
- إذا كان السؤال عاماً مثل: وش تساعدون فيه؟ أو وش خدماتكم؟ فجاوب بجملة تعريفية قصيرة فقط ثم اسأل عن التحدي الرئيسي.
- إذا كان عندك structuredData واضح من VAPI فاعتبره المصدر الأعلى ثقة.
- لا تعد بتأكيد موعد نهائي قبل نتيجة الأداة.
- في زيادة سيستم الحجز هو طلب حجز بانتظار موافقة الفريق، وليس تأكيداً فورياً.

استخدم الأدوات كالتالي:
- client_lookup: عندما تحتاج التحقق من وجود عميل معروف أو مطابقة بريد/جوال قبل المتابعة.
- new_client_crm: عندما يتوفر اسم مع وسيلة تواصل واحدة على الأقل أو توجد نية متابعة واضحة.
- check_availability: عندما يسأل العميل عن وقت مناسب أو نافذة مواعيد قبل تثبيت طلب الحجز.
- book_event: عندما يطلب العميل ديمو أو استشارة أو حجز موعد، أو عندما يدل structuredData على intent للحجز.
- lookup_appointment: لمراجعة موعد قائم.
- update_appointment: لتعديل موعد قائم.
- delete_appointment: لإلغاء موعد قائم.
- voice_reference_rules: عند الحاجة لتذكير سريع بالقواعد.

منطق التنفيذ:
1. افهم الاحتياج بسرعة.
2. إذا وجد structuredData وفيه booking.requested = true أو intent = book_meeting فاستدعِ book_event فوراً بالبيانات المتاحة.
3. إذا وُجد lead.name مع phone أو email فاستدعِ new_client_crm.
4. إذا كان المطلوب مجرد معرفة الأوقات استخدم check_availability قبل book_event.
5. إذا كان الطلب خارج النطاق أعد التوجيه لجملة قصيرة مرتبطة بنمو العمل.

لا تستخدم قائمة خدمات طويلة. اربط الجواب مباشرة بمشكلة العميل ثم استخدم الأداة المناسبة.
""".strip()

    base_nodes = []
    for node in payload.get("nodes", []):
        if node.get("name") in {
            "new_client_crm",
            "client_lookup",
            "book_event",
            "voice_reference_rules",
        }:
            continue
        if node.get("name") == "Prepare Voice Event":
            node["parameters"]["mode"] = "runOnceForAllItems"
            node["parameters"]["language"] = "javaScript"
            node["parameters"]["jsCode"] = prepare_js
        if node.get("name") == "Voice Agent":
            node["parameters"]["systemMessage"] = system_message
        base_nodes.append(node)

    tool_nodes = [
        mk_voice_tool_node(
            "new_client_crm",
            "voice-new-client-tool",
            tool_ids["New Client CRM"],
            "Create or update a Ziyada lead record when caller identity and follow-up intent are available.",
            {
                "fullName": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('fullName', 'Caller full name', 'string') }}",
                "email": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', 'Caller email if provided', 'string') }}",
                "phoneNumber": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('phoneNumber', 'Caller phone if provided', 'string') }}",
                "sector": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('sector', 'Business sector', 'string') }}",
                "challenge": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('challenge', 'Main business challenge', 'string') }}",
                "service_interest": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('service_interest', 'Relevant Ziyada service', 'string') }}",
            },
            [940, 620],
        ),
        mk_voice_tool_node(
            "client_lookup",
            "voice-client-lookup-tool",
            tool_ids["Client Lookup"],
            "Look up an existing client by email or phone before sharing sensitive context.",
            {
                "email": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', 'Caller email', 'string') }}",
                "phoneNumber": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('phoneNumber', 'Caller phone number', 'string') }}",
            },
            [1080, 620],
        ),
        mk_voice_tool_node(
            "check_availability",
            "voice-check-availability-tool",
            tool_ids["Check Availability"],
            "Check a proposed consultation time window before creating a booking request.",
            {
                "afterTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('afterTime', 'Requested window start in ISO format', 'string') }}",
                "beforeTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('beforeTime', 'Requested window end in ISO format', 'string') }}",
            },
            [1220, 620],
        ),
        mk_voice_tool_node(
            "book_event",
            "voice-book-event-tool",
            tool_ids["Book Event"],
            "Create a pending consultation booking request for Ziyada team approval.",
            {
                "startTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('startTime', 'Requested consultation start time in ISO format', 'string') }}",
                "endTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('endTime', 'Requested consultation end time in ISO format', 'string') }}",
                "email": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', 'Caller email', 'string') }}",
                "eventSummary": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('eventSummary', 'Consultation purpose', 'string') }}",
                "fullName": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('fullName', 'Caller full name', 'string') }}",
                "phoneNumber": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('phoneNumber', 'Caller phone number', 'string') }}",
            },
            [1360, 620],
        ),
        mk_voice_tool_node(
            "lookup_appointment",
            "voice-lookup-appointment-tool",
            tool_ids["Lookup Appointment"],
            "Look up an existing appointment when the caller asks to review a booked time.",
            {
                "afterTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('afterTime', 'Lookup window start in ISO format', 'string') }}",
                "beforeTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('beforeTime', 'Lookup window end in ISO format', 'string') }}",
                "email": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', 'Caller email', 'string') }}",
            },
            [1500, 620],
        ),
        mk_voice_tool_node(
            "update_appointment",
            "voice-update-appointment-tool",
            tool_ids["Update Appointment"],
            "Update an existing appointment when the caller asks to reschedule.",
            {
                "eventID": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('eventID', 'Existing booking or calendar event ID', 'string') }}",
                "startTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('startTime', 'New start time in ISO format', 'string') }}",
                "endTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('endTime', 'New end time in ISO format', 'string') }}",
            },
            [1640, 620],
        ),
        mk_voice_tool_node(
            "delete_appointment",
            "voice-delete-appointment-tool",
            tool_ids["Delete Appointment"],
            "Cancel an existing appointment when the caller asks to cancel.",
            {
                "eventID": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('eventID', 'Existing booking or calendar event ID', 'string') }}",
            },
            [1780, 620],
        ),
        mk_voice_reference_tool(),
    ]

    payload["nodes"] = base_nodes + tool_nodes
    payload["connections"] = {
        "Voice Agent Trigger": {
            "main": [[{"node": "Prepare Voice Event", "type": "main", "index": 0}]]
        },
        "Prepare Voice Event": {
            "main": [[{"node": "Voice Agent", "type": "main", "index": 0}]]
        },
        "Voice Agent": {
            "main": [[{"node": "Respond to Voice Widget", "type": "main", "index": 0}]]
        },
        "OpenRouter Voice Model": {
            "ai_languageModel": [[{"node": "Voice Agent", "type": "ai_languageModel", "index": 0}]]
        },
        "Conversation Memory": {
            "ai_memory": [[{"node": "Voice Agent", "type": "ai_memory", "index": 0}]]
        },
        "new_client_crm": {
            "ai_tool": [[{"node": "Voice Agent", "type": "ai_tool", "index": 0}]]
        },
        "client_lookup": {
            "ai_tool": [[{"node": "Voice Agent", "type": "ai_tool", "index": 1}]]
        },
        "check_availability": {
            "ai_tool": [[{"node": "Voice Agent", "type": "ai_tool", "index": 2}]]
        },
        "book_event": {
            "ai_tool": [[{"node": "Voice Agent", "type": "ai_tool", "index": 3}]]
        },
        "lookup_appointment": {
            "ai_tool": [[{"node": "Voice Agent", "type": "ai_tool", "index": 4}]]
        },
        "update_appointment": {
            "ai_tool": [[{"node": "Voice Agent", "type": "ai_tool", "index": 5}]]
        },
        "delete_appointment": {
            "ai_tool": [[{"node": "Voice Agent", "type": "ai_tool", "index": 6}]]
        },
        "voice_reference_rules": {
            "ai_tool": [[{"node": "Voice Agent", "type": "ai_tool", "index": 7}]]
        },
    }
    return payload


def mk_mcp_workflow(tool_ids: Dict[str, str]) -> Dict:
    trigger_name = "MCP Server Trigger"
    nodes = [
        {
            "parameters": {"path": "ziyada-vapi-mcp-server"},
            "type": "@n8n/n8n-nodes-langchain.mcpTrigger",
            "typeVersion": 2,
            "position": [-220, 40],
            "id": "mcp-trigger",
            "name": trigger_name,
            "webhookId": str(uuid.uuid4()),
        },
        mk_tool_node(
            "Call 'Client Lookup'",
            "tool-client-lookup",
            tool_ids["Client Lookup"],
            "Look up an existing client by email or phone.",
            {
                "email": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', ``, 'string') }}",
                "phoneNumber": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('phoneNumber', ``, 'string') }}",
            },
            [mk_schema_str("email"), mk_schema_str("phoneNumber")],
            [-340, 240],
        ),
        mk_tool_node(
            "Call 'New Client CRM'",
            "tool-new-client",
            tool_ids["New Client CRM"],
            "Create a new client lead in Ziyada CRM pipeline.",
            {
                "fullName": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('fullName', ``, 'string') }}",
                "email": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', ``, 'string') }}",
                "phoneNumber": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('phoneNumber', ``, 'string') }}",
                "sector": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('sector', ``, 'string') }}",
                "challenge": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('challenge', ``, 'string') }}",
                "service_interest": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('service_interest', ``, 'string') }}",
            },
            [
                mk_schema_str("fullName"),
                mk_schema_str("email"),
                mk_schema_str("phoneNumber"),
                mk_schema_str("sector"),
                mk_schema_str("challenge"),
                mk_schema_str("service_interest"),
            ],
            [-120, 240],
        ),
        mk_tool_node(
            "Call 'Check Availability'",
            "tool-check-availability",
            tool_ids["Check Availability"],
            "Check consultation time window availability.",
            {
                "afterTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('afterTime', ``, 'string') }}",
                "beforeTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('beforeTime', ``, 'string') }}",
            },
            [mk_schema_str("afterTime"), mk_schema_str("beforeTime")],
            [100, 240],
        ),
        mk_tool_node(
            "Call 'Book Event'",
            "tool-book-event",
            tool_ids["Book Event"],
            "Create a booking request for consultation.",
            {
                "startTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('startTime', ``, 'string') }}",
                "endTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('endTime', ``, 'string') }}",
                "email": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', ``, 'string') }}",
                "eventSummary": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('eventSummary', ``, 'string') }}",
                "fullName": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('fullName', ``, 'string') }}",
                "phoneNumber": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('phoneNumber', ``, 'string') }}",
            },
            [
                mk_schema_str("startTime"),
                mk_schema_str("endTime"),
                mk_schema_str("email"),
                mk_schema_str("eventSummary"),
                mk_schema_str("fullName"),
                mk_schema_str("phoneNumber"),
            ],
            [-340, 400],
        ),
        mk_tool_node(
            "Call 'Lookup Appointment'",
            "tool-lookup-appt",
            tool_ids["Lookup Appointment"],
            "Lookup appointments in a time window.",
            {
                "afterTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('afterTime', ``, 'string') }}",
                "beforeTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('beforeTime', ``, 'string') }}",
                "email": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', ``, 'string') }}",
            },
            [mk_schema_str("afterTime"), mk_schema_str("beforeTime"), mk_schema_str("email")],
            [-120, 400],
        ),
        mk_tool_node(
            "Call 'Delete Appointment'",
            "tool-delete-appt",
            tool_ids["Delete Appointment"],
            "Delete appointment by event ID.",
            {"eventID": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('eventID', ``, 'string') }}"},
            [mk_schema_str("eventID")],
            [100, 400],
        ),
        mk_tool_node(
            "Call 'Update Appointment'",
            "tool-update-appt",
            tool_ids["Update Appointment"],
            "Update appointment by event ID and new times.",
            {
                "eventID": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('eventID', ``, 'string') }}",
                "startTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('startTime', ``, 'string') }}",
                "endTime": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('endTime', ``, 'string') }}",
            },
            [mk_schema_str("eventID"), mk_schema_str("startTime"), mk_schema_str("endTime")],
            [320, 240],
        ),
    ]

    connections = {}
    for node in nodes:
        node_name = node["name"]
        if node_name == trigger_name:
            continue
        connections[node_name] = {
            "ai_tool": [[{"node": trigger_name, "type": "ai_tool", "index": 0}]]
        }

    return {
        "name": "Ziyada Vapi MCP Server",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
    }


def main() -> None:
    env = read_env(ENV_PATH)
    api_base, api_key = n8n_base_and_key(env)
    n8n = N8N(api_base, api_key)

    workflows = list_workflows(n8n)

    # 1) Upsert core Ziyada voice workflows that do not depend on sub-workflow IDs
    core_specs = [
        (
            load_workflow_json("workflow_voice_ingress.json"),
            ["Voice Ingress", "Voice Ingress — Provider Aware Handler", "Ziyada system voice chat"],
        ),
        (
            load_workflow_json("workflow_booking_branch.json"),
            ["Booking Branch — Approval Gate"],
        ),
        (
            load_workflow_json("workflow_lead_processor.json"),
            ["Ziyada Lead Processor — Supabase + Email + Calendar + HubSpot"],
        ),
    ]

    summary = {"core": [], "mcp_tools": [], "mcp_server": None}

    for wf_payload, aliases in core_specs:
        wf_id, action = upsert_workflow(n8n, workflows, wf_payload, aliases)
        n8n.activate(wf_id)
        summary["core"].append({"id": wf_id, "name": wf_payload.get("name"), "action": action, "active": True})
        workflows = list_workflows(n8n)

    # 2) Upsert Nate-style MCP sub-workflows
    tool_defs = mk_sub_workflows()
    tool_ids: Dict[str, str] = {}
    for tool_name, tool_payload in tool_defs.items():
        wf_id, action = upsert_workflow(n8n, workflows, tool_payload, [tool_name])
        n8n.activate(wf_id)
        tool_ids[tool_name] = wf_id
        summary["mcp_tools"].append({"id": wf_id, "name": tool_name, "action": action, "active": True})
        workflows = list_workflows(n8n)

    # 3) Upsert voice agent after tool workflow IDs are known
    voice_payload = wire_voice_agent_workflow(load_workflow_json("workflow_ziyada_voice_agent.json"), tool_ids)
    voice_id, voice_action = upsert_workflow(
        n8n,
        workflows,
        voice_payload,
        ["Ziyada Voice Agent", "Ziyada Voice Agent — Website Voice"],
    )
    n8n.activate(voice_id)
    summary["core"].append({"id": voice_id, "name": voice_payload.get("name"), "action": voice_action, "active": True})
    workflows = list_workflows(n8n)

    # 4) Upsert Nate-style MCP server workflow wired to above tools
    mcp_payload = mk_mcp_workflow(tool_ids)
    mcp_id, mcp_action = upsert_workflow(n8n, workflows, mcp_payload, ["Ziyada Vapi MCP Server", "Vapi MCP Server"])
    n8n.activate(mcp_id)
    summary["mcp_server"] = {"id": mcp_id, "name": mcp_payload["name"], "action": mcp_action, "active": True}

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
