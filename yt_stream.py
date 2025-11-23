#!/usr/bin/env python3
from __future__ import annotations

from typing import List, Optional, Tuple

from dotenv import dotenv_values
from googleapiclient.http import MediaFileUpload

from yt_auth import get_youtube_service


# --------------------------------------------------------------------
# Конфиг из .env (НЕ из окружения)
# --------------------------------------------------------------------
config = dotenv_values(".env")

PERSISTENT_STREAM_ID: Optional[str] = config.get("PERSISTENT_STREAM_ID")

# Те же SCOPES, что и в schedule_range.py
SCOPES: List[str] = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

PlaylistSpec = Tuple[str, str]  # (playlist_id, alias)


# --------------------------------------------------------------------
# Низкоуровневые операции с YouTube API
# --------------------------------------------------------------------
def create_live_broadcast(
    youtube,
    title: str,
    description: str,
    start_time_rfc3339: str,
    privacy_status: str = "public",
    made_for_kids: bool = False,
    enable_auto_start: bool = False,
    enable_auto_stop: bool = False,
):
    """Создаёт liveBroadcast и возвращает ответ API."""
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "scheduledStartTime": start_time_rfc3339,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
        },
        "contentDetails": {
            "enableAutoStart": enable_auto_start,
            "enableAutoStop": enable_auto_stop,
        },
    }

    resp = youtube.liveBroadcasts().insert(
        part="snippet,contentDetails,status",
        body=body,
    ).execute()

    return resp


def create_live_stream(youtube, title: str):
    """Создаёт RTMP liveStream и возвращает ответ API."""

    body = {
        "snippet": {"title": title},
        "cdn": {
            "ingestionType": "rtmp",
            "resolution": "variable",
            "frameRate": "variable",
        },
    }

    resp = (
        youtube.liveStreams()
        .insert(
            part="snippet,cdn",
            body=body,
        )
        .execute()
    )

    return resp


def bind_broadcast_to_stream(
    youtube,
    broadcast_id: str,
    stream_id: str,
):
    """Привязывает liveBroadcast к существующему liveStream."""
    youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id,
    ).execute()


def set_thumbnail(
    youtube,
    broadcast_id: str,
    thumbnail_path: str,
):
    """Загружает thumbnail для видео/стрима."""
    media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
    youtube.thumbnails().set(
        videoId=broadcast_id,
        media_body=media,
    ).execute()


def add_video_to_playlist(
    youtube,
    playlist_id: str,
    video_id: str,
):
    """Добавляет видео/стрим в плейлист."""
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id,
            },
        }
    }

    youtube.playlistItems().insert(
        part="snippet",
        body=body,
    ).execute()


# --------------------------------------------------------------------
# Основная высокоуровневая функция
# --------------------------------------------------------------------
def schedule_stream(
    title: str,
    description: str,
    start_time_rfc3339: str,
    thumbnail_path: str,
    playlist_ids: Optional[List[PlaylistSpec]] = None,
    use_persistent_stream: bool = True,
    enable_auto_start: bool = False,
    enable_auto_stop: bool = False,
) -> dict:
    """
    Создаёт запланированный стрим, привязывает к ПЕРМАНЕНТНОМУ потоку
    (или создаёт отдельный liveStream) и добавляет его в плейлисты.

    Сигнатура совместима с рабочим schedule_range.py:

      - title: заголовок
      - description: описание
      - start_time_rfc3339: время начала (RFC 3339, с таймзоной)
      - thumbnail_path: путь к JPG-обложке
      - playlist_ids: список кортежей (playlist_id, alias)
      - use_persistent_stream: True — привязывать к постоянному потоку,
        False — создавать отдельный liveStream для эфира
      - enable_auto_start / enable_auto_stop: прокидываются в broadcast

    Возвращает dict:
      {
        "broadcast_id": ...,
        "stream_id":    ... (PERSISTENT_STREAM_ID или созданный),
        "watch_url":    ...,
        "rtmp_url":     ...,
        "stream_key":   ...,
      }
    """
    # YouTube API клиент
    youtube = get_youtube_service(SCOPES)

    print("→ Создаём liveBroadcast…")
    broadcast = create_live_broadcast(
        youtube=youtube,
        title=title,
        description=description,
        start_time_rfc3339=start_time_rfc3339,
        enable_auto_start=enable_auto_start,
        enable_auto_stop=enable_auto_stop,
    )
    broadcast_id = broadcast["id"]
    print("   broadcastId:", broadcast_id)

    if use_persistent_stream:
        if not PERSISTENT_STREAM_ID:
            raise RuntimeError(
                "PERSISTENT_STREAM_ID не задан в .env. "
                "Добавь его в automation/.env."
            )

        print("→ Привязываем broadcast к постоянному потоку…")
        stream_id = PERSISTENT_STREAM_ID
    else:
        print("→ Создаём отдельный liveStream для этого эфира…")
        stream_resp = create_live_stream(youtube=youtube, title=title)
        stream_id = stream_resp["id"]
        print("   streamId:", stream_id)

    bind_broadcast_to_stream(
        youtube=youtube,
        broadcast_id=broadcast_id,
        stream_id=stream_id,
    )

    print("→ Загружаем обложку…")
    set_thumbnail(
        youtube=youtube,
        broadcast_id=broadcast_id,
        thumbnail_path=thumbnail_path,
    )

    # Получаем RTMP URL и ключ выбранного потока
    print("→ Получаем данные потока…")
    stream_resp = youtube.liveStreams().list(
        part="cdn",
        id=stream_id,
    ).execute()

    items = stream_resp.get("items", [])
    if not items:
        raise RuntimeError(
            f"Не найден liveStream с id={stream_id}. "
            "Проверь, что ты указал корректный stream id."
        )

    ingestion = items[0]["cdn"]["ingestionInfo"]
    rtmp_url = ingestion["ingestionAddress"]
    stream_key = ingestion["streamName"]

    # Добавляем в плейлисты
    if playlist_ids:
        for pid, alias in playlist_ids:
            print(f"→ Добавляем в плейлист: {alias}…")
            # ВАЖНО: в плейлист добавляем именно broadcast_id (видео),
            # как в твоём рабочем варианте
            add_video_to_playlist(
                youtube=youtube,
                playlist_id=pid,
                video_id=broadcast_id,
            )
        print("→ Добавление в плейлисты завершено.")
    else:
        print("Плейлисты не заданы, пропускаю добавление.")

    watch_url = f"https://www.youtube.com/watch?v={broadcast_id}"

    return {
        "broadcast_id": broadcast_id,
        "stream_id": stream_id,
        "watch_url": watch_url,
        "rtmp_url": rtmp_url,
        "stream_key": stream_key,
    }
