from __future__ import annotations

import math
import subprocess
from pathlib import Path

import arabic_reshaper
import imageio_ffmpeg
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, features


WIDTH = 1080
HEIGHT = 1920
FPS = 24
DURATION_SECONDS = 14
TOTAL_FRAMES = FPS * DURATION_SECONDS

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs" / "ziyada-video"
OUTPUTS.mkdir(parents=True, exist_ok=True)

SOURCE_SAUDI = ROOT / "Ziyada inspairations" / "Screenshot 2026-04-09 at 11.52.16 PM.png"
SOURCE_TECH = ROOT / "Ziyada inspairations" / "Screenshot 2026-04-10 at 2.03.39 AM.png"

SILENT_VIDEO = OUTPUTS / "ziyada_system_awareness_silent.mp4"
VOICEOVER_AIFF = OUTPUTS / "ziyada_system_awareness_vo.aiff"
FINAL_VIDEO = OUTPUTS / "ziyada_system_awareness_reel.mp4"

BRAND_DEEP = "#0f172a"
BRAND_BLUE = "#3b82f6"
BRAND_PURPLE = "#8b5cf6"
BRAND_TEAL = "#06b6d4"
BRAND_PINK = "#ec4899"
WHITE = "#ffffff"

VOICEOVER_TEXT = (
    "في كل رسالة تتأخر، وفي كل فرصة ممكن تضيع، هنا يجي دور زيادة سيستم. "
    "نربط قنواتك، ونتابع عملاءك، ونخلي الوعي بالنظام حاضر في كل لحظة. "
    "زيادة سيستم. وضوح أكثر، متابعة أسرع، ونمو أذكى."
)

IS_RAQM_AVAILABLE = features.check("raqm")


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def shape_ar(text: str) -> str:
    return text if IS_RAQM_AVAILABLE else get_display(arabic_reshaper.reshape(text))


def draw_ar_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    anchor: str = "mm",
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] | None = None,
) -> None:
    kwargs: dict[str, object] = {
        "fill": fill,
        "font": font,
        "anchor": anchor,
        "stroke_width": stroke_width,
        "stroke_fill": stroke_fill,
    }
    if IS_RAQM_AVAILABLE:
        kwargs["direction"] = "rtl"
        kwargs["language"] = "ar"
    draw.text(xy, shape_ar(text), **kwargs)


def draw_text_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    line_gap: int = 18,
) -> None:
    x1, y1, x2, y2 = box
    center_x = (x1 + x2) // 2
    lines = text.split("\n")
    line_boxes = [draw.textbbox((0, 0), shape_ar(line), font=font, direction="rtl" if IS_RAQM_AVAILABLE else None) for line in lines]
    heights = [b[3] - b[1] for b in line_boxes]
    total_h = sum(heights) + line_gap * max(0, len(lines) - 1)
    y = y1 + ((y2 - y1) - total_h) // 2
    for line, h in zip(lines, heights):
        draw_ar_text(draw, (center_x, y + h / 2), line, font, fill)
        y += h + line_gap


def find_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    for path in candidates:
        p = Path(path)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


AR_H1 = find_font(
    [
        "/System/Library/Fonts/SFArabicRounded.ttf",
        "/System/Library/Fonts/SFArabic.ttf",
        "/System/Library/Fonts/GeezaPro.ttc",
    ],
    92,
)
AR_H2 = find_font(
    [
        "/System/Library/Fonts/SFArabicRounded.ttf",
        "/System/Library/Fonts/SFArabic.ttf",
        "/System/Library/Fonts/GeezaPro.ttc",
    ],
    60,
)
AR_BODY = find_font(
    [
        "/System/Library/Fonts/SFArabic.ttf",
        "/System/Library/Fonts/GeezaPro.ttc",
    ],
    42,
)
AR_SMALL = find_font(
    [
        "/System/Library/Fonts/SFArabic.ttf",
        "/System/Library/Fonts/GeezaPro.ttc",
    ],
    34,
)


