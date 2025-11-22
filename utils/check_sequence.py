#!/usr/bin/env python3
import re
from pathlib import Path

# Папка с картинками
SOURCE_DIR = (
    Path.home() / "projects" / "master_touch_meditation" / "sequence" / "sources"
)

# Имена вида "123_.png" → берём только такие
NUMBERED_PATTERN = re.compile(r"^(\d+)_$")


def collect_numbers() -> list[int]:
    numbers: list[int] = []

    for path in SOURCE_DIR.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() != ".png":
            continue

        m = NUMBERED_PATTERN.match(path.stem)
        if not m:
            continue

        n_str = m.group(1)
        try:
            n = int(n_str)
        except ValueError:
            continue

        numbers.append(n)

    return numbers


def main():
    nums = collect_numbers()
    if not nums:
        print("Подходящих файлов вида <Number>_.png не найдено.")
        return

    nums = sorted(set(nums))
    n_min = nums[0]
    n_max = nums[-1]

    missing = [n for n in range(n_min, n_max + 1) if n not in nums]

    print(f"Найдено файлов: {len(nums)}")
    print(f"Диапазон номеров: {n_min} … {n_max}")

    if missing:
        print(f"Пропущенные номера ({len(missing)} шт.):")
        print(", ".join(str(n) for n in missing))
    else:
        print("Пропусков в нумерации нет.")


if __name__ == "__main__":
    main()
