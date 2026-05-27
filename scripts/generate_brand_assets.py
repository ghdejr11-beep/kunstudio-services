"""Generate brand assets (og.png 1200x630, logo.png 512x512, favicon.ico) for kunstudio-services.

Brand:
  Navy  #0b1d3a
  Gold  #c9a857
  Cream #f6f2e7
  Ink   #1a1a1a

Run: python scripts/generate_brand_assets.py
Output: landing/og.png, landing/logo.png, landing/favicon.ico
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "landing"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = (11, 29, 58)
GOLD = (201, 168, 87)
CREAM = (246, 242, 231)
INK = (26, 26, 26)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a system font that supports Latin glyphs at the requested size."""
    candidates_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ]
    candidates_regular = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    paths = candidates_bold if bold else candidates_regular
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    # Fallback (will be bitmap; may not honor size on older Pillow, but works)
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_center(draw, xy_center, text, font, fill):
    w, h = text_size(draw, text, font)
    cx, cy = xy_center
    draw.text((cx - w / 2, cy - h / 2), text, font=font, fill=fill)


def make_og():
    """OG image 1200x630."""
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # Gold thin top + bottom rules
    d.rectangle([(0, 0), (W, 6)], fill=GOLD)
    d.rectangle([(0, H - 6), (W, H)], fill=GOLD)

    # Centered stack
    title_font = load_font(96, bold=True)      # KunStudio
    tagline_font = load_font(46, bold=True)    # AI Bots that Actually Ship
    sub_font = load_font(30)                   # for B2B SMBs ...
    domain_font = load_font(22, bold=True)     # domain bottom-right

    # KunStudio (Gold)
    draw_center(d, (W / 2, 200), "KunStudio", title_font, GOLD)

    # Tagline (Cream)
    draw_center(d, (W / 2, 320), "AI Bots that Actually Ship", tagline_font, CREAM)

    # Subline (Cream, slightly dim via off-white)
    draw_center(
        d,
        (W / 2, 400),
        "for B2B SMBs  -  1-5 days  -  $500-$1,500",
        sub_font,
        CREAM,
    )

    # Domain (Gold, bottom right)
    domain = "kunstudio-services.vercel.app"
    dw, dh = text_size(d, domain, domain_font)
    d.text((W - dw - 40, H - dh - 30), domain, font=domain_font, fill=GOLD)

    # Small "KS" monogram bottom-left
    mono_font = load_font(36, bold=True)
    d.text((40, H - 36 - 30), "KS", font=mono_font, fill=GOLD)

    out = OUT / "og.png"
    img.save(out, "PNG", optimize=True)
    return out


def make_logo():
    """Square logo 512x512."""
    S = 512
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)

    # Gold border ring
    border = 10
    d.rectangle([(0, 0), (S - 1, S - 1)], outline=GOLD, width=border)

    # KS monogram centered upper portion
    mono_font = load_font(240, bold=True)
    draw_center(d, (S / 2, S / 2 - 30), "KS", mono_font, GOLD)

    # KunStudio label below
    label_font = load_font(36, bold=True)
    draw_center(d, (S / 2, S - 70), "KunStudio", label_font, CREAM)

    out = OUT / "logo.png"
    img.save(out, "PNG", optimize=True)
    return out


def make_favicon(logo_path: Path):
    """Multi-size favicon.ico from logo."""
    src = Image.open(logo_path).convert("RGB")
    sizes = [(32, 32), (64, 64), (128, 128)]
    # Generate per-size resampled copies so the icon has crisp small sizes.
    images = [src.resize(s, Image.LANCZOS) for s in sizes]
    out = OUT / "favicon.ico"
    images[0].save(out, format="ICO", sizes=sizes, append_images=images[1:])
    return out


def main():
    og = make_og()
    logo = make_logo()
    fav = make_favicon(logo)
    for p in (og, logo, fav):
        size_kb = p.stat().st_size / 1024
        print(f"OK {p.relative_to(ROOT)}  {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
