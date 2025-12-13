#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import sys

# Жёсткий путь проекта
BASE = Path.home() / "projects" / "master_touch_meditation" / "sequence"

TARGET_WIDTH = 1344
TARGET_HEIGHT = 756
SOURCE_HEIGHT = 768  # что проверяем (1344 x 768)

def crop_file(path: Path):
    with Image.open(path) as img:
        width, height = img.size

        if width != TARGET_WIDTH or height != SOURCE_HEIGHT:
            return  # пропускаем

        total_crop = height - TARGET_HEIGHT  # 768 → 756 = 12 px
        top_crop = total_crop // 2
        bottom_crop = total_crop - top_crop

        cropped = img.crop((0, top_crop, width, height - bottom_crop))
        cropped.save(path)

        print(f"{path.name}: {width}x{height} → {cropped.size[0]}x{cropped.size[1]} "
              f"(cut {top_crop}px top, {bottom_crop}px bottom)")


def main():
    if not BASE.exists():
        print(f"Directory not found: {BASE}")
        sys.exit(1)

    files = sorted(BASE.glob("*.jpg"))
    if not files:
        print(f"No JPG files in {BASE}")
        return

    print(f"Processing {len(files)} JPG files in {BASE}")

    for f in files:
        crop_file(f)


if __name__ == "__main__":
    main()
