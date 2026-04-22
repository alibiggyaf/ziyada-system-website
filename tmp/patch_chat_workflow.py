import json
from pathlib import Path
from urllib.request import Request, urlopen


def load_env(paths):
    cfg = {}
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


cfg = load_env([
    '.env.local',
    '.env',
    'projects/ziyada-system/app/ziyada-system-website/.env.local',
    'projects/ziyada-system/app/ziyada-system-website/.env',
])

base = (cfg.get('N8N_API_URL') or (cfg.get('N8N_BASE_URL', '').rstrip('/') + '/api/v1')).rstrip('/')
key = cfg.get('N8N_API_KEY', '').strip()
wid = 'eO6LzcPrnPT3JlpA'

if not base or not key:
    raise RuntimeError('Missing N8N API config')


def api_get(path):
    req = Request(f"{base}{path}", headers={'X-N8N-API-KEY': key, 'Accept': 'application/json'})
    with urlopen(req) as r:
        return json.loads(r.read().decode())


def api_send(method, path, body):
    req = Request(
        f"{base}{path}",
        data=json.dumps(body).encode('utf-8'),
        headers={'X-N8N-API-KEY': key, 'Content-Type': 'application/json', 'Accept': 'application/json'},
        method=method,
    )
    with urlopen(req) as r:
        return json.loads(r.read().decode())


wf = api_get(f'/workflows/{wid}')

