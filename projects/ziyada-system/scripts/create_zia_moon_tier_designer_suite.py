#!/usr/bin/env python3

from __future__ import annotations

import base64
import io
import mimetypes
import runpy
import subprocess
import zipfile
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
SOCIAL_OUT = OUTPUTS_DIR / "social_media_ar"
EXACT_OUT = OUTPUTS_DIR / "zia_exact_site_assets"
APP_DIR = PROJECT_DIR / "app" / "ziyada-growth-suite"

RECIPIENT = "ali.biggy.af@gmail.com"
SENDER = "ali.biggy.af@gmail.com"

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.compose",
]


def _rgb(h: str):
    h = h.lstrip("#")
    return {
        "red": int(h[0:2], 16) / 255,
        "green": int(h[2:4], 16) / 255,
        "blue": int(h[4:6], 16) / 255,
    }


def creds() -> Credentials:
    token = PROJECT_DIR / "token.json"
    if not token.exists():
        raise RuntimeError("token.json is missing")
    c = Credentials.from_authorized_user_file(str(token), SCOPES)
    if not c.valid and c.expired and c.refresh_token:
        c.refresh(Request())
    if not c.valid:
        raise RuntimeError("token.json is invalid for scopes")
    return c


def services():
    c = creds()
    return (
        build("slides", "v1", credentials=c),
        build("drive", "v3", credentials=c),
        build("gmail", "v1", credentials=c),
    )


def upload_public(drive, path: Path, mime: str) -> str:
    media = MediaFileUpload(str(path), mimetype=mime)
    meta = {"name": path.name, "mimeType": mime}
    file_obj = drive.files().create(body=meta, media_body=media, fields="id").execute()
    fid = file_obj["id"]
    drive.permissions().create(fileId=fid, body={"type": "anyone", "role": "reader"}).execute()
    return f"https://drive.google.com/uc?id={fid}"


def export_pptx(drive, presentation_id: str, output: Path) -> None:
    req = drive.files().export_media(
        fileId=presentation_id,
        mimeType="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with io.FileIO(output, "wb") as fh:
        dl = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            _, done = dl.next_chunk()


def zip_dir(source_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(source_dir.rglob("*")):
            if p.is_file():
                zf.write(p, arcname=p.relative_to(source_dir))


def slide_visual_requests(slide_id: str, idx: int, image_url: str | None) -> List[Dict]:
    bg = f"bgxx_{idx}"
    glow = f"glowx_{idx}"
    card = f"cardx_{idx}"
    cta = f"ctaxx_{idx}"
    reqs = [
        {
            "createShape": {
                "objectId": bg,
                "shapeType": "RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": 960, "unit": "PT"}, "height": {"magnitude": 540, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0, "translateY": 0, "unit": "PT"},
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": bg,
                "shapeProperties": {
                    "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": _rgb("0f172a")}}},
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
                "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
            }
        },
        {
            "createShape": {
                "objectId": glow,
                "shapeType": "ELLIPSE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": 430, "unit": "PT"}, "height": {"magnitude": 430, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 260, "translateY": 30, "unit": "PT"},
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": glow,
                "shapeProperties": {
                    "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": _rgb("3b82f6")}, "alpha": 0.09}},
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
                "fields": "shapeBackgroundFill.solidFill.color,shapeBackgroundFill.solidFill.alpha,outline.propertyState",
            }
        },
        {
            "createShape": {
                "objectId": card,
                "shapeType": "ROUND_RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": 850, "unit": "PT"}, "height": {"magnitude": 410, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 55, "translateY": 68, "unit": "PT"},
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": card,
                "shapeProperties": {
                    "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": _rgb("ffffff")}, "alpha": 0.10}},
                    "outline": {
                        "outlineFill": {"solidFill": {"color": {"rgbColor": _rgb("ffffff")}, "alpha": 0.36}},
                        "weight": {"magnitude": 1, "unit": "PT"},
                    },
                },
                "fields": "shapeBackgroundFill.solidFill.color,shapeBackgroundFill.solidFill.alpha,outline.outlineFill.solidFill.color,outline.outlineFill.solidFill.alpha,outline.weight",
            }
        },
        {
            "createShape": {
                "objectId": cta,
                "shapeType": "ROUND_RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": 170, "unit": "PT"}, "height": {"magnitude": 36, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 730, "translateY": 24, "unit": "PT"},
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": cta,
                "shapeProperties": {
                    "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": _rgb("6366f1")}, "alpha": 0.85}},
                    "outline": {
                        "outlineFill": {"solidFill": {"color": {"rgbColor": _rgb("818cf8")}, "alpha": 1}},
                        "weight": {"magnitude": 1, "unit": "PT"},
                    },
                },
                "fields": "shapeBackgroundFill.solidFill.color,shapeBackgroundFill.solidFill.alpha,outline.outlineFill.solidFill.color,outline.outlineFill.solidFill.alpha,outline.weight",
            }
        },
        {
            "updatePageElementsZOrder": {
                "pageElementObjectIds": [bg, glow],
                "operation": "SEND_TO_BACK",
            }
        },
    ]

    if image_url:
        iid = f"imgxx_{idx}"
        reqs.append(
            {
                "createImage": {
                    "objectId": iid,
                    "url": image_url,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"width": {"magnitude": 960, "unit": "PT"}, "height": {"magnitude": 540, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0, "translateY": 0, "unit": "PT"},
                    },
                }
            }
        )
        reqs.append(
            {
                "updatePageElementsZOrder": {
                    "pageElementObjectIds": [iid],
                    "operation": "SEND_TO_BACK",
                }
            }
        )

    return reqs


