import base64
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
if not NOVITA_API_KEY:
    raise RuntimeError("NOVITA_API_KEY не найден в .env")

BASE_URL = "https://api.novita.ai/v3"


def _start_txt2img(
    prompt: str,
    *,
    negative_prompt: str = "bad hands, extra fingers, deformed fingers, missing fingers",
    width: int = 1024,
    height: int = 576,
    model_name: str = "sd_xl_base_1.0.safetensors",
    steps: int = 25,
    guidance_scale: float = 7.0,
    image_num: int = 1,
) -> str:
    """
    Отправляет запрос на асинхронную генерацию изображения и возвращает task_id.
    """
    url = f"{BASE_URL}/async/txt2img"

    payload = {
        "extra": {
            # хотим сразу jpeg-картинку
            "response_image_type": "jpeg",
        },
        "request": {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "model_name": model_name,
            "width": width,
            "height": height,
            "image_num": image_num,
            "steps": steps,
            "guidance_scale": guidance_scale,
            "sampler_name": "Euler a",
            "seed": -1,
        },
    }

    headers = {
        "Authorization": f"Bearer {NOVITA_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["task_id"]


def _wait_task(task_id: str, *, timeout_sec: int = 90, poll_interval: float = 2.0) -> str:
    """
    Ждёт завершения задачи и возвращает URL первой картинки.
    """
    url = f"{BASE_URL}/async/task-result"
    headers = {
        "Authorization": f"Bearer {NOVITA_API_KEY}",
    }

    deadline = time.time() + timeout_sec

    while True:
        if time.time() > deadline:
            raise TimeoutError(f"Novita task {task_id} не успел завершиться за {timeout_sec} секунд")

        resp = requests.get(url, headers=headers, params={"task_id": task_id}, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        status = data["task"]["status"]
        if status == "TASK_STATUS_SUCCEED":
            images = data.get("images") or []
            if not images:
                raise RuntimeError(f"Novita task {task_id} завершился без изображений")
            return images[0]["image_url"]
        elif status == "TASK_STATUS_FAILED":
            reason = data["task"].get("reason", "unknown")
            raise RuntimeError(f"Novita task {task_id} failed: {reason}")
        elif status in ("TASK_STATUS_QUEUED", "TASK_STATUS_PROCESSING"):
            time.sleep(poll_interval)
        else:
            # на всякий случай
            time.sleep(poll_interval)

def _image_file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _start_img2img(
    init_image_path: str,
    prompt: str,
    *,
    negative_prompt: str = "bad hands, extra fingers, deformed fingers, missing fingers",
    width: int = 1536,
    height: int = 1024,
    model_name: str = "sd_xl_base_1.0.safetensors",
    steps: int = 20,
    guidance_scale: float = 7.0,
    strength: float = 0.45,   # важно: небольшое значение, чтобы геометрия не поплыла
) -> str:
    """
    Асинхронное img2img: берёт init-картинку и промпт, возвращает task_id.
    """
    url = f"{BASE_URL}/async/img2img"

    image_b64 = _image_file_to_base64(init_image_path)

    payload = {
        "extra": {
            "response_image_type": "jpeg",
        },
        "request": {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "model_name": model_name,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance_scale": guidance_scale,
            "sampler_name": "Euler a",
            "seed": -1,
            "image_num": 1,
            "image_base64": image_b64,
            "strength": strength,
        },
    }

    headers = {
        "Authorization": f"Bearer {NOVITA_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["task_id"]


def generate_img2img_to_file(
    init_image_path: str,
    prompt: str,
    output_path: str,
    *,
    width: int = 1536,
    height: int = 1024,
    negative_prompt: str = "bad hands, extra fingers, deformed fingers, missing fingers",
    strength: float = 0.45,
):
    """
    Полный цикл img2img: init-картинка + промпт → JPEG-файл.
    """
    task_id = _start_img2img(
        init_image_path,
        prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        strength=strength,
    )
    image_url = _wait_task(task_id)

    resp = requests.get(image_url, timeout=60)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path



def generate_image_url(
    prompt: str,
    *,
    width: int = 1024,
    height: int = 576,
    negative_prompt: str = "bad hands, extra fingers, deformed fingers, missing fingers",
) -> str:
    """
    Удобная обёртка: вернёт URL готовой картинки.
    """
    task_id = _start_txt2img(
        prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
    )
    return _wait_task(task_id)


def generate_image_to_file(
    prompt: str,
    output_path: str,
    *,
    width: int = 1024,
    height: int = 576,
    negative_prompt: str = "bad hands, extra fingers, deformed fingers, missing fingers",
):
    """
    Полный цикл: сгенерировать картинку и сохранить в файл (JPEG).
    """
    image_url = generate_image_url(
        prompt,
        width=width,
        height=height,
        negative_prompt=negative_prompt,
    )

    resp = requests.get(image_url, timeout=60)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path
