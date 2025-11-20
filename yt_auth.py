import os
from typing import Sequence

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Имена файлов по умолчанию
CLIENT_SECRET_FILE = "client_secret_youtube.json"
TOKEN_FILE = "token_youtube.json"


def get_youtube_service(
    scopes: Sequence[str],
    client_secret_file: str = CLIENT_SECRET_FILE,
    token_file: str = TOKEN_FILE,
):
    """
    Возвращает объект youtube-service с заданными scopes.
    Использует token_file, при необходимости обновляет или переавторизуется.
    """
    creds = None

    # Пробуем использовать уже сохранённый токен
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    # Если токена нет или он невалиден — обновляем или авторизуем заново
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, scopes
            )
            creds = flow.run_local_server(port=0)

        # Сохраняем токен на будущее
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    # Создаём клиент YouTube Data API
    youtube = build("youtube", "v3", credentials=creds)
    return youtube
