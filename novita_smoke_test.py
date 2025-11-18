import os
from novita_client import generate_image_to_file

PROMPT_FILE = "prompt.txt"

if __name__ == "__main__":
    if not os.path.exists(PROMPT_FILE):
        raise RuntimeError(f"{PROMPT_FILE} not found")

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt = f.read().strip()

    output_path = "out/novita_test.jpg"

    path = generate_image_to_file(
        prompt,
        output_path,
        width=1280,
        height=720,
    )

    print("Saved:", path)
    print("Prompt used:")
    print(prompt)
