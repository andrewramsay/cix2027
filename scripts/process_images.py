#!/usr/bin/env python3
"""Turn original photos into web-sized images for the site.

Reads the originals in photos/ (any size or format people send) and writes
small JPEGs to assets/images/, which is where the site loads them from.
The output folders are generated, git-ignored and rebuilt by CI on every
build, so never edit or commit them.

  photos/committee/<file>  ->  assets/images/committee/<id>.jpg   (square crop)

Committee members without a photo get a placeholder with their initials.

Usage: python scripts/process_images.py
Run scripts/validate.py first: this script assumes the data files are valid.
"""

from __future__ import annotations

import hashlib
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

from common import DATA, IMAGES, PHOTOS, load_yaml, rel

# Output size in pixels. Shown at 160 CSS px on the page, so this covers 2x screens.
COMMITTEE_SIZE = 320
JPEG_QUALITY = 85
DEFAULT_FOCUS = (0.5, 0.35)


def save_jpeg(img: Image.Image, dest) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)


def square_photo(src, size: int, focus) -> Image.Image:
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)  # respect camera orientation, then EXIF is dropped on save
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            im = Image.alpha_composite(bg, im)
        return ImageOps.fit(im, (size, size), method=Image.Resampling.LANCZOS, centering=focus)


def initials_placeholder(name: str, size: int) -> Image.Image:
    words = [w for w in name.replace("-", " ").split() if w[:1].isalpha()]
    initials = (words[0][0] + (words[-1][0] if len(words) > 1 else "")).upper() if words else "?"
    # Stable, muted background colour per name
    h = int(hashlib.sha1(name.encode()).hexdigest(), 16)
    bg = tuple(110 + (h >> s) % 80 for s in (0, 8, 16))
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=size // 3)
    draw.text((size / 2, size / 2), initials, fill="white", font=font, anchor="mm")
    return img


def committee() -> int:
    members = load_yaml(DATA / "committee.yml") or []
    out_dir = IMAGES / "committee"
    count = 0
    for m in members:
        dest = out_dir / f"{m['id']}.jpg"
        photo = m.get("photo")
        if photo:
            src = PHOTOS / "committee" / photo
            img = square_photo(src, COMMITTEE_SIZE, tuple(m.get("photo_focus", DEFAULT_FOCUS)))
            note = f"from {rel(src)}"
        else:
            img = initials_placeholder(m["name"], COMMITTEE_SIZE)
            note = "placeholder"
        save_jpeg(img, dest)
        print(f"  {rel(dest)}  ({dest.stat().st_size // 1024} KB, {note})")
        count += 1
    # Remove outputs for people no longer listed
    keep = {f"{m['id']}.jpg" for m in members}
    if out_dir.is_dir():
        for p in out_dir.glob("*.jpg"):
            if p.name not in keep:
                p.unlink()
    return count


def main() -> int:
    print("Committee photos:")
    n = committee()
    print(f"process_images: wrote {n} image(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
