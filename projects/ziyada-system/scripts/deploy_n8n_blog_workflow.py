#!/usr/bin/env python3
"""
Create or update the Ali Content Writer workflow in n8n via REST API.

This script does NOT import workflow JSON files into n8n manually.
It uses your n8n API key and creates/updates the workflow directly.

Required env vars:
- N8N_API_KEY
- N8N_BASE_URL (preferred) or N8N_API_URL (we derive base URL)

Optional env vars:
- N8N_BLOG_WORKFLOW_ID (default: "TI24nDeVCB1IlSav")
- N8N_BLOG_WORKFLOW_NAME (default: "Ali Content Writer")
- N8N_BLOG_TRIGGER_PATH (default: "ziyada-blog-ingest")
- N8N_BLOG_WORKFLOW_ACTIVE (default: "true")
- ZIYADA_SITE_WEBHOOK_URL (default: placeholder URL)
- ZIYADA_SITE_WEBHOOK_SECRET (default: "ziyada-n8n-2026")
- ZIYADA_CONTENT_WRITER_SYSTEM_PROMPT (overrides docs/ZIYADA_VOICE_PROMPT_SYSTEM.txt)
- ZIYADA_BLOG_SHEET_ID (Google Spreadsheet ID)
- ZIYADA_BLOG_REQUEST_SHEET_TAB (default: "ContentIntake")
- ZIYADA_BLOG_RESULTS_SHEET_TAB (default: "ContentResults")
- ZIYADA_BLOG_REQUEST_SHEET_GID (default: "2094549117")
- ZIYADA_GOOGLE_SHEETS_CREDENTIAL_ID
- ZIYADA_GOOGLE_SHEETS_CREDENTIAL_NAME
- ZIYADA_GOOGLE_SHEETS_TRIGGER_CREDENTIAL_ID
- ZIYADA_GOOGLE_SHEETS_TRIGGER_CREDENTIAL_NAME
- ZIYADA_BLOG_SHEET_TAB (legacy fallback for both tabs)
- APIFY_TOKEN
- APIFY_MARKET_INTEL_ACTOR_ID
- APIFY_TWITTER_ACTOR_ID (default: "61RPP7dywgiy0JPD0")
- ZIYADA_BLOG_BUDGET_MODE (lite|balanced|deep, default: "balanced")
- OPENAI_API_KEY
- OPENAI_MODEL (default: "gpt-4o-mini")
- TELEGRAM_BOT_TOKEN
- N8N_BLOG_WORKFLOW_PUBLIC_URL (optional workflow link for Telegram summaries)
- ZIYADA_CONTENT_DOC_URL (default Google Doc link shown in Telegram summary)
- ZIYADA_CONTENT_SLIDES_URL (default Google Slides link shown in Telegram summary)
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


ROOT_DIR = pathlib.Path(__file__).resolve().parents[3]
PROJECT_DIR = pathlib.Path(__file__).resolve().parents[1]
VOICE_PROMPT_PATH = PROJECT_DIR / "docs" / "ZIYADA_VOICE_PROMPT_SYSTEM.txt"


DEFAULT_SYSTEM_PROMPT = (
    "أنت كاتب محتوى ومساعد مبيعات B2B. مهمتك كتابة محتوى لصالح شركة الإدخال نفسها فقط، "
    "وليس لصالح أي نظام أو براند آخر. استخدم نبرة عربية سعودية مهنية وواضحة، واشتغل على فهم نشاط "
    "الشركة وخدماتها من بيانات الإدخال ورابط الموقع. ممنوع ذكر أو الترويج لزيادة سيستم إلا إذا كانت "
    "هي نفسها الشركة في الإدخال."
)
DEFAULT_SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
DEFAULT_REQUEST_SHEET_GID = "2094549117"


def load_env_files() -> None:
    """Load key=value entries from .env files if present."""
    for env_path in (ROOT_DIR / ".env", PROJECT_DIR / ".env"):
        if not env_path.exists():
            continue

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Last assignment wins to avoid duplicate-key drift in .env files.
            if key:
                os.environ[key] = value


def normalize_base_url() -> Optional[str]:
    """Resolve a usable n8n base URL from env vars."""
    base = os.getenv("N8N_BASE_URL", "").strip().strip('"').strip("'")
    api_url = os.getenv("N8N_API_URL", "").strip().strip('"').strip("'")

    candidate = base or api_url
    if not candidate:
        return None

    # Handle callback/rest URLs accidentally saved as API URL values.
    for marker in ("/api/", "/rest/"):
        if marker in candidate:
            candidate = candidate.split(marker, 1)[0]
            break

    return candidate.rstrip("/")


def load_writer_system_prompt() -> str:
    """Load the canonical Ziyada writer prompt from docs."""
    if VOICE_PROMPT_PATH.exists():
        content = VOICE_PROMPT_PATH.read_text(encoding="utf-8").strip()
        if content:
            return content
    return DEFAULT_SYSTEM_PROMPT


def api_request(
    method: str,
    base_url: str,
    api_key: str,
    path: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Tuple[int, Any]:
    """Call n8n API and return (status_code, parsed_json_or_text)."""
    url = f"{base_url}{path}"
    body = None
    headers = {
        "Accept": "application/json",
        "X-N8N-API-KEY": api_key,
    }

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=body, method=method, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw


def build_workflow_payload(
    name: str,
    trigger_path: str,
    request_sheet_gid: str,
    target_url: str,
    secret: str,
    system_prompt: str,
    sheet_id: str,
    request_sheet_tab: str,
    results_sheet_tab: str,
) -> Dict[str, Any]:
    """Build a blog-ingest workflow payload for n8n."""
    apify_actor_id = os.getenv("APIFY_MARKET_INTEL_ACTOR_ID", "apify~website-content-crawler").strip() or "apify~website-content-crawler"
    apify_twitter_actor_id = os.getenv("APIFY_TWITTER_ACTOR_ID", "61RPP7dywgiy0JPD0").strip() or "61RPP7dywgiy0JPD0"
    apify_token = os.getenv("APIFY_TOKEN", "").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    telegram_send_enabled = bool(telegram_bot_token)
    workflow_public_url = os.getenv("N8N_BLOG_WORKFLOW_PUBLIC_URL", "").strip()
    default_doc_url = os.getenv("ZIYADA_CONTENT_DOC_URL", "").strip()
    default_slides_url = os.getenv("ZIYADA_CONTENT_SLIDES_URL", "").strip()
    budget_mode_default = os.getenv("ZIYADA_BLOG_BUDGET_MODE", "balanced").strip().lower() or "balanced"
    if budget_mode_default not in {"lite", "balanced", "deep"}:
        budget_mode_default = "balanced"

    return {
        "name": name,
        "settings": {},
        "nodes": [
            {
                "id": "Webhook In",
                "name": "Webhook In",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [220, 280],
                "webhookId": trigger_path,
                "parameters": {
                    "path": trigger_path,
                    "httpMethod": "POST",
                    "responseMode": "onReceived",
                    "options": {},
                },
            },
            {
                "id": "Poll Intake Schedule",
                "name": "Poll Intake Schedule",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1,
                "position": [220, 120],
                "parameters": {
                    "rule": {"interval": [{"field": "minutes", "minutesInterval": 1}]},
                },
            },
            {
                "id": "Read Intake Rows",
                "name": "Read Intake Rows",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [420, 120],
                "onError": "continueRegularOutput",
                "parameters": {
                    "documentId": {
                        "mode": "id",
                        "value": sheet_id,
                    },
                    "sheetName": {
                        "mode": "name",
                        "value": request_sheet_tab,
                    },
                    "options": {},
                },
            },
            {
                "id": "Select New Intake Rows",
                "name": "Select New Intake Rows",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [620, 120],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const rows = $input.all();\n"
                        "const output = [];\n"
                        "for (const item of rows) {\n"
                        "  const row = item.json || {};\n"
                        "  const statusCandidate = row.trigger_status ?? row['trigger status'] ?? row.send_status ?? row['send status'] ?? row.workflow_status ?? row['workflow status'] ?? row.status ?? row.request_status ?? row['request status'];\n"
                        "  const hasStatusField = statusCandidate !== undefined && statusCandidate !== null && String(statusCandidate).trim() !== '';\n"
                        "  const rawStatus = String(statusCandidate ?? '').trim().toLowerCase();\n"
                        "  // Mandatory status gate: only rows explicitly set to start/continue are processed.\n"
                        "  if (!hasStatusField || !['start','continue'].includes(rawStatus)) {\n"
                        "    continue;\n"
                        "  }\n"
                        "  const sentStatusRaw = String(row.sent_status ?? row['sent status'] ?? '').trim().toLowerCase();\n"
                        "  const workflowStatusRaw = String(row.workflow_status ?? row['workflow status'] ?? '').trim().toLowerCase();\n"
                        "  if (sentStatusRaw === 'done' || sentStatusRaw === 'finish' || workflowStatusRaw === 'done' || workflowStatusRaw === 'completed') {\n"
                        "    continue;\n"
                        "  }\n"
                        "  const requestId = String(row.request_id || row.requestId || '').trim();\n"
                        "  const fallbackKey = [row.company_name || row.company || '', row.industry || '', row.target_audience || row.audience || '', row.company_link || row.website || row.url || ''].join('|').trim();\n"
                        "  const rowNumber = String(row.row_number || row.rowNumber || '').trim();\n"
                        "  const key = requestId || (rowNumber ? `row:${rowNumber}` : fallbackKey);\n"
                        "  if (!key) {\n"
                        "    continue;\n"
                        "  }\n"
                        "  output.push({ json: { ...row, __intake_key: key, __trigger_status: rawStatus || (hasStatusField ? '' : 'start') } });\n"
                        "  // Single-item queue mode: process only one intake row per polling run.\n"
                        "  if (output.length >= 1) {\n"
                        "    break;\n"
                        "  }\n"
                        "}\n"
                        "return output;"
                    ),
                },
            },
            {
                "id": "Normalize Intake Row Input",
                "name": "Normalize Intake Row Input",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [760, 120],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const statusSource = input.trigger_status || input['trigger status'] || input.send_status || input['send status'] || input.workflow_status || input['workflow status'] || input.status || input.request_status || input['request status'] || input.__trigger_status || '';\n"
                        "const statusRaw = String(statusSource).trim().toLowerCase();\n"
                        "const normalizedStatus = ['start','continue','pause','pending','done','finish'].includes(statusRaw) ? statusRaw : (statusRaw ? 'pending' : 'start');\n"
                        "return [{ json: {\n"
                        "  ...input,\n"
                        "  request_id: input.request_id || input.requestId || '',\n"
                        "  company_name: input.company_name || input.company || '',\n"
                        "  industry: input.industry || '',\n"
                        "  target_audience: input.target_audience || input.audience || '',\n"
                        "  company_link: input.company_link || input.website || input.url || '',\n"
                        "  writer_task: input.writer_task || input.prompt || input['prompt text'] || input.prompt_text || input.prompt_ar || input['prompt ar'] || '',\n"
                        "  trigger_status: normalizedStatus,\n"
                        "  sent_status: input.sent_status || input['sent status'] || input.delivery_status || 'pending',\n"
                        "  source: input.source || 'sheet_intake',\n"
                        "  approval_status: input.approval_status || 'approved'\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Prepare Content Writer Input",
                "name": "Prepare Content Writer Input",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [520, 280],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const raw = (input.body && typeof input.body === 'object') ? input.body : input;\n"
                        "const telegramText = raw.message?.text || raw.edited_message?.text || '';\n"
                        "const isTelegram = Object.prototype.hasOwnProperty.call(raw, 'update_id');\n"
                        "const normalizedText = String(telegramText || '').trim();\n"
                        "const topicFromTelegram = normalizedText.replace(/^\\/(start|blog|write)\\b/i, '').trim();\n"
                        "const approvalFromTelegram = /approved|approve|اعتماد|موافق|موافقة/i.test(normalizedText) ? 'approved' : '';\n"
                        "const draftEmailFromTelegram = /send\\s+draft\\s+email|draft\\s+email|مسودة\\s*ايميل|مسودة\\s*بريد/i.test(normalizedText);\n"
                        "let topic = raw.topic || raw.title_ar || raw.title_en || topicFromTelegram || raw.company_name || \"موضوع جديد\";\n"
                        "const now = new Date();\n"
                        "const pad = (n) => String(n).padStart(2, '0');\n"
                        "const generatedRequestId = `REQ-${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}-${Math.random().toString(36).slice(2,6).toUpperCase()}`;\n"
                        "const requestId = String(raw.request_id || raw.id || generatedRequestId);\n"
                        "const intake = {\n"
                        "  request_id: requestId,\n"
                        "  row_number: raw.row_number || raw.rowNumber || '',\n"
                        "  created_at: raw.created_at || raw['created at'] || '',\n"
                        "  company_name: raw.company_name || raw.company || '',\n"
                        "  industry: raw.industry || '',\n"
                        "  target_audience: raw.target_audience || raw.audience || '',\n"
                        "  company_link: raw.company_link || raw.website || raw.url || ''\n"
                        "};\n"
                        "const parseInterviewPairs = (text) => {\n"
                        "  const out = {};\n"
                        "  for (const line of String(text || '').split(/\\n|\\|/)) {\n"
                        "    const part = String(line || '').trim();\n"
                        "    if (!part || !part.includes(':')) continue;\n"
                        "    const [k, ...rest] = part.split(':');\n"
                        "    const key = String(k || '').trim().toLowerCase();\n"
                        "    const value = rest.join(':').trim();\n"
                        "    if (!value) continue;\n"
                        "    out[key] = value;\n"
                        "  }\n"
                        "  return out;\n"
                        "};\n"
                        "const interviewPairs = isTelegram ? parseInterviewPairs(normalizedText) : {};\n"
                        "const alias = (keys) => {\n"
                        "  for (const k of keys) {\n"
                        "    const v = interviewPairs[String(k).toLowerCase()];\n"
                        "    if (v) return v;\n"
                        "  }\n"
                        "  return '';\n"
                        "};\n"
                        "intake.company_name = intake.company_name || alias(['company_name','company','business','اسم الشركة','الشركة','النشاط']);\n"
                        "intake.industry = intake.industry || alias(['industry','sector','القطاع','المجال']);\n"
                        "intake.target_audience = intake.target_audience || alias(['target_audience','audience','الجمهور','الفئة']);\n"
                        "intake.company_link = intake.company_link || alias(['company_link','website','url','الرابط','الموقع']);\n"
                        "topic = topic !== 'موضوع جديد' ? topic : (alias(['topic','title','الموضوع']) || topic);\n"
                        "const requiredInterview = [\n"
                        "  { key: 'company_name', label: 'اسم النشاط/الشركة', value: intake.company_name },\n"
                        "  { key: 'industry', label: 'القطاع', value: intake.industry },\n"
                        "  { key: 'target_audience', label: 'الجمهور المستهدف', value: intake.target_audience },\n"
                        "  { key: 'company_link', label: 'رابط الموقع', value: intake.company_link },\n"
                        "  { key: 'topic', label: 'موضوع المحتوى', value: topic }\n"
                        "];\n"
                        "const missingInterview = requiredInterview.filter((f) => !String(f.value || '').trim()).map((f) => f.key);\n"
                        "const nextQuestionMap = {\n"
                        "  company_name: 'اكتب اسم النشاط/الشركة.',\n"
                        "  industry: 'وش القطاع بالضبط؟',\n"
                        "  target_audience: 'مين الجمهور المستهدف؟',\n"
                        "  company_link: 'ارسل رابط الموقع الرسمي.',\n"
                        "  topic: 'وش موضوع المحتوى المطلوب الآن؟'\n"
                        "};\n"
                        "const explicitConfirm = /^(confirm|generate|ابدأ|تأكيد|اعتماد)$/i.test(normalizedText);\n"
                        "const isDetailsCommand = /^(\\/)?(summary|ملخص|links|روابط|sheet\\s*summary|ملخص\\s*الشيت)$/i.test(normalizedText);\n"
                        "const isGenerationReady = (!isTelegram || missingInterview.length === 0 || explicitConfirm) && !isDetailsCommand;\n"
                        "const nextQuestion = missingInterview.length ? (nextQuestionMap[missingInterview[0]] || 'اكمل بيانات النشاط المطلوبة.') : '';\n"
                        "const summaryText = [\n"
                        f"  'اسم الـWorkflow: {name}',\n"
                        f"  'رابط الـWorkflow: ' + ({json.dumps(workflow_public_url)} || 'غير متوفر'),\n"
                        f"  'رابط الشيت: https://docs.google.com/spreadsheets/d/{sheet_id}/edit',\n"
                        f"  'رابط المستند: ' + ({json.dumps(default_doc_url)} || 'غير متوفر'),\n"
                        f"  'رابط العرض: ' + ({json.dumps(default_slides_url)} || 'غير متوفر'),\n"
                        "  'تقدر تطلب: summary | links | ملخص الشيت'\n"
                        "].join('\\n');\n"
                        "const interviewPrompt = missingInterview.length\n"
                        "  ? `عشان أبدأ التوليد، باقي: ${missingInterview.map((k) => requiredInterview.find((f) => f.key === k)?.label || k).join('، ')}.\\n${nextQuestion}`\n"
                        "  : 'البيانات مكتملة. ارسل: تأكيد أو generate للبدء.';\n"
                        "const brandContext = raw.brand_context || raw.website_summary || '';\n"
                        f"const defaultSystemPrompt = {json.dumps(system_prompt)};\n"
                        "const companyName = intake.company_name || 'هذه الشركة';\n"
                        "const post = raw.post || {\n"
                        "  title_ar: raw.title_ar || `كيف تطور ${companyName} خدماتها في ${topic}` ,\n"
                        "  title_en: raw.title_en || `How ${companyName} Improves Services: ${topic}` ,\n"
                        "  excerpt_ar: raw.excerpt_ar || `محتوى تسويقي وتشغيلي يوضح قيمة ${companyName} وخدماتها في السوق السعودي.`,\n"
                        "  excerpt_en: raw.excerpt_en || `Operational marketing content that highlights ${companyName} and its service value.`,\n"
                        "  content_ar: raw.content_ar || \"\",\n"
                        "  content_en: raw.content_en || \"\",\n"
                        "  tags: raw.tags || [String(companyName || '').toLowerCase(), String(intake.industry || 'services').toLowerCase(), 'saudi'],\n"
                        "  author: raw.author || companyName,\n"
                        "  status: raw.status || \"draft\"\n"
                        "};\n"
                        "const siteGuideline = raw.website_guideline || raw.tone_guideline || raw.brand_guideline || '';\n"
                        "const brandServices = raw.services || raw.service_list || raw.core_services || '';\n"
                        "const writerTask = raw.writer_task || `اكتب محتوى عربي سعودي احترافي لصالح الشركة التالية فقط: ${intake.company_name || 'غير محدد'}.\n"
                        "مهم جداً: المحتوى يجب أن يروّج لخدمات هذه الشركة فقط، وممنوع ذكر أو الترويج لأي شركة أخرى.\n"
                        "بيانات الشركة: الاسم=${intake.company_name || 'غير محدد'} | القطاع=${intake.industry || 'غير محدد'} | الجمهور=${intake.target_audience || 'غير محدد'} | الرابط=${intake.company_link || 'غير متوفر'}.\n"
                        "سياق الموقع/البراند المتاح: ${brandContext || 'لا يوجد ملخص موقع جاهز'}.\n"
                        "الخدمات المتاحة (إن وجدت): ${brandServices || 'استخرج الخدمات من رابط الشركة وسياق الموقع قبل الكتابة'}.\n"
                        "إرشادات النبرة (إن وجدت): ${siteGuideline || 'استخدم نبرة مهنية وودية وواضحة تشبه أسلوب الكتابة المرجعي، بدون نسخ أسماء أو عروضه'}.\n"
                        "المخرجات المطلوبة: 1) عنوان قوي 2) 5 Hooks مرتبطة بخدمات الشركة 3) نصوص قنوات اجتماعية 4) مقال موقع يدعم بيع خدمات الشركة 5) CTA واضح للتواصل مع الشركة نفسها.\n"
                        "الهيكل: المشكلة -> الأثر -> الحل الذي تقدمه الشركة -> دليل/سيناريو تطبيقي -> CTA.\n"
                        "طبّق هذا على موضوع: ${topic}.\n"
                        "واربط كل فقرة بمعلومات الشركة والرابط وليس بأي براند آخر.`;\n"
                        f"const defaultBudgetMode = {json.dumps(budget_mode_default)};\n"
                        "const requestedMode = String(raw.budget_mode || raw.priority_mode || raw.mode || '').trim().toLowerCase();\n"
                        "const budgetMode = ['lite','balanced','deep'].includes(requestedMode) ? requestedMode : defaultBudgetMode;\n"
                        "const budgetProfiles = {\n"
                        "  lite: {\n"
                        "    lookback_days: 90, competitors_limit: 5, max_items: 30, max_posts_per_platform: 10,\n"
                        "    max_posts_per_profile: 8, max_videos_per_profile: 6, trend_pool_size: 8,\n"
                        "    trend_topics_limit: 8, website_signals_limit: 8, profile_signals_limit: 8,\n"
                        "    platform_trends_limit: 3, prompt_profile_limit: 4, prompt_trend_limit: 4,\n"
                        "    prompt_competitor_limit: 4, openai_intel_chars: 3500\n"
                        "  },\n"
                        "  balanced: {\n"
                        "    lookback_days: 90, competitors_limit: 5, max_items: 60, max_posts_per_platform: 20,\n"
                        "    max_posts_per_profile: 12, max_videos_per_profile: 8, trend_pool_size: 12,\n"
                        "    trend_topics_limit: 12, website_signals_limit: 12, profile_signals_limit: 12,\n"
                        "    platform_trends_limit: 5, prompt_profile_limit: 6, prompt_trend_limit: 6,\n"
                        "    prompt_competitor_limit: 5, openai_intel_chars: 7000\n"
                        "  },\n"
                        "  deep: {\n"
                        "    lookback_days: 90, competitors_limit: 5, max_items: 140, max_posts_per_platform: 40,\n"
                        "    max_posts_per_profile: 20, max_videos_per_profile: 20, trend_pool_size: 20,\n"
                        "    trend_topics_limit: 20, website_signals_limit: 24, profile_signals_limit: 24,\n"
                        "    platform_trends_limit: 8, prompt_profile_limit: 10, prompt_trend_limit: 10,\n"
                        "    prompt_competitor_limit: 8, openai_intel_chars: 14000\n"
                        "  }\n"
                        "};\n"
                        "const marketBudget = budgetProfiles[budgetMode] || budgetProfiles.balanced;\n"
                        "const draftValue = String(raw.request_email_draft ?? '').trim().toLowerCase();\n"
                        "const requestEmailDraft = raw.request_email_draft === true || ['1','true','yes','draft','email_draft','send_draft_email'].includes(draftValue) || draftEmailFromTelegram;\n"
                        "return [{\n"
                        f"  json: {{ secret: \"{secret}\", request_id: requestId, topic, intake, post, content_writer: {{\n"
                        "    system_prompt: raw.system_prompt || defaultSystemPrompt,\n"
                        "    user_prompt: writerTask,\n"
                        "    language: \"ar-SA\",\n"
                        "    prompt_version: \"intake-company-tone-v2026-03-20\"\n"
                        "  },\n"
                        "  source: isTelegram ? 'telegram' : (raw.source || 'webhook'),\n"
                        "  telegram_chat_id: raw.message?.chat?.id || raw.edited_message?.chat?.id || '',\n"
                        "  telegram_text: normalizedText,\n"
                        "  approval_status: raw.approval_status || approvalFromTelegram || 'pending',\n"
                        "  trigger_status: raw.trigger_status || raw.send_status || raw.workflow_status || raw.status || raw.request_status || '',\n"
                        "  sent_status: raw.sent_status || raw.delivery_status || 'pending',\n"
                        "  budget_mode: budgetMode,\n"
                        "  market_budget: marketBudget,\n"
                        f"  workflow_name: {json.dumps(name)},\n"
                        f"  workflow_link: raw.workflow_link || {json.dumps(workflow_public_url)},\n"
                        f"  sheet_link: raw.sheet_link || 'https://docs.google.com/spreadsheets/d/{sheet_id}/edit',\n"
                        f"  doc_link: raw.doc_link || raw.google_doc_url || {json.dumps(default_doc_url)},\n"
                        f"  slides_link: raw.slides_link || raw.google_slides_url || {json.dumps(default_slides_url)},\n"
                        "  request_details_mode: isDetailsCommand,\n"
                        "  request_email_draft: requestEmailDraft,\n"
                        "  is_generation_ready: isGenerationReady,\n"
                        "  interview_state: { missing_fields: missingInterview, next_question: nextQuestion, prompt: (isDetailsCommand ? summaryText : interviewPrompt) }\n"
                        " }\n"
                        "}];"
                    ),
                },
            },
            {
                "id": "Interview Readiness Gate",
                "name": "Interview Readiness Gate",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [620, 280],
                "parameters": {
                    "conditions": {
                        "boolean": [
                            {
                                "value1": "={{ !!$json.is_generation_ready }}",
                                "operation": "true"
                            }
                        ]
                    }
                }
            },
            {
                "id": "Build Interview Pending Row",
                "name": "Build Interview Pending Row",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [840, 250],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const intake = input.intake || {};\n"
                        "const interview = input.interview_state || {};\n"
                        "const missing = Array.isArray(interview.missing_fields) ? interview.missing_fields.join('|') : '';\n"
                        "const detailsMode = !!input.request_details_mode;\n"
                        "return [{ json: {\n"
                        "  request_id: input.request_id || intake.request_id || '',\n"
                        "  created_at: new Date().toISOString(),\n"
                        "  company_name: intake.company_name || '',\n"
                        "  company_link: intake.company_link || '',\n"
                        "  industry: intake.industry || '',\n"
                        "  target_audience: intake.target_audience || '',\n"
                        "  topic: input.topic || '',\n"
                        "  approval_status: detailsMode ? 'details_response' : 'interview_pending',\n"
                        "  workflow_status: detailsMode ? 'details_response' : 'interview_pending',\n"
                        "  trigger_status: input.trigger_status || 'pending',\n"
                        "  sent_status: input.sent_status || 'pending',\n"
                        "  output: interview.prompt || 'البيانات غير مكتملة.',\n"
                        "  interview_missing_fields: missing,\n"
                        "  interview_next_question: interview.next_question || '',\n"
                        "  workflow_name: input.workflow_name || '',\n"
                        "  workflow_link: input.workflow_link || '',\n"
                        "  sheet_link: input.sheet_link || '',\n"
                        "  doc_link: input.doc_link || '',\n"
                        "  slides_link: input.slides_link || '',\n"
                        "  telegram_chat_id: input.telegram_chat_id || ''\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Append Interview Pending Row",
                "name": "Append Interview Pending Row",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [1040, 250],
                "onError": "continueRegularOutput",
                "parameters": {
                    "operation": "append",
                    "documentId": {
                        "mode": "id",
                        "value": sheet_id,
                    },
                    "sheetName": {
                        "mode": "name",
                        "value": results_sheet_tab,
                    },
                    "columns": {
                        "mappingMode": "autoMapInputData",
                        "value": {},
                    },
                    "options": {},
                },
            },
            {
                "id": "Build Telegram Run Summary",
                "name": "Build Telegram Run Summary",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [2470, 330],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const chatId = input.telegram_chat_id || '';\n"
                        "if (!chatId) return [];\n"
                        "const wfName = input.workflow_name || 'Ali Content Writer Engine 2026';\n"
                        "const wfLink = input.workflow_link || 'غير متوفر';\n"
                        "const sheetLink = input.sheet_link || 'غير متوفر';\n"
                        "const docLink = input.doc_link || 'غير متوفر';\n"
                        "const slidesLink = input.slides_link || 'غير متوفر';\n"
                        "const status = input.workflow_status || input.approval_status || 'pending';\n"
                        "const requestId = input.request_id || '';\n"
                        "const summaryBody = input.output || input.interview_state?.prompt || '';\n"
                        "const text = [\n"
                        "  `ملخص التنفيذ`,\n"
                        "  `Workflow: ${wfName}`,\n"
                        "  `Status: ${status}`,\n"
                        "  requestId ? `Request ID: ${requestId}` : '',\n"
                        "  '',\n"
                        "  `Workflow Link: ${wfLink}`,\n"
                        "  `Sheet: ${sheetLink}`,\n"
                        "  `Doc: ${docLink}`,\n"
                        "  `Slides: ${slidesLink}`,\n"
                        "  '',\n"
                        "  summaryBody ? `Details:\\n${String(summaryBody).slice(0,1200)}` : '',\n"
                        f"  {json.dumps('ملاحظة: ارسال تيليجرام معطل لأن TELEGRAM_BOT_TOKEN غير مضبوط في بيئة النشر.' if not telegram_send_enabled else '')},\n"
                        "  '',\n"
                        "  `Commands: summary | links | ملخص الشيت`\n"
                        "].filter(Boolean).join('\\n');\n"
                        "return [{ json: {\n"
                        "  ...input,\n"
                        f"  telegram_send_enabled: {json.dumps(telegram_send_enabled)},\n"
                        "  telegram_send_payload: {\n"
                        "    chat_id: chatId,\n"
                        "    text,\n"
                        "    disable_web_page_preview: true\n"
                        "  }\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Telegram Send Enabled Gate",
                "name": "Telegram Send Enabled Gate",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [2570, 330],
                "parameters": {
                    "conditions": {
                        "boolean": [
                            {
                                "value1": "={{ !!$json.telegram_send_enabled }}",
                                "operation": "true"
                            }
                        ]
                    }
                }
            },
            {
                "id": "Send Telegram Run Summary",
                "name": "Send Telegram Run Summary",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [2680, 330],
                "onError": "continueRegularOutput",
                "parameters": {
                    "method": "POST",
                    "url": f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{$json.telegram_send_payload}}",
                    "options": {},
                },
            },
            {
                "id": "Run Apify Market Intel",
                "name": "Run Apify Market Intel",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [700, 430],
                "onError": "continueRegularOutput",
                "parameters": {
                    "method": "POST",
                    "url": f"https://api.apify.com/v2/acts/{apify_actor_id}/run-sync-get-dataset-items?token={urllib.parse.quote(apify_token)}&clean=true&format=json",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": (
                        "={{ { companyName: $json.intake?.company_name || '', companyUrl: $json.intake?.company_link || '', startUrls: ($json.intake?.company_link ? [{ url: $json.intake.company_link }] : []), platforms: ['tiktok', 'linkedin', 'twitter', 'instagram'], includeCompetitors: true, competitorsLimit: ($json.market_budget?.competitors_limit || 5), includeTrending: true, lookbackDays: ($json.market_budget?.lookback_days || 90), includeProfiles: true, maxPostsPerProfile: ($json.market_budget?.max_posts_per_profile || 12), maxVideosPerProfile: ($json.market_budget?.max_videos_per_profile || 8), maxItems: ($json.market_budget?.max_items || 60), maxPostsPerPlatform: ($json.market_budget?.max_posts_per_platform || 20), twitterActorId: '%s', proxyConfiguration: { useApifyProxy: true } } }}"
                        % apify_twitter_actor_id
                    ),
                    "options": {},
                },
            },
            {
                "id": "Build Market Research Context",
                "name": "Build Market Research Context",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [900, 430],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const idx = typeof $itemIndex === 'number' ? $itemIndex : 0;\n"
                        "const base = ($items('Prepare Content Writer Input', 0, idx)?.[0]?.json) || ($items('Prepare Content Writer Input', 0, 0)?.[0]?.json) || {};\n"
                        "const intake = base.intake || {};\n"
                        "const budget = base.market_budget || {};\n"
                        "const topic = base.topic || '';\n"
                        "const data = $json;\n"
                        "const rows = Array.isArray(data) ? data : (Array.isArray(data?.items) ? data.items : (Array.isArray(data?.data) ? data.data : (Array.isArray(data?.body) ? data.body : [])));\n"
                        "const now = new Date();\n"
                        "const lookbackDays = Number(budget.lookback_days || 90);\n"
                        "const lookbackStart = new Date(now.getTime() - lookbackDays * 24 * 60 * 60 * 1000);\n"
                        "const parseDate = (r) => {\n"
                        "  const raw = r.publishedAt || r.createdAt || r.timestamp || r.date || r.postedAt || '';\n"
                        "  const d = raw ? new Date(raw) : null;\n"
                        "  return (d && !Number.isNaN(d.getTime())) ? d : null;\n"
                        "};\n"
                        "const inWindow = (r) => {\n"
                        "  const d = parseDate(r);\n"
                        "  if (!d) return true;\n"
                        "  return d >= lookbackStart && d <= now;\n"
                        "};\n"
                        "const toNum = (v) => { const n = Number(v); return Number.isFinite(n) ? n : 0; };\n"
                        "const scorePost = (r) => {\n"
                        "  const views = toNum(r.views || r.viewCount || r.videoViews || r.playCount);\n"
                        "  const likes = toNum(r.likes || r.likeCount || r.reactions);\n"
                        "  const comments = toNum(r.comments || r.commentCount);\n"
                        "  const shares = toNum(r.shares || r.shareCount || r.retweets || r.reposts);\n"
                        "  const engagementRate = toNum(r.engagementRate || r.engagement || r.er);\n"
                        "  return (views * 0.2) + (likes * 2) + (comments * 3) + (shares * 4) + (engagementRate * 1000);\n"
                        "};\n"
                        "const platformKey = (r) => String(r.platform || r.source || r.network || '').toLowerCase();\n"
                        "const textOf = (r) => String(r.text || r.caption || r.content || r.description || r.title || '').trim();\n"
                        "const urlOf = (r) => String(r.url || r.postUrl || r.link || '').trim();\n"
                        "const scored = rows.filter(inWindow).map((r) => ({\n"
                        "  platform: platformKey(r),\n"
                        "  text: textOf(r),\n"
                        "  url: urlOf(r),\n"
                        "  competitor: String(r.competitor || r.competitorName || r.brand || '').trim(),\n"
                        "  score: scorePost(r),\n"
                        "  raw: r,\n"
                        "})).filter((r) => r.text || r.url);\n"
                        "const topGlobal = [...scored].sort((a,b) => b.score - a.score).slice(0, Number(budget.trend_pool_size || 12));\n"
                        "const byPlatform = { tiktok: [], linkedin: [], twitter: [], instagram: [] };\n"
                        "for (const p of topGlobal) {\n"
                        "  const key = p.platform.includes('tik') ? 'tiktok' : p.platform.includes('link') ? 'linkedin' : (p.platform.includes('x') || p.platform.includes('twit') ? 'twitter' : (p.platform.includes('insta') ? 'instagram' : ''));\n"
                        "  if (!key) continue;\n"
                        "  if (byPlatform[key].length < Number(budget.platform_trends_limit || 5)) byPlatform[key].push(p);\n"
                        "}\n"
                        "const competitorRows = topGlobal.filter((p) => p.competitor && intake.company_name && p.competitor.toLowerCase() !== String(intake.company_name).toLowerCase()).slice(0, Number(budget.competitors_limit || 5));\n"
                        "const isEventExpired = (text) => {\n"
                        "  const t = String(text || '').toLowerCase();\n"
                        "  const mmdd = (d) => `${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;\n"
                        "  const today = mmdd(now);\n"
                        "  const fixed = [\n"
                        "    { keywords: ['national day', 'اليوم الوطني'], date: '09-23' },\n"
                        "    { keywords: ['founding day', 'يوم التأسيس'], date: '02-22' },\n"
                        "    { keywords: ['new year', 'رأس السنة'], date: '01-01' },\n"
                        "    { keywords: ['black friday', 'الجمعة البيضاء'], date: '11-29' },\n"
                        "    { keywords: ['valentine', 'عيد الحب'], date: '02-14' }\n"
                        "  ];\n"
                        "  for (const ev of fixed) {\n"
                        "    if (ev.keywords.some((k) => t.includes(k)) && today > ev.date) return true;\n"
                        "  }\n"
                        "  return false;\n"
                        "};\n"
                        "const websiteSignals = rows\n"
                        "  .map((r) => String(r.pageTitle || r.title || r.h1 || r.metaDescription || r.description || '').trim())\n"
                        "  .filter(Boolean)\n"
                        "  .slice(0, Number(budget.website_signals_limit || 12));\n"
                        "const websiteSummary = websiteSignals.slice(0, 8).join(' | ');\n"
                        "const trendTopics = topGlobal\n"
                        "  .map((p) => p.text)\n"
                        "  .filter(Boolean)\n"
                        "  .filter((t) => !isEventExpired(t))\n"
                        "  .map((t) => t.slice(0, 160))\n"
                        "  .slice(0, Number(budget.trend_topics_limit || 12));\n"
                        "const profileSignals = rows.filter(inWindow)\n"
                        "  .map((r) => String(r.profileBio || r.bio || r.profileDescription || r.channelDescription || '').trim())\n"
                        "  .filter(Boolean)\n"
                        "  .slice(0, Number(budget.profile_signals_limit || 12));\n"
                        "const competitorInsights = competitorRows.map((p) => ({ competitor: p.competitor, platform: p.platform, idea: p.text.slice(0, 200), score: Math.round(p.score), url: p.url }));\n"
                        "const marketIntel = {\n"
                        "  collected_items: rows.filter(inWindow).length,\n"
                        "  lookback_days: lookbackDays,\n"
                        "  competitors_limit: 5,\n"
                        "  topic,\n"
                        "  website_summary: websiteSummary,\n"
                        "  profile_summary: profileSignals.join(' | '),\n"
                        "  top_topics: trendTopics,\n"
                        "  by_platform: Object.fromEntries(Object.entries(byPlatform).map(([k,v]) => [k, v.map((p) => ({ text: p.text.slice(0,200), score: Math.round(p.score), url: p.url }))])),\n"
                        "  competitors: competitorInsights,\n"
                        "};\n"
                        "const enrichedPrompt = `${base.content_writer?.user_prompt || ''}\n\n[Market Intel]\nMode: ${base.budget_mode || 'balanced'}. Window: last ${lookbackDays} days. Competitors analyzed: up to ${Number(budget.competitors_limit || 5)}.\nCompany URL summary: ${websiteSummary || 'not available'}\nProfile/bio signals: ${(profileSignals.slice(0, Number(budget.prompt_profile_limit || 6)).join(' || ') || 'not available')}\nTop trending topics by engagement (expired events removed): ${(trendTopics.slice(0, Number(budget.prompt_trend_limit || 6)).join(' || ') || 'not available')}\nCompetitor angles from latest posts/videos: ${(competitorInsights.map((c) => `${c.competitor}: ${c.idea}`).slice(0, Number(budget.prompt_competitor_limit || 5)).join(' || ') || 'not available')}\nUse this intelligence to produce fresh, non-duplicated content for ${intake.company_name || 'the intake company'} only.`;\n"
                        "return [{ json: {\n"
                        "  ...base,\n"
                        "  market_intel: marketIntel,\n"
                        "  website_summary: websiteSummary,\n"
                        "  top_topics: trendTopics,\n"
                        "  competitor_insights: competitorInsights,\n"
                        "  content_writer: { ...(base.content_writer || {}), user_prompt: enrichedPrompt, prompt_version: 'intake-company-market-intel-v2026-03-20' },\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Build OpenAI Content Request",
                "name": "Build OpenAI Content Request",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1110, 430],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const intake = input.intake || {};\n"
                        "const intel = input.market_intel || {};\n"
                        "const budget = input.market_budget || {};\n"
                        "const topic = input.topic || '';\n"
                        "const systemPrompt = input.content_writer?.system_prompt || '';\n"
                        "const userPrompt = input.content_writer?.user_prompt || '';\n"
                        "const formatGuide = `Return ONLY valid JSON with this exact schema: {\\\"post\\\":{\\\"title_ar\\\":string,\\\"title_en\\\":string,\\\"excerpt_ar\\\":string,\\\"excerpt_en\\\":string,\\\"content_ar\\\":string,\\\"content_en\\\":string,\\\"tags\\\":string[],\\\"author\\\":string,\\\"status\\\":\\\"draft\\\"},\\\"hooks\\\":string[5],\\\"seo\\\":{\\\"seo_title\\\":string,\\\"seo_description\\\":string,\\\"seo_keywords\\\":string,\\\"target_keyword\\\":string},\\\"platform_content\\\":{\\\"instagram\\\":string,\\\"x\\\":string,\\\"tiktok\\\":string,\\\"facebook\\\":string,\\\"linkedin\\\":string,\\\"website_article\\\":string,\\\"caption\\\":string},\\\"design\\\":{\\\"post_type\\\":string,\\\"image_prompt\\\":string,\\\"banana_prompt\\\":string},\\\"cta\\\":string,\\\"audience\\\":string,\\\"brand_guideline\\\":string,\\\"reasoning_summary\\\":string }`;\n"
                        "const intelChars = Number(budget.openai_intel_chars || 7000);\n"
                        "const prompt = `Write fresh Arabic-first content for company context: ${intake.company_name || ''}.\\nIndustry: ${intake.industry || ''}. Audience: ${intake.target_audience || ''}. URL: ${intake.company_link || ''}. Topic: ${topic}.\\n\\nUse these intelligence inputs: ${JSON.stringify(intel).slice(0,intelChars)}\\n\\nCritical role: write as an internal employee/expert from inside ${intake.company_name || 'the company'} using a confident first-person plural tone (\\\"نحن\\\") where suitable.\\n\\nRules: 1) Keep content business-aware and research-led, not direct selling copy. 2) Never promote other brands. 3) Use last 90 days signals only. 4) Ignore expired occasion/event angles. 5) Analyze up to 5 competitors and recent content to identify topic gaps. 6) Keep Saudi market relevance. 7) Focus on educational, awareness, operational and market-insight angles. 8) Mention concrete context/services/evidence from intake or research. 9) CTA should be informational (learn more/follow updates), not sales pressure. 10) DO NOT output outline labels like \\\"Hook:\\\", \\\"المشهد 1\\\", \\\"1)\\\", \\\"2)\\\". Return final ready-to-publish copy with complete sentences and actual answers/solutions. 11) For TikTok, provide final spoken script and caption, not scene placeholders.\\n\\nStyle reference only: ${systemPrompt}\\n\\nTask details: ${userPrompt}\\n\\n${formatGuide}`;\n"
                        "return [{ json: {\n"
                        "  ...input,\n"
                        "  openai_payload: {\n"
                        f"    model: {json.dumps(openai_model)},\n"
                        "    temperature: 0.4,\n"
                        "    messages: [\n"
                        "      { role: 'system', content: 'You are a senior Arabic content lead writing from inside the intake company team. Output strict JSON only and provide final publish-ready copy.' },\n"
                        "      { role: 'user', content: prompt }\n"
                        "    ]\n"
                        "  }\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Generate Content With OpenAI",
                "name": "Generate Content With OpenAI",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [1320, 430],
                "onError": "continueRegularOutput",
                "parameters": {
                    "method": "POST",
                    "url": "https://api.openai.com/v1/chat/completions",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {"name": "Authorization", "value": f"Bearer {openai_api_key}"},
                            {"name": "Content-Type", "value": "application/json"}
                        ]
                    },
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{$json.openai_payload}}",
                    "options": {},
                },
            },
            {
                "id": "Parse OpenAI Generated Content",
                "name": "Parse OpenAI Generated Content",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1530, 430],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const idx = typeof $itemIndex === 'number' ? $itemIndex : 0;\n"
                        "const base = ($items('Build OpenAI Content Request', 0, idx)?.[0]?.json) || ($items('Build OpenAI Content Request', 0, 0)?.[0]?.json) || {};\n"
                        "const response = $json || {};\n"
                        "let rawText = response?.choices?.[0]?.message?.content || '';\n"
                        "if (Array.isArray(rawText)) rawText = rawText.map((x) => x?.text || '').join('\\n');\n"
                        "rawText = String(rawText || '').trim();\n"
                        "if (rawText.startsWith('```')) {\n"
                        "  rawText = rawText.replace(/^```[a-zA-Z]*\\n?/, '').replace(/```$/, '').trim();\n"
                        "}\n"
                        "let parsed = {};\n"
                        "try { parsed = JSON.parse(rawText || '{}'); } catch (e) { parsed = {}; }\n"
                        "const postIn = base.post || {};\n"
                        "const postOut = parsed.post || {};\n"
                        "const hooks = Array.isArray(parsed.hooks) ? parsed.hooks.filter(Boolean).slice(0,5) : (base.hooks || []);\n"
                        "while (hooks.length < 5) hooks.push('');\n"
                        "const seo = parsed.seo || base.seo || {};\n"
                        "const platformContent = parsed.platform_content || {};\n"
                        "const design = parsed.design || {};\n"
                        "const post = {\n"
                        "  title_ar: postOut.title_ar || postIn.title_ar || base.topic || '',\n"
                        "  title_en: postOut.title_en || postIn.title_en || '',\n"
                        "  excerpt_ar: postOut.excerpt_ar || postIn.excerpt_ar || '',\n"
                        "  excerpt_en: postOut.excerpt_en || postIn.excerpt_en || '',\n"
                        "  content_ar: postOut.content_ar || postIn.content_ar || '',\n"
                        "  content_en: postOut.content_en || postIn.content_en || '',\n"
                        "  tags: Array.isArray(postOut.tags) ? postOut.tags : (Array.isArray(postIn.tags) ? postIn.tags : []),\n"
                        "  author: postOut.author || postIn.author || (base.intake?.company_name || ''),\n"
                        "  status: 'draft',\n"
                        "};\n"
                        "return [{ json: {\n"
                        "  ...base,\n"
                        "  post,\n"
                        "  hooks,\n"
                        "  seo: {\n"
                        "    seo_title: seo.seo_title || post.title_ar || '',\n"
                        "    seo_description: seo.seo_description || post.excerpt_ar || '',\n"
                        "    seo_keywords: seo.seo_keywords || '',\n"
                        "    target_keyword: seo.target_keyword || '',\n"
                        "  },\n"
                        "  cta: parsed.cta || base.cta || `اطلع على المستجدات الرسمية من ${base.intake?.company_name || 'الجهة'} حول هذا الموضوع.`,\n"
                        "  platform_content: {\n"
                        "    instagram: platformContent.instagram || '',\n"
                        "    x: platformContent.x || '',\n"
                        "    tiktok: platformContent.tiktok || '',\n"
                        "    facebook: platformContent.facebook || '',\n"
                        "    linkedin: platformContent.linkedin || '',\n"
                        "    website_article: platformContent.website_article || '',\n"
                        "    caption: platformContent.caption || ''\n"
                        "  },\n"
                        "  design: {\n"
                        "    post_type: design.post_type || '',\n"
                        "    image_prompt: design.image_prompt || '',\n"
                        "    banana_prompt: design.banana_prompt || ''\n"
                        "  },\n"
                        "  audience: parsed.audience || base.intake?.target_audience || base.audience || '',\n"
                        "  brand_guideline: parsed.brand_guideline || base.website_summary || '',\n"
                        "  generation_reasoning: parsed.reasoning_summary || '',\n"
                        "  prompt_text: base.content_writer?.user_prompt || base.prompt_text || '',\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Normalize Blog Metadata",
                "name": "Normalize Blog Metadata",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [700, 280],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const post = input.post || {};\n"
                        "const seo = input.seo || {};\n"
                        "const hooksInput = input.hooks || post.hooks || [];\n"
                        "let hooks = Array.isArray(hooksInput)\n"
                        "  ? hooksInput.filter(Boolean)\n"
                        "  : String(hooksInput || '').split('|').map(s => s.trim()).filter(Boolean);\n"
                        "const company = input.intake?.company_name || input.company_name || 'الشركة';\n"
                        "const topic = input.topic || post.title_ar || 'الخدمة';\n"
                        "const writerTask = String(input.content_writer?.user_prompt || input.prompt_text || input.writer_task || '').trim();\n"
                        "const servicePool = [];\n"
                        "const serviceBlock = writerTask.split('الخدمات')[1] || writerTask.split('خدمات')[1] || '';\n"
                        "const rawServiceText = [serviceBlock, writerTask].filter(Boolean).join(' | ');\n"
                        "for (const part of rawServiceText.split(/[,|؛،\\n\\.]/)) {\n"
                        "  const s = String(part || '').replace(/[:\\-]/g, ' ').trim();\n"
                        "  if (!s) continue;\n"
                        "  if (s.length < 4 || s.length > 60) continue;\n"
                        "  if (/=|https?|www\\.|\\/|\\||قطاع|جمهور|رابط|المتاحة|استخرج|اكتب|محتوى|مهم|ممنوع|اربط|مثال|الشركة|السعودي|الهيكل|cta/i.test(s)) continue;\n"
                        "  if (!servicePool.includes(s)) servicePool.push(s);\n"
                        "}\n"
                        "let topServices = servicePool.slice(0, 4);\n"
                        "const companyLower = String(company || '').toLowerCase();\n"
                        "const linkLower = String(input.intake?.company_link || input.company_link || '').toLowerCase();\n"
                        "if (companyLower.includes('غرفة جدة') || linkLower.includes('jcci.org.sa')) {\n"
                        "  topServices = ['التصديق الإلكتروني', 'الاشتراكات وتجديد العضوية', 'اللجان القطاعية وتمثيل الأعمال', 'برامج التدريب والتأهيل'];\n"
                        "}\n"
                        "const generatedHooks = [\n"
                        "  `كيف تساعد ${company} الشركات في ${topic} بخدمات عملية؟`,\n"
                        "  `أهم 3 تحديات تواجه الشركات في ${topic} وكيف تعالجها ${company}`,\n"
                        "  `خطة تنفيذية من ${company} لتحسين كفاءة الأعمال في ${topic}`,\n"
                        "  `متى تحتاج شركتك تدخل ${company} الآن وليس لاحقاً؟`,\n"
                        "  `دليل سريع: اختيار الخدمة الأنسب من ${company} حسب احتياجك`\n"
                        "];\n"
                        "for (const h of generatedHooks) { if (hooks.length < 5) hooks.push(h); }\n"
                        "hooks = hooks.slice(0, 5);\n"
                        "const servicesLine = topServices.length ? `أبرز الخدمات: ${topServices.join(' | ')}.` : '';\n"
                        "const defaultExcerpt = `ملخص تنفيذي يوضح المشهد العملي في ${topic} وعلاقة ذلك بدور ${company} داخل بيئة الأعمال في جدة.`;\n"
                        "const defaultBody = [\n"
                        "  `تواجه الشركات في جدة تحديات تشغيلية وتسويقية متكررة في ${topic} تتطلب حلولاً واضحة وقابلة للتنفيذ.`,\n"
                        "  servicesLine || `يبدأ فريق ${company} بتشخيص احتياج العميل ثم يربط كل مرحلة تنفيذية بمؤشر أداء واضح.`,\n"
                        "  `يعتمد نموذج العمل لدى ${company} على تحويل الاحتياج إلى خطة: تحليل الوضع الحالي، اختيار الخدمة المناسبة، تنفيذ تدريجي، ومتابعة الأثر.`,\n"
                        "  `بهذا الأسلوب تحصل الشركة على سرعة أعلى في الإنجاز وجودة أفضل في الخدمة وتجربة أكثر احترافية للعملاء.`,\n"
                        "  `للاطلاع على التفاصيل الرسمية والتحديثات، يمكن الرجوع إلى ${company} عبر ${input.intake?.company_link || input.company_link || 'قنوات التواصل الرسمية'}.`\n"
                        "].filter(Boolean).join('\\n\\n');\n"
                        "const approvalRaw = input.approval_status ?? input.approval ?? post.approval_status ?? 'pending';\n"
                        "const approvalStr = String(approvalRaw).toLowerCase();\n"
                        "const approvedValues = ['approved', 'yes', 'true', '1'];\n"
                        "const approvedByInput = approvalRaw === true || approvedValues.includes(approvalStr);\n"
                        "const textBundle = [post.title_ar || '', post.excerpt_ar || '', post.content_ar || '', hooks.join(' | ')].join('\\n').toLowerCase();\n"
                        "const companyNorm = String(company || '').trim();\n"
                        "const companyMentions = companyNorm ? ((textBundle.match(new RegExp(companyNorm.toLowerCase().replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'), 'g')) || []).length) : 0;\n"
                        "const serviceMentions = topServices.filter((s) => textBundle.includes(String(s).toLowerCase())).length;\n"
                        "const genericMarkers = ['احجز demo', 'اشتر', 'عرض حصري', 'تواصل الآن', 'سارع', 'لا تفوت', 'اقتراح', 'فكرة محتوى', 'يمكن الحديث', 'اتجاه مقترح', 'موضوع مقترح', 'hook:', 'المشهد 1', 'المشهد 2', 'المشهد 3'];\n"
                        "const genericHit = genericMarkers.some((m) => textBundle.includes(m));\n"
                        "const minLenOk = String(post.content_ar || '').trim().length >= 320;\n"
                        "const businessEvidenceOk = companyMentions >= 2 && (serviceMentions >= 2 || topServices.length === 0);\n"
                        "const hardReject = !minLenOk || !businessEvidenceOk || genericHit;\n"
                        "const isApproved = approvedByInput && !hardReject;\n"
                        "const validationStatus = hardReject ? 'rejected_generic_content' : 'passed_business_specific';\n"
                        "const validationFailures = [];\n"
                        "if (!minLenOk) validationFailures.push('content_too_short');\n"
                        "if (!businessEvidenceOk) validationFailures.push('missing_business_evidence');\n"
                        "if (genericHit) validationFailures.push('generic_or_sales_wording');\n"
                        "const draftRaw = input.request_email_draft ?? input.request_email ?? false;\n"
                        "const draftStr = String(draftRaw).toLowerCase();\n"
                        "const draftValues = ['true', '1', 'yes', 'draft_email', 'email', 'send_draft_email'];\n"
                        "const isDraftEmail = draftRaw === true || draftValues.includes(draftStr);\n"
                        "const normalized = {\n"
                        "  ...input,\n"
                        "  request_email_draft: isDraftEmail,\n"
                        "  request_id: input.request_id || input.intake?.request_id || '',\n"
                        "  row_number: input.row_number || input.intake?.row_number || '',\n"
                        "  intake: {\n"
                        "    request_id: input.request_id || input.intake?.request_id || '',\n"
                        "    row_number: input.row_number || input.intake?.row_number || '',\n"
                        "    created_at: input.intake?.created_at || input.created_at || '',\n"
                        "    company_name: input.intake?.company_name || input.company_name || input.company || '',\n"
                        "    industry: input.intake?.industry || input.industry || '',\n"
                        "    target_audience: input.intake?.target_audience || input.target_audience || input.audience || '',\n"
                        "    company_link: input.intake?.company_link || input.company_link || input.website || input.url || ''\n"
                        "  },\n"
                        "  validation_status: validationStatus,\n"
                        "  validation_failures: validationFailures.join('|'),\n"
                        "  post: {\n"
                        "    ...post,\n"
                        "    excerpt_ar: post.excerpt_ar || defaultExcerpt,\n"
                        "    content_ar: post.content_ar || defaultBody,\n"
                        "    status: isApproved ? 'published' : (post.status || 'draft')\n"
                        "  },\n"
                        "  seo: {\n"
                        "    seo_title: seo.seo_title || input.seo_title || post.title_ar || '',\n"
                        "    seo_description: seo.seo_description || input.seo_description || post.excerpt_ar || '',\n"
                        "    seo_keywords: seo.seo_keywords || input.seo_keywords || (post.tags || []).join(', '),\n"
                        "    target_keyword: seo.target_keyword || input.target_keyword || ''\n"
                        "  },\n"
                        "  hooks,\n"
                        "  approval: {\n"
                        "    is_approved: isApproved,\n"
                        "    status: isApproved ? 'approved' : validationStatus,\n"
                        "    approved_by: input.approved_by || '',\n"
                        "    approval_notes: input.approval_notes || '',\n"
                        "    approval_date: input.approval_date || ''\n"
                        "  }\n"
                        "};\n"
                        "return [{ json: normalized }];"
                    ),
                },
            },
            {
                "id": "Build Request Registry Row",
                "name": "Build Request Registry Row",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [920, 150],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const intake = input.intake || {};\n"
                        "return [{ json: {\n"
                        "  request_id: input.request_id || intake.request_id || '',\n"
                        "  row_number: intake.row_number || input.row_number || '',\n"
                        "  created_at: new Date().toISOString(),\n"
                        "  topic: input.topic || '',\n"
                        "  company_name: intake.company_name || '',\n"
                        "  industry: intake.industry || '',\n"
                        "  target_audience: intake.target_audience || '',\n"
                        "  company_link: intake.company_link || '',\n"
                        "  trigger_status: input.source === 'sheet_intake' ? 'pending' : (input.trigger_status || ''),\n"
                        "  sent_status: input.sent_status || 'pending',\n"
                        "  prompt_text: input.content_writer?.user_prompt || '',\n"
                        "  approval_status: input.approval?.status || 'pending',\n"
                        "  workflow_status: 'triggered',\n"
                        "  writer_prompt_version: input.content_writer?.prompt_version || '',\n"
                        "  language: input.content_writer?.language || 'ar-SA'\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Append Request Registry Row",
                                "onError": "continueRegularOutput",
                "name": "Append Request Registry Row",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [1140, 150],
                "parameters": {
                    "operation": "append",
                    "documentId": {
                        "mode": "id",
                        "value": sheet_id,
                    },
                    "sheetName": {
                        "mode": "name",
                        "value": request_sheet_tab,
                    },
                    "columns": {
                        "mappingMode": "autoMapInputData",
                        "value": {},
                    },
                    "options": {},
                },
            },
            {
                "id": "Draft Email Gate",
                "name": "Draft Email Gate",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [1360, 120],
                "parameters": {
                    "conditions": {
                        "boolean": [
                            {
                                "value1": "={{ !!$json.request_email_draft && String($json.request_email_draft).toLowerCase() !== 'false' }}",
                                "operation": "true",
                            }
                        ]
                    }
                },
            },
            {
                "id": "Approval Gate",
                "name": "Approval Gate",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [1360, 280],
                "parameters": {
                    "conditions": {
                        "boolean": [
                            {
                                "value1": "={{ !!$json.approval?.is_approved && String($json.approval?.is_approved).toLowerCase() !== 'false' && String($json.validation_status || '').toLowerCase() !== 'rejected_generic_content' }}",
                                "operation": "true",
                            }
                        ]
                    }
                },
            },
            {
                "id": "Build Organized Draft Email",
                "name": "Build Organized Draft Email",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1580, 120],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const intake = input.intake || {};\n"
                        "const topic = input.topic || 'موضوع جديد';\n"
                        "const company = intake.company_name || 'نشاطكم';\n"
                        "const industry = intake.industry || 'قطاعكم';\n"
                        "const audience = intake.target_audience || 'فريق التشغيل';\n"
                        "const workflowLabel = 'Ali Content Writer workflow';\n"
                        "const subject = `مسودة إيميل مرتبة | ${topic}`;\n"
                        "const preview = `مسودة إيميل منظمة لقطاع ${industry} مع CTA واضح. المصدر: ${workflowLabel}.`;\n"
                        "const textBody = [\n"
                        "  'السلام عليكم، يعطيكم العافية.',\n"
                        "  '',\n"
                        "  `جهزنا لكم مسودة إيميل تسويقي حول: ${topic}.`,\n"
                        "  '',\n"
                        "  'المشكلة:',\n"
                        "  'ضغط القنوات وتشتت المتابعة يسبب تأخير الرد وضياع فرص.',\n"
                        "  '',\n"
                        "  'الأثر:',\n"
                        "  'نزول التحويل وزيادة العبء على الفريق.',\n"
                        "  '',\n"
                        "  'الحل:',\n"
                        "  `خدمات ${company} تعالج التحدي بطريقة عملية وتساعد العميل يحقق نتيجة واضحة بسرعة أعلى.`,\n"
                        "  '',\n"
                        "  'النتائج المتوقعة:',\n"
                        "  'سرعة رد أعلى، متابعة أدق، وتحويل أفضل.',\n"
                        "  '',\n"
                        "  'الخطوة القادمة:',\n"
                        "  'إذا مناسب لكم، نرتب Demo بسيط ونوضح خطة التنفيذ.',\n"
                        "  '',\n"
                        "  `المصدر: ${workflowLabel}`\n"
                        "].join('\\n');\n"
                        "const htmlBody = `\n"
                        "<div dir=\"rtl\" style=\"font-family:Tahoma,Arial,sans-serif;line-height:1.8;color:#0f172a\">\n"
                        "  <p>السلام عليكم، يعطيكم العافية.</p>\n"
                        "  <p>جهزنا لكم مسودة إيميل تسويقي حول: <strong>${topic}</strong></p>\n"
                        "  <h3>المشكلة</h3><p>ضغط القنوات وتشتت المتابعة يسبب تأخير الرد وضياع فرص.</p>\n"
                        "  <h3>الأثر</h3><p>نزول التحويل وزيادة العبء على الفريق.</p>\n"
                        "  <h3>الحل</h3><p>خدمات ${company} تعالج التحدي بطريقة عملية وتساعد العميل يحقق نتيجة واضحة بسرعة أعلى.</p>\n"
                        "  <h3>النتائج المتوقعة</h3><p>سرعة رد أعلى، متابعة أدق، وتحويل أفضل.</p>\n"
                        "  <h3>الخطوة القادمة</h3><p>إذا مناسب لكم، نرتب Demo بسيط ونوضح خطة التنفيذ.</p>\n"
                        "  <p><strong>المصدر:</strong> ${workflowLabel}</p>\n"
                        "</div>`;\n"
                        "return [{ json: {\n"
                        "  ...input,\n"
                        "  approval_status: 'draft_email',\n"
                        "  publish_target: 'email_draft',\n"
                        "  workflow_status: 'done',\n"
                        "  trigger_status: 'done',\n"
                        "  sent_status: 'done',\n"
                        "  company_name: company,\n"
                        "  audience: input.audience || audience,\n"
                        "  email_subject: subject,\n"
                        "  email_preview: preview,\n"
                        "  email_body_text: textBody,\n"
                        "  email_body_html: htmlBody,\n"
                        "  email_source_workflow: workflowLabel\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Append Draft Email Row To Sheet",
                "name": "Append Draft Email Row To Sheet",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [1800, 120],
                "onError": "continueRegularOutput",
                "parameters": {
                    "operation": "append",
                    "documentId": {
                        "mode": "id",
                        "value": sheet_id,
                    },
                    "sheetName": {
                        "mode": "name",
                        "value": results_sheet_tab,
                    },
                    "columns": {
                        "mappingMode": "autoMapInputData",
                        "value": {},
                    },
                    "options": {},
                },
            },
            {
                "id": "Publish To Site",
                "name": "Publish To Site",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [2270, 390],
                "onError": "continueRegularOutput",
                "parameters": {
                    "method": "POST",
                    "url": target_url,
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{$json}}",
                    "options": {},
                },
            },
            {
                "id": "Build Sheet Row (Approved)",
                "name": "Build Sheet Row (Approved)",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1580, 390],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const intake = input.intake || {};\n"
                        "const post = input.post || {};\n"
                        "const seo = input.seo || {};\n"
                        "const hooks = input.hooks || [];\n"
                        "const tags = Array.isArray(post.tags) ? post.tags : [];\n"
                        "const hook1 = hooks[0] || '';\n"
                        "const hook2 = hooks[1] || '';\n"
                        "const hook3 = hooks[2] || '';\n"
                        "const hook4 = hooks[3] || '';\n"
                        "const hook5 = hooks[4] || '';\n"
                        "const titleAr = post.title_ar || input.topic || '';\n"
                        "const bodyAr = post.content_ar || '';\n"
                        "const excerptAr = post.excerpt_ar || '';\n"
                        "const cta = input.cta || `للمزيد من المعلومات الرسمية حول الموضوع، تابع تحديثات ${intake.company_name || 'الجهة'}.`;\n"
                        "const platform = input.platform_content || {};\n"
                        "const design = input.design || {};\n"
                        "const companyName = intake.company_name || input.company_name || '';\n"
                        "const companyLink = intake.company_link || input.company_link || '';\n"
                        "const topic = input.topic || '';\n"
                        "const requestId = input.request_id || intake.request_id || '';\n"
                        "const baseNarrative = bodyAr || `${titleAr}\\n\\n${excerptAr}\\n\\n${cta}`;\n"
                        "const summaryLine = excerptAr || hook1 || titleAr;\n"
                        "const fallbackInstagram = `${titleAr}\\n\\n${summaryLine}\\n\\nفي هذا الموضوع نستعرض التحديات العملية، وكيف نتعامل معها داخل ${companyName || 'الشركة'} بخطوات واضحة قابلة للتطبيق، مع أمثلة مباشرة من واقع السوق.\\n\\n${cta}`;\n"
                        "const fallbackX = `${titleAr} | ${summaryLine} | نشارك هنا قراءة عملية لما يحدث في السوق وكيفية التعامل معه بشكل مهني داخل ${companyName || 'الشركة'}. | ${cta}`;\n"
                        "const fallbackTikTok = `في هذا الفيديو نشرح واقع ${topic} بلغة واضحة، ونوضح أبرز التحديات الحالية، ثم نقدم معالجة عملية مبنية على خبرة الفريق داخل ${companyName || 'الشركة'} مع مثال تطبيقي مختصر. ${cta}`;\n"
                        "const fallbackFacebook = `${baseNarrative}\\n\\nنستعرض في هذا المنشور تفاصيل أكثر حول التحديات والحلول العملية المرتبطة بالموضوع، مع نقاط قابلة للتطبيق مباشرة.\\n\\n${cta}`;\n"
                        "const fallbackLinkedin = `${titleAr}\\n\\n${summaryLine}\\n\\nنقدم قراءة مهنية مبنية على مؤشرات السوق، مع توضيح ما تغيّر خلال الفترة الأخيرة وكيف نترجم ذلك إلى خطوات تنفيذية داخل الفريق.\\n\\n${cta}`;\n"
                        "const instagram = String(platform.instagram || '').trim() || fallbackInstagram;\n"
                        "const xText = String(platform.x || '').trim() || fallbackX;\n"
                        "const tiktok = String(platform.tiktok || '').trim() || fallbackTikTok;\n"
                        "const facebook = String(platform.facebook || '').trim() || fallbackFacebook;\n"
                        "const linkedin = String(platform.linkedin || '').trim() || fallbackLinkedin;\n"
                        "const imageText = titleAr;\n"
                        "const caption = `${excerptAr} ${cta}`.trim();\n"
                        "const imagePrompt = String(design.image_prompt || '').trim() || `Modern social visual for ${intake.company_name || 'brand'} in Saudi market, clean geometry, bold typography, blue gradient accents.`;\n"
                        "const blogArticle = String(platform.website_article || '').trim() || bodyAr || `${titleAr}\\n\\n${excerptAr}`;\n"
                        "const keywords = seo.seo_keywords || tags.join(', ');\n"
                        "const hashtags = tags.map(t => `#${String(t).replace(/\\s+/g,'')}`).join(' ');\n"
                        "const bananaPrompt = String(design.banana_prompt || '').trim() || `Arabic marketing post visual for ${intake.company_name || 'company'}, reflect brand website style, geometric clean composition, premium business design.`;\n"
                        "const outputText = [titleAr, excerptAr, bodyAr].filter(Boolean).join('\\n\\n');\n"
                        "return [{ json: {\n"
                        "  request_id: requestId,\n"
                        "  created_at: new Date().toISOString(),\n"
                        "  company_name: companyName,\n"
                        "  company_link: companyLink,\n"
                        "  industry: intake.industry || input.industry || '',\n"
                        "  target_audience: intake.target_audience || input.target_audience || input.audience || '',\n"
                        "  topic: topic,\n"
                        "  approval_status: 'approved',\n"
                        "  workflow_status: 'done',\n"
                        "  trigger_status: 'done',\n"
                        "  sent_status: 'done',\n"
                        "  publish_target: 'website',\n"
                        "  'Post Type': String(design.post_type || '').trim() || 'carousel',\n"
                        "  SUBJECT: titleAr,\n"
                        "  TITLE: titleAr,\n"
                        "  hook_1: hook1,\n"
                        "  hook_2: hook2,\n"
                        "  hook_3: hook3,\n"
                        "  hook_4: hook4,\n"
                        "  hook_5: hook5,\n"
                        "  'Content for instagram': instagram,\n"
                        "  'Content for X': xText,\n"
                        "  'Content for Tiktok': tiktok,\n"
                        "  'Content for Facebook': facebook,\n"
                        "  'Content for linkedin': linkedin,\n"
                        "  Caption: String(platform.caption || '').trim() || caption,\n"
                        "  'Image Prompt': imagePrompt,\n"
                        "  'Website Blogs & Article': blogArticle,\n"
                        "  'Keywords used': keywords,\n"
                        "  Hashtags: hashtags,\n"
                        "  'Image Prompt to paste in banana': bananaPrompt,\n"
                        "  output: outputText,\n"
                        "  search_company: String(companyName).toLowerCase(),\n"
                        "  search_url: String(companyLink).toLowerCase(),\n"
                        "  search_topic: String(topic).toLowerCase(),\n"
                        "  search_all: `${String(companyName).toLowerCase()} | ${String(companyLink).toLowerCase()} | ${String(topic).toLowerCase()} | ${String(requestId).toLowerCase()}`,\n"
                        "  author: post.author || '',\n"
                        "  language: input.content_writer?.language || 'ar-SA',\n"
                        "  prompt_text: input.content_writer?.user_prompt || input.prompt_text || '',\n"
                        "  writer_prompt_version: input.content_writer?.prompt_version || '',\n"
                        "  approved_by: input.approval?.approved_by || '',\n"
                        "  approval_notes: input.approval?.approval_notes || '',\n"
                        "  approval_date: input.approval?.approval_date || ''\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Append Approved Row To Sheet",
                                "onError": "continueRegularOutput",
                "name": "Append Approved Row To Sheet",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [1800, 390],
                "parameters": {
                    "operation": "append",
                    "documentId": {
                        "mode": "id",
                        "value": sheet_id,
                    },
                    "sheetName": {
                        "mode": "name",
                        "value": results_sheet_tab,
                    },
                    "columns": {
                        "mappingMode": "autoMapInputData",
                        "value": {},
                    },
                    "options": {},
                },
            },
            {
                "id": "Build Sheet Row (Pending)",
                "name": "Build Sheet Row (Pending)",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1580, 560],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const intake = input.intake || {};\n"
                        "const post = input.post || {};\n"
                        "const hooks = input.hooks || [];\n"
                        "const companyName = intake.company_name || input.company_name || '';\n"
                        "const companyLink = intake.company_link || input.company_link || '';\n"
                        "const topic = input.topic || '';\n"
                        "const requestId = input.request_id || intake.request_id || '';\n"
                        "const titleAr = post.title_ar || topic || '';\n"
                        "const bodyAr = post.content_ar || '';\n"
                        "const excerptAr = post.excerpt_ar || '';\n"
                        "const cta = input.cta || `تابع التحديثات الرسمية من ${intake.company_name || 'الجهة'} لمعرفة المستجدات.`;\n"
                        "const platform = input.platform_content || {};\n"
                        "const design = input.design || {};\n"
                        "const summaryLine = excerptAr || hooks[0] || titleAr;\n"
                        "const contentInstagram = String(platform.instagram || '').trim() || `${titleAr}\\n\\n${summaryLine}\\n\\nنوضح هنا قراءة عملية للتحديات الحالية وكيفية التعامل معها داخل ${companyName || 'الشركة'} بخطوات واضحة ومباشرة.\\n\\n${cta}`;\n"
                        "const contentX = String(platform.x || '').trim() || `${titleAr} | ${summaryLine} | نشارك قراءة تنفيذية موجزة لما يحدث في السوق وكيف نتعامل معه داخل ${companyName || 'الشركة'}. | ${cta}`;\n"
                        "const contentTikTok = String(platform.tiktok || '').trim() || `في هذا المحتوى نشرح الواقع الحالي في ${topic}، ثم نقدم معالجة عملية مدعومة بمثال تطبيقي من خبرة فريق ${companyName || 'الشركة'}، مع خلاصة تنفيذية واضحة. ${cta}`;\n"
                        "const contentFacebook = String(platform.facebook || '').trim() || `${bodyAr || summaryLine}\\n\\nنستعرض التفاصيل التنفيذية والنقاط القابلة للتطبيق بشكل مباشر.\\n\\n${cta}`;\n"
                        "const contentLinkedIn = String(platform.linkedin || '').trim() || `${titleAr}\\n\\n${summaryLine}\\n\\nنقدم قراءة مهنية مبنية على المعطيات الحالية في السوق مع توصيات عملية قابلة للتنفيذ.\\n\\n${cta}`;\n"
                        "return [{ json: {\n"
                        "  request_id: requestId,\n"
                        "  created_at: new Date().toISOString(),\n"
                        "  company_name: companyName,\n"
                        "  company_link: companyLink,\n"
                        "  industry: intake.industry || input.industry || '',\n"
                        "  target_audience: intake.target_audience || input.target_audience || input.audience || '',\n"
                        "  topic: topic,\n"
                        "  approval_status: input.validation_status === 'rejected_generic_content' ? 'rejected_generic_content' : 'pending',\n"
                        "  workflow_status: input.validation_status === 'rejected_generic_content' ? 'rejected_generic_content' : 'done',\n"
                        "  trigger_status: 'done',\n"
                        "  sent_status: 'done',\n"
                        "  publish_target: 'hold',\n"
                        "  'Post Type': String(design.post_type || '').trim() || 'carousel',\n"
                        "  SUBJECT: titleAr,\n"
                        "  TITLE: titleAr,\n"
                        "  hook_1: hooks[0] || '',\n"
                        "  hook_2: hooks[1] || '',\n"
                        "  hook_3: hooks[2] || '',\n"
                        "  hook_4: hooks[3] || '',\n"
                        "  hook_5: hooks[4] || '',\n"
                        "  'Content for instagram': contentInstagram,\n"
                        "  'Content for X': contentX,\n"
                        "  'Content for Tiktok': contentTikTok,\n"
                        "  'Content for Facebook': contentFacebook,\n"
                        "  'Content for linkedin': contentLinkedIn,\n"
                        "  Caption: String(platform.caption || '').trim() || `${excerptAr} ${cta}`.trim(),\n"
                        "  'Website Blogs & Article': String(platform.website_article || '').trim() || bodyAr || `${titleAr}\\n\\n${excerptAr}`,\n"
                        "  'Keywords used': '',\n"
                        "  Hashtags: '',\n"
                        "  'Image Prompt': String(design.image_prompt || '').trim(),\n"
                        "  'Image Prompt to paste in banana': String(design.banana_prompt || '').trim(),\n"
                        "  output: [titleAr, excerptAr, bodyAr].filter(Boolean).join('\\n\\n'),\n"
                        "  search_company: String(companyName).toLowerCase(),\n"
                        "  search_url: String(companyLink).toLowerCase(),\n"
                        "  search_topic: String(topic).toLowerCase(),\n"
                        "  search_all: `${String(companyName).toLowerCase()} | ${String(companyLink).toLowerCase()} | ${String(topic).toLowerCase()} | ${String(requestId).toLowerCase()}`,\n"
                        "  author: post.author || '',\n"
                        "  language: input.content_writer?.language || 'ar-SA',\n"
                        "  prompt_text: input.content_writer?.user_prompt || input.prompt_text || '',\n"
                        "  writer_prompt_version: input.content_writer?.prompt_version || '',\n"
                        "  approved_by: input.approval?.approved_by || '',\n"
                        "  approval_notes: input.approval?.approval_notes || '',\n"
                        "  approval_date: input.approval?.approval_date || ''\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Append Pending Row To Sheet",
                                "onError": "continueRegularOutput",
                "name": "Append Pending Row To Sheet",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [1800, 560],
                "parameters": {
                    "operation": "append",
                    "documentId": {
                        "mode": "id",
                        "value": sheet_id,
                    },
                    "sheetName": {
                        "mode": "name",
                        "value": results_sheet_tab,
                    },
                    "columns": {
                        "mappingMode": "autoMapInputData",
                        "value": {},
                    },
                    "options": {},
                },
            },
            {
                "id": "Build Intake Status Update Row",
                "name": "Build Intake Status Update Row",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [2040, 620],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": (
                        "const input = $json || {};\n"
                        "const source = String(input.source || '').toLowerCase();\n"
                        "if (source && source !== 'sheet_intake') return [];\n"
                        "const rowNumber = String(input.row_number || input.intake?.row_number || '').trim();\n"
                        "const requestId = String(input.request_id || '').trim();\n"
                        "const intake = input.intake || {};\n"
                        "const companyLink = String(intake.company_link || input.company_link || '').trim();\n"
                        "if (!requestId && !rowNumber && !companyLink) return [];\n"
                        "return [{ json: {\n"
                        "  request_id: requestId,\n"
                        "  row_number: rowNumber,\n"
                        "  created_at: input.intake?.created_at || input.created_at || '',\n"
                        "  company_link: companyLink,\n"
                        "  topic: input.topic || intake.topic || '',\n"
                        "  trigger_status: 'done',\n"
                        "  sent_status: 'done',\n"
                        "  workflow_status: input.workflow_status || 'done',\n"
                        "  approval_status: input.approval_status || input.approval?.status || '',\n"
                        "  prompt_text: input.prompt_text || input.content_writer?.user_prompt || ''\n"
                        "} }];"
                    ),
                },
            },
            {
                "id": "Mark Intake Row As Finished",
                "name": "Mark Intake Row As Finished",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [2270, 620],
                "onError": "continueRegularOutput",
                "parameters": {
                    "operation": "update",
                    "documentId": {
                        "mode": "id",
                        "value": sheet_id,
                    },
                    "sheetName": {
                        "mode": "name",
                        "value": request_sheet_tab,
                    },
                    "columns": {
                        "mappingMode": "autoMapInputData",
                        "matchingColumns": ["company_link"],
                        "value": {},
                    },
                    "options": {},
                },
            },
        ],
        "connections": {
            "Webhook In": {
                "main": [[{"node": "Prepare Content Writer Input", "type": "main", "index": 0}]],
            },
            "Poll Intake Schedule": {
                "main": [[{"node": "Read Intake Rows", "type": "main", "index": 0}]],
            },
            "Read Intake Rows": {
                "main": [[{"node": "Select New Intake Rows", "type": "main", "index": 0}]],
            },
            "Select New Intake Rows": {
                "main": [[{"node": "Normalize Intake Row Input", "type": "main", "index": 0}]],
            },
            "Normalize Intake Row Input": {
                "main": [[{"node": "Prepare Content Writer Input", "type": "main", "index": 0}]],
            },
            "Prepare Content Writer Input": {
                "main": [[{"node": "Interview Readiness Gate", "type": "main", "index": 0}]],
            },
            "Interview Readiness Gate": {
                "main": [
                    [{"node": "Run Apify Market Intel", "type": "main", "index": 0}],
                    [{"node": "Build Interview Pending Row", "type": "main", "index": 0}]
                ],
            },
            "Build Interview Pending Row": {
                "main": [[{"node": "Append Interview Pending Row", "type": "main", "index": 0}]],
            },
            "Append Interview Pending Row": {
                "main": [[{"node": "Build Telegram Run Summary", "type": "main", "index": 0}]],
            },
            "Run Apify Market Intel": {
                "main": [[{"node": "Build Market Research Context", "type": "main", "index": 0}]],
            },
            "Build Market Research Context": {
                "main": [[{"node": "Build OpenAI Content Request", "type": "main", "index": 0}]],
            },
            "Build OpenAI Content Request": {
                "main": [[{"node": "Generate Content With OpenAI", "type": "main", "index": 0}]],
            },
            "Generate Content With OpenAI": {
                "main": [[{"node": "Parse OpenAI Generated Content", "type": "main", "index": 0}]],
            },
            "Parse OpenAI Generated Content": {
                "main": [[{"node": "Normalize Blog Metadata", "type": "main", "index": 0}]],
            },
            "Normalize Blog Metadata": {
                "main": [[
                    {"node": "Build Request Registry Row", "type": "main", "index": 0},
                    {"node": "Draft Email Gate", "type": "main", "index": 0}
                ]],
            },
            "Build Request Registry Row": {
                "main": [[{"node": "Append Request Registry Row", "type": "main", "index": 0}]],
            },
            "Append Request Registry Row": {"main": []},
            "Draft Email Gate": {
                "main": [
                    [{"node": "Approval Gate", "type": "main", "index": 0}],
                    [{"node": "Build Organized Draft Email", "type": "main", "index": 0}],
                ],
            },
            "Build Organized Draft Email": {
                "main": [[
                    {"node": "Append Draft Email Row To Sheet", "type": "main", "index": 0},
                    {"node": "Build Intake Status Update Row", "type": "main", "index": 0}
                ]],
            },
            "Approval Gate": {
                "main": [
                    [{"node": "Build Sheet Row (Approved)", "type": "main", "index": 0}],
                    [{"node": "Build Sheet Row (Pending)", "type": "main", "index": 0}],
                ],
            },
            "Build Sheet Row (Approved)": {
                "main": [[
                    {"node": "Append Approved Row To Sheet", "type": "main", "index": 0},
                    {"node": "Build Intake Status Update Row", "type": "main", "index": 0}
                ]],
            },
            "Build Sheet Row (Pending)": {
                "main": [[
                    {"node": "Append Pending Row To Sheet", "type": "main", "index": 0},
                    {"node": "Build Intake Status Update Row", "type": "main", "index": 0}
                ]],
            },
            "Append Approved Row To Sheet": {
                "main": [[{"node": "Publish To Site", "type": "main", "index": 0}]],
            },
            "Publish To Site": {
                "main": [[
                    {"node": "Build Intake Status Update Row", "type": "main", "index": 0},
                    {"node": "Build Telegram Run Summary", "type": "main", "index": 0}
                ]],
            },
            "Append Draft Email Row To Sheet": {
                "main": [[{"node": "Build Telegram Run Summary", "type": "main", "index": 0}]],
            },
            "Append Pending Row To Sheet": {
                "main": [[{"node": "Build Telegram Run Summary", "type": "main", "index": 0}]],
            },
            "Build Intake Status Update Row": {
                "main": [[{"node": "Mark Intake Row As Finished", "type": "main", "index": 0}]],
            },
            "Build Telegram Run Summary": {
                "main": [[{"node": "Telegram Send Enabled Gate", "type": "main", "index": 0}]],
            },
            "Telegram Send Enabled Gate": {
                "main": [
                    [{"node": "Send Telegram Run Summary", "type": "main", "index": 0}],
                    []
                ],
            },
            "Send Telegram Run Summary": {"main": []},
        },
    }


def get_workflow_by_id(base_url: str, api_key: str, workflow_id: str) -> Optional[Dict[str, Any]]:
    """Return a workflow by id if it exists, otherwise None."""
    wf_id = urllib.parse.quote(str(workflow_id), safe="")
    status, data = api_request("GET", base_url, api_key, f"/api/v1/workflows/{wf_id}")
    if status == 404:
        return None
    if status != 200:
        raise RuntimeError(f"Failed to fetch workflow by id. HTTP {status}: {data}")
    if isinstance(data, dict):
        return data
    return None


def find_workflow_by_name(base_url: str, api_key: str, name: str) -> Optional[Dict[str, Any]]:
    """Return existing workflow summary by exact name, if found."""
    status, data = api_request("GET", base_url, api_key, "/api/v1/workflows")
    if status != 200:
        raise RuntimeError(f"Failed to list workflows. HTTP {status}: {data}")

    items: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            items = data["data"]
        elif isinstance(data.get("workflows"), list):
            items = data["workflows"]
    elif isinstance(data, list):
        items = data

    for wf in items:
        if wf.get("name") == name:
            return wf

    return None


def infer_sheet_settings(existing_workflow: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Infer sheet id and tabs from existing workflow to avoid overwriting manual config."""
    nodes = existing_workflow.get("nodes", []) if isinstance(existing_workflow, dict) else []
    inferred_sheet_id: Optional[str] = None
    inferred_request_tab: Optional[str] = None
    inferred_results_tab: Optional[str] = None

    for node in nodes:
        name = node.get("name")
        params = node.get("parameters", {})
        doc = params.get("documentId", {})
        tab = params.get("sheetName", {})

        doc_value = doc.get("value") if isinstance(doc, dict) else None
        tab_value = tab.get("value") if isinstance(tab, dict) else None

        if name in {
            "Append Request Registry Row",
            "Append Approved Row To Sheet",
            "Append Pending Row To Sheet",
            "Append Draft Email Row To Sheet",
        } and doc_value and doc_value != "YOUR_GOOGLE_SHEET_ID":
            inferred_sheet_id = doc_value

        if name == "Append Request Registry Row" and tab_value:
            inferred_request_tab = tab_value

        if name in {"Append Approved Row To Sheet", "Append Pending Row To Sheet", "Append Draft Email Row To Sheet"} and tab_value:
            inferred_results_tab = tab_value

    return inferred_sheet_id, inferred_request_tab, inferred_results_tab


