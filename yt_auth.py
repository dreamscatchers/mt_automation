import os
from pathlib import Path
from typing import Sequence

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Имена файлов по умолчанию
CLIENT_SECRET_FILE = "config/client_secret_youtube.json"
TOKEN_FILE = "config/token_youtube.json"
TOKEN_REVOKED_FLAG = Path("automation/config/.youtube_token_revoked")


def _flag_is_active(flag_path: Path, token_path: Path) -> bool:
    if not flag_path.exists():
        return False

    if not token_path.exists():
        return False

    return token_path.stat().st_mtime <= flag_path.stat().st_mtime


def _mark_token_revoked(flag_path: Path) -> None:
    if flag_path.exists():
        return

    flag_path.parent.mkdir(parents=True, exist_ok=True)
    flag_path.write_text("revoked\n", encoding="utf-8")
    print("YouTube OAuth: refresh token revoked. Manual re-auth required.")


def _clear_revoked_flag(flag_path: Path) -> None:
    if flag_path.exists():
        flag_path.unlink()


def get_youtube_service(
    scopes: Sequence[str],
    client_secret_file: str = CLIENT_SECRET_FILE,
    token_file: str = TOKEN_FILE,
):
    """
    Возвращает объект youtube-service с заданными scopes.
    Использует token_file, при необходимости обновляет или переавторизуется.
    """
    token_path = Path(token_file)
    flag_path = TOKEN_REVOKED_FLAG

    if _flag_is_active(flag_path, token_path):
        return None

    creds = None

    # Пробуем использовать уже сохранённый токен
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    # Если токена нет или он невалиден — обновляем или авторизуем заново
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as exc:
                if "invalid_grant" in str(exc):
                    _mark_token_revoked(flag_path)
                    return None
                raise
            else:
                _clear_revoked_flag(flag_path)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, scopes
            )
            creds = flow.run_local_server(port=0)
            _clear_revoked_flag(flag_path)

        # Сохраняем токен на будущее
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    # Создаём клиент YouTube Data API
    youtube = build("youtube", "v3", credentials=creds)
    return youtube
