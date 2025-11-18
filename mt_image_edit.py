# mt_image_edit.py
import base64
from pathlib import Path
from typing import Optional

from PIL import Image
from openai import OpenAI

from mt_openai_client import get_client


def to_data_url(path: str) -> str:
    p = Path(path)
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return "data:image/png;base64," + b64


def choose_size_for_image(width: int, height: int) -> str:
    """
    Подбираем рекомендованный size для image_generation
    из допустимых вариантов gpt-image-1.
    """
    ratio = width / height

    # почти квадрат
    if 0.95 <= ratio <= 1.05:
        return "1024x1024"

    # явный landscape
    if ratio > 1:
        return "1536x1024"

    # явный portrait
    return "1024x1536"


def edit_image(
    input_path: str,
    prompt: str,
    output_path: str,
    *,
    model: str = "gpt-4o-mini",
    client: Optional[OpenAI] = None,
) -> str:
    """
    Универсальная функция редактирования изображения через Responses API.

    - читает input_path
    - определяет размер и подбирает size
    - вызывает tool image_generation с заданным prompt
    - сохраняет результат в output_path
    - возвращает строку с итоговым путём
    """
    client = client or get_client()

    input_path_obj = Path(input_path)
    if not input_path_obj.is_file():
        raise FileNotFoundError(f"Input image not found: {input_path_obj}")

    # 1. Размер исходного файла
    with Image.open(input_path_obj) as img:
        width, height = img.size

    size = choose_size_for_image(width, height)

    # 2. Кодируем картинку в data URL
    image_data_url = to_data_url(str(input_path_obj))

    # 3. Вызов Responses API с указанием size на tool
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            }
        ],
        tools=[
            {
                "type": "image_generation",
                "size": size,  # используем size, а не пиксели
                # при необходимости можно добавить:
                # "quality": "medium",
                # "n": 1,
            }
        ],
        tool_choice={"type": "image_generation"},
    )

    # 4. Достаём результат
    image_call = None
    for item in response.output:
        if getattr(item, "type", None) == "image_generation_call":
            image_call = item
            break

    if not image_call or not getattr(image_call, "result", None):
        raise RuntimeError("Image generation result not found in response.")

    image_b64 = image_call.result
    image_bytes = base64.b64decode(image_b64)

    out_path_obj = Path(output_path)
    out_path_obj.parent.mkdir(parents=True, exist_ok=True)
    out_path_obj.write_bytes(image_bytes)

    return str(out_path_obj)
