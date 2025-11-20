from yt_stream import schedule_stream

# RFC3339 пример: 2025-11-21T01:30:00-04:00
START_TIME = "2025-11-21T01:30:00-04:00"

result = schedule_stream(
    title="Meditation Test Stream",
    description="Автоматическое тестовое создание стрима через API",
    start_time_rfc3339=START_TIME,
    thumbnail_path="front_base.png"  # укажи путь к существующей обложке (JPEG!)
)

print("Стрим создан!")
for k, v in result.items():
    print(f"{k}: {v}")
