#!/usr/bin/env python3
import sys
import os
import argparse

from datetime import date

from dotenv import load_dotenv
from yt_stream import schedule_stream, SCOPES as YT_SCOPES
from yt_auth import get_youtube_service
from generate_image_gemini import generate_image
from day_index import index_to_date
from mtm_content import (
    build_stream_description,
    build_stream_title,
    get_thumbnail_path,
)



load_dotenv()

# ---------------------------------------------------------
# РЕЖИМЫ
# ---------------------------------------------------------
VERBOSE_EXISTING = False  # True = выводить ВСЕ существующие заголовки
# ---------------------------------------------------------

# Плейлисты из .env
GENERAL_PLAYLIST_ID = os.getenv("GENERAL_YT_PLAYLIST_ID")
HALF_PLAYLIST_ID = os.getenv("HALF_MTM_PLAYLIST_ID")
FULL_PLAYLIST_ID = os.getenv("FULL_MTM_PLAYLIST_ID")


# ---------------------------------------------------------
# ПРОСТЫЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ---------------------------------------------------------

def date_to_start_time_rfc3339(d: date) -> str:
    """Старт всегда в 10:00 -04:00."""
    return f"{d.isoformat()}T10:00:00-04:00"


def parse_range(arg: str) -> tuple[int, int]:
    if "-" not in arg:
        raise ValueError("Используй диапазон вида 275-282")
    a, b = arg.split("-", 1)
    a, b = int(a), int(b)
    return (a, b) if a <= b else (b, a)


def choose_playlists_for_date(d: date) -> list[tuple[str, str]]:
    play = []

    # Всегда — General
    if GENERAL_PLAYLIST_ID:
        play.append((GENERAL_PLAYLIST_ID, "General"))

    is_sunday = d.weekday() == 6

    if is_sunday:
        if FULL_PLAYLIST_ID:
            play.append((FULL_PLAYLIST_ID, "Full Version"))
    else:
        if HALF_PLAYLIST_ID:
            play.append((HALF_PLAYLIST_ID, "1/2 Version"))

    return play


# ---------------------------------------------------------
# ПОЛУЧЕНИЕ СПИСКА ВСЕХ ВИДЕО/СТРИМОВ (UPLOADS PLAYLIST)
# ---------------------------------------------------------

def get_uploads_playlist_id(youtube) -> str:
    resp = youtube.channels().list(
        part="contentDetails",
        mine=True
    ).execute()

    items = resp.get("items", [])
    if not items:
        raise RuntimeError("Не удалось получить канал (mine=True).")

    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def load_existing_titles_from_uploads(youtube) -> list[str]:
    uploads_id = get_uploads_playlist_id(youtube)
    titles = []

    req = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_id,
        maxResults=50,
    )

    while req is not None:
        resp = req.execute()
        for item in resp.get("items", []):
            snippet = item.get("snippet", {})
            title = snippet.get("title")
            if title:
                titles.append(title)

        req = youtube.playlistItems().list_next(
            previous_request=req,
            previous_response=resp
        )

    if VERBOSE_EXISTING:
        print(f"Загружено {len(titles)} видео/стримов:")
        for t in titles:
            print("  •", t)
    else:
        print(f"Найдено {len(titles)} существующих видео/стримов.")

    return titles


def day_already_has_stream(index: int, existing_titles: list[str]) -> bool:
    key = f"Day {index} of 1000"

    matches = [t for t in existing_titles if key in t]

    if matches:
        if VERBOSE_EXISTING:
            print(f"[{index}] Уже есть стримы с '{key}':")
            for t in matches:
                print("      →", t)
        else:
            print(f"[{index}] День уже существует.")
        return True

    print(f"[{index}] Стрима для этого дня нет.")
    return False

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "YouTube stream scheduler for Master's Touch Meditation.\n\n"
            "Примеры:\n"
            "  schedule_range.py 285-300            # dry-run (ничего не создаёт)\n"
            "  schedule_range.py 285-300 --no-dry-run  # создать реальные стримы\n"
            "  schedule_range.py 285-300 -e         # подробно о существующих стримах\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "range",
        help="Диапазон дней в формате START-END, например: 285-287",
    )

    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=True,
        help="Запуск в тестовом режиме (по умолчанию включён)",
    )

    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Отключить тестовый режим и выполнять реальные действия",
    )

    parser.add_argument(
        "--verbose-existing",
        "-e",
        dest="verbose_existing",
        action="store_true",
        help="Показывать подробную информацию о уже существующих стримах",
    )

    parser.add_argument(
        "--stream-mode",
        choices=["persistent", "unique"],
        default="persistent",
        help=(
            "Stream mode: 'persistent' uses PERSISTENT_STREAM_ID, 'unique' "
            "creates a new liveStream (new stream key) for each broadcast."
        ),
    )

    parser.add_argument(
        "--auto-start-stop",
        action="store_true",
        help=(
            "Set enableAutoStart and enableAutoStop on the YouTube broadcast so"
            " Studio automatically starts and stops the scheduled stream when"
            " RTMP input arrives from the encoder (e.g. Prism) without manual"
            " Go Live."
        ),
    )

    return parser.parse_args()


