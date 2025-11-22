from yt_auth import get_youtube_service

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

youtube = get_youtube_service(SCOPES)

resp = youtube.liveStreams().list(
    part="id,snippet,cdn",
    mine=True,
    maxResults=50
).execute()

items = resp.get("items", [])
print(f"Найдено {len(items)} liveStream объектов:\n")

for s in items:
    stream_id = s["id"]
    name = s["snippet"]["title"]
    ingestion = s["cdn"]["ingestionInfo"]
    
    url = ingestion.get("ingestionAddress")
    key = ingestion.get("streamName")
    
    print(f"ID:    {stream_id}")
    print(f"Name:  {name}")
    print(f"URL:   {url}")
    print(f"Key:   {key}")
    print("-" * 40)
