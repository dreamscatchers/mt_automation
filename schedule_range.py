#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from datetime import date, timedelta

from dotenv import load_dotenv
from yt_stream import schedule_stream

load_dotenv()

# Нумерация:
# 1 → 2025-02-20
# 2 → 2025-02-21
# и т.д.
BASE_DATE = date(2025, 2, 20)

# Папка с готовыми заставками: N.jpg
SEQUENCE_DIR = Path.home() / "projects" / "master_touch_meditation" / "sequence"

# Плейлисты из .env
GENERAL_PLAYLIST_ID = os.getenv("GENERAL_YT_PLAYLIST_ID")
HALF_PLAYLIST_ID = os.getenv("HALF_MTM_PLAYLIST_ID")
FULL_PLAYLIST_ID = os.getenv("FULL_MTM_PLAYLIST_ID")


def index_to_date(index: int) -> date:
    if index < 1:
        raise ValueError("Номер дня должен быть >= 1")
    return BASE_DATE + timedelta(days=index - 1)


def date_to_start_time_rfc3339(d: date) -> str:
    return f"{d.isoformat()}T10:00:00-04:00"


def parse_range(arg: str) -> tuple[int, int]:
    if "-" not in arg:
        raise ValueError("Ожидался диапазон вида 275-282")
    start_str, end_str = arg.split("-", 1)
    start, end = int(start_str), int(end_str)
    if start > end:
        start, end = end, start
    return start, end


def choose_playlists_for_date(d: date) -> list[tuple[str, str]]:
    """
    Возвращает список плейлистов в виде:
    [
        (playlist_id, "General"),
        (playlist_id, "1/2 Version") ИЛИ (playlist_id, "Full Version")
    ]
    """
    playlists: list[tuple[str, str]] = []

    # Всегда — общий
    if GENERAL_PLAYLIST_ID:
        playlists.append((GENERAL_PLAYLIST_ID, "General"))

    is_sunday = d.weekday() == 6  # Monday=0, Sunday=6

    if is_sunday:
        if FULL_PLAYLIST_ID:
            playlists.append((FULL_PLAYLIST_ID, "Full Version"))
    else:
        if HALF_PLAYLIST_ID:
            playlists.append((HALF_PLAYLIST_ID, "1/2 Version"))

    return playlists


def main():
    if len(sys.argv) != 2:
        print("Usage: python schedule_range.py <start-end>")
        print("Пример: python schedule_range.py 275-282")
        sys.exit(1)

    try:
        start, end = parse_range(sys.argv[1])
    except Exception as e:
        print(f"Ошибка разбора диапазона: {e}")
        sys.exit(1)

    print(f"Создаём стримы для дней с {start} по {end} включительно.")

    for index in range(start, end + 1):
        d = index_to_date(index)
        start_time = date_to_start_time_rfc3339(d)

        thumb_path = SEQUENCE_DIR / f"{index}.jpg"

        if not thumb_path.exists():
            print(f"[{index}] ВНИМАНИЕ: нет файла обложки: {thumb_path}. Пропускаю.")
            continue

        playlists = choose_playlists_for_date(d)

        print(f"\n[{index}] Создаю стрим…")
        print(f"    Дата: {d.isoformat()} (weekday={d.weekday()})")
        print(f"    Дата/время: {start_time}")
        print(f"    Обложка: {thumb_path}")
        print(f"    Плейлисты:")
        for _, alias in playlists:
            print(f"        • {alias}")

        title = f"{index}. Master's Touch Meditation — Day {index} of 1000"
        description = (
            "#YogiBhajan #Meditation #Sadhana #DailyPractice #1000DaysChallenge "
            "#MastersTouchMeditation #KundaliniYoga #MeditationJourney "
            "#SpiritualDiscipline #MeditationChallenge #DailyMeditation "
            "#LongMeditation #MeditationSadhana #YogaPractice #MeditationLife"
        )

        try:
            result = schedule_stream(
                title=title,
                description=description,
                start_time_rfc3339=start_time,
                thumbnail_path=str(thumb_path),
                playlist_ids=playlists,
            )
        except Exception as e:
            print(f"[{index}] ОШИБКА при создании стрима: {e}")
            continue

        print(f"[{index}] Готово.")
        print(f"    broadcast_id: {result['broadcast_id']}")
        print(f"    watch_url:    {result['watch_url']}")
        print(f"    rtmp_url:     {result['rtmp_url']}")
        print(f"    stream_key:   {result['stream_key']}")


if __name__ == "__main__":
    main()
