# front_recast_block_generator.py
# Usage: python front_recast_block_generator.py <number 1..1000>

def generate_prompt_by_number(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")

    styles = [
        "anime-style illustration",
        "Impressionist illustration",
        "Cubist illustration",
        "Art Deco poster-style illustration",
        "Art Nouveau illustration",
        "Pop Art graphic illustration",
        "engraving-style illustration",
        "watercolor illustration",
        "minimalist line-art illustration",
        "technical line drawing"
    ]

    places = [
        "shallow water with gentle ripples fading toward misty mountains and a tiny tree-covered island",
        "a mountain at sunrise with faceted ridgelines",
        "a sun-dappled forest clearing near a still pond",
        "a quiet desert salt flat with distant dunes",
        "a Buddhist temple lake with stone lanterns",
        "a modern city rooftop with a stylized skyline",
        "a candle-lit cave pool with soft reflections",
        "a cosmic horizon with subtle nebula shapes",
        "an underwater realm with soft caustics",
        "a flowering garden pond with lotus leaves"
    ]

    clothes = [
        "an orange robe",
        "white yogic garments with a green sash",
        "a crimson ceremonial cloak",
        "golden spiritual attire",
        "a modern minimalist outfit",
        "a monochrome robe of radiant light",
        "simple mystical armor (clean, non-aggressive shapes)",
        "an Indian dhoti and sash",
        "a futuristic meditation suit",
        "a transparent light body rendered as clean monochrome contours"
    ]

    atmospheres = [
        "soft golden morning light with a subtle haze",
        "gentle sunrise glow in a light mist",
        "silvery dawn ambiance with crisp clarity",
        "warm evening radiance through drifting mist",
        "twilight glow with tender colors"
    ]

    i0 = index - 1
    style = styles[i0 % len(styles)]
    place = places[(i0 // 10) % len(places)]
    clothing = clothes[i0 // 100]
    atmosphere = atmospheres[i0 % len(atmospheres)]

    return f"""Re-render as a {style}.
Front view. Setting: {place}.
Clothing: {clothing}.
Atmosphere/lighting: {atmosphere}.
Aspect ratio 3:2. Single static illustration (no animation). High quality, clean edges.

Hands/mudra: show exactly four visible fingers on each hand; index fingers extended and touching at their tips to form a small upward-pointing triangle; middle, ring, and pinky curled inward; thumbs hidden. Hands at chest level.

Do not change the pose or proportions. Do not add extra fingers or thumbs. 
Do not remove, distort, or misspell the title. Avoid warped typography and background clutter.
Produce a crisp, refined illustration with no artifacts or watermarks.
""".strip()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python front_recast_block_generator.py <number 1..1000>")
        sys.exit(1)
    n = int(sys.argv[1])
    print(n)
    print(generate_prompt_by_number(n))

