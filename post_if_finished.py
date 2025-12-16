#!/usr/bin/env python3
"""Post to Facebook when a scheduled stream has finished."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

import requests

from day_index import date_to_index
from facebook_post import post_message

load_dotenv()

RUNTIME_DIR = Path(__file__).resolve().parent / "runtime"
RUNTIME_DIR.mkdir(exist_ok=True)

POSTED_STREAMS_FILE = RUNTIME_DIR / "posted_streams.json"


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
    if not POSTED_STREAMS_FILE.exists():
        return {}
    try:
        return json.loads(POSTED_STREAMS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_posted_stream(identifier: str) -> None:
    data = load_posted_streams()
    data[identifier] = True
    POSTED_STREAMS_FILE.write_text(json.dumps(data, indent=2))


def build_message(index: int) -> str:
    return (
        f"Master's touch meditation, day {index}.\n"
        f"Meditación del toque del Maestro, día {index}."
    )


def fetch_finished_status(day: str) -> dict | None:
    gas_url = os.getenv("GAS_WEBAPP_URL")
    gas_token = os.getenv("GAS_WEBAPP_TOKEN")

    if not gas_url or not gas_token:
        raise RuntimeError("GAS_WEBAPP_URL or GAS_WEBAPP_TOKEN not set (check .env)")

    try:
        response = requests.get(
            gas_url,
            params={"ep": "finishedOnDay", "day": day, "token": gas_token},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Ошибка сети при обращении к GAS: {exc}")
        return None

    try:
        return response.json()
    except ValueError:
        print("Не удалось распарсить JSON-ответ от GAS.")
        return None


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

    day = target_date.isoformat()
    print(f"Дата: {day}")
    print(f"Номер дня: {index}")

    status = fetch_finished_status(day)
    if status is None:
        return

    if status.get("ok") is not True:
        print("GAS вернул ошибку (ok != true) — выполнение остановлено.")
        return

    if not status.get("found"):
        print("Стрим ещё не завершён — публикация пропущена.")
        return

    stream = status.get("stream") or {}
    stream_url = stream.get("url") if isinstance(stream, dict) else None

    posted = load_posted_streams()
    identifier = stream_url or day

    if identifier in posted:
        print("Этот стрим уже опубликован в Facebook — пропуск.")
        return

    message = build_message(index)

    if args.dry_run:
        print("Dry run: would post to Facebook.")
        print(message)
        if stream_url:
            print(stream_url)
        return

    try:
        post_message(message, link=stream_url)
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка публикации в Facebook: {exc}")
        return

    save_posted_stream(identifier)
    print("Пост опубликован и отмечен в posted_streams.json.")


if __name__ == "__main__":
    main()
