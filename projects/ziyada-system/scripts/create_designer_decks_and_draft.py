#!/usr/bin/env python3
"""Create two designer Google Slides decks and draft one Gmail with attachments.

What this script does:
1) Generates/refreshes open-source design asset packs.
2) Creates two Google Slides decks:
   - Corporate proposal/quotation template deck.
   - Brand + social media creative production playbook deck.
3) Exports both decks as PPTX attachments.
4) Creates one Gmail draft to ali.biggy.af@gmail.com with all files attached.
"""

from __future__ import annotations

import base64
import io
import mimetypes
import runpy
import zipfile
from dataclasses import dataclass
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
OUTPUTS_DIR = PROJECT_DIR / "outputs"

RECIPIENT = "ali.biggy.af@gmail.com"
SENDER = "ali.biggy.af@gmail.com"

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.compose",
]


@dataclass
class SlideContent:
    title: str
    body: str
    tag: str = ""
    variant: str = "default"  # default | cover | end


def get_creds() -> Credentials:
    token_path = PROJECT_DIR / "token.json"
    if not token_path.exists():
        raise RuntimeError("Missing token.json in projects/ziyada-system. Run OAuth setup first.")

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds.valid:
        raise RuntimeError("token.json is invalid for required Slides/Drive/Gmail scopes.")

    return creds


def slides_service(creds: Credentials):
    return build("slides", "v1", credentials=creds)


def drive_service(creds: Credentials):
    return build("drive", "v3", credentials=creds)


def gmail_service(creds: Credentials):
    return build("gmail", "v1", credentials=creds)


def _rgb(hex_color: str) -> Dict[str, float]:
    hex_color = hex_color.lstrip("#")
    return {
        "red": int(hex_color[0:2], 16) / 255,
        "green": int(hex_color[2:4], 16) / 255,
        "blue": int(hex_color[4:6], 16) / 255,
    }


def _find_placeholder_id(slide: Dict, types: List[str]) -> Optional[str]:
    for el in slide.get("pageElements", []):
        shape = el.get("shape")
        if not shape:
            continue
        ph = shape.get("placeholder")
        if not ph:
            continue
        if ph.get("type") in types:
            return el.get("objectId")
    return None


def _set_text(obj_id: str, text: str) -> List[Dict]:
    return [
        {
            "insertText": {
                "objectId": obj_id,
                "insertionIndex": 0,
                "text": text,
            }
        },
    ]


def _background_requests(slide_id: str, idx: int) -> List[Dict]:
    bg_id = f"bgx_{idx}"
    glow_id = f"glow_{idx}"
    card_id = f"card_{idx}"
    chip_id = f"chip_{idx}"
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
                        "solidFill": {"color": {"rgbColor": _rgb("0f172a")}}
                    },
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
                "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
            }
        },
        {
            "createShape": {
                "objectId": glow_id,
                "shapeType": "ELLIPSE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 460, "unit": "PT"},
                        "height": {"magnitude": 460, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 250,
                        "translateY": 40,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": glow_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {"rgbColor": _rgb("3b82f6")},
                            "alpha": 0.08,
                        }
                    },
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
                "fields": "shapeBackgroundFill.solidFill.color,shapeBackgroundFill.solidFill.alpha,outline.propertyState",
            }
        },
        {
            "createShape": {
                "objectId": card_id,
                "shapeType": "ROUND_RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 840, "unit": "PT"},
                        "height": {"magnitude": 400, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 60,
                        "translateY": 72,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": card_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {"rgbColor": _rgb("ffffff")},
                            "alpha": 0.06,
                        }
                    },
                    "outline": {
                        "outlineFill": {
                            "solidFill": {
                                "color": {"rgbColor": _rgb("ffffff")},
                                "alpha": 0.32,
                            }
                        },
                        "weight": {"magnitude": 1, "unit": "PT"},
                    },
                },
                "fields": "shapeBackgroundFill.solidFill.color,shapeBackgroundFill.solidFill.alpha,outline.outlineFill.solidFill.color,outline.outlineFill.solidFill.alpha,outline.weight",
            }
        },
        {
            "createShape": {
                "objectId": chip_id,
                "shapeType": "ROUND_RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 190, "unit": "PT"},
                        "height": {"magnitude": 28, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 708,
                        "translateY": 26,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": chip_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {"rgbColor": _rgb("8b5cf6")},
                            "alpha": 0.24,
                        }
                    },
                    "outline": {
                        "outlineFill": {
                            "solidFill": {
                                "color": {"rgbColor": _rgb("8b5cf6")},
                                "alpha": 0.45,
                            }
                        },
                        "weight": {"magnitude": 1, "unit": "PT"},
                    },
                },
                "fields": "shapeBackgroundFill.solidFill.color,shapeBackgroundFill.solidFill.alpha,outline.outlineFill.solidFill.color,outline.outlineFill.solidFill.alpha,outline.weight",
            }
        },
        {
            "updatePageElementsZOrder": {
                "pageElementObjectIds": [bg_id, glow_id],
                "operation": "SEND_TO_BACK",
            }
        },
    ]


