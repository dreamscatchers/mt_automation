# mt_openai_client.py
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY не найден в .env или окружении")
        _client = OpenAI(api_key=api_key)
    return _client