def infer_google_sheet_credentials(existing_workflow: Dict[str, Any]) -> Tuple[Optional[Dict[str, str]], Optional[Dict[str, str]]]:
    """Infer Google Sheets credentials from an existing workflow definition."""
    nodes = existing_workflow.get("nodes", []) if isinstance(existing_workflow, dict) else []
    sheets_cred: Optional[Dict[str, str]] = None
    trigger_cred: Optional[Dict[str, str]] = None

    for node in nodes:
        creds = node.get("credentials", {}) or {}
        if not sheets_cred and isinstance(creds.get("googleSheetsOAuth2Api"), dict):
            ref = creds["googleSheetsOAuth2Api"]
            if ref.get("id") and ref.get("name"):
                sheets_cred = {"id": str(ref["id"]), "name": str(ref["name"])}
        if not trigger_cred and isinstance(creds.get("googleSheetsTriggerOAuth2Api"), dict):
            ref = creds["googleSheetsTriggerOAuth2Api"]
            if ref.get("id") and ref.get("name"):
                trigger_cred = {"id": str(ref["id"]), "name": str(ref["name"])}

    return sheets_cred, trigger_cred


def find_any_google_sheet_credentials(base_url: str, api_key: str) -> Tuple[Optional[Dict[str, str]], Optional[Dict[str, str]]]:
    """Find reusable Google Sheets credentials from any existing workflow."""
    status, data = api_request("GET", base_url, api_key, "/api/v1/workflows")
    if status != 200:
        return None, None

    items: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            items = data["data"]
        elif isinstance(data.get("workflows"), list):
            items = data["workflows"]
    elif isinstance(data, list):
        items = data

    found_sheet: Optional[Dict[str, str]] = None
    found_trigger: Optional[Dict[str, str]] = None
    for wf in items:
        wf_id = wf.get("id")
        if not wf_id:
            continue
        one = get_workflow_by_id(base_url, api_key, str(wf_id))
        if not one:
            continue
        sheet_ref, trigger_ref = infer_google_sheet_credentials(one)
        if not found_sheet and sheet_ref:
            found_sheet = sheet_ref
        if not found_trigger and trigger_ref:
            found_trigger = trigger_ref
        if found_sheet and found_trigger:
            break

    return found_sheet, found_trigger


