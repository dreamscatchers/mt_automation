import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

DEZGO_API_KEY = os.getenv("DEZGO_API_KEY")
BASE_URL = "https://api.dezgo.com"


def generate_image_to_jpeg(
    prompt: str,
    out_path: str,
    *,
    endpoint: str = "text2image_sdxl",
    width: int = 1024,
    height: int = 576,
) -> str:
    """
    Генерирует картинку через Dezgo и сохраняет как JPEG (16:9).
    """
    if not DEZGO_API_KEY:
        raise RuntimeError("DEZGO_API_KEY is not set in .env")

    url = f"{BASE_URL}/{endpoint}"

    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        # сюда позже можно добавить negative_prompt, steps, seed и т.п.
    }

    headers = {
        "X-Dezgo-Key": DEZGO_API_KEY,
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()

    # API возвращает PNG-байты, конвертируем сразу в JPEG
    img = Image.open(BytesIO(resp.content))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(out_path, format="JPEG", quality=95)

    return out_path
def generate_controlnet_openpose(
    init_image_path: str,
    prompt: str,
    out_path: str,
    *,
    width: int = 1024,
    height: int = 576,
):
    """
    ControlNet OpenPose (с руками). Гарантированное сохранение позы и мудры.
    """
    if not DEZGO_API_KEY:
        raise RuntimeError("DEZGO_API_KEY is not set in .env")

    url = f"{BASE_URL}/controlnet"

    # читаем изображение как байты
    with open(init_image_path, "rb") as f:
        image_bytes = f.read()

    files = {
        "init_image": ("init.png", image_bytes, "image/png")
    }

    data = {
        "prompt": prompt,
        "width": width,
        "height": height,
        # "model": "openpose",     # <<< ключевой параметр
        "detect_hands": "true",  # <<< обязательно включаем руки!
    }

    headers = {
        "X-Dezgo-Key": DEZGO_API_KEY,
    }

    # resp = requests.post(url, headers=headers, data=data, files=files, timeout=120)
    # resp.raise_for_status()

    resp = requests.post(url, headers=headers, data=data, files=files, timeout=120)

    if resp.status_code != 200:
        print("Status:", resp.status_code)
        print("Response text:", resp.text)
        resp.raise_for_status()


    from PIL import Image
    from io import BytesIO

    img = Image.open(BytesIO(resp.content))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(out_path, format="JPEG", quality=95)

    return out_path
