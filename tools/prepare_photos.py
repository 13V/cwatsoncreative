#!/usr/bin/env python3
"""Resize and clean the site's photos in place.

Usage:
    python3 tools/prepare_photos.py              # every JPG under images/
    python3 tools/prepare_photos.py a.jpg b.jpg  # just these files

Each photo is fitted within 2000 px on its long edge, turned upright using the
camera's rotation flag, and saved as a progressive JPEG at quality 82 with its
colour profile kept and everything else (camera details, GPS) removed.

Needs Pillow:  pip install pillow
"""
import pathlib
import sys

from PIL import Image, ImageOps

MAX_EDGE = 2000
SKIP = {"og-card.jpg"}


def prepare(path):
    with Image.open(path) as original:
        icc = original.info.get("icc_profile")
        photo = ImageOps.exif_transpose(original).convert("RGB")
    photo.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
    photo.save(path, "JPEG", quality=82, optimize=True, progressive=True, icc_profile=icc)
    return photo.size


def main(args):
    root = pathlib.Path(__file__).resolve().parent.parent
    files = [pathlib.Path(a) for a in args] or sorted((root / "images").rglob("*.jpg"))
    for path in files:
        if path.name in SKIP:
            continue
        width, height = prepare(path)
        print(f"{path}: {width}x{height}, {path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
