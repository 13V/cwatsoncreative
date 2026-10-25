#!/usr/bin/env python3
"""Get the site's photos ready for the web, then rebuild the pages.

Usage:
    python3 tools/prepare_photos.py              # every JPG under images/
    python3 tools/prepare_photos.py a.jpg b.jpg  # just these files
    python3 tools/prepare_photos.py --force      # remake every WebP copy, even ones already made
    python3 tools/prepare_photos.py --no-build   # make the copies but do not rebuild the pages

For each photo:
  * A photo that is over 2000 px on its long edge, turned by the camera's rotation flag, or carrying
    camera or GPS details is resized, turned upright and re-saved as a quality-82 progressive JPEG
    with its colour profile kept and everything else removed. Clean 2000 px web exports are left
    exactly as they are, so they lose no quality.
  * WebP copies are made at 480, 800, 1000 and 1200 px wide (where no wider than the photo) and at
    full size (quality 80 for the smaller copies, 72 for the full one). The full-size copy is never
    allowed to be bigger than the JPEG: if quality 72 still is, it steps down a little until it is
    not. Browsers that take WebP load these, and phones load the small ones (an emulated phone
    picks the 1000 px copy of a hero, about 160KB instead of 225KB).

Then the pages are rebuilt (tools/site/build.py), so new photos and galleries appear.

Needs Pillow:  pip install pillow
"""
import io
import pathlib
import sys

from PIL import Image, ImageOps

MAX_EDGE = 2000
WIDTHS = (480, 800, 1000, 1200)  # tools/site/build.py WIDTHS lists the same rungs
WEBP_QUALITY = 80       # the smaller copies, seen on phones and in grids
WEBP_QUALITY_FULL = 72  # the full-size copy, seen up close in the photo viewer
FULL_FLOOR = 60         # the lowest the full-size copy may step down to stay under its JPEG
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


def encode(photo, quality, icc):
    buffer = io.BytesIO()
    photo.save(buffer, "WEBP", quality=quality, method=6, icc_profile=icc)
    return buffer.getvalue()


def full_size(photo, icc, jpeg_bytes):
    quality = WEBP_QUALITY_FULL
    data = encode(photo, quality, icc)
    while len(data) > jpeg_bytes and quality > FULL_FLOOR:
        quality -= 4  # never heavier than the JPEG it stands in for
        data = encode(photo, quality, icc)
    return data, quality


def webp_copies(path, force=False):
    with Image.open(path) as original:
        icc = original.info.get("icc_profile")
        photo = original.convert("RGB")
    jpeg_bytes = path.stat().st_size
    made, full = [], None
    for width in [w for w in WIDTHS if w <= photo.width] + [None]:
        out = path.with_name(f"{path.stem}-{width}.webp" if width else f"{path.stem}.webp")
        if not force and out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
            continue  # already made from this version of the photo
        if width is None or width == photo.width:
            # A rung as wide as the photo stands in for the full-size file (build.py lists one or the
            # other), so it is the same encoding.
            full = full or full_size(photo, icc, jpeg_bytes)
            data, quality = full
        else:
            copy = photo.resize((width, round(photo.height * width / photo.width)), Image.LANCZOS)
            quality = WEBP_QUALITY
            data = encode(copy, quality, icc)
        out.write_bytes(data)
        made.append(f"{out.name} q{quality}")
    return made


def main(args):
    force = "--force" in args
    rebuild = "--no-build" not in args
    names = [a for a in args if not a.startswith("--")]
    files = [pathlib.Path(a).resolve() for a in names] or sorted((ROOT / "images").rglob("*.jpg"))
    for path in files:
        if path.name in SKIP:
            continue
        cleaned = clean(path)
        made = webp_copies(path, force=force or cleaned)
        with Image.open(path) as photo:
            width, height = photo.size
        notes = (["cleaned"] if cleaned else []) + ([f"made {', '.join(made)}"] if made else [])
        print(f"{path.relative_to(ROOT)}: {width}x{height}, {'; '.join(notes) or 'already done'}", flush=True)

    if rebuild:
        sys.path.insert(0, str(ROOT / "tools" / "site"))
        import build
        build.main()


if __name__ == "__main__":
    main(sys.argv[1:])
