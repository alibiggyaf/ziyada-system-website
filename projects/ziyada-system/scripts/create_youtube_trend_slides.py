#!/usr/bin/env python3
"""Create Google Slides report for weekly YouTube trend intelligence."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

ALI_BLACK = {"red": 5 / 255, "green": 1 / 255, "blue": 10 / 255}
ALI_VIOLET = {"red": 112 / 255, "green": 0 / 255, "blue": 1.0}
WHITE = {"red": 1, "green": 1, "blue": 1}
GRAY = {"red": 156 / 255, "green": 163 / 255, "blue": 175 / 255}


def _slides_service():
    token_path = PROJECT_DIR / "token.json"
    if not token_path.exists():
        raise RuntimeError("token.json missing in projects/ziyada-system")
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("token.json is invalid for Slides scopes")
    return build("slides", "v1", credentials=creds)


def _drive_service():
    token_path = PROJECT_DIR / "token.json"
    if not token_path.exists():
        raise RuntimeError("token.json missing in projects/ziyada-system")
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("token.json is invalid for Drive scope")
    return build("drive", "v3", credentials=creds)


def _first_placeholder(elements: List[Dict], placeholder_type: str) -> str | None:
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


def _replace_text_requests(obj_id: str, text: str) -> List[Dict]:
    return [{"insertText": {"objectId": obj_id, "insertionIndex": 0, "text": text}}]


def _style_text_requests(obj_id: str, is_title: bool = False) -> List[Dict]:
    font_size = 30 if is_title else 15
    font_family = "Inter" if is_title else "Inter"
    color = WHITE if is_title else GRAY
    return [
        {
            "updateTextStyle": {
                "objectId": obj_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontFamily": font_family,
                    "fontSize": {"magnitude": font_size, "unit": "PT"},
                    "bold": bool(is_title),
                    "foregroundColor": {"opaqueColor": {"rgbColor": color}},
                },
                "fields": "fontFamily,fontSize,bold,foregroundColor",
            }
        }
    ]


def _dark_backdrop_requests(slide_id: str, idx: int) -> List[Dict]:
    bg_id = f"bg_rect_{idx}"
    return [
        {
            "createShape": {
                "objectId": bg_id,
                "shapeType": "RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 960, "unit": "PT"},
                        "height": {"magnitude": 540, "unit": "PT"},
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
        },
        {
            "updateShapeProperties": {
                "objectId": bg_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {"color": {"rgbColor": ALI_BLACK}}
                    },
                    "outline": {
                        "propertyState": "NOT_RENDERED"
                    },
                },
                "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
            }
        },
        {
            "updatePageElementsZOrder": {
                "pageElementObjectIds": [bg_id],
                "operation": "SEND_TO_BACK",
            }
        },
    ]


def _create_layout_slides(service, deck_id: str, count: int) -> None:
    if count <= 1:
        return
    requests = []
    for _ in range(count - 1):
        requests.append(
            {
                "createSlide": {
                    "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
                }
            }
        )
    service.presentations().batchUpdate(presentationId=deck_id, body={"requests": requests}).execute()


def _upload_logo_and_get_url(drive_service, logo_path: Path) -> str:
    if not logo_path.exists():
        raise RuntimeError(f"Logo file not found: {logo_path}")

    media = MediaFileUpload(str(logo_path), mimetype="image/png")
    metadata = {"name": f"{logo_path.stem}_slides_logo.png", "mimeType": "image/png"}
    created = drive_service.files().create(body=metadata, media_body=media, fields="id").execute()
    file_id = created["id"]

    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"


def _shape_bar_requests(slide_id: str, rows: List[Dict], prefix: str, start_y: int = 150) -> List[Dict]:
    requests: List[Dict] = []
    if not rows:
        return requests

    max_score = max(float(r.get("final_channel_score", 1)) for r in rows)
    for i, row in enumerate(rows):
        label_id = f"{prefix}_label_{i}"
        bar_id = f"{prefix}_bar_{i}"
        label = f"{i+1}. {row.get('channel_title', '')[:26]}"
        raw = float(row.get("final_channel_score", 0))
        width = 80 + int((raw / max_score) * 260) if max_score > 0 else 80
        y = start_y + i * 52

        requests.append(
            {
                "createShape": {
                    "objectId": label_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"width": {"magnitude": 260, "unit": "PT"}, "height": {"magnitude": 26, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 40, "translateY": y, "unit": "PT"},
                    },
                }
            }
        )
        requests.append({"insertText": {"objectId": label_id, "insertionIndex": 0, "text": label}})
        requests.append(
            {
                "updateTextStyle": {
                    "objectId": label_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": "Inter",
                        "fontSize": {"magnitude": 11, "unit": "PT"},
                        "foregroundColor": {"opaqueColor": {"rgbColor": WHITE}},
                    },
                    "fields": "fontFamily,fontSize,foregroundColor",
                }
            }
        )

        requests.append(
            {
                "createShape": {
                    "objectId": bar_id,
                    "shapeType": "RECTANGLE",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"width": {"magnitude": width, "unit": "PT"}, "height": {"magnitude": 20, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 300, "translateY": y + 3, "unit": "PT"},
                    },
                }
            }
        )
        requests.append(
            {
                "updateShapeProperties": {
                    "objectId": bar_id,
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                            "solidFill": {"color": {"rgbColor": ALI_VIOLET}}
                        },
                        "outline": {"propertyState": "NOT_RENDERED"},
                    },
                    "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
                }
            }
        )
    return requests


def _truncate(text: str, max_chars: int) -> str:
    clean = (text or "").strip()
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 1].rstrip() + "..."


def _card_requests(slide_id: str, object_id: str, x: int, y: int, w: int, h: int) -> List[Dict]:
    return [
        {
            "createShape": {
                "objectId": object_id,
                "shapeType": "ROUND_RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": w, "unit": "PT"},
                        "height": {"magnitude": h, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": x,
                        "translateY": y,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": object_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {
                                "rgbColor": {"red": 20 / 255, "green": 14 / 255, "blue": 32 / 255}
                            }
                        }
                    },
                    "outline": {
                        "solidFill": {"color": {"rgbColor": ALI_VIOLET}},
                        "weight": {"magnitude": 1, "unit": "PT"},
                    },
                },
                "fields": "shapeBackgroundFill.solidFill.color,outline.solidFill.color,outline.weight",
            }
        },
    ]


def _textbox_requests(
    slide_id: str,
    object_id: str,
    text: str,
    x: int,
    y: int,
    w: int,
    h: int,
    font_size: int,
    bold: bool,
    align: str,
) -> List[Dict]:
    return [
        {
            "createShape": {
                "objectId": object_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": w, "unit": "PT"},
                        "height": {"magnitude": h, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": x,
                        "translateY": y,
                        "unit": "PT",
                    },
                },
            }
        },
        {"insertText": {"objectId": object_id, "insertionIndex": 0, "text": text}},
        {
            "updateTextStyle": {
                "objectId": object_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontFamily": "Inter",
                    "fontSize": {"magnitude": font_size, "unit": "PT"},
                    "bold": bold,
                    "foregroundColor": {"opaqueColor": {"rgbColor": WHITE}},
                },
                "fields": "fontFamily,fontSize,bold,foregroundColor",
            }
        },
        {
            "updateParagraphStyle": {
                "objectId": object_id,
                "textRange": {"type": "ALL"},
                "style": {"alignment": align, "lineSpacing": 120},
                "fields": "alignment,lineSpacing",
            }
        },
    ]


def create_deck(insights: Dict, scored: Dict, run_cost_usd: float) -> str:
    service = _slides_service()
    drive_service = _drive_service()
    title = f"YouTube Trend Intelligence | {insights['week_start']} to {insights['week_end']}"
    deck = service.presentations().create(body={"title": title}).execute()
    deck_id = deck["presentationId"]

    en_logo_path = PROJECT_DIR.parent / "ALI FALLATAH WEBSITE PORTOFOLIO" / "Ali website  2026" / "Ali Logos-02.png"
    ar_logo_path = PROJECT_DIR.parent / "ALI FALLATAH WEBSITE PORTOFOLIO" / "Ali website  2026" / "Ali Logos-03.png"
    en_logo_url = _upload_logo_and_get_url(drive_service, en_logo_path)
    ar_logo_url = _upload_logo_and_get_url(drive_service, ar_logo_path)

    channels_count = len(scored.get("channels", []))
    videos_count = len(scored.get("videos", []))

    top_videos = insights.get("top_videos", [])[:4]
    top_videos_en = "\n\n".join(
        [f"{r['rank']}. {_truncate(r['title'], 70)}\n{r.get('video_url','')}" for r in top_videos]
    )
    top_videos_ar = "\n\n".join(
        [f"{r['rank']}. {_truncate(r['title'], 60)}\n{r.get('video_url','')}" for r in top_videos]
    )

    slides_content = [
        {
            "title": "Weekly YouTube Trend Intelligence | تقرير اتجاهات يوتيوب الأسبوعي",
            "en": (
                f"Prepared for Ali Fallatah\n"
                f"Scope: Saudi Arabia, Egypt, MENA, Global\n"
                f"Window: {insights['week_start']} to {insights['week_end']}\n\n"
                "This deck is bilingual and designed for client-ready presentation."
            ),
            "ar": (
                f"تم الإعداد لصالح علي فلاطة\n"
                f"النطاق: السعودية، مصر، الشرق الأوسط، عالمي\n"
                f"الفترة: {insights['week_start']} إلى {insights['week_end']}\n\n"
                "هذا العرض ثنائي اللغة ومصمم بشكل احترافي للعرض على العملاء."
            ),
            "chart": False,
        },
        {
            "title": "Executive Summary | الملخص التنفيذي",
            "en": _truncate(insights.get("insights_en", ""), 850),
            "ar": _truncate(insights.get("insights_ar", ""), 850),
            "chart": False,
        },
        {
            "title": "KPI Snapshot | مؤشرات الأداء",
            "en": (
                f"Channels analyzed: {channels_count}\n"
                f"Videos scored: {videos_count}\n"
                f"Estimated run cost: ${run_cost_usd:.2f}\n"
                "Source: YouTube Data API"
            ),
            "ar": (
                f"عدد القنوات المحللة: {channels_count}\n"
                f"عدد الفيديوهات: {videos_count}\n"
                f"التكلفة التقديرية: ${run_cost_usd:.2f}\n"
                "المصدر: YouTube Data API"
            ),
            "chart": True,
        },
        {
            "title": "Top Videos & Links | أبرز الفيديوهات والروابط",
            "en": top_videos_en,
            "ar": top_videos_ar,
            "chart": False,
        },
        {
            "title": "Recommendations | التوصيات",
            "en": (
                "1) Publish weekly AI automation teardown\n"
                "2) Prioritize Saudi business use-cases\n"
                "3) Repurpose winners into short-form\n"
                "4) Keep bilingual EN/AR content cadence"
            ),
            "ar": (
                "1) نشر تحليل أسبوعي لأتمتة الذكاء الاصطناعي\n"
                "2) التركيز على حالات استخدام سعودية عملية\n"
                "3) إعادة توظيف المحتوى الأفضل إلى فيديوهات قصيرة\n"
                "4) الحفاظ على إيقاع محتوى ثنائي اللغة"
            ),
            "chart": False,
        },
        {
            "title": "Thank You | شكراً لكم",
            "en": "Prepared by Ali Fallatah Portfolio Insights Team\nArchitecting Growth with Data-Driven Strategy",
            "ar": "تم إعداد التقرير بواسطة فريق رؤى محفظة علي فلاطة\nنمو مبني على البيانات والاستراتيجية",
            "chart": False,
        },
    ]

    _create_layout_slides(service, deck_id, len(slides_content))
    pres = service.presentations().get(presentationId=deck_id).execute()
    slides = pres.get("slides", [])

    requests: List[Dict] = []
    bar_requests: List[Dict] = []
    image_requests: List[Dict] = []

    for idx, slide in enumerate(slides[: len(slides_content)]):
        content = slides_content[idx]
        elements = slide.get("pageElements", [])
        title_id = _first_placeholder(elements, "TITLE") or _first_placeholder(elements, "CENTERED_TITLE")
        body_id = _first_placeholder(elements, "BODY")

        requests.extend(_dark_backdrop_requests(slide["objectId"], idx))

        if title_id:
            requests.extend(_replace_text_requests(title_id, content["title"]))
            requests.extend(_style_text_requests(title_id, is_title=True))
        if body_id:
            requests.extend(_replace_text_requests(body_id, ""))

        left_card = f"card_en_{idx}"
        right_card = f"card_ar_{idx}"
        requests.extend(_card_requests(slide["objectId"], left_card, 30, 110, 430, 200))
        requests.extend(_card_requests(slide["objectId"], right_card, 500, 110, 430, 200))

        requests.extend(
            _textbox_requests(
                slide["objectId"],
                f"txt_en_{idx}",
                content["en"],
                45,
                125,
                400,
                170,
                12,
                False,
                "START",
            )
        )
        requests.extend(
            _textbox_requests(
                slide["objectId"],
                f"txt_ar_{idx}",
                content["ar"],
                515,
                125,
                400,
                170,
                12,
                False,
                "END",
            )
        )

        image_requests.append(
            {
                "createImage": {
                    "url": en_logo_url,
                    "elementProperties": {
                        "pageObjectId": slide["objectId"],
                        "size": {
                            "width": {"magnitude": 58, "unit": "PT"},
                            "height": {"magnitude": 58, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 25,
                            "translateY": 20,
                            "unit": "PT",
                        },
                    },
                }
            }
        )
        image_requests.append(
            {
                "createImage": {
                    "url": ar_logo_url,
                    "elementProperties": {
                        "pageObjectId": slide["objectId"],
                        "size": {
                            "width": {"magnitude": 58, "unit": "PT"},
                            "height": {"magnitude": 58, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 877,
                            "translateY": 20,
                            "unit": "PT",
                        },
                    },
                }
            }
        )

        if content.get("chart"):
            bar_requests.extend(
                _shape_bar_requests(
                    slide["objectId"], insights.get("top_channels", [])[:4], f"bi_top_channels_{idx}", start_y=330
                )
            )

    if requests:
        service.presentations().batchUpdate(
            presentationId=deck_id,
            body={"requests": requests},
        ).execute()

    if image_requests:
        service.presentations().batchUpdate(
            presentationId=deck_id,
            body={"requests": image_requests},
        ).execute()

    if bar_requests:
        service.presentations().batchUpdate(
            presentationId=deck_id,
            body={"requests": bar_requests},
        ).execute()

    return deck_id
