#!/usr/bin/env python3
"""Generate a corporate open-source design kit inspired by Ziyada visual language.

Outputs separate reusable assets for designers:
- backgrounds (SVG + PNG)
- glass cards (SVG + PNG)
- frames (SVG + PNG)
- icons (SVG + PNG)
- minimal pattern pack (SVG + PNG)
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "corporate-design-kit"

BG = (15, 23, 42)
BLUE = (59, 130, 246)
PURPLE = (139, 92, 246)
CYAN = (6, 182, 212)
WHITE = (255, 255, 255)
SLATE = (148, 163, 184)


def ensure_dirs() -> None:
    for sub in [
        "backgrounds",
        "cards",
        "frames",
        "icons",
        "patterns-minimal",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def _rgba(c: Tuple[int, int, int], a: int) -> Tuple[int, int, int, int]:
    return (c[0], c[1], c[2], a)


def save_png_svg_pair(name: str, folder: str, png: Image.Image, svg: str) -> None:
    png.save(OUT / folder / f"{name}.png")
    (OUT / folder / f"{name}.svg").write_text(svg, encoding="utf-8")


def make_background(name: str, w: int, h: int, rings: int, stars: int) -> None:
    img = Image.new("RGBA", (w, h), BG + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # Soft radial glow layers.
    for r in range(0, max(w, h), max(40, max(w, h) // 16)):
        alpha = max(0, 70 - int(r * 0.06))
        draw.ellipse((w // 2 - r, h // 2 - r, w // 2 + r, h // 2 + r), outline=_rgba(BLUE, alpha), width=2)

    # Purple and cyan accent arcs.
    for i in range(rings):
        rr = int(min(w, h) * (0.18 + i * 0.07))
        box = (w // 2 - rr, h // 2 - rr, w // 2 + rr, h // 2 + rr)
        draw.arc(box, 20 + i * 11, 260 + i * 7, fill=_rgba(PURPLE, 60), width=2)
        draw.arc(box, 200 + i * 9, 330 + i * 6, fill=_rgba(CYAN, 48), width=1)

    # Star dots.
    step = max(13, int(math.sqrt((w * h) / max(stars, 1))))
    idx = 0
    for y in range(step // 2, h, step):
        for x in range(step // 2, w, step):
            if idx >= stars:
                break
            jitter_x = (idx * 17) % 9 - 4
            jitter_y = (idx * 29) % 11 - 5
            size = 1 + (idx % 2)
            draw.ellipse((x + jitter_x, y + jitter_y, x + jitter_x + size, y + jitter_y + size), fill=_rgba(BLUE, 120))
            idx += 1
        if idx >= stars:
            break

    # Gentle blur for glow cohesion.
    img = img.filter(ImageFilter.GaussianBlur(radius=0.35))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <radialGradient id="g" cx="50%" cy="50%" r="70%">
      <stop offset="0%" stop-color="#1e3a8a" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#0f172a" stop-opacity="1"/>
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="#0f172a"/>
  <rect width="100%" height="100%" fill="url(#g)"/>
  <circle cx="{w//2}" cy="{h//2}" r="{min(w,h)//3}" fill="none" stroke="#8b5cf6" stroke-opacity="0.25" stroke-width="2"/>
  <circle cx="{w//2}" cy="{h//2}" r="{min(w,h)//2 - 20}" fill="none" stroke="#3b82f6" stroke-opacity="0.18" stroke-width="2"/>
  <circle cx="{w//2}" cy="{h//2}" r="{min(w,h)//2 - 80}" fill="none" stroke="#06b6d4" stroke-opacity="0.20" stroke-width="1"/>
</svg>'''

    save_png_svg_pair(name, "backgrounds", img, svg)


def make_glass_card(name: str, w: int, h: int, radius: int, border_alpha: int, fill_alpha: int) -> None:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # Outer glow.
    draw.rounded_rectangle((4, 4, w - 4, h - 4), radius=radius + 2, fill=_rgba(BLUE, 20))

    # Glass body.
    draw.rounded_rectangle((8, 8, w - 8, h - 8), radius=radius, fill=(255, 255, 255, fill_alpha), outline=(255, 255, 255, border_alpha), width=2)

    # Top highlight strip.
    draw.rounded_rectangle((14, 14, w - 14, int(h * 0.32)), radius=max(8, radius // 2), fill=(255, 255, 255, 34))

    # Accent corner.
    draw.arc((w - 160, h - 160, w - 20, h - 20), 210, 335, fill=_rgba(PURPLE, 140), width=3)
    draw.arc((20, 20, 180, 180), 20, 120, fill=_rgba(CYAN, 120), width=2)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect x="8" y="8" width="{w-16}" height="{h-16}" rx="{radius}" fill="#ffffff" fill-opacity="{fill_alpha/255:.3f}" stroke="#ffffff" stroke-opacity="{border_alpha/255:.3f}" stroke-width="2"/>
  <rect x="14" y="14" width="{w-28}" height="{int(h*0.3)}" rx="{max(8, radius//2)}" fill="#ffffff" fill-opacity="0.14"/>
  <path d="M {w-150} {h-80} A 90 90 0 0 0 {w-40} {h-35}" fill="none" stroke="#8b5cf6" stroke-opacity="0.55" stroke-width="3"/>
  <path d="M 40 80 A 75 75 0 0 1 140 35" fill="none" stroke="#06b6d4" stroke-opacity="0.45" stroke-width="2"/>
</svg>'''

    save_png_svg_pair(name, "cards", img, svg)


def make_frame(name: str, w: int, h: int, radius: int) -> None:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rounded_rectangle((6, 6, w - 6, h - 6), radius=radius, outline=_rgba(WHITE, 180), width=3)
    draw.rounded_rectangle((18, 18, w - 18, h - 18), radius=max(8, radius - 10), outline=_rgba(BLUE, 130), width=1)

    # Top title bar hint.
    draw.rounded_rectangle((24, 24, int(w * 0.6), 58), radius=12, fill=_rgba(WHITE, 42))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect x="6" y="6" width="{w-12}" height="{h-12}" rx="{radius}" fill="none" stroke="#ffffff" stroke-opacity="0.72" stroke-width="3"/>
  <rect x="18" y="18" width="{w-36}" height="{h-36}" rx="{max(8, radius-10)}" fill="none" stroke="#3b82f6" stroke-opacity="0.52" stroke-width="1"/>
  <rect x="24" y="24" width="{int(w*0.6)-24}" height="34" rx="12" fill="#ffffff" fill-opacity="0.16"/>
</svg>'''

    save_png_svg_pair(name, "frames", img, svg)


def draw_icon_lines(draw: ImageDraw.ImageDraw, kind: str, size: int) -> None:
    c = _rgba(WHITE, 220)
    b = _rgba(BLUE, 190)
    p = _rgba(PURPLE, 170)
    cx, cy = size // 2, size // 2

    if kind == "strategy":
        draw.rectangle((18, size - 40, size - 18, size - 18), outline=c, width=3)
        draw.line((30, size - 55, 58, size - 78, 88, size - 60, size - 25, 34), fill=b, width=4)
    elif kind == "growth":
        draw.line((22, size - 22, size - 22, 22), fill=c, width=3)
        draw.polygon([(size - 22, 22), (size - 36, 36), (size - 40, 18)], fill=c)
        draw.line((26, size - 28, size - 54, 30), fill=b, width=4)
    elif kind == "automation":
        draw.ellipse((18, 18, size - 18, size - 18), outline=c, width=3)
        for a in [0, 60, 120, 180, 240, 300]:
            x = cx + int(math.cos(math.radians(a)) * 28)
            y = cy + int(math.sin(math.radians(a)) * 28)
            draw.line((cx, cy, x, y), fill=b, width=3)
        draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=p)
    elif kind == "analytics":
        draw.rectangle((18, 18, size - 18, size - 18), outline=c, width=3)
        draw.rectangle((30, size - 42, 44, size - 22), fill=b)
        draw.rectangle((52, size - 58, 66, size - 22), fill=b)
        draw.rectangle((74, size - 72, 88, size - 22), fill=b)
    elif kind == "partnership":
        draw.rounded_rectangle((16, 32, 54, 76), radius=14, outline=c, width=3)
        draw.rounded_rectangle((58, 32, 96, 76), radius=14, outline=c, width=3)
        draw.line((54, 54, 58, 54), fill=b, width=4)
    elif kind == "security":
        draw.polygon([(cx, 14), (size - 24, 26), (size - 24, 62), (cx, size - 16), (24, 62), (24, 26)], outline=c, width=3)
        draw.line((cx - 10, 58, cx - 2, 66, cx + 14, 46), fill=b, width=4)
    else:
        draw.ellipse((18, 18, size - 18, size - 18), outline=c, width=3)


def make_icon(kind: str, size: int = 112) -> None:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # Soft glass disc base.
    draw.ellipse((4, 4, size - 4, size - 4), fill=_rgba(WHITE, 26), outline=_rgba(WHITE, 90), width=2)
    draw_icon_lines(draw, kind, size)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <circle cx="{size/2}" cy="{size/2}" r="{size/2 - 4}" fill="#ffffff" fill-opacity="0.10" stroke="#ffffff" stroke-opacity="0.35" stroke-width="2"/>
  <text x="50%" y="54%" text-anchor="middle" fill="#ffffff" fill-opacity="0.9" font-size="13" font-family="Arial">{kind[:2].upper()}</text>
</svg>'''

    save_png_svg_pair(f"icon-{kind}", "icons", img, svg)


def minimal_pattern(name: str, w: int, h: int, spacing: int) -> None:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(-spacing, h + spacing, spacing):
        for x in range(-spacing, w + spacing, spacing):
            r = spacing // 3
            # outer ring light
            draw.ellipse((x - r, y - r, x + r, y + r), outline=_rgba(PURPLE, 44), width=1)
            # inner core light
            draw.ellipse((x - r // 2, y - r // 2, x + r // 2, y + r // 2), outline=_rgba(BLUE, 52), width=1)

    svg_lines: List[str] = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    for y in range(-spacing, h + spacing, spacing):
        for x in range(-spacing, w + spacing, spacing):
            r = spacing // 3
            svg_lines.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#8b5cf6" stroke-opacity="0.18" stroke-width="1"/>')
            svg_lines.append(f'<circle cx="{x}" cy="{y}" r="{r//2}" fill="none" stroke="#3b82f6" stroke-opacity="0.22" stroke-width="1"/>')
    svg_lines.append("</svg>")

    save_png_svg_pair(name, "patterns-minimal", img, "\n".join(svg_lines))


def write_docs() -> None:
    readme = OUT / "README.md"
    readme.write_text(
        """# Corporate Design Kit (Open Source)

