#!/usr/bin/env python3
from __future__ import annotations

import requests


def main() -> None:
    print("Запрос к https://oauth2.googleapis.com/token ...")
    try:
        r = requests.get("https://oauth2.googleapis.com/token")
        print("OK, статус:", r.status_code)
        print("Ответ (первые 200 символов):")
        print(r.text[:200])
    except Exception as e:
        print("ОШИБКА:", repr(e))


if __name__ == "__main__":
    main()
