#!/usr/bin/env python3
"""
DJ BIGGY - Premium YouTube Thumbnail v2
Composites real photo + logo with pro effects.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import math
import os

W, H = 1280, 720

# ── PATHS ──
PHOTO_PATH = "/Users/djbiggy/Downloads/Copy of _61A0193.JPG"  # Jacket pull pose
LIVE_PATH = "/Users/djbiggy/Downloads/_MGL0369.JPG"           # Live DJ shot
LOGO_PATH = "/Users/djbiggy/Downloads/Dj biggy logo .JPG"
OUTPUT = "/Users/djbiggy/Downloads/Claude Code- File Agents/DJ_BIGGY_Thumbnail_V2.png"

# ── LOAD & PREP MAIN PHOTO ──
photo = Image.open(PHOTO_PATH)
# Crop to focus on upper body - the powerful pose
pw, ph = photo.size
# Crop from center-top area (head + jacket)
crop_top = int(ph * 0.02)
crop_bottom = int(ph * 0.85)
crop_left = int(pw * 0.15)
crop_right = int(pw * 0.85)
photo = photo.crop((crop_left, crop_top, crop_right, crop_bottom))

# Resize to fill right 60% of thumbnail
target_h = H
aspect = photo.size[0] / photo.size[1]
target_w = int(target_h * aspect)
photo = photo.resize((target_w, target_h), Image.LANCZOS)

# ── COLOR GRADE THE PHOTO (cinematic cyan/blue tint) ──
# Split channels
r, g, b = photo.split()

# Boost blues, slightly suppress reds, keep greens
from PIL import ImageOps
import numpy as np

# Convert to numpy for precise color grading
photo_arr = np.array(photo, dtype=np.float64)

# Cinematic blue/cyan color grade
# Shadows: push towards deep blue
# Midtones: cyan tint
# Highlights: keep white/cool
shadow_mask = (photo_arr.mean(axis=2, keepdims=True) < 80).astype(float)
mid_mask = ((photo_arr.mean(axis=2, keepdims=True) >= 80) &
            (photo_arr.mean(axis=2, keepdims=True) < 180)).astype(float)
highlight_mask = (photo_arr.mean(axis=2, keepdims=True) >= 180).astype(float)

# Red channel: reduce in shadows, slight reduce in mids
photo_arr[:,:,0] = photo_arr[:,:,0] * (1 - shadow_mask[:,:,0] * 0.3) * (1 - mid_mask[:,:,0] * 0.1)
# Green channel: slight boost in mids for cyan
photo_arr[:,:,1] = photo_arr[:,:,1] * (1 + mid_mask[:,:,0] * 0.05)
# Blue channel: boost everywhere
photo_arr[:,:,2] = np.clip(photo_arr[:,:,2] * 1.15 + shadow_mask[:,:,0] * 25, 0, 255)

# Increase contrast
mean = photo_arr.mean()
photo_arr = np.clip((photo_arr - mean) * 1.2 + mean, 0, 255)

photo_graded = Image.fromarray(photo_arr.astype(np.uint8))

# Enhance sharpness
enhancer = ImageEnhance.Sharpness(photo_graded)
photo_graded = enhancer.enhance(1.3)

# Enhance contrast a touch more
enhancer = ImageEnhance.Contrast(photo_graded)
photo_graded = enhancer.enhance(1.15)

# ── CREATE BASE CANVAS ──
canvas = Image.new("RGB", (W, H), (5, 5, 15))
draw = ImageDraw.Draw(canvas)

# ── DARK GRADIENT BACKGROUND ──
bg_arr = np.zeros((H, W, 3), dtype=np.uint8)
for y in range(H):
    for x in range(W):
        # Dark base with subtle blue gradient
        t_x = x / W
        t_y = y / H
        r_v = int(5 + t_x * 3)
        g_v = int(5 + 8 * (1 - t_y))
        b_v = int(15 + 25 * (1 - t_y) * (1 - t_x * 0.5))
        bg_arr[y, x] = (r_v, g_v, b_v)

canvas = Image.fromarray(bg_arr)

# ── PLACE PHOTO ON RIGHT SIDE ──
# Position photo on right, letting it bleed slightly
photo_x = W - target_w + int(target_w * 0.12)
photo_y = 0
canvas.paste(photo_graded, (photo_x, photo_y))

# ── CREATE LEFT FADE (photo fades into dark background) ──
fade_width = 350
canvas_arr = np.array(canvas, dtype=np.float64)
bg_arr_f = np.array(Image.fromarray(bg_arr), dtype=np.float64)

for x_offset in range(fade_width):
    x = photo_x + x_offset
    if x < 0 or x >= W:
        continue
    t = x_offset / fade_width  # 0 = left edge (full bg), 1 = right (full photo)
    # Smooth ease-in curve
    t = t * t * (3 - 2 * t)  # smoothstep
    for y in range(H):
        canvas_arr[y, x] = bg_arr_f[y, x] * (1 - t) + canvas_arr[y, x] * t

canvas = Image.fromarray(np.clip(canvas_arr, 0, 255).astype(np.uint8))

# ── CYAN GLOW EFFECT behind the person ──
glow = Image.new("RGB", (W, H), (0, 0, 0))
glow_draw = ImageDraw.Draw(glow)

# Big soft cyan glow behind subject
cx, cy = W - int(target_w * 0.35), int(H * 0.35)
for radius in range(400, 0, -3):
    intensity = int(35 * (1 - radius / 400) ** 1.5)
    glow_draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(0, intensity, int(intensity * 1.3))
    )

# Blend glow with canvas using screen mode
canvas_arr = np.array(canvas, dtype=np.float64)
glow_arr = np.array(glow, dtype=np.float64)
# Screen blend: 1 - (1-a)(1-b)
blended = 255 - (255 - canvas_arr) * (255 - glow_arr) / 255
canvas = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8))

# ── VIGNETTE EFFECT ──
vignette = Image.new("L", (W, H), 255)
vig_draw = ImageDraw.Draw(vignette)
for i in range(100):
    opacity = int(255 * (1 - i / 100) * 0.6)
    vig_draw.rectangle(
        [i, i, W - i, H - i],
        outline=opacity
    )
# Apply stronger vignette at edges
vig_arr = np.array(vignette, dtype=np.float64) / 255
canvas_arr = np.array(canvas, dtype=np.float64)
for c in range(3):
    canvas_arr[:,:,c] *= vig_arr
canvas = Image.fromarray(np.clip(canvas_arr, 0, 255).astype(np.uint8))

# ── ADD LOGO (top-left corner) ──
logo = Image.open(LOGO_PATH)
# The logo is black on white - invert it to white on transparent feel
logo_arr = np.array(logo, dtype=np.float64)
# Make it white-on-black (invert)
logo_inv = 255 - logo_arr
logo_inv = Image.fromarray(logo_inv.astype(np.uint8))

# Resize logo
logo_size = 110
logo_inv = logo_inv.resize((logo_size, logo_size), Image.LANCZOS)

# Create mask from logo (white parts become visible)
logo_gray = logo_inv.convert("L")
logo_mask = logo_gray.point(lambda x: min(x * 2, 255))

# Tint logo cyan
logo_cyan = Image.new("RGB", (logo_size, logo_size), (0, 209, 255))
canvas.paste(logo_cyan, (40, 30), logo_mask)

# ── TEXT ──
draw = ImageDraw.Draw(canvas)

# Find fonts
font_paths_bold = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]
font_paths_light = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFCompact.ttf",
]

title_font = sub_font = tag_font = cta_font = None
for fp in font_paths_bold:
    if os.path.exists(fp):
        try:
            title_font = ImageFont.truetype(fp, 120)
            sub_font = ImageFont.truetype(fp, 38)
            cta_font = ImageFont.truetype(fp, 36)
            tag_font = ImageFont.truetype(fp, 24)
            small_font = ImageFont.truetype(fp, 20)
            break
        except:
            continue

if title_font is None:
    title_font = ImageFont.load_default()
    sub_font = tag_font = cta_font = small_font = title_font

# ── "DJ" - white with 3D shadow effect ──
text_x = 50
text_y = 160

# 3D depth shadow layers
for offset in range(8, 0, -1):
    shadow_color = (0, int(30 + offset * 8), int(50 + offset * 12))
    draw.text((text_x + offset, text_y + offset), "DJ", font=title_font, fill=shadow_color)
# Main text
draw.text((text_x, text_y), "DJ", font=title_font, fill=(255, 255, 255))

# ── "BIGGY" - cyan with 3D shadow effect ──
biggy_y = text_y + 110

# 3D depth shadow layers
for offset in range(8, 0, -1):
    shadow_color = (0, int(40 + offset * 5), int(60 + offset * 8))
    draw.text((text_x + offset, biggy_y + offset), "BIGGY", font=title_font, fill=shadow_color)
# Main text - bright cyan
draw.text((text_x, biggy_y), "BIGGY", font=title_font, fill=(0, 220, 255))

# ── Glowing underline ──
bbox = draw.textbbox((text_x, biggy_y), "BIGGY", font=title_font)
line_y = bbox[3] + 10

# Glow layers for the line
for g in range(6, 0, -1):
    glow_alpha = int(40 - g * 5)
    draw.rectangle(
        [text_x, line_y - g, bbox[2] + 10, line_y + 4 + g],
        fill=(0, glow_alpha * 3, glow_alpha * 4)
    )
# Main line
draw.rectangle([text_x, line_y, bbox[2] + 10, line_y + 4], fill=(0, 209, 255))

# ── "THE OFFICIAL MIX" subtitle ──
sub_text = "THE  OFFICIAL  MIX"
draw.text((text_x + 5, line_y + 22), sub_text, font=sub_font, fill=(180, 190, 200))

# ── BOTTOM: Equalizer bars with glow ──
bar_heights = [25, 40, 55, 65, 80, 90, 75, 60, 50, 70, 85, 95, 80, 65, 50, 35, 55, 70, 45, 30]
bar_w = 6
bar_gap = 3
total_w = len(bar_heights) * (bar_w + bar_gap)
bar_start = text_x + 5

for i, h in enumerate(bar_heights):
    x = bar_start + i * (bar_w + bar_gap)
    y_top = H - 40 - h
    y_bot = H - 40

    # Glow behind bar
    glow_rect = [x - 2, y_top - 2, x + bar_w + 2, y_bot + 2]
    draw.rectangle(glow_rect, fill=(0, 30, 50))

    # Gradient bar
    for y in range(y_top, y_bot):
        t = (y - y_top) / max(1, y_bot - y_top)
        g_v = int(220 * (1 - t) + 80 * t)
        b_v = 255
        draw.rectangle([x, y, x + bar_w, y + 1], fill=(0, g_v, b_v))

# ── "BOOK NOW" CTA - bottom right with glow ──
cta_text = "BOOK NOW"
cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
cta_w = cta_bbox[2] - cta_bbox[0] + 50
cta_h = cta_bbox[3] - cta_bbox[1] + 24
cta_x = W - cta_w - 50
cta_y = H - cta_h - 45

# Outer glow
for g in range(12, 0, -1):
    glow_color = (0, int(60 - g * 4), int(80 - g * 5))
    draw.rounded_rectangle(
        [cta_x - g, cta_y - g, cta_x + cta_w + g, cta_y + cta_h + g],
        radius=14 + g,
        fill=glow_color
    )

# Button background
draw.rounded_rectangle(
    [cta_x, cta_y, cta_x + cta_w, cta_y + cta_h],
    radius=14,
    fill=(0, 209, 255)
)
# Button text
draw.text(
    (cta_x + 25, cta_y + 6),
    cta_text,
    font=cta_font,
    fill=(0, 0, 0)
)

# ── TOP ACCENT LINE ──
draw.rectangle([0, 0, W, 3], fill=(0, 209, 255))

# ── FINAL SHARPEN ──
enhancer = ImageEnhance.Sharpness(canvas)
canvas = enhancer.enhance(1.2)

# ── SAVE ──
canvas.save(OUTPUT, "PNG", quality=100)
print(f"✅ Thumbnail saved: {OUTPUT}")
print(f"   Size: {canvas.size[0]}x{canvas.size[1]}px")