def apply_google_sheet_credentials(
    payload: Dict[str, Any],
    sheets_credential: Optional[Dict[str, str]],
    trigger_credential: Optional[Dict[str, str]],
) -> Dict[str, Any]:
    """Attach Google Sheets credentials to payload nodes when available."""
    nodes = payload.get("nodes", []) if isinstance(payload, dict) else []
    for node in nodes:
        node_type = node.get("type", "")
        if node_type == "n8n-nodes-base.googleSheets" and sheets_credential:
            node["credentials"] = {"googleSheetsOAuth2Api": sheets_credential}
        elif node_type == "n8n-nodes-base.googleSheetsTrigger" and trigger_credential:
            node["credentials"] = {"googleSheetsTriggerOAuth2Api": trigger_credential}
    return payload


def set_workflow_active(base_url: str, api_key: str, workflow_id: str, active: bool) -> None:
    """Activate/deactivate workflow if API supports it."""
    wf_id = urllib.parse.quote(str(workflow_id), safe="")

    if active:
        candidates = [
            ("POST", f"/api/v1/workflows/{wf_id}/activate"),
            ("POST", f"/api/v1/workflows/{wf_id}/active"),
        ]
    else:
        candidates = [
            ("POST", f"/api/v1/workflows/{wf_id}/deactivate"),
            ("POST", f"/api/v1/workflows/{wf_id}/inactive"),
        ]

    last_status = None
    last_data = None
    for method, path in candidates:
        status, data = api_request(method, base_url, api_key, path)
        last_status, last_data = status, data
        if status in (200, 201, 204):
            return
        if status in (404, 405):
            continue
        break

    raise RuntimeError(
        f"Failed to set workflow active={active}. HTTP {last_status}: {last_data}"
    )