def eased(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


def smooth_step(start: float, end: float, t: float) -> float:
    if t <= start:
        return 0.0
    if t >= end:
        return 1.0
    return eased((t - start) / (end - start))


def scene_progress(scene_start: float, scene_end: float, t: float) -> float:
    return smooth_step(scene_start, scene_end, t)


def load_image(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def prepare_cover_image(src: Image.Image, max_zoom: float) -> Image.Image:
    scale = max(WIDTH / src.width, HEIGHT / src.height) * max_zoom
    sw = int(src.width * scale)
    sh = int(src.height * scale)
    return src.resize((sw, sh), Image.Resampling.LANCZOS)


def cover_crop(resized: Image.Image, focus: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    sw, sh = resized.size
    left = int((sw - WIDTH) * focus[0])
    top = int((sh - HEIGHT) * focus[1])
    left = max(0, min(left, sw - WIDTH))
    top = max(0, min(top, sh - HEIGHT))
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def make_scene_background(t: float, saudi_img: Image.Image, tech_img: Image.Image) -> Image.Image:
    if t < 4.8:
        pan = 0.15 + 0.08 * smooth_step(0.0, 4.8, t)
        frame = cover_crop(saudi_img, focus=(pan, 0.06))
        gradient = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gradient, "RGBA")
        gd.rectangle([0, 0, WIDTH, HEIGHT], fill=(6, 10, 25, 72))
        gd.rectangle([0, HEIGHT - 760, WIDTH, HEIGHT], fill=(3, 8, 24, 150))
        frame = frame.convert("RGBA")
        frame.alpha_composite(gradient)
        return frame.convert("RGB")

    if t < 10.2:
        drift = 0.52 + 0.06 * math.sin(t * 0.35)
        frame = cover_crop(tech_img, focus=(drift, 0.12))
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), rgba(BRAND_DEEP, 176))
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        gd.ellipse([-220, 280, 760, 1260], fill=rgba(BRAND_PURPLE, 150))
        gd.ellipse([420, 860, 1360, 1780], fill=rgba(BRAND_BLUE, 140))
        gd.ellipse([280, -180, 1160, 700], fill=rgba(BRAND_TEAL, 110))
        glow = glow.filter(ImageFilter.GaussianBlur(90))
        frame = frame.convert("RGBA")
        frame.alpha_composite(overlay)
        frame.alpha_composite(glow)
        return frame.convert("RGB")

    base = Image.new("RGBA", (WIDTH, HEIGHT), rgba(BRAND_DEEP))
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse([-160, -120, 820, 920], fill=rgba(BRAND_PURPLE, 150))
    gd.ellipse([300, 880, 1320, 1940], fill=rgba(BRAND_BLUE, 150))
    gd.ellipse([580, -80, 1260, 560], fill=rgba(BRAND_TEAL, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(110))
    base.alpha_composite(glow)
    return base.convert("RGB")


def draw_network(draw: ImageDraw.ImageDraw, t: float, alpha: int) -> None:
    nodes = [
        (230, 520),
        (530, 420),
        (830, 560),
        (300, 920),
        (760, 920),
        (530, 1220),
    ]
    for a, b in [(0, 1), (1, 2), (1, 3), (1, 4), (3, 5), (4, 5)]:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        draw.line((x1, y1, x2, y2), fill=rgba(BRAND_TEAL, alpha // 2), width=3)

    for idx, (x, y) in enumerate(nodes):
        pulse = 0.5 + 0.5 * math.sin(t * 2.1 + idx)
        r = 22 + int(8 * pulse)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=rgba(WHITE, alpha), outline=rgba(BRAND_BLUE, alpha), width=3)
        draw.ellipse((x - r - 14, y - r - 14, x + r + 14, y + r + 14), outline=rgba(BRAND_PURPLE, int(alpha * 0.55)), width=2)


def draw_scene_one(frame: Image.Image, t: float) -> Image.Image:
    draw = ImageDraw.Draw(frame, "RGBA")
    reveal = scene_progress(0.2, 1.2, t)
    reveal_2 = scene_progress(1.3, 2.3, t)

    panel = [82, 1190, 998, 1720]
    draw.rounded_rectangle(panel, radius=46, fill=rgba(BRAND_DEEP, 172), outline=rgba(BRAND_BLUE, 150), width=3)
    draw.rounded_rectangle([118, 1038, 660, 1146], radius=30, fill=rgba(BRAND_PINK, int(170 * reveal)))
    draw_ar_text(draw, (389, 1092), "زيادة سيستم", AR_BODY, rgba(WHITE, int(255 * reveal)))

    title_y = 1310 - (1 - reveal) * 48
    draw_ar_text(draw, (540, title_y), "في كل رسالة تتأخر", AR_H1, rgba(WHITE, int(255 * reveal)), stroke_width=2, stroke_fill=rgba(BRAND_DEEP, 190))
    draw_ar_text(draw, (540, 1442), "وفي كل فرصة ممكن تضيع", AR_H2, rgba("#dbeafe", int(238 * reveal_2)))

    lines = [
        "عميل ينتظر الرد",
        "فرصة تحتاج متابعة",
        "ضغط يومي على الفريق",
    ]
    y = 1558
    for idx, line in enumerate(lines):
        li = scene_progress(1.9 + idx * 0.22, 2.4 + idx * 0.22, t)
        draw.rounded_rectangle([200, y - 34, 880, y + 34], radius=22, fill=rgba(WHITE, int(34 * li)))
        draw.ellipse([160, y - 12, 184, y + 12], fill=rgba(BRAND_TEAL, int(255 * li)))
        draw_ar_text(draw, (548, y), line, AR_SMALL, rgba(WHITE, int(230 * li)))
        y += 82

    return frame


def draw_scene_two(frame: Image.Image, t: float) -> Image.Image:
    draw = ImageDraw.Draw(frame, "RGBA")
    draw_network(draw, t, 190)

    p1 = scene_progress(4.8, 5.8, t)
    p2 = scene_progress(5.8, 6.9, t)
    p3 = scene_progress(6.9, 8.0, t)

    draw_ar_text(draw, (540, 230), "هنا يجي دور زيادة سيستم", AR_H2, rgba(WHITE, int(255 * p1)))
    chips = [
        ("واتساب", 230, 1460, p1),
        ("الموقع", 540, 1460, p2),
        ("الإعلانات", 850, 1460, p3),
    ]
    for label, x, y, p in chips:
        draw.rounded_rectangle([x - 120, y - 48, x + 120, y + 48], radius=30, fill=rgba(BRAND_BLUE, int(160 * p)), outline=rgba(WHITE, int(200 * p)), width=2)
        draw_ar_text(draw, (x, y), label, AR_SMALL, rgba(WHITE, int(255 * p)))

    cards = [
        ([106, 1560, 470, 1730], "ربط القنوات", "كل الرسائل بمكان واحد", p1),
        ([540, 1560, 974, 1730], "متابعة العملاء", "بدون ما يضيع عليك أحد", p2),
        ([220, 1760, 860, 1886], "تنبيهات فورية", "وعي بالنظام في كل لحظة", p3),
    ]
    for box, title, body, p in cards:
        draw.rounded_rectangle(box, radius=36, fill=rgba(BRAND_DEEP, int(172 * p)), outline=rgba(BRAND_TEAL, int(210 * p)), width=3)
        cx = (box[0] + box[2]) // 2
        draw_ar_text(draw, (cx, box[1] + 44), title, AR_BODY, rgba(WHITE, int(255 * p)))
        draw_ar_text(draw, (cx, box[1] + 96), body, AR_SMALL, rgba("#dbeafe", int(230 * p)))

    return frame


def draw_scene_three(frame: Image.Image, t: float) -> Image.Image:
    draw = ImageDraw.Draw(frame, "RGBA")
    p = scene_progress(10.2, 11.4, t)
    p2 = scene_progress(11.0, 12.5, t)

    # Grid and glow for the end card.
    for x in range(0, WIDTH + 1, 80):
        draw.line((x, 0, x, HEIGHT), fill=rgba(WHITE, 18), width=1)
    for y in range(0, HEIGHT + 1, 80):
        draw.line((0, y, WIDTH, y), fill=rgba(WHITE, 18), width=1)

    for r in [220, 330, 460]:
        draw.ellipse((540 - r, 660 - r, 540 + r, 660 + r), outline=rgba(BRAND_PURPLE, 80), width=3)
    draw.ellipse((360, 480, 720, 840), fill=rgba(WHITE, 18), outline=rgba(BRAND_TEAL, 160), width=3)

    draw_ar_text(draw, (540, 1120), "زيادة سيستم", AR_H1, rgba(WHITE, int(255 * p)))
    draw_ar_text(draw, (540, 1242), "الوعي بالنظام في كل لحظة", AR_H2, rgba("#dbeafe", int(240 * p2)))
    draw_ar_text(draw, (540, 1374), "وضوح أكثر   •   متابعة أسرع   •   نمو أذكى", AR_SMALL, rgba("#cbd5e1", int(225 * p2)))

    cta_box = [244, 1540, 836, 1672]
    draw.rounded_rectangle(cta_box, radius=34, fill=rgba(BRAND_BLUE, int(188 * p2)), outline=rgba(WHITE, int(220 * p2)), width=3)
    draw_ar_text(draw, (540, 1606), "جاهزين نرتب لك التجربة؟", AR_BODY, rgba(WHITE, int(255 * p2)))

    footer = [154, 1748, 926, 1866]
    draw.rounded_rectangle(footer, radius=30, fill=rgba(BRAND_DEEP, int(168 * p2)))
    draw_ar_text(draw, (540, 1806), "زيادة سيستم للحلول الذكية والأتمتة", AR_SMALL, rgba("#dbeafe", int(220 * p2)))
    return frame


def render_frame(t: float, saudi_img: Image.Image, tech_img: Image.Image) -> np.ndarray:
    frame = make_scene_background(t, saudi_img, tech_img)
    frame = frame.convert("RGBA")

    if t < 4.8:
        frame = draw_scene_one(frame, t)
    elif t < 10.2:
        frame = draw_scene_two(frame, t)
    else:
        frame = draw_scene_three(frame, t)

    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette, "RGBA")
    vd.rectangle([0, 0, WIDTH, HEIGHT], outline=(0, 0, 0, 0), width=0)
    vignette = vignette.filter(ImageFilter.GaussianBlur(90))
    frame.alpha_composite(vignette)
    return np.asarray(frame.convert("RGB"))


def generate_voiceover() -> None:
    subprocess.run(
        [
            "say",
            "-v",
            "Majed",
            "-r",
            "320",
            VOICEOVER_TEXT,
            "-o",
            str(VOICEOVER_AIFF),
        ],
        check=True,
    )


def render_silent_video() -> None:
    saudi_img = prepare_cover_image(load_image(SOURCE_SAUDI), max_zoom=1.18)
    tech_img = prepare_cover_image(load_image(SOURCE_TECH), max_zoom=1.24)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen(
        [
            ffmpeg,
            "-y",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{WIDTH}x{HEIGHT}",
            "-r",
            str(FPS),
            "-i",
            "-",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(SILENT_VIDEO),
        ],
        stdin=subprocess.PIPE,
    )

    assert proc.stdin is not None
    try:
        for frame_idx in range(TOTAL_FRAMES):
            t = frame_idx / FPS
            proc.stdin.write(render_frame(t, saudi_img, tech_img).tobytes())
    finally:
        proc.stdin.close()
        return_code = proc.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, proc.args)


def mux_video() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(SILENT_VIDEO),
            "-i",
            str(VOICEOVER_AIFF),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(FINAL_VIDEO),
        ],
        check=True,
    )


def main() -> None:
    generate_voiceover()
    render_silent_video()
    mux_video()
    print(FINAL_VIDEO)


if __name__ == "__main__":
    main()
