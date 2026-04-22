#!/usr/bin/env python3
"""Patch live VAPI assistant:
- Set maxDurationSeconds to 480 (8 minutes)
- Replace system prompt with full voice agent rules incl. 8-min close policy
- Keep existing voice / transcriber / model settings
"""
from __future__ import annotations
import json
from pathlib import Path
import requests


ROOT_ENV = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/.env.local')
APP_ENV = Path('/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/app/ziyada-system-website/.env.local')

SYSTEM_PROMPT = """أنت زياد، موظف مبيعات سعودي من زيادة سيستم داخل الموقع الرسمي.
تكلم باختصار شديد، وبشكل طبيعي، وجملة أو جملتين فقط في كل مرة.

القواعد الأساسية:
- لا تسرد الخدمات الستة دفعة واحدة أبداً.
- إذا سأل العميل سؤالاً عاماً مثل: وش خدماتكم؟ أو وش تقدرون تساعدون فيه؟ جاوبه بجملة تعريفية قصيرة فقط، ثم اسأله عن التحدي الرئيسي.
- لا تستخدم get_services_info إلا إذا طلب خدمة محددة أو تفاصيل أكثر عن مجال معيّن.
- إذا قال: أبي شيء زيك أو أبي voice agent أو chatbot، ابدأ بحالة استخدام تجارية من زيادة سيستم، وليس قائمة أدوات أو خدمات.
- لا تقل انتظر أو wait. استخدم: عطني ثانية، تفضل معي، ثواني عن إذنك.
- الأرقام المهمة تقرأ رقماً رقماً.
- إذا جمعْت الاسم مع الجوال أو الإيميل، استعمل save_lead فوراً.
- إذا وافق على اجتماع، استعمل create_booking_request فوراً.
- اختم دائماً بعرض المتابعة على شات الموقع أو واتساب.

حد المكالمة وإنهاؤها:
- وقت المكالمة محدد بثماني دقائق.
- قبل دقيقة ونصف تقريباً من الثماني دقائق (أي عند الدقيقة السابعة تقريباً) قل بلطف: "نحن نقترب من نهاية وقت المكالمة. أقدر أكمل معك على شات الموقع أو واتساب إذا حبيت نكمل النقاش."
- عند انتهاء الوقت لا توقف فجأة؛ أنهِ بجملة مهذبة قصيرة.

عن زيادة سيستم باختصار:
نساعد الشركات في الأتمتة، CRM والمبيعات، توليد العملاء، التسويق الرقمي، تطوير المواقع، وإدارة السوشيال ميديا.
لكن دائماً اربط الجواب باحتياج العميل بدلاً من تعداد الخدمات."""


def read_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    env: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main() -> None:
    root_env = read_env(ROOT_ENV)
    app_env = read_env(APP_ENV)
    api_key = root_env.get('VAPI_API_KEY') or app_env.get('VAPI_API_KEY')
    assistant_id = app_env.get('VAPI_ASSISTANT_ID') or app_env.get('VITE_VAPI_ASSISTANT_ID')
    if not api_key or not assistant_id:
        raise SystemExit('Missing VAPI_API_KEY or assistant id')

    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    url = f'https://api.vapi.ai/assistant/{assistant_id}'

    current = requests.get(url, headers=headers, timeout=30).json()
    model: dict = dict(current.get('model') or {})
    # Update system prompt
    model['systemPrompt'] = SYSTEM_PROMPT

    payload = {
        'name': current.get('name'),
        'firstMessage': current.get('firstMessage'),
        'maxDurationSeconds': 480,
        'voice': current.get('voice'),
        'transcriber': current.get('transcriber'),
        'model': model,
        'analysisPlan': current.get('analysisPlan'),
        'artifactPlan': current.get('artifactPlan'),
        'startSpeakingPlan': current.get('startSpeakingPlan'),
        'responseDelaySeconds': current.get('responseDelaySeconds', 0),
        'llmRequestDelaySeconds': current.get('llmRequestDelaySeconds', 0),
        'serverMessages': current.get('serverMessages'),
        'clientMessages': current.get('clientMessages'),
        'endCallMessage': current.get('endCallMessage'),
        'voicemailMessage': current.get('voicemailMessage'),
        'backgroundDenoisingEnabled': current.get('backgroundDenoisingEnabled', False),
    }
    r = requests.patch(url, headers=headers, data=json.dumps(payload), timeout=40)
    r.raise_for_status()
    out = r.json()
    out_model = out.get('model') or {}
    print(json.dumps({
        'assistantId': out.get('id'),
        'maxDurationSeconds': out.get('maxDurationSeconds'),
        'modelProvider': (out_model).get('provider'),
        'modelName': (out_model).get('model'),
        'systemPromptSnippet': str(out_model.get('systemPrompt') or '')[:120],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
