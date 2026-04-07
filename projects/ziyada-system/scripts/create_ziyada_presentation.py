#!/usr/bin/env python3
"""
Ziyada System - Guided Google Slides Builder

This script enforces Ziyada brand guidelines before rendering:
- Official palette (#0f172a, #3b82f6, #8b5cf6, #ffffff, #e2e8f0, #06b6d4, #ec4899)
- Bilingual style (EN + AR)
- Arabic-first business tone
- Includes Partnership core value (الشراكة)

Behavior:
- Creates 11 fresh BLANK slides
- Deletes old slides to remove placeholders
- Applies branded composition (background blocks, accent shapes, title/subtitle/content)
"""

from __future__ import annotations

import json
import os
import uuid

from typing import Dict, List
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import brand_validation

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DECK_ID = "1P69LX9nstqY7_kpq7F7ygFLaEn_oOjxaqK7BT1SMRNU"
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(_SCRIPT_DIR, "token.json")

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

# Ziyada official palette from guidelines.
PALETTE_HEX = {
    "deep_blue": "#0f172a",
    "blue": "#3b82f6",
    "purple": "#8b5cf6",
    "white": "#ffffff",
    "light_gray": "#e2e8f0",
    "teal": "#06b6d4",
    "pink": "#ec4899",
}

SLIDES_DATA = [
    {
        "title": "Ziyada System",
        "subtitle": "نصمم أنظمة تشغيل ذكية تنمّي أعمالك بثقة",
        "body": [
            "Build once. Scale logically. Grow predictably.",
            "ابنِ مرة واحدة. توسّع بمنهج. حقق نموًا متوقعًا.",
        ],
    },
    {
        "title": "Mission & Vision",
        "subtitle": "الرسالة والرؤية",
        "body": [
            "Mission: Human-centric digital systems for real operations.",
            "Vision: The region's most trusted transformation partner.",
            "الرسالة: حلول رقمية إنسانية موجهة للتشغيل الحقيقي.",
            "الرؤية: الشريك الأكثر موثوقية للتحول الرقمي في المنطقة.",
        ],
    },
    {
        "title": "What We Build",
        "subtitle": "ماذا نبني",
        "body": [
            "Automation workflows across sales, service, and operations.",
            "Integrated data and reporting for faster decisions.",
            "أتمتة متكاملة للمبيعات وخدمة العملاء والتشغيل.",
            "تكامل بيانات وتقارير تدعم القرار بسرعة.",
        ],
    },
    {
        "title": "Core Services",
        "subtitle": "الخدمات الأساسية",
        "body": [
            "Growth Architecture",
            "Data Integration",
            "Workflow Automation",
            "Brand-aligned AI content systems",
            "هندسة نمو + تكامل بيانات + أتمتة سير العمل",
        ],
    },
    {
        "title": "Why Ziyada",
        "subtitle": "لماذا زيادة",
        "body": [
            "Clear operating model, not buzzwords.",
            "Measured delivery and transparent execution.",
            "Flexible systems that scale with your business.",
            "تنفيذ واضح، ونتائج قابلة للقياس، وشراكة طويلة المدى.",
        ],
    },
    {
        "title": "Execution Method",
        "subtitle": "منهج التنفيذ",
        "body": [
            "1) Assess current state",
            "2) Design architecture",
            "3) Implement integrations",
            "4) Measure and optimize",
            "5) Scale with governance",
            "نبدأ بالتقييم ثم التصميم فالتنفيذ ثم التحسين والتوسع.",
        ],
    },
    {
        "title": "Who We Serve",
        "subtitle": "من نخدم",
        "body": [
            "Founders, CEOs/COOs, growth leaders, revenue teams.",
            "Sectors: SaaS, e-commerce, healthcare, professional services.",
            "نخدم فرق القيادة والتشغيل في الشركات النامية والطموحة.",
        ],
    },
    {
        "title": "Core Values",
        "subtitle": "القيم الأساسية",
        "body": [
            "Innovation | الابتكار",
            "Integrity | النزاهة",
            "Partnership | الشراكة",
            "Excellence | التميّز",
            "We grow alongside our clients. ننمو جنبًا إلى جنب مع عملائنا.",
        ],
    },
    {
        "title": "Proof & Outcomes",
        "subtitle": "الأثر والنتائج",
        "body": [
            "Reduced response time and improved follow-up quality.",
            "Higher visibility on pipeline and operations health.",
            "Improved execution speed with consistent standards.",
            "تحسين الاستجابة، رفع جودة المتابعة، وتسريع اتخاذ القرار.",
        ],
    },
    {
        "title": "Project Organization",
        "subtitle": "تنظيم المشروع على Google Drive",
        "body": [
            "Root folder: ziyada system project",
            "01_Brand_Guidelines | 02_Presentations | 03_Documents",
            "04_Assets | 05_Automation_Outputs | 06_Archive",
            "كل ملفات زيادة وأصولها وتسليماتها ضمن هيكل موحد وواضح.",
        ],
    },
    {
        "title": "Next Step",
        "subtitle": "الخطوة القادمة",
        "body": [
            "Book a working session to activate your operating system.",
            "احجز جلسة عمل لتفعيل نظام النمو الخاص بك.",
            "Email: ali.biggy.af@gmail.com",
        ],
    },
]


