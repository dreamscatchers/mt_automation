import os
from googleapiclient.http import MediaFileUpload
from yt_auth import get_youtube_service

# Полные права — чтобы можно было создавать стримы и загружать обложку
SCOPES = ["https://www.googleapis.com/auth/youtube"]

def create_live_broadcast(youtube, title: str, description: str, start_time_rfc3339: str):
    request = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": start_time_rfc3339,
            },
            "status": {
                "privacyStatus": "public"
            },
            "contentDetails": {
                "monitorStream": {"enableMonitorStream": True}
            }
        }
    )
    return request.execute()


def create_live_stream(youtube, title: str):
    request = youtube.liveStreams().insert(
        part="snippet,cdn,contentDetails",
        body={
            "snippet": {
                "title": title
            },
            "cdn": {
                "frameRate": "30fps",
                "ingestionType": "rtmp",
                "resolution": "1080p",
            }
        }
    )
    return request.execute()


def bind_broadcast_to_stream(youtube, broadcast_id: str, stream_id: str):
    request = youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id,
    )
    return request.execute()


def set_thumbnail(youtube, broadcast_id: str, thumbnail_path: str):
    upload = MediaFileUpload(thumbnail_path, mimetype="image/jpeg", resumable=False)
    request = youtube.thumbnails().set(
        videoId=broadcast_id,
        media_body=upload
    )
    return request.execute()


def schedule_stream(title: str, description: str, start_time_rfc3339: str, thumbnail_path: str):
    youtube = get_youtube_service(SCOPES)

    print("→ Создаём liveBroadcast…")
    broadcast = create_live_broadcast(youtube, title, description, start_time_rfc3339)
    broadcast_id = broadcast["id"]
    print("   broadcastId:", broadcast_id)

    print("→ Создаём liveStream…")
    stream = create_live_stream(youtube, title)
    stream_id = stream["id"]
    print("   streamId:", stream_id)

    print("→ Привязываем broadcast ↔ stream…")
    bind_broadcast_to_stream(youtube, broadcast_id, stream_id)

    print("→ Загружаем обложку…")
    set_thumbnail(youtube, broadcast_id, thumbnail_path)

    # RTMP данные
    ingestion = stream["cdn"]["ingestionInfo"]
    rtmp_url = ingestion["ingestionAddress"]
    stream_key = ingestion["streamName"]

    return {
        "broadcast_id": broadcast_id,
        "stream_id": stream_id,
        "watch_url": f"https://www.youtube.com/watch?v={broadcast_id}",
        "rtmp_url": rtmp_url,
        "stream_key": stream_key,
    }
