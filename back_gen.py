# back_gen.py
# Usage: python back_gen.py <number 1..1000>

from mt_common import pick_common, title_block, build_appearance_line, build_negatives

def generate_prompt_by_number(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")

    # Общие параметры (единый набор стилей)
    style, place, clothing, atmosphere = pick_common(index, mode="back")
    # Единый блок про титул и подпись дня
    title_lines = title_block("back", index)

    # Внешность и связанные отрицания (для back — без бороды по правилам)
    appearance_line = build_appearance_line(index, view="back")
    extra_negatives = build_negatives(index, view="back")

    # Базовые отрицания (позиционные + типографика)
    base_negatives = [
        "Do not change the pose or proportions.",
        "Do not show hands or fingers from behind.",
        "Do not add extra limbs.",
        "Do not remove, distort, or misspell the title or subtitle.",
        "Avoid warped typography and background clutter.",
        "Produce a crisp, refined illustration with no artifacts or watermarks."
    ]
    all_negatives = base_negatives + extra_negatives

    prompt = f"""
Use the uploaded black-and-white line-art image of the monk and arched title as the base reference.
STRICTLY preserve pose and composition: back view; elbows bent; forearms forward; hands are in front of the chest and NOT visible from behind.
{title_lines}

Re-render as a {style}.
Setting: {place}.
Clothing: {clothing}.
{appearance_line}
Atmosphere/lighting: {atmosphere}.
Aspect ratio 16:9. Single static illustration (no animation). High quality, clean edges.

""".strip()

    # Добавим negatives отдельным блоком, чтобы промпт оставался читабельным
    prompt += "\n\n" + "\n".join(all_negatives)

    return prompt


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python back_gen.py <number 1..1000>")
        sys.exit(1)
    try:
        n = int(sys.argv[1])
        print(n, "back")
        print(generate_prompt_by_number(n))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