def hex_to_rgb_obj(color: str) -> Dict[str, float]:
    c = color.lstrip("#")
    return {
        "red": int(c[0:2], 16) / 255,
        "green": int(c[2:4], 16) / 255,
        "blue": int(c[4:6], 16) / 255,
    }


def text_color_style(hex_color: str) -> Dict[str, Dict[str, Dict[str, float]]]:
    return {"opaqueColor": {"rgbColor": hex_to_rgb_obj(hex_color)}}


def shape_color_style(hex_color: str) -> Dict[str, Dict[str, float]]:
    return {"rgbColor": hex_to_rgb_obj(hex_color)}


def authenticate() -> Credentials:
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        token_data = json.load(f)
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def create_clean_slides(service, presentation_id: str, count: int) -> List[str]:
    pres = service.presentations().get(presentationId=presentation_id).execute()
    old_ids = [s["objectId"] for s in pres.get("slides", [])]

    run_id = uuid.uuid4().hex[:6]
    new_ids = [f"ziyada_slide_{i+1}_{run_id}" for i in range(count)]

    create_requests = []
    for sid in new_ids:
        create_requests.append(
            {
                "createSlide": {
                    "objectId": sid,
                    "slideLayoutReference": {"predefinedLayout": "BLANK"},
                }
            }
        )

    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": create_requests},
    ).execute()

    delete_requests = [{"deleteObject": {"objectId": sid}} for sid in old_ids]
    if delete_requests:
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": delete_requests},
        ).execute()

    return new_ids