def _slide_text_style_requests(title_id: Optional[str], body_id: Optional[str], title_size: int = 34) -> List[Dict]:
    reqs: List[Dict] = []
    if title_id:
        reqs.append(
            {
                "updateTextStyle": {
                    "objectId": title_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": "Inter",
                        "fontSize": {"magnitude": title_size, "unit": "PT"},
                        "bold": True,
                        "foregroundColor": {"opaqueColor": {"rgbColor": _rgb("ffffff")}},
                    },
                    "fields": "fontFamily,fontSize,bold,foregroundColor",
                }
            }
        )

    if body_id:
        reqs.append(
            {
                "updateTextStyle": {
                    "objectId": body_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": "Inter",
                        "fontSize": {"magnitude": 17, "unit": "PT"},
                        "foregroundColor": {"opaqueColor": {"rgbColor": _rgb("cbd5e1")}},
                    },
                    "fields": "fontFamily,fontSize,foregroundColor",
                }
            }
        )

    return reqs


def upload_public_file(drive, path: Path, mime: str) -> str:
    meta = {"name": path.name, "mimeType": mime}
    media = MediaFileUpload(str(path), mimetype=mime)
    created = drive.files().create(body=meta, media_body=media, fields="id").execute()
    file_id = created["id"]

    drive.permissions().create(fileId=file_id, body={"type": "anyone", "role": "reader"}).execute()
    return f"https://drive.google.com/uc?id={file_id}"


