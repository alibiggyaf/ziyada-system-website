#!/usr/bin/env python3
"""Create a bilingual Ziyada System company profile deck in Google Slides."""

from pathlib import Path
from typing import Dict, List, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

DECK_TITLE = "Ziyada System | زيادة سيستم | Corporate Company Profile"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

SLIDES = [
    {
        "title": "Ziyada System | زيادة سيستم",
        "body": "EN: Jeddah-centered, KSA-wide enablement.\nAR: تمركز في جدة، وتمكين على مستوى المملكة.\n\nAI-Enabled Operations for Corporate Scale\nتشغيل مؤسسي مدعوم بالذكاء الاصطناعي",
    },
    {
        "title": "Executive Snapshot | الملخص التنفيذي",
        "body": "• Corporate-first AI transformation partner\n• Enterprise-grade operating model\n• Measurable impact on cost, speed, and quality\n\n• شريك تحول ذكاء اصطناعي بتركيز مؤسسي\n• نموذج تشغيل مصمم لاعتمادية المؤسسات\n• أثر قابل للقياس في التكلفة والسرعة والجودة",
    },
    {
        "title": "Who We Are | من نحن",
        "body": "Ziyada System supports corporate companies, B2B organizations, and enterprise teams through AI-powered automation and scalable digital operations.\n\nتدعم زيادة سيستم الشركات المؤسسية وشركات B2B وفرق المؤسسات الكبرى عبر أتمتة مدعومة بالذكاء الاصطناعي وعمليات رقمية قابلة للتوسع.",
    },
    {
        "title": "Our Core Audience | جمهورنا المستهدف",
        "body": "• Corporate companies (primary)\n• Enterprise operations teams\n• B2B platform and service companies\n• Regulated organizations\n\n• الشركات المؤسسية (التركيز الأساسي)\n• فرق تشغيل المؤسسات الكبرى\n• شركات الخدمات والمنصات B2B\n• الجهات ذات المتطلبات التنظيمية العالية",
    },
    {
        "title": "Operational Gaps We Solve | الفجوات التشغيلية التي نعالجها",
        "body": "• Fragmented systems and duplicated effort\n• Slow manual workflows\n• Low KPI visibility\n• High operating cost without proportional growth\n\n• تشتت الأنظمة وتكرار الجهد\n• بطء سير العمل اليدوي\n• انخفاض وضوح مؤشرات الأداء\n• ارتفاع التكلفة التشغيلية دون نمو متناسب",
    },
    {
        "title": "AI Enablement Framework | إطار تفعيل الذكاء الاصطناعي",
        "body": "1) Assess workflows and data readiness\n2) Design governance-first AI architecture\n3) Automate critical operations with human oversight\n4) Scale with controls and measurable KPIs\n\n1) تقييم جاهزية سير العمل والبيانات\n2) تصميم بنية ذكاء اصطناعي بحوكمة واضحة\n3) أتمتة العمليات الحرجة مع إشراف بشري\n4) التوسع مع رقابة ومؤشرات أداء قابلة للقياس",
    },
    {
        "title": "Services | خدمات زيادة سيستم",
        "body": "• AI Opportunity Mapping\n• Workflow Automation and Integration\n• Data and Analytics Enablement\n• Enterprise Process Orchestration\n• Change Management and Team Adoption\n\n• تحديد فرص الذكاء الاصطناعي\n• أتمتة وتكامل سير العمل\n• تمكين البيانات والتحليلات\n• تنسيق العمليات المؤسسية\n• إدارة التغيير وتبنّي الفرق",
    },
    {
        "title": "Corporate Use Cases | حالات استخدام مؤسسية",
        "body": "• Finance approvals automation\n• HR onboarding orchestration\n• Sales-to-delivery handoff\n• Executive dashboards\n\n• أتمتة الموافقات المالية\n• تنسيق انضمام الموظفين\n• ربط المبيعات بالتنفيذ\n• لوحات مؤشرات تنفيذية",
    },
    {
        "title": "Impact Model | نموذج الأثر",
        "body": "• Process cycle-time reduction\n• Manual task reduction\n• SLA compliance improvement\n• Decision latency reduction\n\n• تقليل زمن دورة العملية\n• خفض المهام اليدوية\n• رفع الالتزام بمستوى الخدمة\n• تقليل زمن اتخاذ القرار",
    },
    {
        "title": "Case Study 1 | دراسة حالة 1",
        "body": "Challenge | التحدي\nApproach | المنهج\nOutcome | النتيجة\n\nUse realistic, measurable outcomes only.\nاستخدم نتائج واقعية وقابلة للقياس فقط.",
    },
    {
        "title": "Case Study 2 | دراسة حالة 2",
        "body": "Challenge | التحدي\nApproach | المنهج\nOutcome | النتيجة\n\nB2B workflow modernization scenario.\nسيناريو تحديث سير عمل B2B.",
    },
    {
        "title": "Security and Governance | الأمان والحوكمة",
        "body": "• Role-based controls\n• Data handling governance\n• Auditability and traceability\n• Business continuity standards\n\n• ضوابط مبنية على الصلاحيات\n• حوكمة واضحة للبيانات\n• قابلية التتبع والمراجعة\n• معايير استمرارية الأعمال",
    },
    {
        "title": "Engagement Models | نماذج التعاقد والتنفيذ",
        "body": "• Assessment Sprint\n• Transformation Program\n• Managed Automation Operations\n\n• تقييم تشغيلي سريع\n• برنامج تحول متكامل\n• تشغيل أتمتة مُدار",
    },
    {
        "title": "Why Ziyada System | لماذا زيادة سيستم",
        "body": "• Corporate-first execution\n• Saudi market context fluency\n• AI + automation implementation capability\n• Outcome accountability\n\n• نموذج تنفيذ بتركيز مؤسسي\n• فهم عميق لسياق السوق السعودي\n• قدرة فعلية على تطبيق الذكاء الاصطناعي والأتمتة\n• التزام واضح بالنتائج",
    },
    {
        "title": "Regional Presence | الحضور الإقليمي",
        "body": "EN: Jeddah-centered, KSA-wide enablement.\nAR: تمركز في جدة، وتمكين على مستوى المملكة.",
    },
    {
        "title": "Message to Corporate Leaders | رسالة إلى القيادات التنفيذية",
        "body": "We help corporate companies implement AI and automation as an operating capability, not a short-term experiment.\n\nنساعد الشركات المؤسسية على تطبيق الذكاء الاصطناعي والأتمتة كقدرة تشغيلية مستمرة، وليس كتجربة قصيرة المدى.",
    },
    {
        "title": "Call to Action | دعوة للعمل",
        "body": "Book an executive discovery session with Ziyada System.\n\nاحجز جلسة تشخيص تنفيذية مع زيادة سيستم.",
    },
    {
        "title": "Ziyada System | زيادة سيستم",
        "body": "Jeddah-centered. KSA-wide. Corporate-ready.\n\nمن جدة إلى المملكة. جاهزون لتمكين الشركات المؤسسية.",
    },
]


