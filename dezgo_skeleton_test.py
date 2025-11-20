# dezgo_skeleton_test.py
import os
import requests
from dotenv import load_dotenv

def main():
    # 1. Загружаем .env (как у тебя сделано в edit_image.py)
    load_dotenv()

    api_key = os.getenv("DEZGO_API_KEY")
    if not api_key:
        raise RuntimeError("DEZGO_API_KEY не найден в .env")

    # 2. Путь к skeleton1.png внутри проекта
    skeleton_path = "skeleton1.png"
    if not os.path.exists(skeleton_path):
        raise FileNotFoundError(f"{skeleton_path} не найден")

    # 3. Промпт любой — сейчас тестируем ControlNet
    prompt = "Meditating man, clean illustration, front view, soft background, high quality."
    prompt = "Meditating man, clean illustration, front view, soft background, high quality. Hands in Maha Gyan Mudra: show exactly four visible fingers on each hand, index fingers extended and touching at their tips to form a small upward-pointing triangle, middle ring and pinky fingers curled inward, thumbs hidden behind the curled fingers. No prayer pose, no namaste, no palms pressed together."


    negative_prompt = (
        # "blurry, distorted, extra limbs, extra fingers, bad anatomy, watermark, text"
        "prayer pose, namaste, palms touching, fingers together, incorrect mudra, open palms"

    )

    url = "https://api.dezgo.com/controlnet"

    files = {
        "init_image": (skeleton_path, open(skeleton_path, "rb"), "image/png"),
    }

    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "control_model": "scribble",
        "control_scale": "1.0",
        "control_preprocess": "true",
        "width": "1024",   # <= 1024 и кратно 8
        "height": "576",   # между 320 и 1024, кратно 8
        "guidance": "7",
        "steps": "25",
        "sampler": "dpmpp_2m_karras",
        "format": "jpg",
    }


    headers = {
        "X-Dezgo-Key": api_key,
    }

    response = requests.post(url, data=data, files=files, headers=headers)
    response.raise_for_status()

    out_path = "skeleton1_result.jpg"
    with open(out_path, "wb") as f:
        f.write(response.content)

    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
