"""Draw the site's preview image, shown where a link to a page is shared.

    social_image.py [OUT]       # docs/assets/social.png by default

The image is 1200 by 630 pixels, the size Open Graph and Twitter cards display without
cropping, and the same file is the repository's social preview on GitHub. It is the
site's logo, the sixteen bits of a hash in the site's accent, beside the package's name
and what it does, in Pillow's built-in font so that it draws the same wherever Pillow is
installed. overrides/main.html names it in every page's ``og:image`` and
``twitter:image``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = (1200, 630)

BACKGROUND = (255, 255, 255)
ACCENT = (42, 120, 214)  # #2a78d6, the accent of both sites
#: A clear bit of the logo: the accent at the logo's 0.28 opacity, on white.
FAINT = (190, 214, 243)
TEXT = (28, 33, 41)
MUTED = (88, 96, 107)

#: The logo's bits, row by row, as docs/assets/logo.svg sets them.
LOGO = ("1011", "0110", "1101", "0100")

ALGORITHMS = (
    "pHash · dHash · aHash · wHash · BMH · mHash · Radial · ColorHash · ColorMoments"
)


def draw() -> Image.Image:
    """Return the preview image."""
    image = Image.new("RGB", SIZE, BACKGROUND)
    canvas = ImageDraw.Draw(image)

    # The logo, 16 cells of the 31-unit grid of logo.svg, scaled to 300 px.
    unit = 300 / 31
    left, top = 80, (SIZE[1] - 300) // 2
    for row, bits in enumerate(LOGO):
        for column, bit in enumerate(bits):
            x = left + (2 + 7 * column) * unit
            y = top + (2 + 7 * row) * unit
            canvas.rounded_rectangle(
                (x, y, x + 6 * unit, y + 6 * unit),
                radius=1.2 * unit,
                fill=ACCENT if bit == "1" else FAINT,
            )

    def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        return ImageFont.load_default(size)

    x = 440
    canvas.text((x, 170), "python-libphash", font=font(72), fill=TEXT)
    canvas.text((x, 270), "Perceptual image hashing", font=font(44), fill=ACCENT)
    canvas.text((x, 326), "for Python, in C", font=font(44), fill=ACCENT)
    canvas.text(
        (x, 410), "Find duplicate and near-duplicate images", font=font(28), fill=MUTED
    )
    # The nine algorithms under a rule, along the bottom of the card.
    canvas.line((80, 520, SIZE[0] - 80, 520), fill=FAINT, width=2)
    canvas.text((80, 545), ALGORITHMS, font=font(26), fill=MUTED)
    return image


def main() -> None:
    """Write the preview image."""
    parser = argparse.ArgumentParser(description="Draw the site's preview image.")
    parser.add_argument(
        "out",
        nargs="?",
        type=Path,
        default=ROOT / "docs" / "assets" / "social.png",
    )
    args = parser.parse_args()
    out: Path = args.out
    draw().save(out, optimize=True)


if __name__ == "__main__":
    main()
