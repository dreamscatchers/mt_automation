# mt_inpaint.py
import base64
from pathlib import Path
from typing import Optional

from PIL import Image
from openai import OpenAI

from mt_openai_client import get_client


def _choose_size_for_image(width: int, height: int) -> str:
    """
    Простейший подбор размера под gpt-image-1.
    """
    ratio = width / height

    if 0.95 <= ratio <= 1.05:
        return "1024x1024"
    if ratio > 1:
        return "1536x1024"
    return "1024x1536"


def inpaint_image(
    image_path: str,
    mask_path: str,
    prompt: str,
    output_path: str,
    *,
    model: str = "gpt-image-1",
    size: Optional[str] = None,
    quality: Optional[str] = None,  # "low" | "hd" (в зависимости от версии API)
    client: Optional[OpenAI] = None,
) -> str:
    """
    Inpainting через Images API (client.images.edit):

    - image_path: исходное изображение (PNG/JPEG).
    - mask_path: PNG-маска того же размера:
        • прозрачные области (alpha=0) — где можно редактировать,
        • непрозрачные — что нужно сохранить.
    - prompt: текст с описанием изменений (фон и т.п.).
    - output_path: куда сохранить результат.

    Возвращает итоговый путь к файлу.
    """
    client = client or get_client()

    image_p = Path(image_path)
    mask_p = Path(mask_path)

    if not image_p.is_file():
        raise FileNotFoundError(f"Base image not found: {image_p}")
    if not mask_p.is_file():
        raise FileNotFoundError(f"Mask image not found: {mask_p}")

    # Проверяем размер и при необходимости вычисляем size автоматически
    with Image.open(image_p) as img:
        width, height = img.size

    if size is None:
        size = _choose_size_for_image(width, height)

    # Вызов Images API: edit (inpainting)
    kwargs = dict(
        model=model,
        image=image_p.open("rb"),
        mask=mask_p.open("rb"),
        prompt=prompt,
        size=size,
        n=1,
    )
    if quality is not None:
        kwargs["quality"] = quality

    result = client.images.edit(**kwargs)

    # Ответ содержит base64 в поле data[0].b64_json
    b64_data = result.data[0].b64_json
    image_bytes = base64.b64decode(b64_data)

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_bytes(image_bytes)

    return str(out_p)


if __name__ == "__main__":
    base = "front_base.png"
    mask = "front_mask.png"  # твоя маска с прозрачным фоном
    out = "out/front_inpaint_test.png"

    test_prompt = (
        "Do not change the person, pose or hands. "
        "Only replace the background with a warm sepia-toned sunset over the ocean."
    )

    print(inpaint_image(base, mask, test_prompt, out))
