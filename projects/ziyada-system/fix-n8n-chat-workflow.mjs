/**
 * fix-n8n-chat-workflow.mjs   —   v4 Final Fix
 * Run:  node fix-n8n-chat-workflow.mjs
 *
 * Fixes applied to the LIVE n8n workflow:
 *  1. Updates system prompt → ZERO URLs from AI, use create_booking_request tool
 *  2. Fixes chatInput + sessionId expressions
 *  3. Fixes booking tool (toolCode or toolHttpRequest) → no URL output
 *  4. Fixes get_services_info → real service data
 *  5. Fixes capture_lead → toolHttpRequest to lead-intake webhook
 *  6. ADDS "Output Sanitizer" Code node between AI Agent → Respond to Chat
 *     (strips Calendly / cal.com / localhost / any external URL from AI output)
 *  7. Rewires connections: AI Agent → Output Sanitizer → Respond to Chat
 *  8. Updates Respond to Chat to read from Output Sanitizer
 *  9. Pushes and activates
 * 10. Runs 3 live test messages and checks for bad URLs
 */

const N8N_API_KEY = process.env.N8N_API_KEY || "";
const N8N_BASE = process.env.N8N_BASE || "https://n8n.srv953562.hstgr.cloud";
const WORKFLOW_ID = process.env.N8N_WORKFLOW_ID || "Y6WTad9ORgiyYEmc";
const CHAT_WEBHOOK = process.env.N8N_CHAT_WEBHOOK || `${N8N_BASE}/webhook/0f30c293-c375-45a2-9cf6-d55208de387b`;
const LEAD_INTAKE = process.env.N8N_LEAD_INTAKE || `${N8N_BASE}/webhook/ziyada-lead-intake`;
const BOOKING_WEBHOOK = process.env.N8N_BOOKING_WEBHOOK || `${N8N_BASE}/webhook/booking-webhook`;
const SKIP_ACTIVATE = /^(1|true|yes)$/i.test(process.env.N8N_SKIP_ACTIVATE || "");
const SKIP_LIVE_TESTS = /^(1|true|yes)$/i.test(process.env.N8N_SKIP_LIVE_TESTS || "");

// ─── System prompt: strict language lock + booking flow without links ───────
const NEW_SYSTEM_PROMPT = `You are "مساعد زيادة" for Ziyada System.

CRITICAL LANGUAGE LOCK (must follow):
- Reply in the SAME language as the user's last message.
- If the user's last message contains Arabic letters, reply fully in Arabic.
- If the user's last message is English/Latin text, reply fully in English.
- Never mix Arabic and English in the same reply (except one short technical term if needed).

CRITICAL RULES:
- Never output any URL or link under any condition.
- Never mention Calendly, cal.com, localhost, or any external booking link.
- Never expose chain-of-thought, internal notes, tool traces, or planning text.
- Never mention model/provider names.

BOOKING BEHAVIOR:
- If the user asks to book a consultation, do NOT apologize and do NOT ask them to click a link.
- Collect politely: full name, phone, email, preferred time, and business concern.
- Confirm collected data with the user first.
- Then call create_booking_request.
- After success, send only short confirmation that team will contact to confirm timing.

LEAD CAPTURE BEHAVIOR:
- Use capture_lead only after collecting and confirming at least full name, phone, and email.
- Include company, sector, challenge, and service_interest when available.

MANDATORY TOOL EXECUTION TRIGGERS:
- If the user confirms shown lead details (e.g., yes/نعم/صحيح/confirmed), call capture_lead immediately in the same turn.
- If the user confirms shown booking details (full name + phone + email + preferred_time + main_concern), call create_booking_request immediately in the same turn.
- If user asks about services, pricing approach, or sector use-cases, call get_services_info before answering.
- Never claim success unless the tool call succeeded.
- If a required field is missing or invalid, ask only for the missing field and do not call the tool yet.

STYLE:
- Keep replies short, practical, respectful, and conversational.
- No markdown symbols (*, **, #, bullets).
- End each reply with one clear next step.`;

