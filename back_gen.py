# sora_recast_generator.py
# Usage: python sora_recast_generator.py <number 1..1000>

from mt_common import pick_common, title_block

def generate_prompt_by_number(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")

    styles = [
        "Impressionist illustration", "Cubist illustration", "Baroque painting",
        "Art Deco poster", "Art Nouveau illustration", "Pop Art graphic",
        "engraving-style illustration", "watercolor painting",
        "anime-style illustration", "minimalist line art"
    ]

    # Единая логика подбора общих параметров
    style, place, clothing, atmosphere = pick_common(index, styles)
    # Единый блок про титул и подпись дня
    title_lines = title_block("back", index)

    prompt = f"""
Use the uploaded black-and-white line-art image of the monk and arched title as the base reference.
STRICTLY preserve pose and composition: back view; elbows bent; forearms forward; hands are in front of the chest and NOT visible from behind.
{title_lines}

Re-render as a {style}.
Setting: {place}.
Clothing: {clothing}.
Atmosphere/lighting: {atmosphere}.
Aspect ratio 16:9. Single static illustration (no animation). High quality, clean edges.

Do not change the pose or proportions. Do not show hands or fingers from behind. Do not add extra limbs.
Do not remove, distort, or misspell the title or subtitle. Avoid warped typography and background clutter.
Produce a crisp, refined illustration with no artifacts or watermarks.
""".strip()

    return prompt


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python sora_recast_generator.py <number 1..1000>")
        sys.exit(1)
    try:
        n = int(sys.argv[1])
        print(n)
        print(generate_prompt_by_number(n))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

