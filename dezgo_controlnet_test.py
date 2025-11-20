from dezgo_client import generate_controlnet_openpose

INIT = "front_base.png"          # твой шаблон
PROMPT_FILE = "dezgo_prompt_controlnet.txt"
OUT_FILE = "dezgo_controlnet_result.jpg"

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompt = f.read().strip()

path = generate_controlnet_openpose(INIT, prompt, OUT_FILE)
print("Saved:", path)
