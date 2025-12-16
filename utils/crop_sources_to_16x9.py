#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import argparse
import sys
from datetime import datetime

SOURCES_DIR = Path.home() / "projects" / "master_touch_meditation" / "sequence"
TARGET_RATIO = 16 / 9
RATIO_EPS = 0.0015

DEFAULT_SINCE = "2025-11-01"


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def is_close_to_16_9(w: int, h: int) -> bool:
    return abs((w / h) - TARGET_RATIO) <= RATIO_EPS


def crop_vertical_to_ratio(img: Image.Image):
    w, h = img.size

    if is_close_to_16_9(w, h):
        return None

    target_h = int(round(w * 9 / 16))

    if target_h >= h:
        return None

    total_crop = h - target_h
    top_crop = total_crop // 2
    bottom_crop = total_crop - top_crop

    return img.crop((0, top_crop, w, h - bottom_crop))


def process_file(path: Path, dry_run: bool):
    with Image.open(path) as img:
        w, h = img.size

        cropped = crop_vertical_to_ratio(img)

        if cropped is None:
            if is_close_to_16_9(w, h):
                print(f"OK    {path.name}: {w}x{h}")
            else:
                target_h = int(round(w * 9 / 16))
                if target_h > h:
                    print(f"SKIP  {path.name}: {w}x{h} (cannot reach 16:9 by vertical crop)")
                else:
                    print(f"SKIP  {path.name}: {w}x{h}")
            return

        cw, ch = cropped.size
        total_crop = h - ch
        top_crop = total_crop // 2
        bottom_crop = total_crop - top_crop

        if dry_run:
            print(f"DRY   {path.name}: {w}x{h} -> {cw}x{ch} (cut {top_crop}px top, {bottom_crop}px bottom)")
        else:
            cropped.save(path)
            print(f"DONE  {path.name}: {w}x{h} -> {cw}x{ch} (cut {top_crop}px top, {bottom_crop}px bottom)")


def main():
    parser = argparse.ArgumentParser(
        description="Crop JPGs in sources to 16:9 by trimming top/bottom only."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print actions, do not modify files.",
    )
    parser.add_argument(
        "--since",
        default=DEFAULT_SINCE,
        help=f"Process files modified after this date (YYYY-MM-DD). Default: {DEFAULT_SINCE}",
    )
    args = parser.parse_args()

    since_dt = parse_date(args.since)

    if not SOURCES_DIR.is_dir():
        print(f"Directory not found: {SOURCES_DIR}")
        sys.exit(1)

    files = sorted(SOURCES_DIR.glob("*.jpg"))
    if not files:
        print(f"No .jpg files found in {SOURCES_DIR}")
        return

    for f in files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime <= since_dt:
            continue

        process_file(f, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
