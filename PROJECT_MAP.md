PROJECT_MAP.md
Overview

Этот репозиторий реализует полный автоматизированный пайплайн для проекта Master’s Touch Meditation: генерация изображений, хранение превью, генерация промптов, создание запланированных YouTube-стримов и распределение их по плейлистам.

Directory Structure
master_touch_meditation/
│
├─ automation/
│   ├─ prompt_generator.py
│   ├─ generate_image_gemini.py
│   ├─ yt_auth.py
│   ├─ yt_stream.py
│   ├─ schedule_range.py
│   └─ sources/
│        └─ front_base.png
│
├─ sequence/
│   ├─ sources/          # PNG originals from Gemini
│   └─ *.jpg             # JPEG final thumbnails
│
└─ .env                  # API keys + playlist IDs + PERSISTENT_STREAM_ID

Key Modules
prompt_generator.py

Генерирует структурированный промпт для каждого дня:

пол

стиль

локация

одежда

волосяной покров

палитра (воскресенье = только красные тона)

Читает текстовые файлы вариантов из automation/sources/*.

generate_image_gemini.py

Использует модель Gemini 2.5 Flash Image:

Загружает front_base.png

Передаёт в модель: prompt + базовое изображение

Сохраняет результат:

PNG → sequence/sources/

JPEG → sequence/

Использует GEMINI_API_KEY из .env.

yt_auth.py

Загружает OAuth-креды:

config/client_secret_youtube.json

config/token_youtube.json

Создаёт клиент YouTube Data API.

yt_stream.py

Инкапсулирует низкоуровневые операции YouTube API:

создание liveBroadcast

привязка к постоянному RTMP-стриму (PERSISTENT_STREAM_ID)

загрузка thumbnail

добавление стрима в плейлисты

schedule_range.py

Главный управляющий скрипт автоматики:

читает диапазон дней

определяет их даты

проверяет, есть ли стримы в YouTube Uploads playlist

при необходимости генерирует обложки

выбирает нужные плейлисты (воскресенье → Full Version, иначе 1/2 Version)

создаёт новый стрим через yt_stream.schedule_stream

Environment Variables (.env)
GEMINI_API_KEY=...
PERSISTENT_STREAM_ID=...
GENERAL_YT_PLAYLIST_ID=...
HALF_MTM_PLAYLIST_ID=...
FULL_MTM_PLAYLIST_ID=...

Workflow Summary

generate_image_gemini.py <day>
→ генерирует PNG + JPEG.

schedule_range.py 280-286 --no-dry-run
→ создаёт стримы, загружает обложки, привязывает к постоянному RTMP-потоку.

Превью автоматически загружается в YouTube.

Стримы распределяются по плейлистам.

Все стилистические данные приходят из prompt_generator.py.