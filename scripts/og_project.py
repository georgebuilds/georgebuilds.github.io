#!/usr/bin/env python3
"""Generate per-project OG cards (1200x630) for degu and kalos.

Same visual language as the main site's og.png: night-sky gradient, faint
stars, amber corner brackets, JetBrains-Mono-style wordmark, and the
project's character illustration on the right.

Outputs:
    /Users/georgef/Code/degu/landing/og.png
    /Users/georgef/Code/kalos/docs/og.png
"""

import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

W, H = 1200, 630

# palette (mirrors site CSS tokens)
SKY_0 = np.array([5, 7, 21])
SKY_1 = np.array([10, 15, 36])
SKY_2 = np.array([19, 26, 54])
HORIZON = np.array([26, 23, 20])
BONE = (239, 231, 215, 255)
MUTED = (142, 134, 117, 255)
SOFT = (126, 119, 105, 255)  # the lifted --soft from main-site quality pass
ACCENT = (212, 162, 76, 255)

MENLO_REG = [("/System/Library/Fonts/Menlo.ttc", 0)]
MENLO_BOLD = [("/System/Library/Fonts/Menlo.ttc", 1)]


def try_font(paths_with_index, size):
    for entry in paths_with_index:
        path, idx = entry if isinstance(entry, tuple) else (entry, 0)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=idx)
            except Exception:
                continue
    return ImageFont.load_default()


def make_background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    yn = yy / (H - 1)
    xn = xx / (W - 1)

    t = np.exp(-3.2 * yn)
    r = SKY_0[0] + (SKY_2[0] - SKY_0[0]) * t
    g = SKY_0[1] + (SKY_2[1] - SKY_0[1]) * t
    b = SKY_0[2] + (SKY_2[2] - SKY_0[2]) * t

    horizon = np.exp(-10 * (1 - yn))
    r += horizon * (HORIZON[0] - SKY_0[0]) * 0.55
    g += horizon * (HORIZON[1] - SKY_0[1]) * 0.55
    b += horizon * (HORIZON[2] - SKY_0[2]) * 0.55

    dur = np.sqrt((xn - 0.82) ** 2 + (yn - 0.18) ** 2)
    bloom = np.exp(-10 * dur)
    r += bloom * 60 * 0.35
    g += bloom * 50 * 0.35
    b += bloom * 110 * 0.35

    dul = np.sqrt((xn - 0.18) ** 2 + (yn - 0.30) ** 2)
    bloom2 = np.exp(-12 * dul)
    r += bloom2 * 40 * 0.25
    g += bloom2 * 60 * 0.25
    b += bloom2 * 130 * 0.25

    arr = np.clip(np.stack([r, g, b], axis=-1), 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def add_stars(img, n=80, seed=12):
    rng = random.Random(seed)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(n):
        x = rng.randint(0, W - 1)
        y = int((rng.random() ** 1.7) * H * 0.6)
        big = rng.random() < 0.07
        op = int(70 + rng.random() * 160)
        if big:
            r = rng.choice([1.6, 2.0])
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 238, 208, op))
        else:
            r = rng.choice([0.5, 1.0])
            color = (239, 231, 215, op)
            if r < 1:
                draw.point((x, y), fill=color)
            else:
                draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=color)


def draw_corner(draw, x, y, dx, dy, length=32, thick=4, color=(212, 162, 76, 235)):
    if dx > 0:
        draw.rectangle([x, y, x + length, y + thick], fill=color)
    else:
        draw.rectangle([x - length, y, x, y + thick], fill=color)
    if dy > 0:
        draw.rectangle([x, y, x + thick, y + length], fill=color)
    else:
        draw.rectangle([x, y - length, x + thick, y], fill=color)


