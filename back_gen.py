# sora_recast_generator.py
# Usage: python sora_recast_generator.py <number 1..1000>

from mt_common import core_params, inject_appearance

def generate_prompt_by_number(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")

    cp = core_params(index, view="back")
    title = "MASTER'S TOUCH MEDITATION"

    prompt_parts = [
        "Use the uploaded black-and-white line-art image of the monk and arched title as the base reference.",
        "STRICTLY preserve pose and composition: back view; elbows bent; forearms forward; hands are in front of the chest and NOT visible from behind.",
        f"Keep the arched title exactly as “{title}” with the same arc, spacing, and spelling.",
        "",
        f"Re-render as a {cp.style}.",
        f"Setting: {cp.place}.",
        f"Clothing: {cp.clothing}.",
        f"Atmosphere/lighting: {cp.atmosphere}.",
        "Aspect ratio 16:9. Single static illustration (no animation). High quality, clean edges.",
        "",
        "Do not change the pose or proportions. Do not show hands or fingers from behind. Do not add extra limbs.",
        "Do not remove, distort, or misspell the title. Avoid warped typography and background clutter.",
        "Produce a crisp, refined illustration with no artifacts or watermarks.",
    ]

    negatives: list[str] = []
    # Вставим Appearance (без бороды на back) и дополним негативные ограничения
    prompt_parts, negatives = inject_appearance(prompt_parts, negatives, index, "back")

    if negatives:
        prompt_parts.append("\n".join(negatives))

    return "\n".join(prompt_parts).strip()


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