# ---------------------------------------------------------
# ОСНОВНАЯ ЛОГИКА
# ---------------------------------------------------------

def main():
    global VERBOSE_EXISTING

    args = parse_args()

    # Парсим диапазон из args.range
    try:
        start, end = parse_range(args.range)
    except Exception as e:
        print("Ошибка диапазона:", e)
        sys.exit(1)

    DRY_RUN = args.dry_run
    VERBOSE_EXISTING = args.verbose_existing

    print(f"Проверяем / создаём стримы для дней {start}–{end}")
    print(f"DRY_RUN = {DRY_RUN}")
    print(f"VERBOSE_EXISTING = {VERBOSE_EXISTING}")
    print(f"STREAM_MODE = {args.stream_mode}")
    print(f"AUTO_START_STOP = {args.auto_start_stop}")

    youtube = get_youtube_service(YT_SCOPES)
    existing_titles = load_existing_titles_from_uploads(youtube)

    use_persistent = args.stream_mode == "persistent"

    for index in range(start, end + 1):

        # 1) Проверка существования
        if day_already_has_stream(index, existing_titles):
            print(f"[{index}] Пропуск.\n")
            continue

        # 2) Данные нового дня
        d = index_to_date(index)
        start_time = date_to_start_time_rfc3339(d)
        thumb_path = get_thumbnail_path(index)

        # Если обложки нет — пробуем сгенерировать
        if not thumb_path.exists():
            if DRY_RUN:
                # В DRY_RUN режиме не тратим запросы к Gemini, просто сообщаем
                print(f"[{index}] Нет обложки {thumb_path}. DRY_RUN — не генерирую, пропуск.\n")
                continue

            print(f"[{index}] Нет обложки {thumb_path}, генерирую через Gemini...")

            try:
                generate_image(index)
            except Exception as e:
                print(f"[{index}] ОШИБКА при генерации обложки: {e}. Пропуск.\n")
                continue

            # На всякий случай проверим ещё раз, что файл появился
            if not thumb_path.exists():
                print(f"[{index}] После генерации обложка {thumb_path} не найдена. Пропуск.\n")
                continue


        playlists = choose_playlists_for_date(d)

        print(f"\n[{index}] Нужно создать стрим:")
        print(f"    Дата:       {d.isoformat()}")
        print(f"    Старт:      {start_time}")
        print(f"    Обложка:    {thumb_path}")
        print( "    Плейлисты:")
        for _, alias in playlists:
            print(f"      • {alias}")

        title = build_stream_title(index)
        description = build_stream_description()

        if DRY_RUN:
            print(f"[{index}] DRY_RUN: стрим НЕ создаю.\n")
            continue

        # 3) СОЗДАНИЕ стрима
        try:
            result = schedule_stream(
                title=title,
                description=description,
                start_time_rfc3339=start_time,
                thumbnail_path=str(thumb_path),
                playlist_ids=playlists,
                use_persistent_stream=use_persistent,
                enable_auto_start=args.auto_start_stop,
                enable_auto_stop=args.auto_start_stop,
            )
        except Exception as e:
            print(f"[{index}] ОШИБКА при создании стрима:", e, "\n")
            continue

        print(f"[{index}] Создан:")
        print("    watch URL:", result["watch_url"])
        print("    RTMP URL: ", result["rtmp_url"])
        print("    Stream Key:", result["stream_key"])
        print()


if __name__ == "__main__":
    main()
