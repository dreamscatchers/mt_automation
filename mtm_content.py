"""Shared content utilities for Master's Touch Meditation videos/streams."""
from pathlib import Path

# Папка с JPG-обложками
SEQUENCE_DIR = Path.home() / "projects" / "master_touch_meditation" / "sequence"


def build_stream_title(index: int) -> str:
    """Return the canonical title for a meditation day."""
    return f"{index}. Master's Touch Meditation — Day {index} of 1000"


def build_stream_description() -> str:
    """Return the canonical description used for all videos/streams."""
    return (
        "#YogiBhajan #Meditation #Sadhana #DailyPractice #1000DaysChallenge "
        "#MastersTouchMeditation #KundaliniYoga #MeditationJourney "
        "#SpiritualDiscipline #MeditationChallenge #DailyMeditation "
        "#LongMeditation #MeditationSadhana #YogaPractice #MeditationLife"
    )


def get_thumbnail_path(index: int) -> Path:
    """Return the expected thumbnail path for the given day index."""
    return SEQUENCE_DIR / f"{index}.jpg"
