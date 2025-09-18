# front_recast_block_generator.py
# Usage: python front_recast_block_generator.py <number 1..1000>

from mt_common import core_params, inject_appearance

def generate_prompt_by_number(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")

    cp = core_params(index, view="front")

    prompt_parts = [
        f"Re-render as a {cp.style}.",
        f"Front view. Setting: {cp.place}.",
        f"Clothing: {cp.clothing}.",
        f"Atmosphere/lighting: {cp.atmosphere}.",
        "Aspect ratio 3:2. Single static illustration (no animation). High quality, clean edges.",
        "",
        "Hands/mudra: show exactly four visible fingers on each hand; index fingers extended and touching at their tips to form a small upward-pointing triangle; middle, ring, and pinky curled inward; thumbs hidden. Hands at chest level.",
        "",
        "Do not change the pose or proportions. Do not add extra fingers or thumbs.",
        "Do not remove, distort, or misspell the title. Avoid warped typography and background clutter.",
        "Produce a crisp, refined illustration with no artifacts or watermarks.",
    ]

    negatives: list[str] = []
    # Вставим Appearance и дополним негативные ограничения
    prompt_parts, negatives = inject_appearance(prompt_parts, negatives, index, "front")

    # Приклеим негативные инструкции в конец (если есть)
    if negatives:
        prompt_parts.append("\n".join(negatives))

    return "\n".join(prompt_parts).strip()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python front_recast_block_generator.py <number 1..1000>")
        sys.exit(1)
    n = int(sys.argv[1])
    print(n)
    print(generate_prompt_by_number(n))

