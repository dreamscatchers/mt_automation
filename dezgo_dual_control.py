import os
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("DEZGO_API_KEY")
    if not api_key:
        raise RuntimeError("DEZGO_API_KEY не найден в .env")

    files = {
        # ControlNet 1 — поза тела
        "init_image": ("skeleton1.png", open("skeleton1.png", "rb"), "image/png"),

        # ControlNet 2 — точная схема мудры
        "init_image_2": ("hands1.png", open("hands1.png", "rb"), "image/png"),
    }

    data = {
        "prompt": (
            "Meditating man, clean illustration, front view, soft background, high quality. "
            "Hands MUST follow the exact finger configuration from the second control image. "
            "No prayer pose, no namaste."
        ),
        "negative_prompt": (
            "prayer pose, namaste, palms touching, incorrect mudra, fingers together"
        ),

        # ControlNet 1
        "control_model": "scribble",
        "control_scale": "1.0",

        # ControlNet 2 (мудра)
        "control_model_2": "lineart",
        "control_scale_2": "1.0",

        "width": "1024",
        "height": "576",
        "steps": "25",
        "sampler": "dpmpp_2m_karras",
        "format": "jpg",
    }

    headers = {"X-Dezgo-Key": api_key}

    response = requests.post(
        "https://api.dezgo.com/controlnet",
        data=data,
        files=files,
        headers=headers
    )
    print(response.status_code, response.text)
    response.raise_for_status()

    with open("dual_result.jpg", "wb") as f:
        f.write(response.content)

    print("Saved dual_result.jpg")

if __name__ == "__main__":
    main()
