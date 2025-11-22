#!/usr/bin/env python3
import random
from datetime import date, timedelta
from pathlib import Path


# Дата, соответствующая дню 1
START_DATE = date(2025, 2, 20)

# Папка с текстовыми файлами вариантов
SOURCES_DIR = Path(__file__).parent / "sources"


def load_variants(filename: str) -> list[str]:
    """Считывает варианты из текстового файла, по одному на строку."""
    path = SOURCES_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_date_for_day(day_number: int) -> date:
    """Возвращает календарную дату для указанного порядкового номера."""
    if day_number < 1:
        raise ValueError("day_number должен быть >= 1")
    return START_DATE + timedelta(days=day_number - 1)


def choose_hair(gender: str) -> str:
    """Выбор варианта волосяного покрова в зависимости от пола."""
    if gender == "женский":
        variants = load_variants("hair_female.txt")
    else:
        variants = load_variants("hair_male.txt")
    return random.choice(variants)


def choose_palette(current_date: date) -> str:
    """
    Выбор цветовой палитры:
    - если воскресенье → всегда 'только красные тона'
    - иначе случайный вариант из palette.txt
    """
    # Monday=0 ... Sunday=6
    if current_date.weekday() == 6:
        return "только красные тона"

    variants = load_variants("palette.txt")
    return random.choice(variants)


def generate_prompt(day_number: int) -> str:
    """Генерирует текст промпта для указанного дня (1–1000)."""
    current_date = get_date_for_day(day_number)

    genders = load_variants("genders.txt")
    styles = load_variants("styles.txt")
    locations = load_variants("locations.txt")
    clothes = load_variants("clothes.txt")

    gender = random.choice(genders)
    style = random.choice(styles)
    location = random.choice(locations)
    clothes_choice = random.choice(clothes)
    hair = choose_hair(gender)
    palette = choose_palette(current_date)

    prompt = f"""
Перерисовать изображение в стиле: {style}
Текст: Сохранить арочный заголовок "MASTER'S TOUCH MEDITATION". Добавить под ним четкий подзаголовок "Day {day_number} of 1000". Текст и заголовок должен контрастировать с фоном.
Пол: {gender}
Локация: {location}
Одежда: {clothes_choice}
Волосяной покров: {hair}
Цветовая палитра: {palette}
Ориентация: Альбомная
""".strip()

    return prompt

if __name__ == "__main__":
    import sys

    # По умолчанию используем 308-й день, если аргумент не передан
    default_day = 308

    if len(sys.argv) > 1:
        try:
            day_number = int(sys.argv[1])
            if day_number < 1:
                raise ValueError
        except ValueError:
            print("Использование: python prompt_generator.py [day_number>=1]")
            sys.exit(1)
    else:
        day_number = default_day

    print(generate_prompt(day_number))
