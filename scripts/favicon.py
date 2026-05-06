#!/usr/bin/env python3
"""Render favicon-32.png and apple-touch-icon.png by recreating the favicon.svg design in PIL.

Output:
    assets/favicon-32.png      (32x32)
    assets/apple-touch-icon.png (180x180)
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

MENLO_BOLD = [("/System/Library/Fonts/Menlo.ttc", 1), "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"]


def try_font(paths_with_index, size):
    for entry in paths_with_index:
        if isinstance(entry, tuple):
            path, idx = entry
        else:
            path, idx = entry, 0
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=idx)
            except Exception:
                continue
    return ImageFont.load_default()


def render(size: int, out_path: str):
    """Render the favicon at `size` pixels. Geometry mirrors favicon.svg's 32-unit viewbox."""
    s = size  # convenience
    scale = size / 32.0

    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))

    # rounded-rect dark navy background
    bg = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    radius = max(2, int(round(5 * scale)))
    bd.rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=(10, 15, 36, 255))

    # radial highlight (top-left): build by drawing concentric ellipses with decreasing alpha
    # this approximates the SVG <radialGradient cx=30% cy=20% r=60%>
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = int(round(0.30 * s)), int(round(0.20 * s))
    max_r = int(round(0.60 * s))
    steps = 24
    for i in range(steps, 0, -1):
        r = int(max_r * i / steps)
        # interpolate from inner (#1a2040) to outer (#050715)
        t = i / steps  # 1 at center, 0 at edge
        col = (
            int(0x1a * t + 0x05 * (1 - t)),
            int(0x20 * t + 0x07 * (1 - t)),
            int(0x40 * t + 0x15 * (1 - t)),
            int(160 * (1 - i / steps)),  # fade out from center
        )
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # mask the highlight to the rounded rect
    mask = Image.new("L", (s, s), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=255)
    glow.putalpha(Image.eval(mask, lambda v: v))

    img.alpha_composite(bg)
    img.alpha_composite(glow)

    # text: "gb" — JetBrains Mono Bold isn't installed locally, fall back to Menlo Bold
    # SVG has font-size=17 in a 32-unit canvas; replicate the proportion
    font_px = max(8, int(round(17 * scale)))
    font = try_font(MENLO_BOLD, font_px)
    d = ImageDraw.Draw(img)
    # SVG x=2.5, y=24 (text baseline). PIL's text() uses top-left by default,
    # so we need to convert baseline → top. Use textbbox to measure ascent.
    bbox = d.textbbox((0, 0), "gb", font=font)
    text_h = bbox[3] - bbox[1]
    # SVG baseline 24 in 32-unit space ≈ y_top = baseline - ascent
    # We approximate by placing text so its bottom at ~26*scale (visually matches SVG)
    text_x = int(round(1.5 * scale))
    text_y = int(round(26 * scale)) - text_h - bbox[1]
    d.text((text_x, text_y), "gb", font=font, fill=(239, 231, 215, 255))

    # amber dot with glow — render bright dot, blur a copy for the halo, composite
    dot_layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dot_layer)
    dot_cx = int(round(26.5 * scale))
    dot_cy = int(round(23 * scale))
    dot_r = max(1, int(round(3.2 * scale)))
    dd.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=(212, 162, 76, 255))

    halo = dot_layer.filter(ImageFilter.GaussianBlur(radius=max(1.0, 1.6 * scale)))
    # boost halo intensity a touch
    halo = Image.eval(halo, lambda v: min(255, int(v * 1.3)))
    img.alpha_composite(halo)
    img.alpha_composite(dot_layer)

    img.save(out_path, optimize=True)
    print(f"wrote {out_path} ({os.path.getsize(out_path) / 1024:.1f} KB)")


def main():
    render(32, os.path.join(ASSETS, "favicon-32.png"))
    render(180, os.path.join(ASSETS, "apple-touch-icon.png"))


if __name__ == "__main__":
    main()
