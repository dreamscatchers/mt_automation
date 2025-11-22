#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path
from datetime import date, timedelta
import argparse

from day_index import date_to_index


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Запланировать стримы на ближайшую неделю "
            "для Master's Touch Meditation.\n\n"
            "По умолчанию: с завтрашнего дня на 7 дней вперёд "
            "(DRY-RUN, без реального создания стримов).\n\n"
            "Примеры:\n"
            "  schedule_week.py                # dry-run, 7 дней с завтрашнего\n"
            "  schedule_week.py --no-dry-run   # реальные стримы\n"
            "  schedule_week.py --days 10      # 10 дней с завтрашнего\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Сколько дней планировать (по умолчанию 7)",
    )

    parser.add_argument(
        "--start-from-today",
        dest="start_from_today",
        action="store_true",
        help="Начать с сегодняшнего дня (по умолчанию — с завтрашнего)",
    )

    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=True,
        help="Запуск schedule_range.py в режиме dry-run (по умолчанию включён)",
    )

    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Отключить dry-run и создавать реальные стримы",
    )

    parser.add_argument(
        "--verbose-existing",
        "-e",
        dest="verbose_existing",
        action="store_true",
        help="Пробрасывать -e/--verbose-existing в schedule_range.py",
    )

    return parser.parse_args()


def build_range_indices(start_date: date, days: int) -> tuple[int, int]:
    """Дата начала + количество дней → (start_index, end_index)."""
    end_date = start_date + timedelta(days=days - 1)
    start_index = date_to_index(start_date)
    end_index = date_to_index(end_date)
    return start_index, end_index


def main():
    args = parse_args()

    today = date.today()
    if args.start_from_today:
        start_date = today
    else:
        start_date = today + timedelta(days=1)

    start_index, end_index = build_range_indices(start_date, args.days)
    range_str = f"{start_index}-{end_index}"

    print(f"Сегодня:           {today.isoformat()}")
    print(
        f"Планируем период:  {start_date.isoformat()} .. "
        f"{(start_date + timedelta(days=args.days - 1)).isoformat()}"
    )
    print(f"Диапазон дней:     {range_str}")
    print(f"DRY_RUN:           {args.dry_run}")
    print(f"VERBOSE_EXISTING:  {args.verbose_existing}")

    # Формируем команду вызова schedule_range.py
    script_path = Path(__file__).with_name("schedule_range.py")
    cmd = [sys.executable, str(script_path), range_str]

    if not args.dry_run:
        cmd.append("--no-dry-run")
    # dry_run=True — ничего не добавляем, по умолчанию schedule_range в dry-run

    if args.verbose_existing:
        cmd.append("--verbose-existing")

    print("\nЗапуск:", " ".join(cmd))
    # Пробрасываем код выхода schedule_range.py
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
