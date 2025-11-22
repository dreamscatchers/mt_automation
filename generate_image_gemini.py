#!/usr/bin/env python3
import os
from pathlib import Path
from io import BytesIO

from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

from prompt_generator import generate_prompt


# Базовые пути проекта
PROJECT_ROOT = Path.home() / "projects" / "master_touch_meditation"
SEQUENCE_DIR = PROJECT_ROOT / "sequence"
SOURCES_DIR = SEQUENCE_DIR / "sources"

# Базовая картинка для редактирования
BASE_IMAGE = PROJECT_ROOT / "automation" / "sources" / "front_base.png"

# Модель Nano Banana
MODEL_ID = "gemini-2.5-flash-image"


def _init_client() -> genai.Client:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY не найден в окружении/.env")
    return genai.Client(api_key=api_key)


def _get_output_paths(day_number: int) -> tuple[Path, Path]:
    """
    Возвращает пути:
    - png_path:  .../sequence/sources/XXXX.png
    - jpg_path:  .../sequence/XXXX.jpeg
    """
    day_str = str(day_number)
    png_path = SOURCES_DIR / f"{day_str}.png"
    jpg_path = SEQUENCE_DIR / f"{day_str}.jpg"
    return png_path, jpg_path


def generate_image(day_number: int) -> None:
    client = _init_client()

    prompt = generate_prompt(day_number)
    base_img = Image.open(BASE_IMAGE).convert("RGB")

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[prompt, base_img],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
            ),
        ),
    )

    # Достаём байты изображения
    image_bytes = None
    for part in response.parts:
        if getattr(part, "inline_data", None) is not None:
            image_bytes = part.inline_data.data
            break

    if not image_bytes:
        raise RuntimeError("Модель не вернула изображение")

    img = Image.open(BytesIO(image_bytes))

    png_path, jpg_path = _get_output_paths(day_number)

    # PNG в sources/
    png_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(png_path, format="PNG")

    # JPEG-копия в sequence/
    jpg_path.parent.mkdir(parents=True, exist_ok=True)
    # На всякий случай приводим к RGB (на случай прозрачности)
    img_rgb = img.convert("RGB")
    img_rgb.save(jpg_path, format="JPEG", quality=95)

    print(f"Saved PNG:  {png_path}")
    print(f"Saved JPEG: {jpg_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_image_gemini.py <day_number>")
        raise SystemExit(1)

    day_number = int(sys.argv[1])
    if day_number < 1:
        print("day_number должен быть >= 1")
        raise SystemExit(1)

    generate_image(day_number)
