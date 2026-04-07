#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import List

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "outputs" / "social_media_ar"
EXACT_DIR = PROJECT_DIR / "outputs" / "zia_exact_site_assets"

WHITE = (255, 255, 255)
LIGHT = (226, 232, 240)
CTA_FILL = (99, 102, 241, 232)
CTA_STROKE = (129, 140, 248, 255)


def _font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Tahoma.ttf",
    ]
    for c in candidates:
        p = Path(c)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def _pick_base() -> Image.Image:
    candidates = [
        EXACT_DIR / "ziya_home_exact_ar.png",
        EXACT_DIR / "ziya_home_exact_en.png",
    ]
    for c in candidates:
        if c.exists():
            return Image.open(c).convert("RGBA")
    raise RuntimeError("Exact site screenshots are missing. Run capture_zia_exact_screenshots.mjs first.")


def _cover(img: Image.Image, w: int, h: int) -> Image.Image:
    return ImageOps.fit(img, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35)).convert("RGBA")


def _paste_brain_overlay(base: Image.Image, w: int, h: int) -> None:
    # Reuse existing ring/core from workspace pack rather than generating new geometry.
    ring = ASSETS_DIR / "brain-element-pattern" / "brain-element-ring-front.png"
    core = ASSETS_DIR / "brain-element-pattern" / "brain-element-core-front.png"
    if not ring.exists() or not core.exists():
        return

    ring_img = Image.open(ring).convert("RGBA")
    core_img = Image.open(core).convert("RGBA")

    target_w = int(w * 0.60)
    scale = target_w / max(1, ring_img.width)
    target_h = int(ring_img.height * scale)

    ring_img = ring_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    core_img = core_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    x = (w - target_w) // 2
    y = int(h * 0.05)

    base.alpha_composite(ring_img, (x, y))
    base.alpha_composite(core_img, (x, y))