// ─── Tool code: get_services_info ─────────────────────────────────────────────
const SERVICES_TOOL_CODE = `const query = $fromAI('query', 'What specific service or information is being asked about', 'string');

const services = {
  automation: {
    ar: 'أتمتة الأعمال: نربط واتساب + CRM + إيميل + جداول البيانات في منظومة واحدة ذكية. كل رسالة تجيك، كل طلب، كل عميل — يتسجّل ويتابَع أوتوماتيك. نوفّر 80 ساعة شهرياً.',
    en: 'Business Automation: We connect WhatsApp + CRM + Email + spreadsheets into one smart system. Every message and lead is captured and followed up automatically. Saves 80 hours/month.',
    sectors: 'Restaurants, clinics, real estate, retail, education',
    timeline: '2-4 weeks'
  },
  crm: {
    ar: 'إدارة العملاء والمبيعات: نبني نظام CRM مخصص — مسارات البيع، تذكيرات المتابعة، تصنيف العملاء. ما يضيع لك ولا صفقة.',
    en: 'CRM & Sales: Custom CRM — sales pipelines, automated follow-ups, lead scoring. No deal falls through the cracks.',
    sectors: 'Professional services, consulting, B2B',
    timeline: '1-3 weeks'
  },
  leads: {
    ar: 'اكتساب العملاء: ماكينة توليد عملاء B2B على LinkedIn + Google Ads مع تأهيل أوتوماتيك. 40+ عميل محتمل مؤهّل شهرياً.',
    en: 'Lead Generation: B2B lead engine on LinkedIn + Google Ads with automatic qualification. 40+ qualified leads/month.',
    sectors: 'Tech, consulting, professional services',
    timeline: '3-6 weeks for first results'
  },
  marketing: {
    ar: 'التسويق الأدائي والـ SEO: Google Ads + Meta Ads + SEO مرتبطة بالنتائج الفعلية. كل ريال له عائد قابل للقياس.',
    en: 'Performance Marketing + SEO: Google + Meta Ads + SEO tied to real results. Every riyal tracked.',
    sectors: 'E-commerce, education, real estate',
    timeline: 'First results report after 2-3 weeks'
  },
  website: {
    ar: 'المواقع الذكية: موقعك مربوط بـ CRM وأتمتة. كل زائر يتحوّل لعميل محتمل أوتوماتيك.',
    en: 'Smart Websites: Connected to CRM and automation. Every visitor becomes a potential lead automatically.',
    sectors: 'All sectors',
    timeline: '2-6 weeks'
  },
  social: {
    ar: 'أنظمة المحتوى: من الاستراتيجية للنشر للتقارير — منظومة محتوى تشتغل بدون ضغط.',
    en: 'Content Systems: Strategy to publishing to reporting — runs without the stress.',
    sectors: 'Retail, restaurants, consumer brands',
    timeline: 'First content in week one'
  },
  summary: {
    ar: 'زيادة سيستم تقدم 6 خدمات رئيسية: أتمتة الأعمال — إدارة العملاء والمبيعات — اكتساب العملاء — التسويق الأدائي والـ SEO — المواقع الذكية — أنظمة المحتوى.',
    en: 'Ziyada System offers 6 core services: Business Automation — CRM & Sales — Lead Generation — Performance Marketing & SEO — Smart Websites — Content Systems.'
  }
};

return { services, query };`;

// ─── capture_lead tool HTTP params ────────────────────────────────────────────
const CAPTURE_LEAD_HTTP_PARAMS = {
  name: "capture_lead",
  description: "ONLY call this tool AFTER collecting all three: full name, phone number, AND email — and ONLY after the visitor has confirmed that their info is correct. Saves the lead to Supabase.",
  method: "POST",
  url: LEAD_INTAKE,
  sendBody: true,
  contentType: "raw",
  rawContentType: "application/json",
  body: `={
  "full_name": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('full_name', 'Full name of the visitor', 'string') }}",
  "email": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', 'Email address of the visitor', 'string') }}",
  "phone": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('phone', 'Phone/mobile number of the visitor', 'string') }}",
  "company": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('company', 'Company name if mentioned, otherwise empty string', 'string') }}",
  "sector": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('sector', 'Industry sector if mentioned', 'string') }}",
  "challenge": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('challenge', 'Main business challenge they described', 'string') }}",
  "service_interest": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('service_interest', 'Which Ziyada service they are most interested in', 'string') }}",
  "source": "chat_widget"
}`,
  options: {
    timeout: 20000,
    response: { response: { responseFormat: "json" } }
  }
};

