#!/usr/bin/env python3
from pathlib import Path
import sys

BASE = Path.home() / "projects" / "master_touch_meditation" / "sequence" 

def main():
    if not BASE.exists():
        print(f"Directory not found: {BASE}")
        sys.exit(1)

    files = sorted(BASE.glob("*.jpeg"))
    if not files:
        print("No .jpeg files found")
        return

    print(f"Found {len(files)} .jpeg files")

    for src in files:
        dst = src.with_suffix(".jpg")

        if dst.exists():
            print(f"Skip {src.name}: {dst.name} already exists")
            continue

        src.rename(dst)
        print(f"{src.name} → {dst.name}")

if __name__ == "__main__":
    main()
