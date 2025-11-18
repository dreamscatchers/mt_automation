import os
from novita_client import generate_img2img_to_file

PROMPT_FILE = "prompt_front_img2img.txt"
INIT_IMAGE = "front_base.png"          # твой базовый контур
OUTPUT = "out/front_img2img_test.jpg"

if __name__ == "__main__":
    if not os.path.exists(PROMPT_FILE):
        raise RuntimeError(f"{PROMPT_FILE} not found")
    if not os.path.exists(INIT_IMAGE):
        raise RuntimeError(f"{INIT_IMAGE} not found")

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt = f.read().strip()

    path = generate_img2img_to_file(
        INIT_IMAGE,
        prompt,
        OUTPUT,
        width=1536,
        height=1024,
        strength=0.75,
    )

    print("Saved:", path)
    print("Prompt used:")
    print(prompt)