// ─── create_booking_request tool HTTP params ──────────────────────────────────
const BOOKING_HTTP_PARAMS = {
  name: "create_booking_request",
  description: "Create a booking/consultation request. Use ONLY after collecting full name, phone, and email. Also ask for preferred date/time. Do NOT output any URL — the tool handles everything.",
  method: "POST",
  url: BOOKING_WEBHOOK,
  sendBody: true,
  contentType: "raw",
  rawContentType: "application/json",
  body: `={
  "session_id": "{{ $json.body?.sessionId || $json.sessionId || '' }}",
  "lead_name": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('full_name', 'Full name of the visitor (required)', 'string') }}",
  "phone_e164": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('phone', 'Phone number of the visitor, required', 'string') }}",
  "email": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', 'Email of the visitor, required', 'string') }}",
  "requested_datetime": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('preferred_time', 'Preferred booking date/time (required)', 'string') }}",
  "channel": "website_chat",
  "conversation_summary": "{{ /*n8n-auto-generated-fromAI-override*/ $fromAI('main_concern', 'Short summary of the visitor concern', 'string') }}"
}`,
  options: {
    timeout: 20000,
    response: { response: { responseFormat: "json" } }
  }
};

// ─── Output Sanitizer Code node ───────────────────────────────────────────────
const SANITIZER_NODE = {
  parameters: {
    jsCode: `// Output Sanitizer — enforces no URLs/markdown in final user-facing text
const raw = $input.first().json.output || '';

const clean = String(raw)
  // Remove URL-like tokens (including bare domains and localhost)
  .replace(/(?:https?:\\/\\/)?(?:www\\.)?(?:calendly\\.com|app\\.cal\\.com|cal\\.com|acuityscheduling\\.com)\\/?[^\\s\\n]*/gi, '')
  .replace(/(?:https?:\\/\\/)?localhost(?::\\d+)?\\/?[^\\s\\n]*/gi, '')
  .replace(/(?:https?:\\/\\/|www\\.)[^\\s\\n]+/gi, '')
  // Remove markdown formatting tokens
  .replace(/\\*\\*/g, '')
  .replace(/(^|\\s)[#*_]{1,3}(?=\\s|$)/g, ' ')
  // Turn bullet style lines into short readable paragraphs
  .replace(/^\\s*[-•]\\s+/gm, '\\n\\n')
  .replace(/\\s+-\\s+/g, '\\n\\n')
  // Remove lines that still mention links explicitly
  .split('\\n')
  .map((line) => line.trim())
  .filter((line) => line && !/(?:\\burl\\b|\\blink\\b|\\bhttp\\b|\\bwww\\b|\\bcalendly\\b|\\bcal\\.com\\b|رابط|لينك|localhost)/i.test(line))
  .join('\\n')
  // Remove booking-tool failure chatter from final user response
  .replace(/I apologize[^\n]*booking tool[^\n]*/gi, '')
  .replace(/(تعذّر|فشل)[^\n]*(أداة|الحجز)[^\n]*/gi, '')
  // Normalize whitespace
  .replace(/\\n{3,}/g, '\\n\\n')
  .replace(/[ \\t]{2,}/g, ' ')
  .replace(/^\\s*[\\-—]?\\s*$/gm, '')
  .trim();

return [{
  json: {
    output: clean || (/[\u0600-\u06FF]/.test(raw)
      ? 'أكيد. عشان أحجز لك الاستشارة، أحتاج الاسم الكامل، رقم الجوال، والإيميل، وبعدها الوقت المناسب لك.'
      : 'Sure. To book your consultation, please share your full name, phone number, and email, then your preferred time.')
  }
}];`
  },
  id: "output-sanitizer-008",
  name: "Output Sanitizer",
  type: "n8n-nodes-base.code",
  typeVersion: 2,
  position: [700, 400]
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

const headers = {
  "X-N8N-API-KEY": N8N_API_KEY,
  "Content-Type": "application/json",
};

function log(emoji, msg) { console.log(`${emoji}  ${msg}`); }
function findNode(nodes, matcher) { return nodes.find(matcher); }

// ─── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  if (!N8N_API_KEY) {
    throw new Error("Missing N8N_API_KEY. Export it before running this script.");
  }

  console.log("\n═══════════════════════════════════════════════");
  console.log("  Ziyada Chat Workflow — Fix Script v4");
  console.log("  + Output Sanitizer node (strips bad URLs)");
  console.log("═══════════════════════════════════════════════\n");

  // ── Step 1: Fetch live workflow ────────────────────────────────────────
  log("📥", "Fetching live workflow from n8n...");
  const fetchRes = await fetch(`${N8N_BASE}/api/v1/workflows/${WORKFLOW_ID}`, { headers });
  if (!fetchRes.ok) {
    const body = await fetchRes.text();
    throw new Error(`Failed to fetch workflow: ${fetchRes.status} — ${body}`);
  }
  const workflow = await fetchRes.json();
  log("✅", `Got workflow: "${workflow.name}" (${workflow.nodes.length} nodes)`);

  const nodes = workflow.nodes;

  // ── Step 2: Discover key nodes ─────────────────────────────────────────
  const webhook1 = findNode(nodes, (n) =>
    n.type === "n8n-nodes-base.webhook" &&
    (n.name === "Webhook1" || (n.webhookId && n.webhookId === "0f30c293-c375-45a2-9cf6-d55208de387b"))
  );
  const chatTrigger = findNode(nodes, (n) => n.type === "@n8n/n8n-nodes-langchain.chatTrigger");
  const agent = findNode(nodes, (n) => n.type === "@n8n/n8n-nodes-langchain.agent");
  const memory = findNode(nodes, (n) => n.type === "@n8n/n8n-nodes-langchain.memoryBufferWindow");
  const respondNode = findNode(nodes, (n) =>
    n.type === "n8n-nodes-base.respondToWebhook" ||
    n.name?.toLowerCase().includes("respond")
  );

  const allTools = nodes.filter((n) =>
    n.type === "@n8n/n8n-nodes-langchain.toolCode" ||
    n.type === "@n8n/n8n-nodes-langchain.toolHttpRequest" ||
    n.type === "@n8n/n8n-nodes-langchain.toolWorkflow"
  );

  // Try to find tools by multiple name patterns
  const bookingTool  = findNode(allTools, (n) => /book|consult|booking/i.test(n.name));
  const servicesTool = findNode(allTools, (n) => /service|info/i.test(n.name));
  const leadTool     = findNode(allTools, (n) => /capture|lead/i.test(n.name));

  // Check if sanitizer already exists
  const existingSanitizer = findNode(nodes, (n) =>
    n.name === "Output Sanitizer" || n.id === "output-sanitizer-008"
  );

  console.log("\n── Node Discovery ──────────────────────────────────");
  console.log(`  Webhook1       : ${webhook1      ? `"${webhook1.name}"` : "— (not found)"}`);
  console.log(`  Chat Trigger   : ${chatTrigger   ? `"${chatTrigger.name}"` : "— (not found)"}`);
  console.log(`  AI Agent       : ${agent         ? `"${agent.name}"` : "❌ NOT FOUND"}`);
  console.log(`  Memory         : ${memory        ? `"${memory.name}"` : "❌ NOT FOUND"}`);
  console.log(`  Booking tool   : ${bookingTool   ? `"${bookingTool.name}" [${bookingTool.type.split('.').pop()}]` : "❌ NOT FOUND"}`);
  console.log(`  Services tool  : ${servicesTool  ? `"${servicesTool.name}" [${servicesTool.type.split('.').pop()}]` : "❌ NOT FOUND"}`);
  console.log(`  Lead tool      : ${leadTool      ? `"${leadTool.name}" [${leadTool.type.split('.').pop()}]` : "❌ NOT FOUND"}`);
  console.log(`  Respond node   : ${respondNode   ? `"${respondNode.name}"` : "❌ NOT FOUND"}`);
  console.log(`  Sanitizer      : ${existingSanitizer ? "✅ already present" : "— will add"}`);
  console.log(`  All tools      : ${allTools.map(t => `"${t.name}"`).join(", ") || "none"}`);
  console.log("");

  let changed = false;

  // ── Fix: Agent chatInput + systemPrompt ────────────────────────────────
  if (agent) {
    const newText = "={{ ((($json.body?.chatInput || $json.chatInput || '').match(/[\\u0600-\\u06FF]/) ? 'Language rule: reply in Arabic only.\\nUser message: ' : 'Language rule: reply in English only.\\nUser message: ') + ($json.body?.chatInput || $json.chatInput || '')) }}";
    if (agent.parameters.text !== newText) {
      agent.parameters.text = newText;
      log("🔧", "Fixed Agent chatInput expression");
      changed = true;
    } else {
      log("✔️ ", "Agent chatInput already correct");
    }
    agent.parameters.systemMessage = NEW_SYSTEM_PROMPT;
    log("📝", "System prompt updated → ZERO URL output, booking via create_booking_request only");
    changed = true;
  }

  // ── Fix: Memory session key ────────────────────────────────────────────
  if (memory) {
    const newKey = "={{ $json.body?.sessionId || $json.sessionId || 'default' }}";
    if (memory.parameters.sessionKey !== newKey) {
      memory.parameters.sessionKey = newKey;
      log("🔧", "Fixed Memory sessionKey");
      changed = true;
    } else {
      log("✔️ ", "Memory sessionKey already correct");
    }
  }

  // ── Fix: booking tool ──────────────────────────────────────────────────
  if (bookingTool) {
    // If it's still a toolCode returning a URL, replace it with toolHttpRequest
    if (bookingTool.type === "@n8n/n8n-nodes-langchain.toolCode") {
      const nodeIndex = nodes.indexOf(bookingTool);
      nodes[nodeIndex] = {
        ...bookingTool,
        type: "@n8n/n8n-nodes-langchain.toolHttpRequest",
        typeVersion: 1.1,
        parameters: BOOKING_HTTP_PARAMS,
        name: "create_booking_request",
      };
      log("🔧", `Converted "${bookingTool.name}" from toolCode → toolHttpRequest (create_booking_request)`);
      changed = true;
    } else if (bookingTool.type === "@n8n/n8n-nodes-langchain.toolHttpRequest") {
      // Update params to ensure they're correct
      bookingTool.parameters = { ...bookingTool.parameters, ...BOOKING_HTTP_PARAMS };
      bookingTool.name = "create_booking_request";
      log("🔧", `Updated "${bookingTool.name}" → create_booking_request params refreshed`);
      changed = true;
    }
  } else {
    // No booking tool found — add one
    log("➕", "No booking tool found — adding create_booking_request node");
    const newBookingNode = {
      ...SANITIZER_NODE,
      id: "booking-tool-new",
      name: "create_booking_request",
      type: "@n8n/n8n-nodes-langchain.toolHttpRequest",
      typeVersion: 1.1,
      parameters: BOOKING_HTTP_PARAMS,
      position: [700, 620],
    };
    // Remove sanitizer-specific fields
    delete newBookingNode.jsCode;
    nodes.push(newBookingNode);
    changed = true;
  }

  // ── Fix: get_services_info tool ────────────────────────────────────────
  if (servicesTool && servicesTool.type === "@n8n/n8n-nodes-langchain.toolCode") {
    const code = servicesTool.parameters?.code || "";
    if (code.includes("toUpperCase") || !code.includes("ziyadasystem")) {
      servicesTool.parameters.code = SERVICES_TOOL_CODE;
      log("🔧", `Fixed "${servicesTool.name}" → returns full service data`);
      changed = true;
    } else {
      log("✔️ ", `"${servicesTool.name}" already has real service data`);
    }
  } else if (servicesTool) {
    log("ℹ️ ", `"${servicesTool.name}" is type ${servicesTool.type.split('.').pop()} — skipping code fix`);
  } else {
    log("⚠️ ", "No services info tool found");
  }

  // ── Fix: capture_lead tool ─────────────────────────────────────────────
  if (leadTool) {
    if (
      leadTool.type === "@n8n/n8n-nodes-langchain.toolWorkflow" ||
      (leadTool.parameters?.workflowId || "").includes("YOUR_CAPTURE_LEAD") ||
      (leadTool.parameters?.workflowId || "").includes("placeholder")
    ) {
      const nodeIndex = nodes.indexOf(leadTool);
      nodes[nodeIndex] = {
        ...leadTool,
        type: "@n8n/n8n-nodes-langchain.toolHttpRequest",
        typeVersion: 1.1,
        parameters: CAPTURE_LEAD_HTTP_PARAMS,
      };
      log("🔧", `Converted "${leadTool.name}" from toolWorkflow → toolHttpRequest → ${LEAD_INTAKE}`);
      changed = true;
    } else if (
      leadTool.type === "@n8n/n8n-nodes-langchain.toolHttpRequest" &&
      (leadTool.parameters?.url || "").includes("localhost")
    ) {
      leadTool.parameters.url = LEAD_INTAKE;
      log("🔧", `Fixed "${leadTool.name}" URL → ${LEAD_INTAKE}`);
      changed = true;
    } else {
      log("✔️ ", `"${leadTool.name}" looks OK [${leadTool.type.split('.').pop()}]`);
    }
  } else {
    log("⚠️ ", "No capture_lead tool found");
  }

  // ── Fix: Connect Webhook1 → AI Agent ──────────────────────────────────
  if (webhook1 && agent) {
    if (!workflow.connections) workflow.connections = {};
    const wh1Name = webhook1.name;
    if (!workflow.connections[wh1Name]) workflow.connections[wh1Name] = { main: [[]] };
    if (!workflow.connections[wh1Name].main) workflow.connections[wh1Name].main = [[]];
    if (!workflow.connections[wh1Name].main[0]) workflow.connections[wh1Name].main[0] = [];

    const outgoing = workflow.connections[wh1Name].main[0];
    const alreadyLinked = outgoing.some((c) => c.node === agent.name);
    if (!alreadyLinked) {
      outgoing.push({ node: agent.name, type: "main", index: 0 });
      log("🔗", `Connected: "${wh1Name}" → "${agent.name}"`);
      changed = true;
    } else {
      log("✔️ ", `"${wh1Name}" already wired to "${agent.name}"`);
    }
  }

  // ── ADD / UPDATE: Output Sanitizer node ───────────────────────────────
  if (!existingSanitizer) {
    // Position it between agent and respond node
    const sanitizerNode = {
      ...SANITIZER_NODE,
      position: [
        agent ? agent.position[0] + 280 : 820,
        agent ? agent.position[1] : 400,
      ],
    };
    nodes.push(sanitizerNode);
    log("➕", `Added "Output Sanitizer" Code node (id: ${sanitizerNode.id})`);
    changed = true;
  } else {
    // Update the code in the existing sanitizer
    existingSanitizer.parameters.jsCode = SANITIZER_NODE.parameters.jsCode;
    log("🔧", `Updated existing "Output Sanitizer" node code`);
    changed = true;
  }

  // ── Rewire: AI Agent → Output Sanitizer → Respond to Chat ─────────────
  const sanitizerName = existingSanitizer?.name || SANITIZER_NODE.name;

  if (agent && respondNode) {
    if (!workflow.connections) workflow.connections = {};
    const agentName = agent.name;
    const respondName = respondNode.name;

    // Remove direct Agent → Respond connection
    if (workflow.connections[agentName]?.main?.[0]) {
      const before = workflow.connections[agentName].main[0].length;
      workflow.connections[agentName].main[0] = workflow.connections[agentName].main[0].filter(
        (c) => c.node !== respondName
      );
      const after = workflow.connections[agentName].main[0].length;
      if (before !== after) {
        log("✂️ ", `Removed direct "${agentName}" → "${respondName}" connection`);
        changed = true;
      }

      // Add Agent → Sanitizer
      if (!workflow.connections[agentName].main[0].some((c) => c.node === sanitizerName)) {
        workflow.connections[agentName].main[0].push({ node: sanitizerName, type: "main", index: 0 });
        log("🔗", `Connected: "${agentName}" → "${sanitizerName}"`);
        changed = true;
      }
    }

    // Add Sanitizer → Respond
    if (!workflow.connections[sanitizerName]) workflow.connections[sanitizerName] = { main: [[]] };
    if (!workflow.connections[sanitizerName].main) workflow.connections[sanitizerName].main = [[]];
    if (!workflow.connections[sanitizerName].main[0]) workflow.connections[sanitizerName].main[0] = [];

    if (!workflow.connections[sanitizerName].main[0].some((c) => c.node === respondName)) {
      workflow.connections[sanitizerName].main[0].push({ node: respondName, type: "main", index: 0 });
      log("🔗", `Connected: "${sanitizerName}" → "${respondName}"`);
      changed = true;
    } else {
      log("✔️ ", `"${sanitizerName}" already wired to "${respondName}"`);
    }

    // Update Respond to Chat to read from Sanitizer
    if (respondNode && respondNode.parameters?.responseBody) {
      const oldBody = respondNode.parameters.responseBody;
      const newBody = `={{ JSON.stringify({ output: $('${sanitizerName}').item.json.output }) }}`;
      if (oldBody !== newBody) {
        respondNode.parameters.responseBody = newBody;
        log("🔧", `Updated "Respond to Chat" to read from "${sanitizerName}"`);
        changed = true;
      }
    }
  }

  // ── Step: Push workflow ────────────────────────────────────────────────
  if (!changed) {
    log("ℹ️ ", "No changes detected — workflow already up to date");
  } else {
    log("📤", "Pushing patched workflow to n8n...");

    const putBody = {
      name: workflow.name,
      nodes: workflow.nodes,
      connections: workflow.connections,
      settings: workflow.settings || {},
      staticData: workflow.staticData || null,
    };

    const putRes = await fetch(`${N8N_BASE}/api/v1/workflows/${WORKFLOW_ID}`, {
      method: "PUT",
      headers,
      body: JSON.stringify(putBody),
    });

    if (!putRes.ok) {
      const body = await putRes.text();
      throw new Error(`Failed to update workflow: ${putRes.status} — ${body}`);
    }
    log("✅", "Workflow saved successfully");

    // ── Activate (optional) ───────────────────────────────────────────
    if (SKIP_ACTIVATE) {
      log("⏸️ ", "Skipping activation (N8N_SKIP_ACTIVATE is enabled)");
    } else {
      log("▶️ ", "Activating workflow...");
      const activateRes = await fetch(`${N8N_BASE}/api/v1/workflows/${WORKFLOW_ID}/activate`, {
        method: "POST",
        headers,
      });
      if (!activateRes.ok) {
        const body = await activateRes.text();
        if (activateRes.status === 409) {
          log("ℹ️ ", "Workflow already active");
        } else {
          log("⚠️ ", `Activate returned ${activateRes.status}: ${body}`);
        }
      } else {
        log("✅", "Workflow is active and live");
      }
    }
  }

  if (SKIP_LIVE_TESTS) {
    console.log("\n── Live Tests ────────────────────────────────────────");
    console.log("  Skipped (N8N_SKIP_LIVE_TESTS is enabled)\n");
    console.log("═══════════════════════════════════════════════════");
    console.log("  ✅ Workflow draft patched successfully");
    console.log("  ✅ Test now inside n8n editor chat panel");
    console.log("═══════════════════════════════════════════════════\n");
    return;
  }

  // ── Step: Live tests ───────────────────────────────────────────────────
  console.log("\n── Live Tests ────────────────────────────────────────");
  console.log("  Waiting 3s for n8n to reload...\n");
  await new Promise((r) => setTimeout(r, 3000));

  const tests = [
    { label: "Arabic greeting",    chatInput: "يا هلا",                                sessionId: "v4-test-ar-001" },
    { label: "Booking request",    chatInput: "أبي أحجز استشارة مجانية",               sessionId: "v4-test-ar-002" },
    { label: "English services",   chatInput: "Hi, what do you offer?",                sessionId: "v4-test-en-003" },
  ];

  let allPassed = true;

  for (const test of tests) {
    process.stdout.write(`  [${test.label}] → `);
    try {
      const r = await fetch(CHAT_WEBHOOK, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "sendMessage",
          chatInput: test.chatInput,
          sessionId: test.sessionId,
          channel: "website_chat",
          event_ts: new Date().toISOString(),
        }),
      });

      const raw = await r.text();
      let reply = "";
      try {
        const data = JSON.parse(raw);
        reply = data.output || data.response || data.text || data.message || JSON.stringify(data);
      } catch { reply = raw; }

      const preview = reply.slice(0, 180).replace(/\n/g, " ");
      const hasCalendly    = /calendly|cal\.com/i.test(reply);
      const hasLocalhost   = /localhost/i.test(reply);
      const hasBoldMD      = /\*\*/i.test(reply);
      const hasExtURL      = /https?:\/\/(?!(?:www\.)?ziyadasystem\.com)/i.test(reply);
      const hasPlaceholder = /YOUR_CAPTURE|toUpperCase/i.test(reply);

      const statusIcon =
        !r.ok           ? "❌ HTTP " + r.status :
        hasCalendly     ? "⚠️  CALENDLY STILL PRESENT" :
        hasLocalhost    ? "⚠️  LOCALHOST" :
        hasExtURL       ? "⚠️  EXTERNAL URL" :
        hasBoldMD       ? "⚠️  MARKDOWN **" :
        hasPlaceholder  ? "⚠️  PLACEHOLDER" :
        "✅ CLEAN";

      console.log(`${statusIcon}`);
      console.log(`       Sent  : "${test.chatInput}"`);
      console.log(`       Reply : "${preview}${reply.length > 180 ? "…" : ""}"`);
      if (hasCalendly)    { console.log("       ⚠️  Calendly still in output — check system prompt!"); allPassed = false; }
      if (hasLocalhost)   { console.log("       ⚠️  Localhost URL in output!"); allPassed = false; }
      if (hasExtURL)      { console.log("       ⚠️  External URL escaped sanitizer!"); allPassed = false; }
      if (hasBoldMD)      { console.log("       ⚠️  ** markdown still in output!"); allPassed = false; }
      if (hasPlaceholder) { console.log("       ⚠️  Placeholder data returned!"); allPassed = false; }
      console.log("");
    } catch (err) {
      console.log(`❌ ERROR: ${err.message}`);
      allPassed = false;
    }
  }

  // ── Summary ────────────────────────────────────────────────────────────
  console.log("═══════════════════════════════════════════════════");
  if (allPassed) {
    console.log("  ✅ ALL FIXES APPLIED — Chat is clean and live");
    console.log("  ✅ No Calendly / localhost / external URLs / markdown");
    console.log("  Test the live site: https://ziyadasystem.com");
  } else {
    console.log("  ⚠️  Some checks flagged — see output above");
    console.log("  Workflow was saved — test from https://ziyadasystem.com");
    console.log("  If Calendly still appears, the LLM may need a stronger system prompt.");
  }
  console.log("═══════════════════════════════════════════════════\n");
}

main().catch((err) => {
  console.error("\n❌ Script failed:", err.message);
  process.exit(1);
});
