# front_gen.py  (бывш. front_recast_block_generator.py)
# Usage: python front_gen.py <number 1..1000>

from mt_common import pick_common, title_block

def generate_prompt_by_number(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")

    # Единая логика подбора общих параметров (стиль берётся из общего набора)
    style, place, clothing, atmosphere = pick_common(index, mode="front")
    # Единый блок про титул и подпись дня
    title_lines = title_block("front", index)

    return f"""Re-render as a {style}.
Front view. Setting: {place}.
Clothing: {clothing}.
Atmosphere/lighting: {atmosphere}.
Aspect ratio 3:2. Single static illustration (no animation). High quality, clean edges.

{title_lines}

Hands/mudra: show exactly four visible fingers on each hand; index fingers extended and touching at their tips to form a small upward-pointing triangle; middle, ring, and pinky curled inward; thumbs hidden. Hands at chest level.

Do not change the pose or proportions. Do not add extra fingers or thumbs.
Do not remove, distort, or misspell the title or subtitle. Avoid warped typography and background clutter.
Produce a crisp, refined illustration with no artifacts or watermarks.
""".strip()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python front_gen.py <number 1..1000>")
        sys.exit(1)
    n = int(sys.argv[1])
    print(n)
    print(generate_prompt_by_number(n))

