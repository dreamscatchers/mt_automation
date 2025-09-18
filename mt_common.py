# mt_common.py
from dataclasses import dataclass
from typing import List

# ====== Общий заголовок ======
TITLE = "MASTER'S TOUCH MEDITATION"

# ====== Единый пул стилей для front и back ======
STYLES = [
    "anime-style illustration",
    "Impressionist illustration",
    "Cubist illustration",
    "Art Deco poster-style illustration",
    # "Art Nouveau illustration",  # при необходимости можно вернуть
    "Pop Art graphic illustration",
    "engraving-style illustration",
    "watercolor illustration",
    "minimalist line-art illustration",
    "technical line drawing",
    "Baroque painting",
]

# ====== Локации / Одежда / Атмосферы ======
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

# ====== День серии ======
def day_label(index: int) -> str:
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")
    return f"Day {index} of 1000"

# ====== Выбор стиля/окружения по индексу ======
@dataclass(frozen=True)
class CoreParams:
    style: str
    place: str
    clothing: str
    atmosphere: str

def pick_style(index: int) -> str:
    """Единый стиль из STYLES (циклично)."""
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")
    i0 = (index - 1) % len(STYLES)
    return STYLES[i0]

def core_params(index: int) -> CoreParams:
    """
    Детерминированный выбор style/place/clothing/atmosphere по номеру.
      - style: циклично по STYLES
      - place: блоками по 10
      - clothing: блоками по 100
      - atmosphere: циклично по ATMOSPHERES
    """
    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")
    i0 = index - 1
    style = pick_style(index)
    place = PLACES[(i0 // 10) % len(PLACES)]
    clothing = CLOTHES[i0 // 100]
    atmosphere = ATMOSPHERES[i0 % len(ATMOSPHERES)]
    return CoreParams(style, place, clothing, atmosphere)

# Обратная совместимость с генераторами (тот же интерфейс что и раньше)
def pick_common(index: int, mode: str):
    """Совместимая обёртка: возвращает (style, place, clothing, atmosphere)."""
    cp = core_params(index)
    return cp.style, cp.place, cp.clothing, cp.atmosphere

# ====== Единый блок про титул/подзаголовок ======
def title_block(mode: str, index: int) -> str:
    """
    mode: 'front' или 'back' — влияет только на формулировку текста.
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

# ====== Разнообразие внешности (борода / чалма / волосы) ======
@dataclass(frozen=True)
class Features:
    beard: bool
    turban: bool
    hair: bool
    bald: bool

BEARD_STYLES  = ["neatly trimmed beard", "short close-cropped beard", "full well-groomed beard"]
TURBAN_STYLES = ["plain turban", "lightly patterned turban", "silk-wrapped turban"]
HAIR_STYLES   = ["short natural head hair", "medium-length hair", "tied-back hair bun"]

def features_for(n: int, view: str) -> Features:
    """
    Правила:
      - чётные (n % 2 == 0): борода
      - кратные 3: чалма
      - кратные 4: волосы (если нет чалмы)
    Уточнения:
      - борода упоминается только для front (на back — нет)
      - чалма перекрывает волосы
      - 'bald' = нет чалмы и нет волос
    """
    beard = (n % 2 == 0)
    turban = (n % 3 == 0)
    hair = (n % 4 == 0)
    if turban:
        hair = False
    if view != "front":
        beard = False
    return Features(beard=beard, turban=turban, hair=hair, bald=(not turban and not hair))

def build_appearance_line(n: int, view: str) -> str:
    f = features_for(n, view)
    bits: List[str] = []
    if f.turban:
        bits.append(f"wearing a {TURBAN_STYLES[(n // 3) % len(TURBAN_STYLES)]}")
    elif f.hair:
        bits.append(f"with {HAIR_STYLES[(n // 4) % len(HAIR_STYLES)]}")
    else:
        bits.append("with a clean-shaven bald head")
    if f.beard:
        bits.append(BEARD_STYLES[(n // 2) % len(BEARD_STYLES)])
    return "Appearance: " + ", ".join(bits) + "."

def build_negatives(n: int, view: str) -> List[str]:
    f = features_for(n, view)
    negatives: List[str] = []
    if not f.hair and not f.turban:
        negatives.append("Do not add any head hair or headwear.")
    if f.turban:
        negatives.append("Do not show head hair outside the turban.")
    if not f.beard:
        negatives.append("Do not add a beard or mustache.")
    return negatives