def render_project(out_path: str, character_path: str, project: dict):
    """Render an OG card for a single project.

    project keys:
        name (str)            — e.g. "degu"
        tagline (str)         — short one-liner
        body_lines (list[str])— 1-2 lines of body
        stack (list[str])     — short tech tokens
        license (str)
        url (str)             — canonical short URL like "georgebuilds.com/degu"
    """
    img = make_background()
    add_stars(img, n=90, seed=hash(project["name"]) & 0xFFFF)

    draw = ImageDraw.Draw(img, "RGBA")

    margin = 36
    draw_corner(draw, margin, margin, 1, 1)
    draw_corner(draw, W - margin, margin, -1, 1)
    draw_corner(draw, margin, H - margin, 1, -1)
    draw_corner(draw, W - margin, H - margin, -1, -1)

    f_brand = try_font(MENLO_BOLD, 84)
    f_role = try_font(MENLO_REG, 22)
    f_tag = try_font(MENLO_BOLD, 32)
    f_body = try_font(MENLO_REG, 19)
    f_chip = try_font(MENLO_REG, 19)
    f_url = try_font(MENLO_BOLD, 22)
    f_meta = try_font(MENLO_REG, 16)
    # left-side text zone has to leave the right ~360px clear for the character
    TEXT_ZONE_W = 720

    text_x = 80

    # brand: "gb / project"
    brand_y = 90
    gb_text = "gb"
    sep_text = " / "
    proj_text = project["name"]
    glyph_text = "."
    # render piece by piece, advancing x
    cursor_x = text_x
    draw.text((cursor_x, brand_y), gb_text, font=f_brand, fill=MUTED)
    cursor_x += draw.textlength(gb_text, font=f_brand)
    draw.text((cursor_x, brand_y), sep_text, font=f_brand, fill=SOFT)
    cursor_x += draw.textlength(sep_text, font=f_brand)
    draw.text((cursor_x, brand_y), proj_text, font=f_brand, fill=BONE)
    cursor_x += draw.textlength(proj_text, font=f_brand)
    draw.text((cursor_x, brand_y), glyph_text, font=f_brand, fill=ACCENT)

    # rule under brand
    rule_y = brand_y + 96
    draw.rectangle([text_x, rule_y, text_x + 60, rule_y + 3], fill=ACCENT)

    # subtitle role line
    sub_y = rule_y + 18
    draw.text((text_x, sub_y), "BY GEORGE FERNANDEZ", font=f_role, fill=BONE)
    name_w = draw.textlength("BY GEORGE FERNANDEZ", font=f_role)
    draw.text((text_x + name_w + 12, sub_y + 4), "/  GEORGEBUILDS.COM", font=f_meta, fill=ACCENT)

    # tagline (short one-liner, pops)
    tag_y = sub_y + 56
    draw.text((text_x, tag_y), project["tagline"], font=f_tag, fill=BONE)

    # body lines below tagline
    body_y = tag_y + 64
    for i, line in enumerate(project.get("body_lines", [])):
        draw.text((text_x, body_y + i * 30), line, font=f_body, fill=MUTED)

    # stack chips (tag-style)
    chip_y = body_y + len(project.get("body_lines", [])) * 30 + 32
    chip_pad_x, chip_pad_y = 10, 5
    chip_gap = 8
    cx = text_x
    cy = chip_y
    for token in project["stack"]:
        tw = draw.textlength(token, font=f_chip)
        chip_w = int(tw + chip_pad_x * 2)
        chip_h = 30
        # pill background
        draw.rounded_rectangle(
            [cx, cy, cx + chip_w, cy + chip_h],
            radius=4,
            fill=(239, 231, 215, 12),
            outline=(239, 231, 215, 40),
            width=1,
        )
        draw.text((cx + chip_pad_x, cy + chip_pad_y - 2), token, font=f_chip, fill=MUTED)
        cx += chip_w + chip_gap
        if cx > text_x + TEXT_ZONE_W - 80:  # wrap inside the text zone
            cx = text_x
            cy += chip_h + 6

    # bottom-left URL
    draw.text((text_x, H - 64), project["url"], font=f_url, fill=BONE)

    # license meta bottom-right textual
    lic_text = f"license · {project['license']}"
    lic_w = draw.textlength(lic_text, font=f_meta)
    draw.text((W - 80 - lic_w, H - 58), lic_text, font=f_meta, fill=SOFT)

    # right-side character illustration with soft shadow
    if os.path.exists(character_path):
        char = Image.open(character_path).convert("RGBA")
        target_h = 380
        ratio = char.width / char.height
        char_r = char.resize((int(target_h * ratio), target_h), Image.LANCZOS)
        char_x = W - 90 - char_r.width
        char_y = (H - char_r.height) // 2 + 10

        # shadow
        sh = Image.new("RGBA", (char_r.width + 80, char_r.height + 80), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle(
            [40, 40, 40 + char_r.width, 40 + char_r.height], radius=22, fill=(0, 0, 0, 150)
        )
        sh = sh.filter(ImageFilter.GaussianBlur(20))
        img.alpha_composite(sh, (char_x - 40 + 8, char_y - 40 + 14))
        img.alpha_composite(char_r, (char_x, char_y))

    img.convert("RGB").save(out_path, optimize=True)
    print(f"wrote {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def main():
    render_project(
        "/Users/georgef/Code/degu/landing/og.png",
        "/Users/georgef/Code/degu/landing/og-character.png",
        {
            "name": "degu",
            "tagline": "a media browser that travels.",
            "body_lines": [
                "drop on a drive · tags + thumbnails ride along",
                "local-first · nothing leaves your machine",
            ],
            "stack": ["Preact", "TypeScript", "Vite", "Tailwind", "Go", "SQLite", "Wails", "ffmpeg.wasm"],
            "license": "AGPL-3.0",
            "url": "georgebuilds.com/degu",
        },
    )

    render_project(
        "/Users/georgef/Code/kalos/docs/og.png",
        "/Users/georgef/Code/kalos/docs/og-character.png",
        {
            "name": "kalos",
            "tagline": "a self-hosted coding agent.",
            "body_lines": [
                "POST a task · runs Claude Code headless",
                "commits, pushes, opens the PR",
            ],
            "stack": ["Node 22", "TypeScript", "Hono", "better-sqlite3", "Claude Code", "GitHub App", "MCP", "Docker"],
            "license": "MIT",
            "url": "georgebuilds.com/kalos",
        },
    )


if __name__ == "__main__":
    main()