new_code = r'''
const payload = $input.first().json || {};
const msg = String(payload.chatInput || '').trim();
const isArabic = /[\u0600-\u06FF]/.test(msg);

const BASE_URL = 'https://ziyadasystem.com';
const ALLOWED_HOSTS = new Set(['ziyadasystem.com', 'www.ziyadasystem.com']);

function sanitizeLinks(text) {
  return String(text || '').replace(/https?:\/\/[^\s)]+/gi, (url) => {
    const lower = url.toLowerCase();
    if (lower.startsWith('https://ziyadasystem.com') || lower.startsWith('https://www.ziyadasystem.com')) {
      return url;
    }
    return BASE_URL;
  });
}

function detectIntent(text) {
  const t = text.toLowerCase();
  if (/مرح|أهلا|اهلا|سلام|هلا|hello|hi\b|hey|good\s*(morning|evening)/.test(t)) return 'greeting';
  if (/خدم|services?|what do you|what can/.test(t)) return 'services';
  if (/استشار|consult|book|احجز|meeting|جلسة|session|appointment|demo/.test(t)) return 'consult';
  if (/سعر|price|pricing|cost|كم|تكلف|budget|quote|عرض سعر/.test(t)) return 'price';
  if (/تواصل|contact|اتصل|email|phone|رقم|واتس|whatsapp/.test(t)) return 'contact';
  if (/أتمت|automat|workflow|n8n|agent|integration/.test(t)) return 'automation';
  return 'default';
}

function extractEmail(text, fallback) {
  if (fallback && /@/.test(String(fallback))) return String(fallback).trim();
  const m = text.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
  return m ? m[0] : '';
}

function extractPhone(text, fallback) {
  if (fallback) return String(fallback).trim();
  const m = text.match(/(?:\+?966|0)?5\d{8}|\+?\d{8,15}/);
  return m ? m[0].replace(/\s+/g, '') : '';
}

function extractName(text) {
  const ar = text.match(/(?:اسمي|انا|أنا)\s+([\u0600-\u06FF\s]{2,40})/);
  if (ar) return ar[1].trim();
  const en = text.match(/(?:my name is|i am)\s+([a-zA-Z\s]{2,40})/i);
  if (en) return en[1].trim();
  return '';
}

function extractCompany(text) {
  const ar = text.match(/(?:شركة|مؤسسة|اسم الشركة)\s*[:\-]?\s*([\u0600-\u06FFa-zA-Z0-9\s\-_.]{2,60})/i);
  if (ar) return ar[1].trim();
  const en = text.match(/(?:company|business)\s*[:\-]?\s*([a-zA-Z0-9\s\-_.]{2,60})/i);
  if (en) return en[1].trim();
  return '';
}

function mapService(text) {
  const t = text.toLowerCase();
  if (/أتمت|automat|workflow|n8n|agent/.test(t)) return isArabic ? 'أتمتة الأعمال' : 'Business Automation';
  if (/crm|عملاء|مبيعات/.test(t)) return isArabic ? 'إدارة العملاء والمبيعات' : 'CRM & Sales';
  if (/تسويق|ads|marketing/.test(t)) return isArabic ? 'التسويق الأدائي' : 'Performance Marketing';
  if (/موقع|website|ويب/.test(t)) return isArabic ? 'المواقع الذكية' : 'Smart Websites';
  if (/محتو|content|social/.test(t)) return isArabic ? 'أنظمة المحتوى' : 'Content Systems';
  return '';
}

const lead = {
  name: extractName(msg),
  email: extractEmail(msg, payload.email),
  phone: extractPhone(msg, payload.phone_e164),
  company: extractCompany(msg),
  challenge: msg,
  service_interest: mapService(msg),
  source: 'chat_widget',
  language: isArabic ? 'ar' : 'en',
};

const hasLeadData = Boolean((lead.email || lead.phone) && lead.challenge);

const links = {
  home: 'https://ziyadasystem.com',
  book: 'https://ziyadasystem.com/BookMeeting',
  quote: 'https://ziyadasystem.com/RequestProposal',
  contact: 'https://ziyadasystem.com/Contact',
  services: 'https://ziyadasystem.com/work',
};

const arResponses = {
  greeting: `أهلاً وسهلاً 👋\nأنا مساعد زيادة سيستم.\n\nتقدر تتصفح خدماتنا هنا: ${links.services}\nأو تحجز استشارة مجانية: ${links.book}`,
  services: `خدماتنا الرئيسية في زيادة سيستم:\n• أتمتة الأعمال\n• CRM وإدارة المبيعات\n• اكتساب العملاء\n• التسويق الأدائي\n• المواقع الذكية\n• أنظمة المحتوى\n\nتفاصيل الخدمات: ${links.services}`,
  consult: `ممتاز، نقدر نرتب لك استشارة مجانية من هنا: ${links.book}\n\nقبل الحجز النهائي، أرسل لي:\n1) الاسم\n2) الإيميل\n3) رقم الجوال\n4) التحدي الرئيسي في نشاطك`,
  price: `الأسعار تعتمد على نطاق العمل وحجم النشاط.\n\nعشان نعطيك عرض دقيق، قدم طلب عرض سعر من: ${links.quote}\nأو أرسل اسمك + إيميلك + جوالك + التحدي الرئيسي هنا ونرتبها لك.`,
  contact: `تقدر تتواصل معنا عبر صفحة التواصل: ${links.contact}\nأو تحجز استشارة مباشرة: ${links.book}`,
  automation: `ممتاز، الأتمتة عندنا تركّز على تقليل العمل اليدوي وربط الأنظمة (CRM, WhatsApp, Email).\n\nابدأ من هنا: ${links.book}`,
  default: `فهمت عليك. إذا حاب نبدأ بشكل عملي، أرسل:\n• الاسم\n• الإيميل\n• رقم الجوال\n• التحدي الرئيسي\n\nوأنا بجهزها كطلب داخل النظام.\n\nالخدمات: ${links.services}`,
  lead_capture: `وصلتني بياناتك بشكل واضح.\n\nبجهز طلبك الآن للفريق باستخدام نفس حقول النموذج عندنا، وإذا حاب تكمل مباشرة تقدر تزور: ${links.book}`,
};

const enResponses = {
  greeting: `Hi there 👋 I am Ziyada Systems assistant.\n\nServices: ${links.services}\nBook free consultation: ${links.book}`,
  services: `Our main services:\n• Business Automation\n• CRM & Sales Systems\n• Lead Generation\n• Performance Marketing\n• Smart Websites\n• Content Systems\n\nSee details: ${links.services}`,
  consult: `Great. You can book a free consultation here: ${links.book}\n\nTo prepare your case, please send:\n1) Name\n2) Email\n3) Phone\n4) Main business concern`,
  price: `Pricing depends on scope and goals.\n\nRequest a tailored quote here: ${links.quote}\nOr share your name + email + phone + main concern and I will log it for the team.`,
  contact: `Contact page: ${links.contact}\nBook consultation: ${links.book}`,
  automation: `Our automation service connects your tools (CRM, WhatsApp, Email) and removes manual work.\n\nStart here: ${links.book}`,
  default: `I can help with your request. Please share:\n• Name\n• Email\n• Phone\n• Main concern\n\nI will log it for follow-up.\nServices: ${links.services}`,
  lead_capture: `I have your details clearly now.\n\nI will pass this into the same lead fields used on the website form, and if you want to continue directly you can visit: ${links.book}`,
};

const intent = detectIntent(msg);
const responses = isArabic ? arResponses : enResponses;
const output = sanitizeLinks(hasLeadData ? responses.lead_capture : (responses[intent] || responses.default));

return [{
  json: {
    output,
    status: 'success',
    model: 'ziyada-smart-agent-v2',
    lead_capture: {
      ...lead,
      captured: hasLeadData,
    },
  }
}];
'''

for node in wf.get('nodes', []):
    if node.get('name') == 'Smart Response Engine':
        node.setdefault('parameters', {})['jsCode'] = new_code

payload = {
    'name': wf.get('name'),
    'nodes': wf.get('nodes', []),
    'connections': wf.get('connections', {}),
  'settings': {'executionOrder': 'v1'},
}

api_send('PUT', f'/workflows/{wid}', payload)

activated = False
for method in ('POST', 'PUT'):
    try:
        api_send(method, f'/workflows/{wid}/activate', {})
        activated = True
        break
    except Exception:
        continue

final = api_get(f'/workflows/{wid}')
Path('tmp/live_chat_workflow_after_patch.json').write_text(json.dumps(final, ensure_ascii=False, indent=2))

print('patched_workflow', final.get('id'))
print('active', final.get('active'))
print('activated_via_api', activated)
print('versionCounter', final.get('versionCounter'))
