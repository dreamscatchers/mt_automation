# mt_common.py
from dataclasses import dataclass
from typing import List, Tuple

# ====== Общие списки ======
STYLES_FRONT = [
    "anime-style illustration",
    "Impressionist illustration",
    "Cubist illustration",
    "Art Deco poster-style illustration",
    "Surrealist painting",
    "Pop Art graphic illustration",
    "engraving-style illustration",
    "watercolor illustration",
    "minimalist line-art illustration",
    "technical line drawing",
]

STYLES_BACK = [
    "Impressionist illustration",
    "Cubist illustration",
    "Baroque painting",
    "Art Deco poster",
    "Fauvist style",
    "Pop Art graphic",
    "engraving-style illustration",
    "watercolor painting",
    "anime-style illustration",
    "minimalist line art",
]

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

# ====== Выбор параметров по индексу ======
@dataclass(frozen=True)
class CoreParams:
    style: str
    place: str
    clothing: str
    atmosphere: str

def core_params(index: int, view: str) -> CoreParams:
    """Детерминированный выбор style/place/clothing/atmosphere по номеру."""
    i0 = index - 1
    style_list = STYLES_FRONT if view == "front" else STYLES_BACK
    style = style_list[i0 % len(style_list)]
    place = PLACES[(i0 // 10) % len(PLACES)]
    clothing = CLOTHES[i0 // 100]  # 0..9 при 1..1000
    atmosphere = ATMOSPHERES[i0 % len(ATMOSPHERES)]
    return CoreParams(style, place, clothing, atmosphere)

# ====== Правила внешности ======
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

def inject_appearance(prompt_parts: List[str], negatives: List[str], n: int, view: str) -> Tuple[List[str], List[str]]:
    """Вставляет строку 'Appearance:' логично после блока одежды, дополняет negatives."""
    appearance = build_appearance_line(n, view)
    extra_negs = build_negatives(n, view)

    insert_idx = None
    for i, part in enumerate(prompt_parts):
        if part.strip().startswith("Clothing:") or "Clothing:" in part or "Outfit:" in part or "Attire:" in part:
            insert_idx = i + 1
            break
    if insert_idx is None:
        prompt_parts.append(appearance)
    else:
        prompt_parts.insert(insert_idx, appearance)

    return prompt_parts, (negatives + extra_negs)

