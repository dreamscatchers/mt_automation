from dezgo_client import generate_image_to_jpeg

PROMPT_FILE = "dezgo_prompt.txt"
OUT_FILE = "out/dezgo_test.jpg"


def main():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt = f.read().strip()

    path = generate_image_to_jpeg(prompt, OUT_FILE)
    print("Saved:", path)


if __name__ == "__main__":
    main()
