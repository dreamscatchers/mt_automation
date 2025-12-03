#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

# Делаем импорт так, чтобы скрипт работал из папки utils/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from yt_auth import get_youtube_service, TOKEN_FILE
from yt_stream import SCOPES as YT_SCOPES


def main() -> None:
    token_path = Path(TOKEN_FILE)

    print("=== Обновление OAuth токена для YouTube ===")
    print("Корневая директория:", ROOT)
    print("Файл токена:", token_path)

    # 1. Удаляем старый токен, если есть
    if token_path.exists():
        print(f"Удаляю старый токен: {token_path}")
        token_path.unlink()
    else:
        print("Старый токен не найден — создадим новый.")

    # 2. Запускаем авторизацию
    print("Запускаю OAuth-авторизацию в браузере...")
    youtube = get_youtube_service(YT_SCOPES)

    # 3. Шаг успешного завершения
    if youtube:
        print("Новый токен успешно создан.")
        print("Сохранён в:", token_path)
    else:
        print("Ошибка: YouTube service не создан.")

    print("Готово.")


if __name__ == "__main__":
    main()
