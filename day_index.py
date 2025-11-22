#!/usr/bin/env python3
from datetime import date, timedelta

# Единственный источник правды
BASE_DATE = date(2025, 2, 20)  # Day 1


def index_to_date(index: int) -> date:
    """
    Преобразует порядковый номер дня (1-based)
    в календарную дату.
    """
    if index < 1:
        raise ValueError("index должен быть >= 1")
    return BASE_DATE + timedelta(days=index - 1)


def date_to_index(d: date) -> int:
    """
    Преобразует календарную дату в порядковый номер дня (1-based).
    """
    if d < BASE_DATE:
        raise ValueError("Дата раньше начала садханы")
    return (d - BASE_DATE).days + 1