This package is designed for B2B/corporate usage inspired by Ziyada visual direction.

## Included

- backgrounds/: atmospheric corporate backgrounds (SVG + PNG)
- cards/: glass card components (SVG + PNG)
- frames/: presentation and media frames (SVG + PNG)
- icons/: reusable icon badges (SVG + PNG)
- patterns-minimal/: lighter/minimal repeating patterns (SVG + PNG)

## License

- CC0 1.0 (public domain dedication)
- Designers can use, edit, and distribute freely.

## Recommended use

- Use backgrounds as base layers.
- Stack frames/cards above backgrounds.
- Use icons for feature bullets and service tiles.
- Use patterns-minimal for stationery and social post textures.
""",
        encoding="utf-8",
    )

    (OUT / "LICENSE-CC0.txt").write_text(
        """CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

The assets in this folder are released under CC0 1.0.
You can copy, modify, distribute, and use them for any purpose,
including commercial use, without asking permission.

No warranties are provided.

Reference: https://creativecommons.org/publicdomain/zero/1.0/
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()

    make_background("bg-corporate-hero", 1920, 1080, rings=8, stars=360)
    make_background("bg-corporate-square", 2000, 2000, rings=10, stars=420)
    make_background("bg-corporate-story", 1080, 1920, rings=9, stars=340)

    make_glass_card("glass-card-wide", 1200, 680, radius=34, border_alpha=150, fill_alpha=42)
    make_glass_card("glass-card-compact", 780, 520, radius=28, border_alpha=130, fill_alpha=34)
    make_glass_card("glass-chip", 520, 160, radius=30, border_alpha=165, fill_alpha=58)

    make_frame("frame-presentation-16x9", 1600, 900, radius=34)
    make_frame("frame-social-square", 1200, 1200, radius=38)
    make_frame("frame-story-9x16", 1080, 1920, radius=42)

    for kind in ["strategy", "growth", "automation", "analytics", "partnership", "security"]:
        make_icon(kind)

    minimal_pattern("pattern-minimal-square", 2000, 2000, spacing=300)
    minimal_pattern("pattern-minimal-16x9", 1920, 1080, spacing=260)
    minimal_pattern("pattern-minimal-9x16", 1080, 1920, spacing=240)

    write_docs()
    print(f"Corporate design kit generated at: {OUT}")


if __name__ == "__main__":
    main()
