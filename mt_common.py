# mt_common.py
# Общие константы и функции для генераторов промптов

TITLE = "MASTER'S TOUCH MEDITATION"

# Единые локации / одежда / атмосферы
PLACES = [
    "shallow water with gentle ripples fading toward misty mountains and a tiny tree-covered island",
    "a mountain at sunrise with faceted ridgelines",
    "a sun-dappled forest clearing near a still pond",
    "a quiet desert salt flat with distant dunes",
    "a Buddhist temple lake with stone lanterns",
    "a modern city rooftop with a stylized skyline",
    "a candle-lit cave pool with soft reflections",
    "a cosmic horizon with subtle nebula shapes",
    "an underwater realm with soft caustics",
    "a flowering garden pond with lotus leaves",
]

CLOTHES = [
    "an orange robe",
    "white yogic garments with a green sash",
    "a crimson ceremonial cloak",
    "golden spiritual attire",
    "a modern minimalist outfit",
    "a monochrome robe of radiant light",
    "simple mystical armor (clean, non-aggressive shapes)",
    "an Indian dhoti and sash",
    "a futuristic meditation suit",
    "a transparent light body rendered as clean monochrome contours",
]

ATMOSPHERES = [
    "soft golden morning light with a subtle haze",
    "gentle sunrise glow in a light mist",
    "silvery dawn ambiance with crisp clarity",
    "warm evening radiance through drifting mist",
    "twilight glow with tender colors",
]

STYLES = [
    "anime-style illustration",
    "Impressionist illustration",
    "Cubist illustration",
    "Art Deco poster-style illustration",
    "Art Nouveau illustration",
    "Pop Art graphic illustration",
    "engraving-style illustration",
    "watercolor illustration",
    "minimalist line-art illustration",
    "technical line drawing",
]

def day_label(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")
    return f"Day {index} of 1000"

def pick_style(index: int) -> str:
    """Возвращает стиль из общего списка STYLES по индексу (циклично)."""
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")
    i0 = (index - 1) % len(STYLES)
    return STYLES[i0]

def pick_common(index: int):
    """
    Возвращает (style, place, clothing, atmosphere) по индексу.
    style берётся из единого набора через pick_style(mode, index).
    place меняется каждые 10; clothing — каждые 100; atmosphere — по модулю.
    """
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")
    i0 = index - 1
    style = pick_style(index)
    place = PLACES[(i0 // 10) % len(PLACES)]
    clothing = CLOTHES[i0 // 100]
    atmosphere = ATMOSPHERES[i0 % len(ATMOSPHERES)]
    return style, place, clothing, atmosphere


def title_block(mode: str, index: int) -> str:
    """
    Единый текст про титул и подзаголовок с номером дня.
    mode: 'front' или 'back'
    """
    dl = day_label(index)
    if mode == "back":
        return (
            f'Keep the arched title exactly as “{TITLE}” with the same arc, spacing, and spelling.\n'
            f'Add a clearly legible subtitle just below the title that reads “{dl}”.'
        )
    if mode == "front":
        return (
            f'Typography: keep the arched title “{TITLE}” and add a clear subtitle under it that reads “{dl}”.'
        )
    raise ValueError("mode must be 'front' or 'back'")