def _cta(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> None:
    w, h = 250, 58
    draw.rounded_rectangle((x, y, x + w, y + h), radius=30, fill=CTA_FILL, outline=CTA_STROKE, width=2)
    font = _font(28)
    tw = draw.textlength(text, font=font)
    draw.text((x + (w - tw) // 2, y + 12), text, font=font, fill=WHITE + (255,))


def _card(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=28, fill=(255, 255, 255, 34), outline=(255, 255, 255, 118), width=2)


def _write_multiline(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, size: int, fill=(255, 255, 255, 255), spacing=14) -> None:
    font = _font(size)
    draw.multiline_text((x, y), text, font=font, fill=fill, spacing=spacing, direction="rtl", align="right")


def create_post(base_ref: Image.Image, path: Path, w: int, h: int, title: str, subtitle: str, bullets: List[str], cta: str) -> None:
    img = _cover(base_ref, w, h)
    draw = ImageDraw.Draw(img, "RGBA")

    # Add subtle readability veil while keeping exact site visual feel.
    draw.rectangle((0, 0, w, h), fill=(6, 10, 24, 92))
    _paste_brain_overlay(img, w, h)

    overlay_y = int(h * 0.16)
    _card(draw, int(w * 0.08), overlay_y, int(w * 0.84), int(h * 0.62))

    _write_multiline(draw, title, int(w * 0.82), overlay_y + 42, 68, fill=(99, 102, 241, 255))
    _write_multiline(draw, subtitle, int(w * 0.82), overlay_y + 150, 34, fill=(226, 232, 240, 240))

    yy = overlay_y + 245
    for b in bullets:
        _write_multiline(draw, f"• {b}", int(w * 0.82), yy, 30, fill=(226, 232, 240, 235))
        yy += 56

    _cta(draw, int(w * 0.34), overlay_y + int(h * 0.46), cta)
    img.save(path)


def create_story_pack() -> List[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files: List[Path] = []
    base_ref = _pick_base()

    p1 = OUT_DIR / "post_static_square_ar.png"
    create_post(
        base_ref,
        p1,
        1080,
        1080,
        "خلّ أنظمة مبيعاتك تشتغل بذكاء",
        "تسويق + أتمتة + CRM في مسار واحد واضح",
        [
            "تصميم رحلة عميل كاملة",
            "ربط الإعلانات بالتحويلات",
            "لوحات متابعة تنفيذية",
        ],
        "احجز جلسة",
    )
    files.append(p1)

    for i, t in enumerate([
        "منشور كاروسيل 1: المشكلة",
        "منشور كاروسيل 2: الحل",
        "منشور كاروسيل 3: النتائج",
    ], start=1):
        p = OUT_DIR / f"carousel_{i:02d}_ar.png"
        create_post(
            base_ref,
            p,
            1080,
            1350,
            t,
            "قالب جاهز للفِرق التسويقية B2B",
            ["رسالة واضحة", "هوية بصرية ثابتة", "CTA مباشر"],
            "ابدأ الآن",
        )
        files.append(p)

    story = OUT_DIR / "story_vertical_ar.png"
    create_post(
        base_ref,
        story,
        1080,
        1920,
        "ريلز سريعة\nبطابع احترافي",
        "إيقاع سريع + انتقالات نظيفة + نصوص عربية",
        ["هوك أول 2 ثانية", "قيمة واضحة", "دعوة إجراء"],
        "اطلب عرض",
    )
    files.append(story)

    return files


def create_mockups() -> List[Path]:
    files: List[Path] = []
    src = _cover(_pick_base(), 700, 1450).convert("RGBA")

    iphone = OUT_DIR / "mockup_iphone_open_source.png"
    img = Image.new("RGBA", (1400, 1800), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((300, 80, 1100, 1720), radius=120, fill=(12, 18, 35, 255), outline=(180, 190, 210, 200), width=6)
    d.rounded_rectangle((350, 170, 1050, 1620), radius=70, fill=(25, 35, 60, 255), outline=(120, 140, 180, 180), width=3)
    d.rounded_rectangle((640, 112, 760, 150), radius=16, fill=(38, 48, 75, 255))
    img.alpha_composite(src, (350, 170))
    img.save(iphone)
    files.append(iphone)

    macbook = OUT_DIR / "mockup_macbook_2025_open_source.png"
    img = Image.new("RGBA", (2200, 1400), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((250, 80, 1950, 1120), radius=34, fill=(10, 14, 28, 255), outline=(170, 180, 200, 190), width=4)
    d.rounded_rectangle((320, 150, 1880, 1040), radius=16, fill=(20, 28, 48, 255), outline=(110, 130, 165, 170), width=2)
    d.rounded_rectangle((120, 1090, 2080, 1250), radius=24, fill=(75, 80, 95, 220), outline=(185, 190, 205, 160), width=2)
    mac_src = _cover(_pick_base(), 1560, 890)
    img.alpha_composite(mac_src, (320, 150))
    img.save(macbook)
    files.append(macbook)

    return files


def _ken_burns(base: Image.Image, w: int, h: int, t: float, zoom_from: float, zoom_to: float, drift: float) -> np.ndarray:
    z = zoom_from + (zoom_to - zoom_from) * t
    ww = int(w / z)
    hh = int(h / z)

    cx = base.width // 2 + int((t - 0.5) * drift)
    cy = base.height // 2 + int((0.5 - t) * drift * 0.3)

    x1 = max(0, min(base.width - ww, cx - ww // 2))
    y1 = max(0, min(base.height - hh, cy - hh // 2))
    crop = base.crop((x1, y1, x1 + ww, y1 + hh)).resize((w, h), Image.Resampling.LANCZOS)
    return np.array(crop.convert("RGB"))


def create_reel_video(images: List[Path], out_path: Path, fps: int = 30) -> Path:
    frames = []
    hold_frames = int(0.9 * fps)
    trans_frames = int(0.20 * fps)

    loaded = [Image.open(p).convert("RGBA").resize((1240, 2200), Image.Resampling.LANCZOS) for p in images]

    for idx, im in enumerate(loaded):
        for k in range(hold_frames):
            t = k / max(1, hold_frames - 1)
            frames.append(_ken_burns(im, 1080, 1920, t, zoom_from=1.03, zoom_to=1.12, drift=180))

        if idx < len(loaded) - 1:
            nxt = loaded[idx + 1]
            for t in range(1, trans_frames + 1):
                a = t / float(trans_frames)
                cur = _ken_burns(im, 1080, 1920, 1.0, zoom_from=1.03, zoom_to=1.12, drift=180)
                nxtf = _ken_burns(nxt, 1080, 1920, 0.0, zoom_from=1.03, zoom_to=1.12, drift=180)
                mix = (cur * (1.0 - a) + nxtf * a).astype(np.uint8)
                frames.append(mix)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    imageio.mimwrite(out_path, frames, fps=fps, codec="libx264", quality=8, macro_block_size=1)
    return out_path


def main() -> None:
    posts = create_story_pack()
    mockups = create_mockups()

    reel_inputs = [
        OUT_DIR / "story_vertical_ar.png",
        OUT_DIR / "carousel_01_ar.png",
        OUT_DIR / "carousel_02_ar.png",
        OUT_DIR / "carousel_03_ar.png",
        OUT_DIR / "post_static_square_ar.png",
    ]
    reel = create_reel_video(reel_inputs, OUT_DIR / "zia_reel_fast_transition_ar.mp4")

    print("Generated social assets:")
    for p in posts:
        print(f"- {p}")
    print("Generated mockups:")
    for p in mockups:
        print(f"- {p}")
    print(f"Generated reel: {reel}")


if __name__ == "__main__":
    main()
