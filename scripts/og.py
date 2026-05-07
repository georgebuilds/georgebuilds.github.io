#!/usr/bin/env python3
"""Generate the OpenGraph card for georgebuilds.com.

Output: assets/og.png (1200x630, the OG/Twitter standard).
On-brand with the site: night-sky gradient, faint stars, corner brackets,
amber accent, kalos + degu illustrations. Career positioning emphasizes
agentic systems / AI workflow / LLM wrangling.
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
OUT_PNG = os.path.join(ASSETS, "og.png")

W, H = 1200, 630

# === palette (matches the site css) ===
SKY_0 = np.array([5, 7, 21])
SKY_1 = np.array([10, 15, 36])
SKY_2 = np.array([19, 26, 54])
HORIZON = np.array([26, 23, 20])
BONE = (239, 231, 215, 255)
MUTED = (142, 134, 117, 255)
SOFT = (90, 84, 72, 255)
AMBER = (212, 162, 76, 255)
AMBER_SOFT = (212, 162, 76, 90)


# === background gradient ===
def make_background():
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]

    # vertical band: dark navy → near black, with a subtle top lift
    base = SKY_0 + (SKY_2 - SKY_0) * np.exp(-3.2 * yy)

    # warm horizon glow at the bottom
    horizon_strength = np.exp(-10 * (1 - yy))
    base = base + horizon_strength * (HORIZON - SKY_0) * 0.55

    # a faint cosmic dust glow upper-right (purple) and upper-left (blue)
    dist_ur = np.sqrt((xx - 0.82) ** 2 + (yy - 0.18) ** 2)
    base = base + np.exp(-10 * dist_ur) * np.array([60, 50, 110]) * 0.35

    dist_ul = np.sqrt((xx - 0.18) ** 2 + (yy - 0.30) ** 2)
    base = base + np.exp(-12 * dist_ul) * np.array([40, 60, 130]) * 0.25

    base = np.clip(base, 0, 255).astype(np.uint8)
    return Image.fromarray(np.broadcast_to(base[..., None, :], (H, W, 3)).copy() if base.ndim == 3 else base, "RGB").convert("RGBA")


def make_background_v2():
    """Cleaner: build per-pixel using broadcasting, not the broadcast_to trick."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    yn = yy / (H - 1)
    xn = xx / (W - 1)

    # vertical: SKY_0 → SKY_2 with darkening at very top
    t = np.exp(-3.2 * yn)
    r = SKY_0[0] + (SKY_2[0] - SKY_0[0]) * t
    g = SKY_0[1] + (SKY_2[1] - SKY_0[1]) * t
    b = SKY_0[2] + (SKY_2[2] - SKY_0[2]) * t

    # bottom horizon warm tint
    horizon = np.exp(-10 * (1 - yn))
    r += horizon * (HORIZON[0] - SKY_0[0]) * 0.55
    g += horizon * (HORIZON[1] - SKY_0[1]) * 0.55
    b += horizon * (HORIZON[2] - SKY_0[2]) * 0.55

    # purple cloud upper-right
    dur = np.sqrt((xn - 0.82) ** 2 + (yn - 0.18) ** 2)
    bloom = np.exp(-10 * dur)
    r += bloom * 60 * 0.35
    g += bloom * 50 * 0.35
    b += bloom * 110 * 0.35

    # blue cloud upper-left
    dul = np.sqrt((xn - 0.18) ** 2 + (yn - 0.30) ** 2)
    bloom2 = np.exp(-12 * dul)
    r += bloom2 * 40 * 0.25
    g += bloom2 * 60 * 0.25
    b += bloom2 * 130 * 0.25

    arr = np.stack([r, g, b], axis=-1)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def add_stars(img: Image.Image, n=80, seed=7):
    rng = random.Random(seed)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(n):
        x = rng.randint(0, W - 1)
        # weight stars to upper portion
        y = int((rng.random() ** 1.7) * H * 0.6)
        big = rng.random() < 0.07
        opacity = int(70 + rng.random() * 160)
        if big:
            r = rng.choice([1.6, 2.0])
            color = (255, 238, 208, opacity)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        else:
            r = rng.choice([0.5, 1.0])
            color = (239, 231, 215, opacity)
            if r < 1:
                draw.point((x, y), fill=color)
            else:
                draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=color)
    return img


def draw_corner_bracket(draw, x, y, dx, dy, length=28, thick=4, color=(212, 162, 76, 230)):
    # horizontal arm
    if dx > 0:
        draw.rectangle([x, y, x + length, y + thick], fill=color)
    else:
        draw.rectangle([x - length, y, x, y + thick], fill=color)
    # vertical arm
    if dy > 0:
        draw.rectangle([x, y, x + thick, y + length], fill=color)
    else:
        draw.rectangle([x, y - length, x + thick, y], fill=color)


def try_font(paths_with_index, size):
    for entry in paths_with_index:
        if isinstance(entry, tuple):
            path, index = entry
        else:
            path, index = entry, 0
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=index)
            except Exception:
                continue
    return ImageFont.load_default()


# Menlo.ttc indexing on macOS: 0=Regular, 1=Bold, 2=Italic, 3=BoldItalic
MENLO_REG = [("/System/Library/Fonts/Menlo.ttc", 0), "/System/Library/Fonts/Monaco.ttf", "/System/Library/Fonts/Supplemental/Andale Mono.ttf"]
MENLO_BOLD = [("/System/Library/Fonts/Menlo.ttc", 1), "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"]