def create_deck(
    slides_api,
    drive,
    title: str,
    slides_content: List[SlideContent],
    cover_bg: Optional[Path] = None,
    end_bg: Optional[Path] = None,
) -> Dict[str, str]:
    created = slides_api.presentations().create(body={"title": title}).execute()
    pres_id = created["presentationId"]

    if len(slides_content) > 1:
        requests = []
        for _ in range(len(slides_content) - 1):
            requests.append(
                {
                    "createSlide": {
                        "slideLayoutReference": {
                            "predefinedLayout": "TITLE_AND_BODY"
                        }
                    }
                }
            )
        slides_api.presentations().batchUpdate(presentationId=pres_id, body={"requests": requests}).execute()

    cover_url = None
    end_url = None
    if cover_bg and cover_bg.exists():
        cover_url = upload_public_file(drive, cover_bg, "image/png")
    if end_bg and end_bg.exists():
        end_url = upload_public_file(drive, end_bg, "image/png")

    pres = slides_api.presentations().get(presentationId=pres_id).execute()
    slides = pres.get("slides", [])

    for idx, (slide_obj, payload) in enumerate(zip(slides, slides_content)):
        sid = slide_obj["objectId"]
        reqs: List[Dict] = []
        reqs.extend(_background_requests(sid, idx))

        # Cover/end full image backdrop overlay.
        if payload.variant == "cover" and cover_url:
            reqs.append(
                {
                    "createImage": {
                        "objectId": f"cover_img_{idx}",
                        "url": cover_url,
                        "elementProperties": {
                            "pageObjectId": sid,
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
                }
            )
            reqs.append(
                {
                    "updatePageElementsZOrder": {
                        "pageElementObjectIds": [f"cover_img_{idx}"],
                        "operation": "SEND_TO_BACK",
                    }
                }
            )

        if payload.variant == "end" and end_url:
            reqs.append(
                {
                    "createImage": {
                        "objectId": f"end_img_{idx}",
                        "url": end_url,
                        "elementProperties": {
                            "pageObjectId": sid,
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
                }
            )
            reqs.append(
                {
                    "updatePageElementsZOrder": {
                        "pageElementObjectIds": [f"end_img_{idx}"],
                        "operation": "SEND_TO_BACK",
                    }
                }
            )

        title_id = _find_placeholder_id(slide_obj, ["CENTERED_TITLE", "TITLE"])
        body_id = _find_placeholder_id(slide_obj, ["SUBTITLE", "BODY"])

        if title_id:
            reqs.extend(_set_text(title_id, payload.title))
        if body_id:
            reqs.extend(_set_text(body_id, payload.body))

        title_size = 44 if payload.variant == "cover" else 34
        reqs.extend(_slide_text_style_requests(title_id, body_id, title_size=title_size))

        if payload.tag:
            tag_box = f"tag_{idx}"
            reqs.append(
                {
                    "createShape": {
                        "objectId": tag_box,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": sid,
                            "size": {
                                "width": {"magnitude": 180, "unit": "PT"},
                                "height": {"magnitude": 20, "unit": "PT"},
                            },
                            "transform": {
                                "scaleX": 1,
                                "scaleY": 1,
                                "translateX": 716,
                                "translateY": 32,
                                "unit": "PT",
                            },
                        },
                    }
                }
            )
            reqs.append({"insertText": {"objectId": tag_box, "insertionIndex": 0, "text": payload.tag}})
            reqs.append(
                {
                    "updateTextStyle": {
                        "objectId": tag_box,
                        "textRange": {"type": "ALL"},
                        "style": {
                            "fontFamily": "Inter",
                            "fontSize": {"magnitude": 10, "unit": "PT"},
                            "bold": True,
                            "foregroundColor": {"opaqueColor": {"rgbColor": _rgb("e2e8f0")}},
                        },
                        "fields": "fontFamily,fontSize,bold,foregroundColor",
                    }
                }
            )

        slides_api.presentations().batchUpdate(presentationId=pres_id, body={"requests": reqs}).execute()

    return {
        "id": pres_id,
        "url": f"https://docs.google.com/presentation/d/{pres_id}/edit",
    }


def export_pptx(drive, presentation_id: str, target_path: Path) -> None:
    request = drive.files().export_media(
        fileId=presentation_id,
        mimeType="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with io.FileIO(target_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()


def create_zip_from_dir(source_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(source_dir.rglob("*")):
            if p.is_file():
                zf.write(p, arcname=p.relative_to(source_dir))


def create_gmail_draft_with_attachments(gmail, subject: str, body_text: str, attachments: List[Path]) -> str:
    msg = MIMEMultipart()
    msg["To"] = RECIPIENT
    msg["From"] = SENDER
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    for path in attachments:
        ctype, _ = mimetypes.guess_type(str(path))
        if not ctype:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        with open(path, "rb") as f:
            payload = f.read()

        if maintype == "application":
            part = MIMEApplication(payload, _subtype=subtype)
        else:
            part = MIMEApplication(payload, _subtype="octet-stream")

        part.add_header("Content-Disposition", "attachment", filename=path.name)
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    draft = gmail.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft.get("id", "")


def corporate_template_slides() -> List[SlideContent]:
    return [
        SlideContent(
            title="Ziyada Corporate Proposal Template",
            body="B2B-ready Google Slides template system\nCover, sections, pricing, quotation, and closing variants\nDesigned with glass cards, clean frames, and corporate rhythm",
            tag="COVER",
            variant="cover",
        ),
        SlideContent("How To Use This Deck", "Duplicate this file and keep master styles\nSwap colors/photos while preserving spacing\nUse frame and card components from the asset pack", "START"),
        SlideContent("Section Cover Options", "Option A: Statement headline\nOption B: KPI headline\nOption C: Problem-solution angle\nUse one visual motif per section", "SECTIONS"),
        SlideContent("Executive Summary Layout", "Client objective\nCurrent challenge\nStrategic thesis\nExpected measurable impact", "PROPOSAL"),
        SlideContent("Problem -> Opportunity", "What is broken in the funnel\nWhat opportunity is being missed\nWhat this proposal changes", "PROPOSAL"),
        SlideContent("Solution Architecture", "Workstreams\nDependencies\nTools and automation layers\nOwnership model", "PROPOSAL"),
        SlideContent("Pricing Options", "Package A: Foundation\nPackage B: Growth\nPackage C: Performance\nInclude scope, timeline, and assumptions", "QUOTATION"),
        SlideContent("Quotation Page", "Client details\nService line items\nCommercial terms\nApproval signature block", "QUOTATION"),
        SlideContent("Timeline & Milestones", "Week-by-week rollout\nReview checkpoints\nDelivery ownership and governance", "DELIVERY"),
        SlideContent("Case Study Template", "Client context\nActions executed\nResult with numbers\nKey lesson", "TRUST"),
        SlideContent("Team & Operating Model", "Who leads strategy\nWho manages execution\nReporting cadence\nEscalation path", "TEAM"),
        SlideContent(
            title="Thank You",
            body="Ziyada System\nDesign and growth systems for measurable B2B outcomes\nContact: ali.biggy.af@gmail.com",
            tag="END",
            variant="end",
        ),
    ]


def social_playbook_slides() -> List[SlideContent]:
    return [
        SlideContent(
            title="Ziyada Social & Creative Production Playbook",
            body="Brand guideline + platform-specific design standards\nFor social media designers, editors, and marketing teams",
            tag="COVER",
            variant="cover",
        ),
        SlideContent("Brand Core Rules", "Color system and typography hierarchy\nIcon language and spacing rules\nWhen to use glass cards, frames, and patterns", "BRAND"),
        SlideContent("Platform Specs", "LinkedIn, Instagram, X, YouTube, TikTok\nAspect ratios, safe zones, and export formats\nText limits and hook placement", "PLATFORMS"),
        SlideContent("Static Post System", "Hero headline card\nProblem-solution cards\nCTA card variants\nLogo lockup rules", "STATIC"),
        SlideContent("Carousel Design System", "Slide 1 hook formats\nStory arc from slide 2-7\nSlide 8 CTA and lead capture\nProgress markers and consistency", "CAROUSEL"),
        SlideContent("Reels & Short Video System", "0-3 sec hook\n3-12 sec value\n12-25 sec proof\n25-35 sec CTA\nSubtitle placement standards", "REELS"),
        SlideContent("Animation Guidelines", "Motion pacing: calm, confident, intentional\nUse transitions to support meaning\nAvoid distracting effects in B2B contexts", "ANIMATION"),
        SlideContent("Montage Workflow", "Script -> shot list -> edit map\nPrimary and secondary footage strategy\nB-roll layering and text timing\nMusic and VO balance", "MONTAGE"),
        SlideContent("Transition Library", "Fade for insight shifts\nDirectional slide for process steps\nScale reveal for highlights\nGlitch only for rare emphasis", "TRANSITIONS"),
        SlideContent("Creative QA Checklist", "Brand compliance\nMessage clarity\nPlatform fit\nReadability on mobile\nCTA and tracking tags", "QA"),
        SlideContent("Content Production Pipeline", "Brief template\nAsset request format\nReview rounds\nApproval flow between marketing and design", "PROCESS"),
        SlideContent("Examples To Build", "3x static templates\n3x carousel templates\n3x reel templates\n1x campaign board per quarter", "SAMPLES"),
        SlideContent(
            title="Creative Team Enablement",
            body="Use this deck as your operating design manual\nUpdate monthly with tested patterns and platform changes\nKeep one source of truth for all teams",
            tag="END",
            variant="end",
        ),
    ]


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Refresh asset generators.
    runpy.run_path(str(SCRIPT_DIR / "generate_corporate_design_kit.py"), run_name="__main__")
    runpy.run_path(str(SCRIPT_DIR / "export_brain_element_pattern.py"), run_name="__main__")

    corporate_pack = ASSETS_DIR / "corporate-design-kit-pack.zip"
    create_zip_from_dir(ASSETS_DIR / "corporate-design-kit", corporate_pack)

    # 2) Build decks.
    creds = get_creds()
    slides_api = slides_service(creds)
    drive = drive_service(creds)
    gmail = gmail_service(creds)

    cover_bg = ASSETS_DIR / "corporate-design-kit" / "backgrounds" / "bg-corporate-hero.png"
    end_bg = ASSETS_DIR / "corporate-design-kit" / "backgrounds" / "bg-corporate-square.png"

    deck1 = create_deck(
        slides_api,
        drive,
        title="Ziyada Corporate Proposal & Quotation Designer Template",
        slides_content=corporate_template_slides(),
        cover_bg=cover_bg,
        end_bg=end_bg,
    )

    deck2 = create_deck(
        slides_api,
        drive,
        title="Ziyada Social Media & Creative Production Playbook",
        slides_content=social_playbook_slides(),
        cover_bg=cover_bg,
        end_bg=end_bg,
    )

    # 3) Export decks as PPTX for attachment.
    deck1_pptx = OUTPUTS_DIR / "ziyada_corporate_proposal_template_deck.pptx"
    deck2_pptx = OUTPUTS_DIR / "ziyada_social_media_creative_playbook_deck.pptx"
    export_pptx(drive, deck1["id"], deck1_pptx)
    export_pptx(drive, deck2["id"], deck2_pptx)

    brain_pack = ASSETS_DIR / "brain-element-pattern-pack.zip"

    # 4) Draft email with both decks + open-source asset packs.
    subject = "Ziyada Designer Kits: Corporate Templates + Social Playbook (Draft)"
    body = (
        "Hi,\n\n"
        "Attached are the requested designer deliverables:\n"
        "1) Corporate proposal/quotation Google Slides template (PPTX export)\n"
        "2) Social media & creative production playbook (PPTX export)\n"
        "3) Corporate open-source design kit (backgrounds, glass cards, frames, icons, minimal patterns)\n"
        "4) Brain element pattern pack (combined + separated elements + pattern variants)\n\n"
        "Google Slides links:\n"
        f"- Deck 1: {deck1['url']}\n"
        f"- Deck 2: {deck2['url']}\n\n"
        "This draft is ready for review and send.\n"
    )

    attachments = [deck1_pptx, deck2_pptx, corporate_pack]
    if brain_pack.exists():
        attachments.append(brain_pack)

    draft_id = create_gmail_draft_with_attachments(gmail, subject, body, attachments)

    print("Done")
    print(f"Deck1: {deck1['url']}")
    print(f"Deck2: {deck2['url']}")
    print(f"Draft ID: {draft_id}")
    print("Attachments:")
    for p in attachments:
        print(f"- {p}")


if __name__ == "__main__":
    main()
