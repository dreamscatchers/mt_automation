#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from googleapiclient.http import MediaFileUpload
from dotenv import dotenv_values

from day_index import date_to_index
from generate_image_gemini import generate_image
from mtm_content import (
    build_stream_description,
    build_stream_title,
    get_thumbnail_path,
)
from yt_auth import get_youtube_service
from yt_stream import SCOPES

BackupVideo = Tuple[str, str, date, Optional[str]]  # (video_id, title, date, published_at)


DATE_TITLE_PATTERN = re.compile(r"^VID[ _]+(\d{8})[ _].+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Оформляет резервное видео с телефона: устанавливает заголовок, описание "
            "и thumbnail по стандарту стримов."
        )
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Дата резервного видео в формате YYYY-MM-DD (по умолчанию — сегодня)",
    )

    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=True,
        help="Проверочный запуск без изменений на YouTube (по умолчанию)",
    )

    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Внести реальные изменения на YouTube",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Подробный вывод",
    )

    return parser.parse_args()


def parse_target_date(arg_date: Optional[str]) -> date:
    if arg_date:
        try:
            return date.fromisoformat(arg_date)
        except ValueError:
            raise ValueError("--date должен быть в формате YYYY-MM-DD")
    return date.today()


def get_backup_playlist_id() -> str:
    env = dotenv_values(".env")
    playlist_id = env.get("BACKUP_YT_PLAYLIST_ID")
    if not playlist_id:
        raise RuntimeError(
            "BACKUP_YT_PLAYLIST_ID не задан в .env — добавьте резервный плейлист"
        )
    return playlist_id


def get_uploads_playlist_id(youtube) -> str:
    resp = youtube.channels().list(part="contentDetails", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        raise RuntimeError("Не удалось получить канал (mine=True)")
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def extract_date_from_title(title: str) -> Optional[date]:
    match = DATE_TITLE_PATTERN.match(title)
    if not match:
        return None
    raw_date = match.group(1)
    try:
        return datetime.strptime(raw_date, "%Y%m%d").date()
    except ValueError:
        return None


def load_uploads_items(youtube, verbose: bool = False) -> List[Dict[str, Any]]:
    uploads_id = get_uploads_playlist_id(youtube)
    items: List[Dict[str, Any]] = []

    req = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploads_id,
        maxResults=50,
    )

    while req is not None:
        resp = req.execute()
        batch = resp.get("items", [])
        items.extend(batch)
        if verbose:
            print(f"Загружено {len(items)} элементов uploads playlist...")
        req = youtube.playlistItems().list_next(
            previous_request=req, previous_response=resp
        )

    return items


