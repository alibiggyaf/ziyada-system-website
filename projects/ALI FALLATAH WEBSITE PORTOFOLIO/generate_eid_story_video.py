from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import arabic_reshaper
import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont, features


WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION_SECONDS = 9
TOTAL_FRAMES = FPS * DURATION_SECONDS
SAMPLE_RATE = 44100

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "Ali website  2026"
BG_IMAGE_PATH = ASSETS_DIR / "Ali Story size1.png"
LOGO_IMAGE_PATH = ASSETS_DIR / "Ali Logos trans-03.png"

IS_RAQM_AVAILABLE = features.check("raqm")


def shape_ar_legacy(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def ar_text_for_draw(text: str) -> str:
    return text if IS_RAQM_AVAILABLE else shape_ar_legacy(text)


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
    draw.text(xy, ar_text_for_draw(text), **kwargs)


def find_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


AR_FONT_H1 = find_font([
    "/System/Library/Fonts/SFArabicRounded.ttf",
    "/System/Library/Fonts/GeezaPro.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
], 120)
AR_FONT_H2 = find_font([
    "/System/Library/Fonts/SFArabicRounded.ttf",
    "/System/Library/Fonts/SFArabic.ttf",
    "/System/Library/Fonts/GeezaPro.ttc",
], 72)
AR_FONT_BODY = find_font([
    "/System/Library/Fonts/SFArabic.ttf",
    "/System/Library/Fonts/GeezaPro.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
], 48)
AR_FONT_BRAND = find_font([
    "/System/Library/Fonts/SFArabicRounded.ttf",
    "/System/Library/Fonts/GeezaPro.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
], 62)
EN_FONT = find_font([
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
], 40)


def eased(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


def pulse(t: float, speed: float, phase: float = 0.0) -> float:
    return 0.5 + 0.5 * math.sin((t * speed + phase) * math.tau)


def load_story_background() -> Image.Image:
    if not BG_IMAGE_PATH.exists():
        raise FileNotFoundError(f"Missing background image: {BG_IMAGE_PATH}")
    bg = Image.open(BG_IMAGE_PATH).convert("RGB")
    return bg


def get_background_frame(bg_src: Image.Image, t: float) -> Image.Image:
    # Gentle zoom + drift for premium motion while preserving the exact supplied artwork.
    scale = 1.0 + 0.024 * eased(t / DURATION_SECONDS)
    sw = int(bg_src.width * scale)
    sh = int(bg_src.height * scale)
    scaled = bg_src.resize((sw, sh), Image.Resampling.LANCZOS)

    drift_x = int(12 * math.sin(t * 0.42))
    drift_y = int(20 * math.sin(t * 0.33 + 0.8))

    left = max(0, (sw - WIDTH) // 2 + drift_x)
    top = max(0, (sh - HEIGHT) // 2 + drift_y)
    right = min(sw, left + WIDTH)
    bottom = min(sh, top + HEIGHT)

    frame = scaled.crop((left, top, right, bottom))
    if frame.size != (WIDTH, HEIGHT):
        frame = frame.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    return frame


def draw_celebration_overlay(frame: Image.Image, t: float) -> Image.Image:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")

    # Moving star flares and celebration particles.
    for i in range(30):
        sx = int(40 + (i * 93) % 980)
        sy = int(120 + (i * 157) % 1660)
        p = pulse(t, speed=0.28 + (i % 5) * 0.12, phase=i * 0.24)
        alpha = int(60 + 170 * p)
        size = int(4 + 9 * p)
        d.line([(sx - size, sy), (sx + size, sy)], fill=(213, 125, 255, alpha), width=2)
        d.line([(sx, sy - size), (sx, sy + size)], fill=(213, 125, 255, alpha), width=2)

    for i in range(80):
        x = int((i * 38 + t * (85 + (i % 3) * 20)) % WIDTH)
        y = int((i * 123 + t * (130 + (i % 4) * 26)) % (HEIGHT + 180)) - 100
        rad = 2 + (i % 4)
        p = pulse(t, speed=0.5 + (i % 6) * 0.16, phase=i * 0.11)
        if i % 3 == 0:
            color = (247, 206, 98, int(90 + 110 * p))
        elif i % 3 == 1:
            color = (178, 108, 255, int(90 + 100 * p))
        else:
            color = (255, 255, 255, int(70 + 90 * p))
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=color)

    glow = overlay.filter(ImageFilter.GaussianBlur(radius=5.5))
    frame.paste(glow, (0, 0), glow)
    frame.paste(overlay, (0, 0), overlay)
    return frame


def draw_logo(frame: Image.Image, t: float) -> Image.Image:
    if not LOGO_IMAGE_PATH.exists():
        return frame

    logo = Image.open(LOGO_IMAGE_PATH).convert("RGBA")
    target_w = 160
    ratio = target_w / logo.width
    target_h = max(40, int(logo.height * ratio))
    logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Subtle breathing glow around logo mark.
    alpha_mul = 0.78 + 0.22 * pulse(t, speed=0.7, phase=0.4)
    a = logo.split()[-1].point(lambda px: int(px * alpha_mul))
    logo.putalpha(a)

    x = WIDTH - target_w - 42
    y = 56
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse([x - 36, y - 18, x + target_w + 36, y + target_h + 24], fill=(112, 0, 255, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=14))
    frame.paste(glow, (0, 0), glow)
    frame.paste(logo, (x, y), logo)
    return frame


def draw_text_block(frame: Image.Image, t: float) -> Image.Image:
    d = ImageDraw.Draw(frame, "RGBA")

    reveal_1 = eased((t - 0.5) / 1.0)
    reveal_2 = eased((t - 1.1) / 0.95)
    reveal_3 = eased((t - 1.8) / 0.95)
    reveal_4 = eased((t - 2.5) / 0.9)

    y1 = int(780 - (1 - reveal_1) * 52)
    y2 = int(915 - (1 - reveal_2) * 44)
    y3 = int(1032 - (1 - reveal_3) * 38)

    a1 = int(255 * reveal_1)
    a2 = int(240 * reveal_2)
    a3 = int(235 * reveal_3)
    a4 = int(255 * reveal_4)

    draw_ar_text(
        d,
        (WIDTH // 2, y1),
        "عيد فطر مبارك",
        AR_FONT_H1,
        (255, 255, 255, a1),
        stroke_width=2,
        stroke_fill=(85, 45, 178, min(220, a1)),
    )
    draw_ar_text(
        d,
        (WIDTH // 2, y2),
        "كل عام وأنتم بخير",
        AR_FONT_H2,
        (243, 233, 255, a2),
    )
    draw_ar_text(
        d,
        (WIDTH // 2, y3),
        "نسأل الله لكم السعادة والطمأنينة",
        AR_FONT_BODY,
        (255, 255, 255, a3),
    )
    draw_ar_text(
        d,
        (WIDTH // 2, y3 + 62),
        "وتقبل الله طاعاتكم",
        AR_FONT_BODY,
        (247, 206, 98, a3),
    )

    chip = [250, 1560, 830, 1712]
    d.rounded_rectangle(chip, radius=30, fill=(8, 4, 28, int(155 * reveal_4)), outline=(112, 0, 255, int(225 * reveal_4)), width=3)
    draw_ar_text(d, (WIDTH // 2, 1615), "علي فلاتة", AR_FONT_BRAND, (255, 255, 255, a4))
    d.text((360, 1676), "ALI FALLATAH", font=EN_FONT, fill=(184, 128, 255, a4))

    return frame


def render_silent_video(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bg_src = load_story_background()

    writer = imageio.get_writer(
        path.as_posix(),
        fps=FPS,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
        macro_block_size=1,
    )

    for idx in range(TOTAL_FRAMES):
        t = idx / FPS
        frame = get_background_frame(bg_src, t)
        frame = draw_celebration_overlay(frame, t)
        frame = draw_text_block(frame, t)
        frame = draw_logo(frame, t)

        if t > DURATION_SECONDS - 1.0:
            frame = frame.filter(ImageFilter.GaussianBlur(radius=0.15))

        writer.append_data(np.asarray(frame.convert("RGB"), dtype=np.uint8))

    writer.close()


def synthesize_trendy_eid_audio(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    total = int(SAMPLE_RATE * DURATION_SECONDS)
    t = np.linspace(0.0, DURATION_SECONDS, total, endpoint=False)

    # Warm uplifting pad.
    pad = 0.22 * np.sin(2 * np.pi * 146.83 * t)
    pad += 0.16 * np.sin(2 * np.pi * 220.00 * t)
    pad += 0.10 * np.sin(2 * np.pi * 293.66 * t)

    # Bright celebratory motif.
    motif = np.zeros_like(t)
    note_times = [0.4, 1.0, 1.6, 2.2, 2.8, 3.4, 4.1, 4.8, 5.5, 6.2, 6.9, 7.6]
    note_freqs = [392.00, 440.00, 493.88, 523.25, 493.88, 440.00, 392.00, 440.00, 493.88, 523.25, 587.33, 659.26]
    for nt, f in zip(note_times, note_freqs):
        env = np.exp(-6.0 * np.maximum(0.0, t - nt))
        gate = (t >= nt).astype(np.float32)
        motif += 0.24 * gate * env * np.sin(2 * np.pi * f * t)

    # Khaleeji-inspired percussion pulse.
    rhythm = np.zeros_like(t)
    bpm = 112
    beat_interval = 60.0 / bpm
    for b in np.arange(0.0, DURATION_SECONDS, beat_interval):
        i0 = int(b * SAMPLE_RATE)
        burst_len = int(0.09 * SAMPLE_RATE)
        if i0 + burst_len < len(rhythm):
            env = np.linspace(1.0, 0.0, burst_len)
            low = np.sin(2 * np.pi * 84 * np.arange(burst_len) / SAMPLE_RATE)
            click = np.sin(2 * np.pi * 1800 * np.arange(burst_len) / SAMPLE_RATE)
            rhythm[i0:i0 + burst_len] += 0.32 * env * low + 0.07 * env * click

    # Intro and transition whoosh impacts.
    fx = np.zeros_like(t)
    for s in [0.6, 1.3, 2.1, 2.9]:
        i0 = int(s * SAMPLE_RATE)
        length = int(0.25 * SAMPLE_RATE)
        if i0 + length < len(fx):
            env = np.linspace(1.0, 0.0, length)
            noise = np.random.uniform(-1.0, 1.0, length)
            fx[i0:i0 + length] += 0.05 * env * noise

    audio = pad + motif + rhythm + fx

    fade = int(0.35 * SAMPLE_RATE)
    audio[:fade] *= np.linspace(0.0, 1.0, fade)
    audio[-fade:] *= np.linspace(1.0, 0.0, fade)

    audio /= max(1e-6, float(np.max(np.abs(audio))))
    mono = (audio * 0.95 * 32767).astype(np.int16)

    # Slight stereo widening.
    shift = int(0.008 * SAMPLE_RATE)
    left = mono
    right = np.roll(mono, shift)
    stereo = np.stack([left, right], axis=1)

    with wave.open(path.as_posix(), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(stereo.tobytes())


def mux_video_with_audio(video_path: Path, audio_path: Path, out_path: Path) -> None:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        video_path.as_posix(),
        "-i",
        audio_path.as_posix(),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "224k",
        "-shortest",
        out_path.as_posix(),
    ]
    subprocess.run(cmd, check=True)


def write_generation_prompts(prompt_file: Path) -> None:
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    text = """Veo/Sora Prompt (Ali Fallatah Eid Story - Saudi celebratory):
Create a premium Instagram Story video (9:16, 1080x1920, 9 seconds) using Ali Fallatah's exact story-style visual identity.

Background:
- Use the provided purple Eid ornamental background as the exact base layer.
- Keep luminous festive details and subtle parallax movement.
- Add celebratory sparkles and premium motion graphics.

Text:
1) عيد فطر مبارك
2) كل عام وأنتم بخير
3) نسأل الله لكم السعادة والطمأنينة
4) وتقبل الله طاعاتكم
5) علي فلاتة
6) ALI FALLATAH

Audio:
- Trendy joyful Saudi Eid mood: warm synth, festive percussion, clear cinematic mix.

Animation:
- Smooth text reveal + final hold for screenshot.
"""
    prompt_file.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    outputs = ROOT / "outputs"

    silent_video = outputs / "eid_story_af_celebration_1080x1920_silent.mp4"
    audio_track = outputs / "eid_story_af_celebration_audio.wav"
    final_video = outputs / "eid_story_af_celebration_1080x1920_with_audio.mp4"
    prompt_out = outputs / "eid_story_veo_sora_prompt.txt"

    render_silent_video(silent_video)
    synthesize_trendy_eid_audio(audio_track)
    mux_video_with_audio(silent_video, audio_track, final_video)
    write_generation_prompts(prompt_out)

    print(f"Created: {silent_video}")
    print(f"Created: {audio_track}")
    print(f"Created: {final_video}")
    print(f"Created: {prompt_out}")
