from yt_auth import get_youtube_service

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


def main():
    youtube = get_youtube_service(SCOPES)

    response = youtube.channels().list(
        part="snippet,contentDetails",
        mine=True,
    ).execute()

    for item in response.get("items", []):
        title = item["snippet"]["title"]
        channel_id = item["id"]
        print("Канал:", title)
        print("ID канала:", channel_id)


if __name__ == "__main__":
    main()
