#!/usr/bin/env python3
"""
DJ BIGGY - YouTube Thumbnail Generator
Creates a professional 1280x720 thumbnail optimized for YouTube.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# YouTube recommended thumbnail size
W, H = 1280, 720

img = Image.new("RGB", (W, H), "#000000")
draw = ImageDraw.Draw(img)

# ── BACKGROUND: Dark gradient with cyan/blue energy ──

# Create layered radial gradient effect
for y in range(H):
    for x in range(W):
        # Distance from center-right (where the DJ would be)
        cx, cy = W * 0.65, H * 0.45
        dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        max_dist = math.sqrt(W ** 2 + H ** 2) * 0.5

        # Normalized distance
        t = min(dist / max_dist, 1.0)

        # Dark base with cyan-blue glow from center
        r = int(0 * (1 - t) + 5 * t)
        g = int(30 * (1 - t ** 0.7) + 2 * t)
        b = int(60 * (1 - t ** 0.5) + 10 * t)

        img.putpixel((x, y), (r, g, b))

# ── GEOMETRIC ACCENT LINES (energy/motion feel) ──

draw = ImageDraw.Draw(img)

# Cyan accent streaks
for i in range(15):
    angle = i * 24
    length = 200 + i * 40
    cx, cy = W * 0.65, H * 0.45
    rad = math.radians(angle)
    x1 = cx + math.cos(rad) * 80
    y1 = cy + math.sin(rad) * 80
    x2 = cx + math.cos(rad) * length
    y2 = cy + math.sin(rad) * length
    alpha = max(10, 40 - i * 2)
    draw.line([(x1, y1), (x2, y2)], fill=(0, 209, 255, alpha), width=1)

# Bright cyan circle (DJ booth light effect)
for radius in range(180, 60, -2):
    alpha = max(0, int(25 * (1 - radius / 180)))
    draw.ellipse(
        [W * 0.65 - radius, H * 0.45 - radius,
         W * 0.65 + radius, H * 0.45 + radius],
        outline=(0, 180 + alpha * 2, 255),
        width=1
    )

# ── BOTTOM GRADIENT BAR ──
for y in range(H - 120, H):
    t = (y - (H - 120)) / 120
    r = int(0 * (1 - t) + 0 * t)
    g = int(15 * (1 - t) + 0 * t)
    b = int(40 * (1 - t) + 0 * t)
    a = int(200 * t)
    for x in range(W):
        bg = img.getpixel((x, y))
        blended = (
            int(bg[0] * (1 - t * 0.7) + 0),
            int(bg[1] * (1 - t * 0.7) + 0),
            int(bg[2] * (1 - t * 0.7) + 0),
        )
        img.putpixel((x, y), blended)

# ── EQUALIZER BARS (bottom center) ──
bar_heights = [35, 55, 70, 85, 95, 100, 90, 80, 95, 100, 85, 70, 55, 40, 60, 75, 90, 80, 65, 45]
bar_width = 8
bar_gap = 4
total_bars_width = len(bar_heights) * (bar_width + bar_gap)
bar_start_x = (W - total_bars_width) // 2

for i, h in enumerate(bar_heights):
    x = bar_start_x + i * (bar_width + bar_gap)
    y_top = H - 30 - h
    y_bot = H - 30

    # Gradient bar: cyan to blue
    for y in range(y_top, y_bot):
        t = (y - y_top) / max(1, (y_bot - y_top))
        r_c = int(0 * (1 - t) + 0 * t)
        g_c = int(209 * (1 - t) + 100 * t)
        b_c = int(255 * (1 - t) + 255 * t)
        draw.rectangle([x, y, x + bar_width, y + 1], fill=(r_c, g_c, b_c))

# ── TEXT ──

# Try to find a bold font
font_paths = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/SFCompact.ttf",
]

title_font = None
sub_font = None
tag_font = None

for fp in font_paths:
    if os.path.exists(fp):
        try:
            title_font = ImageFont.truetype(fp, 130)
            sub_font = ImageFont.truetype(fp, 42)
            tag_font = ImageFont.truetype(fp, 28)
            break
        except Exception:
            continue

if title_font is None:
    title_font = ImageFont.load_default()
    sub_font = ImageFont.load_default()
    tag_font = ImageFont.load_default()

# "DJ" text - white with cyan shadow
dj_text = "DJ"
# Shadow
draw.text((82, 82), dj_text, font=title_font, fill=(0, 100, 150))
# Main
draw.text((80, 80), dj_text, font=title_font, fill=(255, 255, 255))

# "BIGGY" text - cyan, bold
biggy_text = "BIGGY"
# Shadow
draw.text((82, 202), biggy_text, font=title_font, fill=(0, 80, 120))
# Main - bright cyan
draw.text((80, 200), biggy_text, font=title_font, fill=(0, 209, 255))

# Cyan accent line under the name
bbox_biggy = draw.textbbox((80, 200), biggy_text, font=title_font)
line_y = bbox_biggy[3] + 15
draw.rectangle([80, line_y, bbox_biggy[2], line_y + 4], fill=(0, 209, 255))

# "THE OFFICIAL MIX" subtitle
sub_text = "THE OFFICIAL MIX"
draw.text((85, line_y + 25), sub_text, font=sub_font, fill=(200, 200, 200))

# "BOOK NOW" call-to-action badge (bottom-right)
cta_text = "BOOK NOW"
cta_bbox = draw.textbbox((0, 0), cta_text, font=sub_font)
cta_w = cta_bbox[2] - cta_bbox[0] + 40
cta_h = cta_bbox[3] - cta_bbox[1] + 20
cta_x = W - cta_w - 60
cta_y = H - cta_h - 50

# CTA background - cyan rounded rect
draw.rounded_rectangle(
    [cta_x, cta_y, cta_x + cta_w, cta_y + cta_h],
    radius=12,
    fill=(0, 209, 255)
)
# CTA text - dark
draw.text(
    (cta_x + 20, cta_y + 5),
    cta_text,
    font=sub_font,
    fill=(0, 0, 0)
)

# "🎧 Saudi Arabia" location tag (bottom-left)
loc_text = "SAUDI ARABIA"
draw.text((85, H - 55), loc_text, font=tag_font, fill=(150, 150, 150))

# ── HEADPHONE ICON (simple geometric) ──
# Small headphone shape near top-right
hx, hy = W - 150, 60
# Arc
draw.arc([hx - 30, hy - 20, hx + 30, hy + 20], 180, 360, fill=(0, 209, 255), width=4)
# Ear cups
draw.rounded_rectangle([hx - 35, hy, hx - 22, hy + 25], radius=3, fill=(0, 209, 255))
draw.rounded_rectangle([hx + 22, hy, hx + 35, hy + 25], radius=3, fill=(0, 209, 255))

# ── SAVE ──
output_path = "/Users/djbiggy/Downloads/Claude Code- File Agents/DJ_BIGGY_YouTube_Thumbnail.png"
img.save(output_path, "PNG", quality=100)
print(f"✅ Thumbnail saved: {output_path}")
print(f"   Size: {W}x{H}px (YouTube recommended)")
print(f"   Format: PNG")
