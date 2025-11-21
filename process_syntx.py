#!/home/yyk/.pyenv/versions/3.11.9/bin/python3.11


import os
import re
import sys
import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


SEQUENCE_DIR = Path.home() / "projects" / "master_touch_meditation" / "sequence"
SOURCES_DIR = SEQUENCE_DIR / "sources"


def to_data_url(path: Path) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return "data:image/png;base64," + b64


def extract_number_from_text(text: str) -> int:
    nums = re.findall(r"\d+", text)
    for n in nums:
        value = int(n)
        if 1 <= value <= 2000:
            return value
    raise ValueError(f"Не удалось выделить номер дня: {text!r}")


def read_day_number_with_openai(client: OpenAI, image_path: Path) -> int:
    prompt = (
        "На изображении присутствует номер дня, например 'Day 123', "
        "'123 of 1000', 'День 123'. Определи номер и ответь только числом."
    )

    image_data_url = to_data_url(image_path)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            }
        ],
    )

    text_parts = []
    for item in response.output:
        if getattr(item, "type", None) == "message":
            for c in getattr(item, "content", []):
                if getattr(c, "type", None) == "output_text":
                    text_parts.append(c.text)

    if not text_parts:
        raise RuntimeError("Не удалось извлечь ответ из модели")

    full_text = " ".join(text_parts)
    return extract_number_from_text(full_text)


def convert_png_to_jpg(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGB")
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, format="JPEG", quality=95)


def main():
    if len(sys.argv) != 2:
        print("Usage: process_syntx.py <path-to-gemini-image>")
        sys.exit(1)

    image_path = Path(sys.argv[1]).expanduser().resolve()
    if not image_path.exists():
        print(f"File not found: {image_path}")
        sys.exit(1)

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY не найден в .env")

    client = OpenAI(api_key=api_key)

    # 1. Распознаём номер
    day_number = read_day_number_with_openai(client, image_path)
    print(f"Detected day number: {day_number}")

    # 2. Генерируем имена
    png_name = f"{day_number}.png"
    jpg_name = f"{day_number}.jpg"

    new_png_path = SOURCES_DIR / png_name
    jpg_path = SEQUENCE_DIR / jpg_name

    # 3. Переименовываем PNG
    new_png_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.rename(new_png_path)
    print(f"Renamed PNG to {new_png_path}")

    # 4. Делаем JPG-копию
    convert_png_to_jpg(new_png_path, jpg_path)
    print(f"Saved JPG copy to {jpg_path}")


if __name__ == "__main__":
    main()