def textbox_requests(slide_id: str, idx: int, title: str, body: str, tag: str) -> List[Dict]:
    t_id = f"tboxx_{idx}"
    b_id = f"bboxx_{idx}"
    g_id = f"tagbx_{idx}"
    reqs = [
        {
            "createShape": {
                "objectId": t_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": 760, "unit": "PT"}, "height": {"magnitude": 90, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 110, "translateY": 118, "unit": "PT"},
                },
            }
        },
        {
            "insertText": {
                "objectId": t_id,
                "insertionIndex": 0,
                "text": title,
            }
        },
        {
            "updateTextStyle": {
                "objectId": t_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontFamily": "Inter",
                    "fontSize": {"magnitude": 36, "unit": "PT"},
                    "bold": True,
                    "foregroundColor": {"opaqueColor": {"rgbColor": _rgb("6366f1")}},
                },
                "fields": "fontFamily,fontSize,bold,foregroundColor",
            }
        },
        {
            "createShape": {
                "objectId": b_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": 760, "unit": "PT"}, "height": {"magnitude": 240, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 110, "translateY": 220, "unit": "PT"},
                },
            }
        },
        {
            "insertText": {
                "objectId": b_id,
                "insertionIndex": 0,
                "text": body,
            }
        },
        {
            "updateTextStyle": {
                "objectId": b_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontFamily": "Inter",
                    "fontSize": {"magnitude": 18, "unit": "PT"},
                    "foregroundColor": {"opaqueColor": {"rgbColor": _rgb("e2e8f0")}},
                },
                "fields": "fontFamily,fontSize,foregroundColor",
            }
        },
    ]

    if tag:
        reqs.extend(
            [
                {
                    "createShape": {
                        "objectId": g_id,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {"width": {"magnitude": 150, "unit": "PT"}, "height": {"magnitude": 22, "unit": "PT"}},
                            "transform": {"scaleX": 1, "scaleY": 1, "translateX": 740, "translateY": 32, "unit": "PT"},
                        },
                    }
                },
                {
                    "insertText": {
                        "objectId": g_id,
                        "insertionIndex": 0,
                        "text": tag,
                    }
                },
                {
                    "updateTextStyle": {
                        "objectId": g_id,
                        "textRange": {"type": "ALL"},
                        "style": {
                            "fontFamily": "Inter",
                            "fontSize": {"magnitude": 10, "unit": "PT"},
                            "bold": True,
                            "foregroundColor": {"opaqueColor": {"rgbColor": _rgb("f8fafc")}},
                        },
                        "fields": "fontFamily,fontSize,bold,foregroundColor",
                    }
                },
            ]
        )

    return reqs


