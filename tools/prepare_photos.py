#!/usr/bin/env python3
"""Get the site's photos ready for the web, then rebuild the pages.

Usage:
    python3 tools/prepare_photos.py              # every JPG under images/
    python3 tools/prepare_photos.py a.jpg b.jpg  # just these files

For each photo:
  * A photo that is over 2000 px on its long edge, turned by the camera's rotation flag, or carrying
    camera or GPS details is resized, turned upright and re-saved as a quality-82 progressive JPEG
    with its colour profile kept and everything else removed. Clean 2000 px web exports are left
    exactly as they are, so they lose no quality.
  * WebP copies are made at 480, 800 and 1200 px wide (where narrower than the photo) and at full
    size (quality 80 for the smaller copies, 85 for the full one). Browsers that take WebP load
    these, and phones load the small ones.

Then the pages are rebuilt (tools/site/build.py), so new photos and galleries appear.

Needs Pillow:  pip install pillow
"""
import pathlib
import sys

from PIL import Image, ImageOps

MAX_EDGE = 2000
WIDTHS = (480, 800, 1200)
WEBP_QUALITY = 80       # the smaller copies, seen on phones and in grids
WEBP_QUALITY_FULL = 85  # the full-size copy, seen up close in the photo viewer
SKIP = {"og-card.jpg"}
ROOT = pathlib.Path(__file__).resolve().parent.parent


def needs_cleaning(photo):
    if max(photo.size) > MAX_EDGE:
        return True
    if len(photo.getexif()):  # camera details, GPS or a rotation flag
        return True
    return any(key in photo.info for key in ("exif", "xmp", "photoshop", "comment"))


def clean(path):
    with Image.open(path) as original:
        if not needs_cleaning(original):
            return False
        icc = original.info.get("icc_profile")
        photo = ImageOps.exif_transpose(original).convert("RGB")
    photo.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
    photo.save(path, "JPEG", quality=82, optimize=True, progressive=True, icc_profile=icc)
    return True


def webp_copies(path):
    with Image.open(path) as original:
        icc = original.info.get("icc_profile")
        photo = original.convert("RGB")
    made = []
    for width in [w for w in WIDTHS if w < photo.width] + [None]:
        out = path.with_name(f"{path.stem}-{width}.webp" if width else f"{path.stem}.webp")
        if out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
            continue  # already made from this version of the photo
        copy = photo if width is None else photo.resize((width, round(photo.height * width / photo.width)), Image.LANCZOS)
        quality = WEBP_QUALITY_FULL if width is None else WEBP_QUALITY
        copy.save(out, "WEBP", quality=quality, method=6, icc_profile=icc)
        made.append(out.name)
    return made


def main(args):
    files = [pathlib.Path(a).resolve() for a in args] or sorted((ROOT / "images").rglob("*.jpg"))
    for path in files:
        if path.name in SKIP:
            continue
        cleaned = clean(path)
        made = webp_copies(path)
        with Image.open(path) as photo:
            width, height = photo.size
        notes = (["cleaned"] if cleaned else []) + ([f"{len(made)} WebP copies made"] if made else [])
        print(f"{path.relative_to(ROOT)}: {width}x{height}, {', '.join(notes) or 'already done'}")

    sys.path.insert(0, str(ROOT / "tools" / "site"))
    import build
    build.main()


if __name__ == "__main__":
    main(sys.argv[1:])