def build_slide_requests() -> List[dict]:
    requests: List[dict] = []

    # Composition constants.
    page_w = 960
    page_h = 540

    backgrounds = [PALETTE_HEX["deep_blue"], "#111827"]
    accent_cycle = [PALETTE_HEX["blue"], PALETTE_HEX["purple"], PALETTE_HEX["teal"], PALETTE_HEX["pink"]]

    run_id = uuid.uuid4().hex[:6]

    for idx, slide in enumerate(SLIDES_DATA):
        slide_id = slide["_slide_id"]
        bg = backgrounds[idx % len(backgrounds)]
        accent = accent_cycle[idx % len(accent_cycle)]

        bg_id = f"bg_{idx}_{run_id}"
        stripe_id = f"stripe_{idx}_{run_id}"
        card_id = f"card_{idx}_{run_id}"
        title_id = f"title_{idx}_{run_id}"
        subtitle_id = f"subtitle_{idx}_{run_id}"
        body_id = f"body_{idx}_{run_id}"
        orb1_id = f"orb1_{idx}_{run_id}"
        orb2_id = f"orb2_{idx}_{run_id}"

        # Full background block.
        requests.append(
            {
                "createShape": {
                    "objectId": bg_id,
                    "shapeType": "RECTANGLE",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": page_w, "unit": "PT"},
                            "height": {"magnitude": page_h, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 0,
                            "translateY": 0,
                            "unit": "PT",
                        },
                    },
                }
            }
        )
        requests.append(
            {
                "updateShapeProperties": {
                    "objectId": bg_id,
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                                "solidFill": {"color": shape_color_style(bg)}
                        },
                        "outline": {
                            "propertyState": "NOT_RENDERED"
                        },
                    },
                    "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
                }
            }
        )

        # Accent stripe.
        requests.append(
            {
                "createShape": {
                    "objectId": stripe_id,
                    "shapeType": "RECTANGLE",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": 16, "unit": "PT"},
                            "height": {"magnitude": page_h, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 0,
                            "translateY": 0,
                            "unit": "PT",
                        },
                    },
                }
            }
        )
        requests.append(
            {
                "updateShapeProperties": {
                    "objectId": stripe_id,
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                                "solidFill": {"color": shape_color_style(accent)}
                        },
                        "outline": {
                            "propertyState": "NOT_RENDERED"
                        },
                    },
                    "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
                }
            }
        )

        # Geometric orbs for signature motif.
        for orb_id, tx, ty, size, orb_color in [
            (orb1_id, 760, -30, 220, PALETTE_HEX["purple"]),
            (orb2_id, 700, 380, 180, PALETTE_HEX["blue"]),
        ]:
            requests.append(
                {
                    "createShape": {
                        "objectId": orb_id,
                        "shapeType": "ELLIPSE",
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {
                                "width": {"magnitude": size, "unit": "PT"},
                                "height": {"magnitude": size, "unit": "PT"},
                            },
                            "transform": {
                                "scaleX": 1,
                                "scaleY": 1,
                                "translateX": tx,
                                "translateY": ty,
                                "unit": "PT",
                            },
                        },
                    }
                }
            )
            requests.append(
                {
                    "updateShapeProperties": {
                        "objectId": orb_id,
                        "shapeProperties": {
                            "shapeBackgroundFill": {
                                "solidFill": {"color": shape_color_style(orb_color)}
                            },
                            "outline": {"propertyState": "NOT_RENDERED"},
                        },
                        "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
                    }
                }
            )

        # Content card.
        requests.append(
            {
                "createShape": {
                    "objectId": card_id,
                    "shapeType": "ROUND_RECTANGLE",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": 830, "unit": "PT"},
                            "height": {"magnitude": 430, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 60,
                            "translateY": 55,
                            "unit": "PT",
                        },
                    },
                }
            }
        )
        requests.append(
            {
                "updateShapeProperties": {
                    "objectId": card_id,
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                                "solidFill": {"color": shape_color_style("#1f2937")}
                        },
                            "outline": {"propertyState": "NOT_RENDERED"},
                    },
                    "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
                }
            }
        )

        # Title.
        requests.append(
            {
                "createShape": {
                    "objectId": title_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": 760, "unit": "PT"},
                            "height": {"magnitude": 70, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 90,
                            "translateY": 90,
                            "unit": "PT",
                        },
                    },
                }
            }
        )
        requests.append(
            {"insertText": {"objectId": title_id, "insertionIndex": 0, "text": slide["title"]}}
        )
        requests.append(
            {
                "updateTextStyle": {
                    "objectId": title_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": "Inter",
                        "bold": True,
                        "fontSize": {"magnitude": 42, "unit": "PT"},
                        "foregroundColor": text_color_style(PALETTE_HEX["white"]),
                    },
                    "fields": "fontFamily,bold,fontSize,foregroundColor",
                }
            }
        )

        # Subtitle.
        requests.append(
            {
                "createShape": {
                    "objectId": subtitle_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": 760, "unit": "PT"},
                            "height": {"magnitude": 60, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 90,
                            "translateY": 150,
                            "unit": "PT",
                        },
                    },
                }
            }
        )
        requests.append(
            {"insertText": {"objectId": subtitle_id, "insertionIndex": 0, "text": slide["subtitle"]}}
        )
        requests.append(
            {
                "updateTextStyle": {
                    "objectId": subtitle_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": "Noto Kufi Arabic",
                        "fontSize": {"magnitude": 24, "unit": "PT"},
                        "foregroundColor": text_color_style(PALETTE_HEX["light_gray"]),
                    },
                    "fields": "fontFamily,fontSize,foregroundColor",
                }
            }
        )

        body_text = "\n".join(f"• {line}" for line in slide["body"])
        requests.append(
            {
                "createShape": {
                    "objectId": body_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": 760, "unit": "PT"},
                            "height": {"magnitude": 250, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 90,
                            "translateY": 230,
                            "unit": "PT",
                        },
                    },
                }
            }
        )
        requests.append(
            {"insertText": {"objectId": body_id, "insertionIndex": 0, "text": body_text}}
        )
        requests.append(
            {
                "updateTextStyle": {
                    "objectId": body_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": "Inter",
                        "fontSize": {"magnitude": 18, "unit": "PT"},
                        "foregroundColor": text_color_style(PALETTE_HEX["light_gray"]),
                    },
                    "fields": "fontFamily,fontSize,foregroundColor",
                }
            }
        )

    return requests


def main() -> None:
    print("Ziyada guided design mode: enforcing brand guidelines before rendering.")
    creds = authenticate()
    service = build("slides", "v1", credentials=creds)

    slide_ids = create_clean_slides(service, DECK_ID, len(SLIDES_DATA))

    for i, sid in enumerate(slide_ids):
        SLIDES_DATA[i]["_slide_id"] = sid
        # Inject official icon and brain pattern for each slide
        SLIDES_DATA[i] = brand_validation.inject_approved_icons(SLIDES_DATA[i], icon_name="automation")
        SLIDES_DATA[i] = brand_validation.inject_pattern(SLIDES_DATA[i], pattern_variant="front")
        # Validate slide compliance
        if not brand_validation.validate_slide(SLIDES_DATA[i]):
            print(f"[ERROR] Slide {i+1} failed brand validation. Aborting.")
            return

    requests = build_slide_requests()
    service.presentations().batchUpdate(
        presentationId=DECK_ID,
        body={"requests": requests},
    ).execute()

    print("Done: deck rebuilt with clean slides and guideline-based design.")
    print(f"https://docs.google.com/presentation/d/{DECK_ID}/edit")


if __name__ == "__main__":
    main()
