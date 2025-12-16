import sys
import types
import unittest
from datetime import date, timedelta
from unittest import mock

from day_index import BASE_DATE, date_to_index, index_to_date

# Тестовые заглушки для тяжёлых зависимостей, которые не нужны в юнит-тестах
sys.modules.setdefault(
    "yt_stream", types.SimpleNamespace(schedule_stream=None, SCOPES=[])
)
sys.modules.setdefault("yt_auth", types.SimpleNamespace(get_youtube_service=None))
sys.modules.setdefault(
    "generate_image_gemini", types.SimpleNamespace(generate_image=lambda *_, **__: None)
)

import schedule_range


class DayIndexTests(unittest.TestCase):
    def test_index_to_date_converts_from_base(self):
        self.assertEqual(index_to_date(1), BASE_DATE)
        self.assertEqual(index_to_date(5), BASE_DATE + timedelta(days=4))

    def test_index_to_date_rejects_zero_or_negative(self):
        for invalid in (0, -1):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    index_to_date(invalid)

    def test_date_to_index_converts_to_one_based(self):
        self.assertEqual(date_to_index(BASE_DATE), 1)
        self.assertEqual(date_to_index(BASE_DATE + timedelta(days=9)), 10)

    def test_date_to_index_rejects_before_base_date(self):
        before_base = BASE_DATE - timedelta(days=1)
        with self.assertRaises(ValueError):
            date_to_index(before_base)


class ScheduleRangeHelpersTests(unittest.TestCase):
    def test_parse_range_preserves_order_for_forward_range(self):
        self.assertEqual(schedule_range.parse_range("10-12"), (10, 12))

    def test_parse_range_sorts_reverse_range(self):
        self.assertEqual(schedule_range.parse_range("12-10"), (10, 12))

    def test_parse_range_requires_dash(self):
        with self.assertRaises(ValueError):
            schedule_range.parse_range("101")

    def test_choose_playlists_for_sunday_prefers_full(self):
        with mock.patch.multiple(
            schedule_range,
            GENERAL_PLAYLIST_ID="GENERAL",
            HALF_PLAYLIST_ID="HALF",
            FULL_PLAYLIST_ID="FULL",
        ):
            playlists = schedule_range.choose_playlists_for_date(date(2025, 2, 23))

        self.assertEqual(
            playlists,
            [
                ("GENERAL", "General"),
                ("FULL", "Full Version"),
            ],
        )

    def test_choose_playlists_for_weekday_prefers_half(self):
        with mock.patch.multiple(
            schedule_range,
            GENERAL_PLAYLIST_ID="GENERAL",
            HALF_PLAYLIST_ID="HALF",
            FULL_PLAYLIST_ID="FULL",
        ):
            playlists = schedule_range.choose_playlists_for_date(date(2025, 2, 24))

        self.assertEqual(
            playlists,
            [
                ("GENERAL", "General"),
                ("HALF", "1/2 Version"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