def main():
    img = make_background_v2()
    add_stars(img, n=90, seed=12)

    draw = ImageDraw.Draw(img, "RGBA")

    # corner brackets (thicker than the site's, scaled for OG)
    margin = 36
    bcolor = (212, 162, 76, 235)
    blen = 32
    bthick = 4
    draw_corner_bracket(draw, margin, margin, 1, 1, blen, bthick, bcolor)
    draw_corner_bracket(draw, W - margin, margin, -1, 1, blen, bthick, bcolor)
    draw_corner_bracket(draw, margin, H - margin, 1, -1, blen, bthick, bcolor)
    draw_corner_bracket(draw, W - margin, H - margin, -1, -1, blen, bthick, bcolor)

    # === fonts ===
    f_brand = try_font(MENLO_BOLD, 96)
    f_role = try_font(MENLO_BOLD, 28)
    f_tag_big = try_font(MENLO_BOLD, 44)
    f_tag_med = try_font(MENLO_REG, 26)
    f_small = try_font(MENLO_REG, 20)
    f_url = try_font(MENLO_BOLD, 22)
    f_meta = try_font(MENLO_REG, 16)

    # === LEFT SIDE: text ===
    text_x = 80
    # brand wordmark
    brand_y = 80
    draw.text((text_x, brand_y), "georgebuilds", font=f_brand, fill=BONE)
    brand_w = draw.textlength("georgebuilds", font=f_brand)
    draw.text((text_x + brand_w, brand_y), ".", font=f_brand, fill=AMBER)

    # rule line under brand
    rule_y = brand_y + 102
    draw.rectangle([text_x, rule_y, text_x + 60, rule_y + 3], fill=AMBER)

    # role / subtitle line
    role_y = rule_y + 18
    draw.text((text_x, role_y), "GEORGE FERNANDEZ", font=f_role, fill=BONE)
    george_w = draw.textlength("GEORGE FERNANDEZ", font=f_role)
    draw.text((text_x + george_w + 14, role_y + 4), "/  AGENT WRANGLER", font=f_small, fill=AMBER)

    # primary tagline — three short lines, no overlap with right-side illustrations
    tag_y = role_y + 52
    line_h = 50
    draw.text((text_x, tag_y),                  "agentic systems",   font=f_tag_big, fill=BONE)
    draw.text((text_x, tag_y +  line_h),        "llm workflows",     font=f_tag_big, fill=BONE)
    draw.text((text_x, tag_y +  line_h * 2),    "ai infrastructure", font=f_tag_big, fill=BONE)

    # tool list (bottom-left)
    list_y = tag_y + line_h * 3 + 18
    items = [
        ("degu",   "drive-resident media browser"),
        ("kalos",  "self-hosted coding agent · ships prs"),
    ]
    for i, (name, tag) in enumerate(items):
        y = list_y + i * 24
        draw.text((text_x,        y), ">", font=f_small, fill=AMBER)
        draw.text((text_x + 18,   y), name, font=f_small, fill=BONE)
        draw.text((text_x + 100,  y), tag, font=f_small, fill=MUTED)

    # bottom URL
    url_y = H - 56
    draw.text((text_x, url_y), "georgebuilds.com", font=f_url, fill=BONE)

    # === RIGHT SIDE: kalos + degu illustrations ===
    try:
        kalos = Image.open(os.path.join(ASSETS, "kalos.png")).convert("RGBA")
        degu = Image.open(os.path.join(ASSETS, "degu.png")).convert("RGBA")

        # target height — sized so they sit clear of the left-side text column
        icon_h = 230

        def fit_h(im, h):
            return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)

        kalos_r = fit_h(kalos, icon_h)
        degu_r = fit_h(degu, icon_h)

        # right side, slightly overlapping for compositional interest
        right_margin = 70
        gap = -32  # negative = overlap
        # kalos in front (right), degu behind (left, slightly higher)
        kalos_x = W - right_margin - kalos_r.width
        kalos_y = (H - icon_h) // 2 + 10
        degu_x = kalos_x - degu_r.width - gap
        degu_y = kalos_y - 30

        # cast a soft shadow under each card
        def shadow(im, offset=(8, 12), blur=14, alpha=140):
            sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
            sd = ImageDraw.Draw(sh)
            sd.rounded_rectangle([30, 30, 30 + im.width, 30 + im.height], radius=18, fill=(0, 0, 0, alpha))
            from PIL import ImageFilter
            return sh.filter(ImageFilter.GaussianBlur(blur))

        sh1 = shadow(degu_r)
        img.alpha_composite(sh1, (degu_x - 30 + 8, degu_y - 30 + 12))
        sh2 = shadow(kalos_r)
        img.alpha_composite(sh2, (kalos_x - 30 + 8, kalos_y - 30 + 12))

        img.alpha_composite(degu_r, (degu_x, degu_y))
        img.alpha_composite(kalos_r, (kalos_x, kalos_y))

        # tiny labels under each
        label_font = f_meta
        d2 = ImageDraw.Draw(img, "RGBA")
        d2.text((degu_x + degu_r.width // 2 - 18, degu_y + degu_r.height + 6), "DEGU", font=label_font, fill=MUTED)
        d2.text((kalos_x + kalos_r.width // 2 - 24, kalos_y + kalos_r.height + 6), "KALOS", font=label_font, fill=MUTED)

    except FileNotFoundError as e:
        print(f"Warning: illustration not found: {e}")

    # bottom-right meta
    meta_text = "live: degu · inbound: kalos"
    meta_w = draw.textlength(meta_text, font=f_meta)
    draw.text((W - 80 - meta_w, H - 64), meta_text, font=f_meta, fill=SOFT)

    # save
    img.convert("RGB").save(OUT_PNG, optimize=True)
    print(f"wrote {OUT_PNG} ({os.path.getsize(OUT_PNG) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