def create_or_update_workflow() -> int:
    load_env_files()

    api_key = os.getenv("N8N_API_KEY", "").strip().strip('"').strip("'")
    base_url = normalize_base_url()

    if not api_key or not base_url:
        print("Missing required env vars: N8N_API_KEY and N8N_BASE_URL (or N8N_API_URL)")
        return 1

    workflow_name = os.getenv("N8N_BLOG_WORKFLOW_NAME", "Ali Content Writer")
    workflow_id_hint = os.getenv("N8N_BLOG_WORKFLOW_ID", "TI24nDeVCB1IlSav").strip()
    trigger_path = os.getenv("N8N_BLOG_TRIGGER_PATH", "ziyada-blog-ingest")
    target_url = os.getenv(
        "ZIYADA_SITE_WEBHOOK_URL",
        "https://your-site-domain/functions/n8nWebhook",
    )
    secret = os.getenv("ZIYADA_SITE_WEBHOOK_SECRET", "ziyada-n8n-2026")
    system_prompt = os.getenv("ZIYADA_CONTENT_WRITER_SYSTEM_PROMPT", "").strip() or load_writer_system_prompt()
    legacy_tab = os.getenv("ZIYADA_BLOG_SHEET_TAB", "").strip()
    explicit_sheet_id = os.getenv("ZIYADA_BLOG_SHEET_ID", "").strip()
    explicit_request_tab = os.getenv("ZIYADA_BLOG_REQUEST_SHEET_TAB", "").strip()
    explicit_results_tab = os.getenv("ZIYADA_BLOG_RESULTS_SHEET_TAB", "").strip()
    request_sheet_gid = os.getenv("ZIYADA_BLOG_REQUEST_SHEET_GID", DEFAULT_REQUEST_SHEET_GID).strip() or DEFAULT_REQUEST_SHEET_GID

    explicit_sheets_cred_id = os.getenv("ZIYADA_GOOGLE_SHEETS_CREDENTIAL_ID", "").strip()
    explicit_sheets_cred_name = os.getenv("ZIYADA_GOOGLE_SHEETS_CREDENTIAL_NAME", "").strip()
    explicit_trigger_cred_id = os.getenv("ZIYADA_GOOGLE_SHEETS_TRIGGER_CREDENTIAL_ID", "").strip()
    explicit_trigger_cred_name = os.getenv("ZIYADA_GOOGLE_SHEETS_TRIGGER_CREDENTIAL_NAME", "").strip()

    sheet_id = explicit_sheet_id or DEFAULT_SHEET_ID
    request_sheet_tab = explicit_request_tab or legacy_tab or "ContentIntake"
    results_sheet_tab = explicit_results_tab or legacy_tab or "ContentResults"
    active_raw = os.getenv("N8N_BLOG_WORKFLOW_ACTIVE", "true").strip().lower()
    active = active_raw in {"1", "true", "yes", "on", "active"}

    existing: Optional[Dict[str, Any]] = None
    if workflow_id_hint:
        try:
            existing = get_workflow_by_id(base_url, api_key, workflow_id_hint)
        except RuntimeError as exc:
            print(str(exc))
            return 1

    if existing is None:
        try:
            existing = find_workflow_by_name(base_url, api_key, workflow_name)
        except RuntimeError as exc:
            print(str(exc))
            return 1

    if existing is not None:
        inferred_sheet_id, inferred_request_tab, inferred_results_tab = infer_sheet_settings(existing)
        if not explicit_sheet_id and sheet_id in {"", "YOUR_GOOGLE_SHEET_ID", DEFAULT_SHEET_ID} and inferred_sheet_id:
            sheet_id = inferred_sheet_id
        if not explicit_request_tab and request_sheet_tab in {"", "ContentIntake", "ContentCalendar"} and inferred_request_tab:
            request_sheet_tab = inferred_request_tab
        if not explicit_results_tab and results_sheet_tab in {"", "ContentResults", "ContentCalendar"} and inferred_results_tab:
            results_sheet_tab = inferred_results_tab

    payload = build_workflow_payload(
        name=workflow_name,
        trigger_path=trigger_path,
        request_sheet_gid=request_sheet_gid,
        target_url=target_url,
        secret=secret,
        system_prompt=system_prompt,
        sheet_id=sheet_id,
        request_sheet_tab=request_sheet_tab,
        results_sheet_tab=results_sheet_tab,
    )

    sheets_cred: Optional[Dict[str, str]] = None
    trigger_cred: Optional[Dict[str, str]] = None
    if explicit_sheets_cred_id and explicit_sheets_cred_name:
        sheets_cred = {"id": explicit_sheets_cred_id, "name": explicit_sheets_cred_name}
    if explicit_trigger_cred_id and explicit_trigger_cred_name:
        trigger_cred = {"id": explicit_trigger_cred_id, "name": explicit_trigger_cred_name}

    if existing is not None:
        inferred_sheet_cred, inferred_trigger_cred = infer_google_sheet_credentials(existing)
        if not sheets_cred and inferred_sheet_cred:
            sheets_cred = inferred_sheet_cred
        if not trigger_cred and inferred_trigger_cred:
            trigger_cred = inferred_trigger_cred

    if not sheets_cred or not trigger_cred:
        found_sheet_cred, found_trigger_cred = find_any_google_sheet_credentials(base_url, api_key)
        if not sheets_cred and found_sheet_cred:
            sheets_cred = found_sheet_cred
        if not trigger_cred and found_trigger_cred:
            trigger_cred = found_trigger_cred

    payload = apply_google_sheet_credentials(payload, sheets_cred, trigger_cred)

    if existing and existing.get("id"):
        wf_id = urllib.parse.quote(str(existing["id"]), safe="")
        status, data = api_request("PUT", base_url, api_key, f"/api/v1/workflows/{wf_id}", payload)
        if status not in (200, 201):
            print(f"Failed to update workflow. HTTP {status}: {data}")
            return 1
        if active:
            try:
                set_workflow_active(base_url, api_key, str(existing["id"]), active=True)
            except RuntimeError as exc:
                print(str(exc))
                return 1
        print(
            f"Updated workflow '{workflow_name}' (id={existing['id']}) with sheet_id '{sheet_id}', request tab '{request_sheet_tab}', and results tab '{results_sheet_tab}'."
        )
        print(
            f"Google Sheets credentials: append={'configured' if sheets_cred else 'missing'}, trigger={'configured' if trigger_cred else 'missing'}"
        )
        print("Note: Google Sheets nodes are configured to continue on error if credentials are missing.")
        return 0

    status, data = api_request("POST", base_url, api_key, "/api/v1/workflows", payload)
    if status not in (200, 201):
        print(f"Failed to create workflow. HTTP {status}: {data}")
        return 1

    wf_id = data.get("id") if isinstance(data, dict) else None
    if active and wf_id:
        try:
            set_workflow_active(base_url, api_key, str(wf_id), active=True)
        except RuntimeError as exc:
            print(str(exc))
            return 1
    print(f"Created workflow '{workflow_name}' (id={wf_id}).")
    print(
        f"Google Sheets credentials: append={'configured' if sheets_cred else 'missing'}, trigger={'configured' if trigger_cred else 'missing'}"
    )
    print("Note: Google Sheets nodes are configured to continue on error if credentials are missing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(create_or_update_workflow())
