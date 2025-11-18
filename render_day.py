# render_day.py
import sys
from pathlib import Path
from typing import Literal

from mt_prompts_router import generate_prompt, Side
from mt_image_edit import edit_image

BASE_IMAGES = {
    "front": "front_base.png",
    "back": "back_base.png",
}

OUT_DIR = Path("out")


def render_for_day(index: int, side: Side) -> str:
    base_path = BASE_IMAGES[side]
    prompt = generate_prompt(side, index)

    OUT_DIR.mkdir(exist_ok=True)
    filename = f"{side}_{index:03d}.png"
    out_path = OUT_DIR / filename

    result_path = edit_image(base_path, prompt, str(out_path))
    return result_path


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python render_day.py <day 1..1000> <front|back|both>")
        sys.exit(1)

    day = int(sys.argv[1])
    mode = sys.argv[2]

    if not (1 <= day <= 1000):
        print("Day must be between 1 and 1000")
        sys.exit(1)

    if mode == "both":
        front_path = render_for_day(day, "front")
        back_path = render_for_day(day, "back")
        print("Front:", front_path)
        print("Back:", back_path)
    elif mode in ("front", "back"):
        path = render_for_day(day, mode)  # type: ignore[arg-type]
        print(path)
    else:
        print("Second argument must be front|back|both")
        sys.exit(1)


if __name__ == "__main__":
    main()
