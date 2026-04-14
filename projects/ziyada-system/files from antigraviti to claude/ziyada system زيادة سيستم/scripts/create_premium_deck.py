#!/usr/bin/env python3
import os
import json
import time
from typing import List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configuration
_WORKSPACE = "/Users/djbiggy/Downloads/ANTI GRAVETY WEBSITES MY MAC/ziyada system زيادة سيستم"
_PROJECT_DIR = "/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system"
TOKEN_PATH = os.path.join(_PROJECT_DIR, "scripts", "token.json")
# If token not in scripts_dir, check project root
if not os.path.exists(TOKEN_PATH):
    TOKEN_PATH = os.path.join(_PROJECT_DIR, "token.json")
# Finally check workspace
if not os.path.exists(TOKEN_PATH):
    TOKEN_PATH = os.path.join(_WORKSPACE, "token.json")

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

PALETTE_HEX = {
    "deep_blue": "#0f172a",
    "blue": "#3b82f6",
    "purple": "#8b5cf6",
    "white": "#ffffff",
    "light_gray": "#e2e8f0",
    "teal": "#06b6d4",
}

SLIDES_CONTENT = [
    {
        "title": "زيادة سيستم – منظومة نمو متكاملة",
        "subtitle": "نحو نمو أسرع، أكثر وضوحًا، وقابلية للقياس",
        "body": "",
        "bg_key": "manual_cover"
    },
    {
        "title": "التحدي: الفوضى التشغيلية",
        "subtitle": "عندما يصبح النمو عائقًا بدلاً من كونه إنجازًا",
        "body": "• فرق عمل متباعدة وقنوات تواصل مشتتة\n• رحلة عميل مجزأة تؤدي لضياع الفرص\n• بيانات متناثرة تجعل اتخاذ القرار مقامرة\n• هدر تشغيلي في مهام يدوية متكررة",
        "bg_key": "problem"
    },
    {
        "title": "الرؤية: النمو كمنظومة منسقة",
        "subtitle": "تحويل الفوضى إلى تدفق بيانات وعمليات ذكية",
        "body": "• سريعة: استجابة فورية لاحتياجات السوق\n• مرئية: لوحة تحكم شاملة لكل تفاصيل النمو\n• مستدامة: أنظمة تبني نفسها وتتوسع معك",
        "bg_key": "vision"
    },
    {
        "title": "منهجية التحول: رحلة الـ 5 مراحل",
        "subtitle": "خارطة طريق واضحة من التقييم إلى التوسع",
        "body": "1. التشخيص: فهم الفجوات التشغيلية الحالية\n2. التصميم: بناء هندسة النظام المناسبة لنموك\n3. الربط: تكامل الأدوات والبيانات في واجهة واحدة\n4. التشغيل: تفعيل الأتمتة لرفع الكفاءة\n5. التحسين: تطوير مستمر بناءً على لغة الأرقام",
        "bg_key": "methodology"
    },
    {
        "title": "المنظومة المتكاملة",
        "subtitle": "كل ما تحتاجه للسيطرة على مسار النمو",
        "body": "• أتمتة مسارات البيع (Sales Funnels)\n• إدارة ذكية للعملاء المحتملين (CRM)\n• لوحات أداء تنفيذية لحظية\n• ربط شامل بين التسويق والمبيعات والتشغيل",
        "bg_key": "ecosystem"
    },
    {
        "title": "القيمة والأثر الاستراتيجي",
        "subtitle": "نتائج ملموسة تنعكس على أداء شركتك",
        "body": "• تقليل الهدر الزمني بنسبة تصل إلى 40%\n• تسريع الاستجابة للعملاء لزيادة نسب التحويل\n• دقة عالية في توقعات المبيعات والنمو\n• تحرير الفريق للتركيز على القرارات الكبرى",
        "bg_key": "value"
    },
    {
        "title": "لماذا زيادة سيستم؟",
        "subtitle": "شريكك في هندسة مستقبل أعمالك",
        "body": "• تفكير استراتيجي يسبق التنفيذ التقني\n• تكامل شامل لا يعرف الجزر المنعزلة\n• فهم عميق لمتطلبات وتحديات السوق السعودي\n• انضباط عالٍ في التنفيذ والجودة",
        "bg_key": "manual_diff"
    },
    {
        "title": "الخطوة التالية: ابدأ رحلة التغيير",
        "subtitle": "لنصمم معًا نظام النمو الخاص بك",
        "body": "احجز جلسة استكشاف لبناء خارطة الطريق\n\ninfo@ziyadasystem.com\nwww.ziyadasystem.com",
        "bg_key": "manual_contact"
    }
]

