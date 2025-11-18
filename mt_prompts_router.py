# mt_prompts_router.py
from typing import Literal

import front_gen
import back_gen

Side = Literal["front", "back"]


def generate_prompt(side: Side, index: int) -> str:
    if side == "front":
        return front_gen.generate_prompt_by_number(index)
    if side == "back":
        return back_gen.generate_prompt_by_number(index)
    raise ValueError("side must be 'front' or 'back'")
