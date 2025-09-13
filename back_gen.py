# sora_recast_generator.py
# Usage: python sora_recast_generator.py <number 1..1000>

def generate_prompt_by_number(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")

    styles = [
        "Impressionist illustration", "Cubist illustration", "Baroque painting",
        "Art Deco poster", "Art Nouveau illustration", "Pop Art graphic",
        "engraving-style illustration", "watercolor painting",
        "anime-style illustration", "minimalist line art"
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

    title = "MASTER'S TOUCH MEDITATION"

    prompt = f"""
Use the uploaded black-and-white line-art image of the monk and arched title as the base reference.
STRICTLY preserve pose and composition: back view; elbows bent; forearms forward; hands are in front of the chest and NOT visible from behind.
Keep the arched title exactly as “{title}” with the same arc, spacing, and spelling.

Re-render as a {style}.
Setting: {place}.
Clothing: {clothing}.
Atmosphere/lighting: {atmosphere}.
Aspect ratio 16:9. Single static illustration (no animation). High quality, clean edges.

Do not change the pose or proportions. Do not show hands or fingers from behind. Do not add extra limbs.
Do not remove, distort, or misspell the title. Avoid warped typography and background clutter.
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

