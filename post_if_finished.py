#!/usr/bin/env python3
"""Post to Facebook when a scheduled stream has finished."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Dict, Optional

from day_index import date_to_index
from facebook_post import post_message
from yt_auth import get_youtube_service
from yt_stream import (
    SCOPES as YT_SCOPES,
    find_broadcast_by_day,
    load_live_broadcasts,
)


POSTED_STREAMS_PATH = Path("posted_streams.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Post to Facebook if the stream for the given date has completed. "
            "Date format: YYYY-MM-DD."
        )
    )
    parser.add_argument(
        "date",
        nargs="?",
        help="Target date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without posting or writing files.",
    )
    return parser.parse_args()


def parse_target_date(raw_date: Optional[str]) -> date:
    if raw_date:
        try:
            return date.fromisoformat(raw_date)
        except ValueError as exc:  # noqa: BLE001
            raise ValueError("Date must be in YYYY-MM-DD format") from exc
    return date.today()


def load_posted_streams() -> Dict[str, bool]:
    if not POSTED_STREAMS_PATH.exists():
        return {}
    try:
        return json.loads(POSTED_STREAMS_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_posted_stream(broadcast_id: str) -> None:
    data = load_posted_streams()
    data[broadcast_id] = True
    POSTED_STREAMS_PATH.write_text(json.dumps(data, indent=2))


def get_broadcast_status(youtube, broadcast_id: str) -> tuple[str, bool]:
    resp = youtube.liveBroadcasts().list(
        part="status,contentDetails", id=broadcast_id
    ).execute()
    items = resp.get("items", [])
    if not items:
        return "not found", False

    item = items[0]
    status = item.get("status", {}).get("lifeCycleStatus", "unknown")
    content_details = item.get("contentDetails", {})
    finished = status == "complete" or bool(content_details.get("actualEndTime"))
    return status, finished


def build_message(index: int) -> str:
    return (
        f"Master's touch meditation, day {index}.\n"
        f"Meditación del toque del Maestro, día {index}."
    )


def main() -> None:
    args = parse_args()

    try:
        target_date = parse_target_date(args.date)
    except ValueError as exc:
        print(f"Ошибка даты: {exc}")
        return

    try:
        index = date_to_index(target_date)
    except ValueError as exc:
        print(f"Ошибка вычисления номера дня: {exc}")
        return

    print(f"Дата: {target_date.isoformat()}")
    print(f"Номер дня: {index}")

    youtube = get_youtube_service(YT_SCOPES)

    broadcasts = load_live_broadcasts(youtube)
    broadcast = find_broadcast_by_day(index, broadcasts)
    if not broadcast:
        print("Стрим для этого дня не найден — публикация невозможна.")
        return

    broadcast_id = broadcast.get("id")
    if not broadcast_id:
        print("Не удалось получить broadcast_id для этого дня.")
        return

    print("Стрим найден.")
    print(f"broadcast_id: {broadcast_id}")
    status, finished = get_broadcast_status(youtube, broadcast_id)
    print(f"Статус трансляции: {status}")

    if not finished:
        print("Трансляция ещё не завершена — публикация пропущена.")
        return

    posted = load_posted_streams()
    if broadcast_id in posted:
        print("Этот стрим уже опубликован в Facebook — пропуск.")
        return

    message = build_message(index)
    youtube_url = f"https://youtube.com/live/{broadcast_id}"

    if args.dry_run:
        print("Dry run: would post to Facebook.")
        print(message)
        print(youtube_url)
        return

    try:
        post_message(message, link=youtube_url)
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка публикации в Facebook: {exc}")
        return

    save_posted_stream(broadcast_id)
    print("Пост опубликован и отмечен в posted_streams.json.")


if __name__ == "__main__":
    main()