def create_blank_slides(slides_api, presentation_id: str, n: int) -> None:
    if n <= 1:
        return
    reqs = []
    for _ in range(n - 1):
        reqs.append({"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}})
    slides_api.presentations().batchUpdate(presentationId=presentation_id, body={"requests": reqs}).execute()


def create_deck(slides_api, title: str, slides_payload: List[Dict], cover_url: str | None, end_url: str | None, base_url: str | None) -> Dict[str, str]:
    created = slides_api.presentations().create(body={"title": title}).execute()
    pid = created["presentationId"]
    create_blank_slides(slides_api, pid, len(slides_payload))

    pres = slides_api.presentations().get(presentationId=pid).execute()
    slides = pres.get("slides", [])

    for i, (sl, payload) in enumerate(zip(slides, slides_payload)):
        sid = sl["objectId"]
        image_url = base_url
        if payload.get("variant") == "cover":
            image_url = cover_url
        elif payload.get("variant") == "end":
            image_url = end_url

        reqs = []
        reqs.extend(slide_visual_requests(sid, i, image_url))
        reqs.extend(textbox_requests(sid, i, payload["title"], payload["body"], payload.get("tag", "")))
        slides_api.presentations().batchUpdate(presentationId=pid, body={"requests": reqs}).execute()

    return {"id": pid, "url": f"https://docs.google.com/presentation/d/{pid}/edit"}


def make_payloads(video_link: str, folder_link: str) -> Dict[str, List[Dict]]:
    proposal = [
        {
            "variant": "cover",
            "tag": "MOON TIER",
            "title": "قالب العروض والـ Quotations | زيادة سيستم",
            "body": "تصميم حديث بنفس روح الموقع\nقابل للتخصيص للفِرق التجارية B2B\nغلاف ونهائي متناسقين مع الهوية",
        },
        {
            "tag": "GUIDE",
            "title": "كيف تستخدم القالب بسرعة",
            "body": "1) انسخ الملف كنسخة مشروع\n2) استخدم خلفية اليوم + كروت زجاجية خفيفة\n3) حافظ على ألوان CTA البنفسجي/الأزرق\n4) لا تزحم النص، ركز على الوضوح",
        },
        {
            "tag": "FLOW",
            "title": "هيكل العرض المقترح",
            "body": "غلاف -> تشخيص -> الحل -> خطة التنفيذ -> التسعير -> المخاطر -> CTA\nكل قسم له Divider بصري كبير مثل واجهة الموقع",
        },
        {
            "tag": "QUOTE",
            "title": "قوالب صفحات التسعير",
            "body": "باقة تأسيس / نمو / أداء\nبنود واضحة + افتراضات + مدة التنفيذ\nصفحة جاهزة للتوقيع والاعتماد",
        },
        {
            "tag": "MOCKUPS",
            "title": "استخدام الموك اب في الشرائح",
            "body": "iPhone mockup و MacBook mockup مرفقة كملفات مفتوحة\nحط التصميم داخل الإطار مع هوامش ثابتة\nاستخدمها لعرض posts والـ reels previews",
        },
        {
            "variant": "end",
            "tag": "END",
            "title": "جاهز للإرسال للعميل",
            "body": "تم بناء القالب للفِرق الداخلية في Zia\nنسق حديث + قراءة مريحة + CTA واضح",
        },
    ]

    social = [
        {
            "variant": "cover",
            "tag": "PLAYBOOK",
            "title": "دليل السوشال والمونتاج | عربي سعودي",
            "body": "إرشادات تصميم، كتابة، حركة، وانتقالات\nمخصص لفريق التسويق والإبداع في زيادة سيستم",
        },
        {
            "tag": "BRAND",
            "title": "قواعد الهوية البصرية",
            "body": "الخلفيات: #0f172a أساس + تدرجات أزرق/بنفسجي\nالعناصر: Brain element + كروت زجاجية + Frames\nCTA: لون قريب من زر الموقع (بنفسجي مضيء)",
        },
        {
            "tag": "POSTS",
            "title": "قوالب المنشورات الثابتة",
            "body": "Static 1: عنوان قوي + 3 نقاط + CTA\nStatic 2: مشكلة/حل\nStatic 3: إثبات رقمي + عرض جلسة",
        },
        {
            "tag": "CAROUSEL",
            "title": "نظام الكاروسيل",
            "body": "شريحة 1 هوك\n2-6 قيمة عملية\n7-8 إثبات + CTA\nاستخدم نفس الإيقاع اللوني والتباين للقراءة",
        },
        {
            "tag": "REELS",
            "title": "دليل فيديو الريلز السريع",
            "body": "0-2 ثانية Hook قوي\n2-12 ثانية القيمة\n12-22 ثانية Proof\n22-30 ثانية CTA\nسرعة انتقالات عالية بدون تشتيت",
        },
        {
            "tag": "TRANSITIONS",
            "title": "الانتقالات والحركة",
            "body": "Auto animation عبر API غير مدعومة بالكامل في Google Slides\nالمعتمد: دليل واضح داخل الشريحة لتطبيق Motion يدوي بسرعة\nالموصى به: Fade سريع + Slide + Scale Reveal",
        },
        {
            "tag": "VIDEO",
            "title": "رابط فيديو Reel الجاهز",
            "body": f"فيديو انتقالات سريع بأسلوب Zia:\n{video_link}\n\nأصول التصميم المفتوحة:\n{folder_link}",
        },
        {
            "variant": "end",
            "tag": "END",
            "title": "مرجع الفريق الإبداعي",
            "body": "استخدم هذا الدليل كقالب تشغيلي دائم\nحدّثه شهرياً بنتائج الأداء والمنصات",
        },
    ]

    moon = [
        {
            "variant": "cover",
            "tag": "MOON TIER",
            "title": "Moon Tier Creative System",
            "body": "تصميم أكثر جرأة للمحتوى التنفيذي\nخلفيات نهارية أخف + تباين أعلى للقراءة",
        },
        {
            "tag": "MOOD",
            "title": "Moodboard وتوجيه الألوان",
            "body": "Day mood: خلفية أهدأ\nNight mood: خلفية عميقة\nاستخدم نفس CTA البنفسجي لضمان الثبات",
        },
        {
            "tag": "ELEMENTS",
            "title": "استخدام Brain Element",
            "body": "Ring منفصل للخلفيات\nCore منفصل للنقاط المحورية\nالجمع بينهم عند الرسائل الكبرى فقط",
        },
        {
            "tag": "WORKFLOW",
            "title": "Workflow للإنتاج",
            "body": "Brief -> Storyboard -> Design -> Motion -> QA -> Publish\nقالب جاهز للفريق بالكامل",
        },
        {
            "variant": "end",
            "tag": "SHIP",
            "title": "جاهز للتنفيذ",
            "body": "كل الملفات مرفقة Open Source\nقابل للتعديل للمنشورات، العروض، والريلز",
        },
    ]

    return {"proposal": proposal, "social": social, "moon": moon}


def create_draft(gmail, subject: str, body: str, attachments: List[Path]) -> str:
    msg = MIMEMultipart()
    msg["To"] = RECIPIENT
    msg["From"] = SENDER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    for path in attachments:
        ctype, _ = mimetypes.guess_type(str(path))
        if not ctype:
            ctype = "application/octet-stream"
        _, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            part = MIMEApplication(f.read(), _subtype=subtype)
        part.add_header("Content-Disposition", "attachment", filename=path.name)
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    draft = gmail.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft.get("id", "")


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Capture exact visuals from the running canonical Zia app.
    capture_script = APP_DIR / "scripts" / "capture_zia_exact_screenshots.mjs"
    if capture_script.exists():
                subprocess.run(["node", str(capture_script)], check=True, cwd=str(APP_DIR))

    # Keep existing brain-element package as-is from workspace assets.
    runpy.run_path(str(SCRIPT_DIR / "generate_zia_ar_social_media_assets.py"), run_name="__main__")

    slides_api, drive, gmail = services()

    cover_img = EXACT_OUT / "ziya_home_exact_ar.png"
    end_img = EXACT_OUT / "ziya_home_exact_en.png"
    base_img = EXACT_OUT / "ziya_home_exact_ar.png"
    reel_mp4 = SOCIAL_OUT / "zia_reel_fast_transition_ar.mp4"

    cover_url = upload_public(drive, cover_img, "image/png") if cover_img.exists() else None
    end_url = upload_public(drive, end_img, "image/png") if end_img.exists() else None
    base_url = upload_public(drive, base_img, "image/png") if base_img.exists() else cover_url
    reel_url = upload_public(drive, reel_mp4, "video/mp4") if reel_mp4.exists() else ""

    social_zip = ASSETS_DIR / "social_media_ar_pack.zip"
    zip_dir(SOCIAL_OUT, social_zip)

    exact_assets_zip = ASSETS_DIR / "zia_exact_site_assets_pack.zip"
    zip_dir(EXACT_OUT, exact_assets_zip)

    app_source_zip = ASSETS_DIR / "zia_real_app_brand_source_pack.zip"
    with zipfile.ZipFile(app_source_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        include_paths = [
            APP_DIR / "src" / "pages" / "Home.jsx",
            APP_DIR / "src" / "components" / "ziyada" / "ThreeBackground.jsx",
            APP_DIR / "src" / "components" / "ziyada" / "BrandIcons.jsx",
            APP_DIR / "src" / "components" / "ziyada" / "GlassPanel.jsx",
            APP_DIR / "src" / "globals.css",
            APP_DIR / "src" / "index.css",
        ]
        for p in include_paths:
            if p.exists():
                zf.write(p, arcname=p.relative_to(APP_DIR))

    payloads = make_payloads(reel_url, "https://drive.google.com/drive/my-drive")

    d1 = create_deck(
        slides_api,
        "Zia V2 Corporate Proposal Template | Arabic",
        payloads["proposal"],
        cover_url,
        end_url,
        base_url,
    )
    d2 = create_deck(
        slides_api,
        "Zia V2 Social Media & Montage Playbook | Arabic",
        payloads["social"],
        cover_url,
        end_url,
        base_url,
    )
    d3 = create_deck(
        slides_api,
        "Zia Moon Tier Creative Template",
        payloads["moon"],
        cover_url,
        end_url,
        base_url,
    )

    p1 = OUTPUTS_DIR / "zia_v2_corporate_proposal_template_ar.pptx"
    p2 = OUTPUTS_DIR / "zia_v2_social_media_montage_playbook_ar.pptx"
    p3 = OUTPUTS_DIR / "zia_moon_tier_creative_template.pptx"

    export_pptx(drive, d1["id"], p1)
    export_pptx(drive, d2["id"], p2)
    export_pptx(drive, d3["id"], p3)

    attachments = [p1, p2, p3, exact_assets_zip, app_source_zip, social_zip]
    brain_zip = ASSETS_DIR / "brain-element-pattern-pack.zip"
    if brain_zip.exists():
        attachments.append(brain_zip)

    body = (
        "مرحبا فريق Zia،\n\n"
        "هذا Draft محدث باستخدام أصول النظام الفعلية من التطبيق نفسه (بدون توليد نمط جديد):\n"
        "1) قالب عروض وQuotations عربي\n"
        "2) دليل السوشال والمونتاج بالتفصيل (Static/Carousel/Reels/Transitions)\n"
        "3) قالب Moon Tier الإبداعي\n"
        "4) حزمة لقطات الموقع الحقيقية + ملفات المصدر البصرية + نماذج منشورات عربية + فيديو ريلز متحرك\n\n"
        f"روابط Google Slides:\n- {d1['url']}\n- {d2['url']}\n- {d3['url']}\n\n"
        f"رابط فيديو الريلز: {reel_url}\n\n"
        "ملاحظة: الخلفيات في الشرائح الآن من لقطات الموقع الفعلية الملتقطة من النسخة الصحيحة للتطبيق.\n"
    )

    draft_id = create_draft(
        gmail,
        "Zia V3 Exact Brand Suite (Real App Assets) + Moon Tier + Arabic Playbook (Draft)",
        body,
        attachments,
    )

    print("Done")
    print("Decks:")
    print(d1["url"])
    print(d2["url"])
    print(d3["url"])
    print(f"Reel: {reel_url}")
    print(f"Draft: {draft_id}")
    print("Attachments:")
    for a in attachments:
        print(f"- {a}")


if __name__ == "__main__":
    main()