def to_datetime_or_none(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def find_backup_video(
    items: List[Dict[str, Any]],
    target_date: date,
    verbose: bool = False,
) -> Optional[BackupVideo]:
    candidates: List[BackupVideo] = []

    for item in items:
        snippet = item.get("snippet", {})
        title = snippet.get("title", "")
        parsed_date = extract_date_from_title(title)
        if parsed_date != target_date:
            continue

        video_id = snippet.get("resourceId", {}).get("videoId")
        if not video_id:
            continue

        published = (
            item.get("contentDetails", {}).get("videoPublishedAt")
            or snippet.get("publishedAt")
        )
        candidates.append((video_id, title, parsed_date, published))

    if not candidates:
        return None

    def sort_key(entry: BackupVideo):
        _, _, _, published = entry
        dt = to_datetime_or_none(published)
        return dt or datetime.min

    candidates.sort(key=sort_key, reverse=True)
    if verbose and len(candidates) > 1:
        print(
            "Найдено несколько резервных видео за дату, выберу самое свежее по publishedAt:"
        )
        for c in candidates:
            print(f"  • {c[0]} — {c[1]} — {c[3]}")

    return candidates[0]


def print_video_info(video: BackupVideo) -> None:
    video_id, old_title, _, published = video
    print("Найдено резервное видео:")
    print(f"  videoId:     {video_id}")
    print(f"  title:       {old_title}")
    print(f"  publishedAt: {published}")


def ensure_thumbnail(index: int, dry_run: bool) -> Optional[str]:
    thumb_path = get_thumbnail_path(index)

    if thumb_path.exists():
        return str(thumb_path)

    print(f"Обложка {thumb_path} отсутствует.")
    if dry_run:
        print("DRY_RUN — не генерирую, только сообщаю о необходимости.")
        return None

    try:
        print("Генерирую обложку через Gemini…")
        generate_image(index)
    except Exception as e:  # noqa: BLE001
        print(f"Ошибка при генерации обложки: {e}")
        return None

    if thumb_path.exists():
        print(f"Сгенерированная обложка: {thumb_path}")
        return str(thumb_path)

    print("После генерации обложка всё ещё не найдена.")
    return None


def update_video_metadata(
    youtube,
    video_id: str,
    new_title: str,
    new_description: str,
    dry_run: bool,
    verbose: bool = False,
) -> None:
    resp = (
        youtube.videos()
        .list(part="snippet", id=video_id)
        .execute()
    )
    items = resp.get("items", [])
    if not items:
        raise RuntimeError(f"Видео с id={video_id} не найдено")

    snippet = items[0].get("snippet", {})
    old_title = snippet.get("title", "")
    old_description = snippet.get("description", "")

    print("Обновление метаданных:")
    print(f"  Старый title: {old_title}")
    print(f"  Новый  title: {new_title}")
    if verbose:
        print("  Старое описание:")
        print(old_description)
        print("  Новое описание:")
        print(new_description)
    else:
        print("  Описание будет заменено на стандартное.")

    if dry_run:
        print("DRY_RUN — изменения snippet не применяются.")
        return

    new_snippet = dict(snippet)
    new_snippet["title"] = new_title
    new_snippet["description"] = new_description

    youtube.videos().update(
        part="snippet",
        body={"id": video_id, "snippet": new_snippet},
    ).execute()
    print("Snippet обновлён.")


def update_thumbnail(youtube, video_id: str, thumbnail_path: str, dry_run: bool) -> None:
    print(f"Обновление thumbnail ({thumbnail_path})…")
    if dry_run:
        print("DRY_RUN — thumbnail не загружается.")
        return

    media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
    youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    print("Thumbnail обновлён.")


def add_video_to_playlist(
    youtube,
    playlist_id: str,
    video_id: str,
    dry_run: bool,
) -> None:
    print(f"Добавление видео в плейлист BACKUP_YT_PLAYLIST_ID={playlist_id}")

    if dry_run:
        print("DRY_RUN — видео было бы добавлено в плейлист, но вызов API пропущен.")
        return

    try:
        req = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50,
        )

        while req is not None:
            resp = req.execute()
            items = resp.get("items", [])
            for item in items:
                resource = item.get("snippet", {}).get("resourceId", {})
                if resource.get("videoId") == video_id:
                    print("Видео уже есть в плейлисте, пропускаю.")
                    return

            req = youtube.playlistItems().list_next(
                previous_request=req, previous_response=resp
            )
    except Exception as e:  # noqa: BLE001
        print(f"Ошибка при проверке плейлиста: {e}")
        return

    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id,
                    },
                }
            },
        ).execute()
        print("Видео добавлено в плейлист.")
    except Exception as e:  # noqa: BLE001
        print(f"Ошибка при добавлении видео в плейлист: {e}")


def main():
    args = parse_args()

    try:
        target_date = parse_target_date(args.date)
    except ValueError as e:
        print("Ошибка даты:", e)
        sys.exit(1)

    print(f"Целевая дата резервного видео: {target_date.isoformat()}")
    print(f"DRY_RUN: {args.dry_run}")
    try:
        backup_playlist_id = get_backup_playlist_id()
    except RuntimeError as e:
        print("Ошибка переменной окружения:", e)
        sys.exit(1)

    youtube = get_youtube_service(SCOPES)

    try:
        items = load_uploads_items(youtube, verbose=args.verbose)
    except Exception as e:  # noqa: BLE001
        print("Ошибка при загрузке списка видео:", e)
        sys.exit(1)

    video = find_backup_video(items, target_date, verbose=args.verbose)
    if not video:
        print("Видео с нужной датой не найдено в uploads playlist.")
        sys.exit(1)

    print_video_info(video)
    try:
        index = date_to_index(target_date)
    except ValueError as e:
        print("Ошибка при вычислении номера дня:", e)
        sys.exit(1)

    new_title = build_stream_title(index)
    new_description = build_stream_description()
    update_video_metadata(
        youtube=youtube,
        video_id=video[0],
        new_title=new_title,
        new_description=new_description,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    thumb_path = ensure_thumbnail(index=index, dry_run=args.dry_run)
    if thumb_path:
        update_thumbnail(
            youtube=youtube,
            video_id=video[0],
            thumbnail_path=thumb_path,
            dry_run=args.dry_run,
        )
    else:
        print("Thumbnail не обновлён (файл отсутствует).")

    add_video_to_playlist(
        youtube=youtube,
        playlist_id=backup_playlist_id,
        video_id=video[0],
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