def authenticate():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Auth token not found at {TOKEN_PATH}")
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        token_data = json.load(f)
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

def upload_image(drive_service, local_path, name):
    print(f"Uploading {name}...")
    file_metadata = {'name': name, 'parents': []} # Can add specific parent folder if needed
    media = MediaFileUpload(local_path, mimetype='image/png')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink, webContentLink').execute()
    
    # Set permissions to anyone with link so Slides can see it
    drive_service.permissions().create(
        fileId=file['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    
    # We need the direct download link
    return f"https://drive.google.com/uc?export=download&id={file['id']}"

def create_presentation(slides_service, title):
    body = {'title': title}
    presentation = slides_service.presentations().create(body=body).execute()
    return presentation.get('presentationId')

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return {
        "red": int(hex_color[0:2], 16) / 255.0,
        "green": int(hex_color[2:4], 16) / 255.0,
        "blue": int(hex_color[4:6], 16) / 255.0
    }

def build_requests(slides_service, presentation_id, slides_content, bg_urls):
    requests = []
    
    # 1. Create slides (excluding first one which exists by default)
    # Actually it's easier to just create 8 fresh slides and delete the first one later or reuse it.
    # Let's create 8 fresh BLANK slides.
    slide_ids = [f"ziyada_slide_{i}" for i in range(8)]
    for i in range(8):
        requests.append({
            "createSlide": {
                "objectId": slide_ids[i],
                "slideLayoutReference": {"predefinedLayout": "BLANK"}
            }
        })
    
    # 2. Setup backgrounds and content
    for i, slide in enumerate(slides_content):
        sid = slide_ids[i]
        
        # Background
        if slide["bg_key"] in bg_urls:
            requests.append({
                "updatePageProperties": {
                    "objectId": sid,
                    "pageProperties": {
                        "pageBackgroundFill": {
                            "stretchedPictureFill": {
                                "contentUrl": bg_urls[slide["bg_key"]]
                            }
                        }
                    },
                    "fields": "pageBackgroundFill.stretchedPictureFill.contentUrl"
                }
            })
        else:
            # Manual background for cover/diff/contact
            # Deep navy gradient or solid color
            requests.append({
                "updatePageProperties": {
                    "objectId": sid,
                    "pageProperties": {
                        "pageBackgroundFill": {
                            "solidFill": {"color": {"rgbColor": hex_to_rgb(PALETTE_HEX["deep_blue"])}}
                        }
                    },
                    "fields": "pageBackgroundFill.solidFill.color"
                }
            })
            # Add decorative shapes for "manual" slides
            if slide["bg_key"] == "manual_cover":
                # Large blue circle in background
                requests.append({
                    "createShape": {
                        "objectId": f"decor_{i}_1",
                        "shapeType": "ELLIPSE",
                        "elementProperties": {
                            "pageObjectId": sid,
                            "size": {"width": {"magnitude": 600, "unit": "PT"}, "height": {"magnitude": 600, "unit": "PT"}},
                            "transform": {"scaleX": 1, "scaleY": 1, "translateX": 500, "translateY": -200, "unit": "PT"}
                        }
                    }
                })
                requests.append({
                    "updateShapeProperties": {
                        "objectId": f"decor_{i}_1",
                        "shapeProperties": {
                            "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": hex_to_rgb(PALETTE_HEX["blue"])}, "alpha": 0.1}},
                            "outline": {"propertyState": "NOT_RENDERED"}
                        },
                        "fields": "shapeBackgroundFill,outline"
                    }
                })

        # Titles/Content
        # Using centered layout for premium feel
        title_id = f"title_{i}"
        requests.append({
            "createShape": {
                "objectId": title_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": sid,
                    "size": {"width": {"magnitude": 600, "unit": "PT"}, "height": {"magnitude": 80, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 60, "translateY": 80, "unit": "PT"}
                }
            }
        })
        requests.append({
            "insertText": {
                "objectId": title_id,
                "text": slide["title"],
                "insertionIndex": 0
            }
        })
        requests.append({
            "updateTextStyle": {
                "objectId": title_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontFamily": "Noto Kufi Arabic",
                    "bold": True,
                    "fontSize": {"magnitude": 36, "unit": "PT"},
                    "foregroundColor": {"opaqueColor": {"rgbColor": hex_to_rgb(PALETTE_HEX["white"])}}
                },
                "fields": "fontFamily,bold,fontSize,foregroundColor"
            }
        })
        requests.append({
            "updateParagraphStyle": {
                "objectId": title_id,
                "textRange": {"type": "ALL"},
                "style": {"alignment": "CENTER"},
                "fields": "alignment"
            }
        })

        if slide["subtitle"]:
            sub_id = f"subtitle_{i}"
            requests.append({
                "createShape": {
                    "objectId": sub_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": sid,
                        "size": {"width": {"magnitude": 600, "unit": "PT"}, "height": {"magnitude": 40, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 60, "translateY": 160, "unit": "PT"}
                    }
                }
            })
            requests.append({
                "insertText": {
                    "objectId": sub_id,
                    "text": slide["subtitle"],
                    "insertionIndex": 0
                }
            })
            requests.append({
                "updateTextStyle": {
                    "objectId": sub_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": "Noto Kufi Arabic",
                        "fontSize": {"magnitude": 20, "unit": "PT"},
                        "foregroundColor": {"opaqueColor": {"rgbColor": hex_to_rgb(PALETTE_HEX["blue"])}}
                    },
                    "fields": "fontFamily,fontSize,foregroundColor"
                }
            })
            requests.append({
                "updateParagraphStyle": {
                    "objectId": sub_id,
                    "textRange": {"type": "ALL"},
                    "style": {"alignment": "CENTER"},
                    "fields": "alignment"
                }
            })

        if slide["body"]:
            body_id = f"body_{i}"
            requests.append({
                "createShape": {
                    "objectId": body_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": sid,
                        "size": {"width": {"magnitude": 500, "unit": "PT"}, "height": {"magnitude": 250, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 110, "translateY": 240, "unit": "PT"}
                    }
                }
            })
            requests.append({
                "insertText": {
                    "objectId": body_id,
                    "text": slide["body"],
                    "insertionIndex": 0
                }
            })
            requests.append({
                "updateTextStyle": {
                    "objectId": body_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": "Noto Kufi Arabic",
                        "fontSize": {"magnitude": 16, "unit": "PT"},
                        "foregroundColor": {"opaqueColor": {"rgbColor": hex_to_rgb(PALETTE_HEX["white"])}}
                    },
                    "fields": "fontFamily,fontSize,foregroundColor"
                }
            })
            # RTL alignment for body text with bullets
            requests.append({
                "updateParagraphStyle": {
                    "objectId": body_id,
                    "textRange": {"type": "ALL"},
                    "style": {"direction": "RIGHT_TO_LEFT", "alignment": "START"},
                    "fields": "direction,alignment"
                }
            })

    # Delete the original blank first slide
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    first_slide_id = presentation.get('slides')[0].get('objectId')
    requests.append({"deleteObject": {"objectId": first_slide_id}})
    
    return requests

def main():
    creds = authenticate()
    slides_service = build('slides', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # 1. Upload images
    asset_dir = os.path.join(_WORKSPACE, "presentation_assets")
    bg_keys = ["problem", "vision", "methodology", "ecosystem", "value"] # Cover skipped for manual v2
    bg_urls = {}
    for key in bg_keys:
        path = os.path.join(asset_dir, f"{key}.png")
        if os.path.exists(path):
            bg_urls[key] = upload_image(drive_service, path, f"ziyada_{key}.png")

    # 2. Create presentation
    pres_id = create_presentation(slides_service, "زيادة سيستم - منظومة نمو متكاملة")
    print(f"Created presentation with ID: {pres_id}")

    # 3. Build and execute requests
    requests = build_requests(slides_service, pres_id, SLIDES_CONTENT, bg_urls)
    slides_service.presentations().batchUpdate(
        presentationId=pres_id,
        body={'requests': requests}
    ).execute()

    print(f"DONE! View your presentation at: https://docs.google.com/presentation/d/{pres_id}/edit")

if __name__ == "__main__":
    main()
