#!/usr/bin/env python3
"""DJ BIGGY - Premium YouTube Thumbnail Generator v3"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np
import math, os

W, H = 1280, 720

FILES = {
    "logo": "/Users/djbiggy/Downloads/Dj biggy logo .JPG",
    "jacket": "/Users/djbiggy/Downloads/Copy of _61A0193.JPG",
    "closeup": "/Users/djbiggy/Downloads/_MGL0109.JPG",
    "colorful": "/Users/djbiggy/Downloads/_MGL0395.JPG",
    "live_dj": "/Users/djbiggy/Downloads/_MGL0369.JPG",
}
OUT = "/Users/djbiggy/Downloads/Claude Code- File Agents/"


def gradient_bg():
    bg = np.zeros((H, W, 3), dtype=np.float64)
    yy = np.linspace(0, 1, H).reshape(-1, 1)
    xx = np.linspace(0, 1, W).reshape(1, -1)
    bg[:,:,0] = 8 - xx * 3 + yy * 2
    bg[:,:,1] = 8 + 12 * (1 - yy)
    bg[:,:,2] = 20 + 30 * (1 - yy) * (1 - xx * 0.3)
    return np.clip(bg, 0, 255).astype(np.uint8)


def color_grade(arr):
    a = arr.astype(np.float64)
    lum = a.mean(axis=2)
    shadow = lum < 80
    mid = (lum >= 80) & (lum < 180)
    a[:,:,0][shadow] *= 0.65
    a[:,:,0][mid] *= 0.88
    a[:,:,1][mid] *= 1.05
    a[:,:,2] = a[:,:,2] * 1.2 + 15
    a[:,:,2][shadow] += 20
    m = a.mean()
    a = (a - m) * 1.25 + m
    return np.clip(a, 0, 255).astype(np.uint8)


def cyan_glow(arr, cx, cy, r=350, strength=40):
    Y, X = np.ogrid[:H, :W]
    d = np.sqrt((X - cx)**2 + (Y - cy)**2)
    f = np.clip(1 - d / r, 0, 1) ** 1.8
    g = np.zeros_like(arr, dtype=np.float64)
    g[:,:,1] = f * strength * 0.8
    g[:,:,2] = f * strength
    c = arr.astype(np.float64)
    return np.clip(255 - (255 - c) * (255 - g) / 255, 0, 255).astype(np.uint8)


def apply_vignette(arr, s=0.5):
    Y, X = np.ogrid[:H, :W]
    d = np.sqrt((X - W/2)**2 + (Y - H/2)**2)
    v = np.clip(1 - d / math.sqrt((W/2)**2 + (H/2)**2) * s, 0, 1)
    r = arr.astype(np.float64)
    for c in range(3):
        r[:,:,c] *= v
    return np.clip(r, 0, 255).astype(np.uint8)


def fade_left(arr, bg, px, fw=380):
    r = arr.astype(np.float64)
    b = bg.astype(np.float64)
    for xo in range(fw):
        x = px + xo
        if 0 <= x < W:
            t = xo / fw
            t = t * t * (3 - 2 * t)
            r[:, x, :] = b[:, x, :] * (1 - t) + r[:, x, :] * t
    return np.clip(r, 0, 255).astype(np.uint8)


def get_font(sz):
    for p in ["/System/Library/Fonts/Supplemental/Impact.ttf", "/Library/Fonts/Arial Bold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def text_3d(d, pos, txt, fnt, color, shadow, depth=7):
    x, y = pos
    for i in range(depth, 0, -1):
        f = i / depth
        sc = tuple(int(c * f) for c in shadow)
        d.text((x + i, y + i), txt, font=fnt, fill=sc)
    d.text(pos, txt, font=fnt, fill=color)


def build(photo_path, name, crop=None):
    print(f"  Building {name}...")
    photo = Image.open(photo_path)
    pw, ph = photo.size
    if crop:
        photo = photo.crop([int(pw*crop[0]), int(ph*crop[1]), int(pw*crop[2]), int(ph*crop[3])])

    th = H + 40
    asp = photo.size[0] / photo.size[1]
    tw = max(int(th * asp), int(W * 0.55))
    th = int(tw / asp)
    photo = photo.resize((tw, th), Image.LANCZOS)

    graded = Image.fromarray(color_grade(np.array(photo)))
    graded = ImageEnhance.Sharpness(graded).enhance(1.4)
    graded = ImageEnhance.Contrast(graded).enhance(1.15)

    bg = gradient_bg()
    canvas = Image.fromarray(bg.copy())
    px = W - tw + int(tw * 0.08)
    py = max(0, (H - th) // 2)
    canvas.paste(graded, (px, py))

    ca = np.array(canvas)
    ca = fade_left(ca, bg, px)
    ca = cyan_glow(ca, W - int(tw * 0.3), int(H * 0.35), 380, 45)
    ca = cyan_glow(ca, int(W * 0.15), int(H * 0.8), 200, 15)
    ca = apply_vignette(ca)

    canvas = Image.fromarray(ca)

    # Logo (white on dark)
    logo = Image.open(FILES["logo"]).convert("L").resize((95, 95), Image.LANCZOS)
    mask = np.clip((255 - np.array(logo)) * 1.5, 0, 255).astype(np.uint8)
    mask_img = Image.fromarray(mask)
    logo_layer = Image.new("RGB", (95, 95), (255, 255, 255))
    canvas.paste(logo_layer, (40, 22), mask_img)

    draw = ImageDraw.Draw(canvas)
    tf = get_font(130)
    sf = get_font(36)
    cf = get_font(34)

    # DJ - white 3D
    text_3d(draw, (45, 150), "DJ", tf, (255, 255, 255), (80, 80, 80))
    # BIGGY - white 3D
    text_3d(draw, (45, 275), "BIGGY", tf, (255, 255, 255), (60, 60, 60))

    # Underline
    bb = draw.textbbox((45, 275), "BIGGY", font=tf)
    ly = bb[3] + 12
    for g in range(8, 0, -1):
        v = int(40 * (1 - g/8))
        draw.rectangle([45, ly-g, bb[2]+15, ly+5+g], fill=(v, v, v))
    draw.rectangle([45, ly, bb[2]+15, ly+5], fill=(255, 255, 255))

    # Subtitle
    draw.text((48, ly + 20), "THE  OFFICIAL  MIX", font=sf, fill=(180, 195, 210))

    # EQ bars
    bars = [20,35,50,60,75,88,70,55,45,65,82,92,75,60,45,30,50,66,40,25]
    for i, h in enumerate(bars):
        x = 48 + i * 10
        yt = H - 35 - h
        for y in range(yt, H - 35):
            t = (y - yt) / max(1, H - 35 - yt)
            draw.rectangle([x, y, x+7, y+1], fill=(0, int(215*(1-t)+60*t), 255))
        draw.rectangle([x, yt, x+7, yt+2], fill=(150, 255, 255))

    # Book Now button
    cta = "BOOK  NOW"
    cb = draw.textbbox((0,0), cta, font=cf)
    cw, ch = cb[2]-cb[0]+56, cb[3]-cb[1]+28
    cx, cy = W-cw-45, H-ch-38
    for g in range(15, 0, -1):
        draw.rounded_rectangle([cx-g,cy-g,cx+cw+g,cy+ch+g], radius=16+g,
                               fill=(0, max(0,40-g*3), max(0,60-g*4)))
    draw.rounded_rectangle([cx,cy,cx+cw,cy+ch], radius=16, fill=(0,209,255))
    draw.text((cx+28, cy+10), cta, font=cf, fill=(0,0,0))

    # Accent lines
    draw.rectangle([0,0,W,3], fill=(0,209,255))
    draw.rectangle([0,H-2,W,H], fill=(0,100,140))

    canvas = ImageEnhance.Sharpness(canvas).enhance(1.15)
    path = os.path.join(OUT, name)
    canvas.save(path, "PNG")
    print(f"  ✅ {name} ({canvas.size[0]}x{canvas.size[1]})")


print("🎨 Generating DJ BIGGY thumbnails...\n")
build(FILES["jacket"], "DJ_BIGGY_Thumb_A_JacketPose.png", (0.12, 0.0, 0.88, 0.82))
build(FILES["live_dj"], "DJ_BIGGY_Thumb_B_LiveDJ.png", (0.05, 0.0, 0.95, 0.95))
build(FILES["colorful"], "DJ_BIGGY_Thumb_C_Style.png", (0.10, 0.0, 0.90, 0.85))
print("\n🎉 All 3 thumbnails ready!")