def get_creds() -> Credentials:
    token_path = PROJECT_DIR / "token.json"
    if not token_path.exists():
        raise RuntimeError("token.json not found. Run scripts/populate_manual_auth.py first.")
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid:
        raise RuntimeError("token.json exists but is invalid for Slides scope. Re-run scripts/populate_manual_auth.py.")
    return creds


def first_placeholder(elements: List[Dict], placeholder_type: str) -> Optional[str]:
    for el in elements:
        shape = el.get("shape")
        if not shape:
            continue
        ph = shape.get("placeholder")
        if not ph:
            continue
        if ph.get("type") == placeholder_type:
            return el.get("objectId")
    return None


def insert_text_request(object_id: str, text: str) -> Dict:
    return {"insertText": {"objectId": object_id, "insertionIndex": 0, "text": text}}


def style_text_request(object_id: str, font_family: str, font_size: int, bold: bool = False) -> Dict:
    return {
        "updateTextStyle": {
            "objectId": object_id,
            "textRange": {"type": "ALL"},
            "style": {
                "fontFamily": font_family,
                "fontSize": {"magnitude": font_size, "unit": "PT"},
                "bold": bold,
            },
            "fields": "fontFamily,fontSize,bold",
        }
    }


def main() -> None:
    creds = get_creds()
    service = build("slides", "v1", credentials=creds)

    created = service.presentations().create(body={"title": DECK_TITLE}).execute()
    deck_id = created["presentationId"]

    # Add remaining slides (new deck already has one slide)
    create_requests = []
    for _ in range(len(SLIDES) - 1):
        create_requests.append(
            {"createSlide": {"slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"}}}
        )
    if create_requests:
        service.presentations().batchUpdate(
            presentationId=deck_id,
            body={"requests": create_requests},
        ).execute()

    pres = service.presentations().get(presentationId=deck_id).execute()
    slide_objs = pres.get("slides", [])

    text_requests: List[Dict] = []
    for idx, slide in enumerate(slide_objs[: len(SLIDES)]):
        data = SLIDES[idx]
        elements = slide.get("pageElements", [])

        title_id = first_placeholder(elements, "TITLE") or first_placeholder(elements, "CENTERED_TITLE")
        body_id = first_placeholder(elements, "BODY")

        if title_id:
            text_requests.append(insert_text_request(title_id, data["title"]))
            text_requests.append(style_text_request(title_id, "Outfit", 34, True))

        if body_id:
            text_requests.append(insert_text_request(body_id, data["body"]))
            text_requests.append(style_text_request(body_id, "Cairo", 16, False))

    if text_requests:
        service.presentations().batchUpdate(
            presentationId=deck_id,
            body={"requests": text_requests},
        ).execute()

    print(f"https://docs.google.com/presentation/d/{deck_id}/edit")


if __name__ == "__main__":
    main()
