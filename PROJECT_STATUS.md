# Project Status Overview

This repository automates daily content production for the **Master's Touch Meditation** series. It already covers prompt creation, thumbnail generation, YouTube scheduling, and Facebook posting; credentials and runtime paths are expected in the user's environment as described below.

## Implemented Pipelines
- **Prompt + thumbnail generation**
  - `prompt_generator.py` builds a day-specific prompt using random attributes from `sources/` text files and a fixed start date (`START_DATE=2025-02-20`).
  - `generate_image_gemini.py` calls Gemini 2.5 Flash Image with the prompt and a base image (`automation/sources/front_base.png`), then saves PNGs to `~/projects/master_touch_meditation/sequence/sources/` and JPGs to `~/projects/master_touch_meditation/sequence/`.
- **YouTube scheduling**
  - `schedule_range.py` is the main orchestrator. It checks existing uploads, generates missing thumbnails (unless `--dry-run`), computes dates via `day_index.py`, builds titles/descriptions via `mtm_content.py`, and schedules broadcasts through `yt_stream.schedule_stream` with optional auto start/stop and playlist assignment. Supports persistent vs unique stream keys.
  - `schedule_week.py` is a wrapper that converts a date window (default: tomorrow +7 days) into a numeric range and delegates to `schedule_range.py`.
  - `yt_stream.py` wraps low-level YouTube API actions: creating broadcasts/streams, binding to a persistent stream (`PERSISTENT_STREAM_ID` in `.env`), uploading thumbnails, adding to playlists, and returning RTMP info.
  - `yt_auth.py` handles OAuth token loading/refresh for YouTube (`config/client_secret_youtube.json`, `config/token_youtube.json`) and sets a "token revoked" flag when refresh fails.
- **Social posting**
  - `facebook_post.py` posts to a Facebook page using environment variables `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN`, and `FB_GRAPH_API_VERSION`.
  - `post_if_finished.py` checks a GAS endpoint (`GAS_WEBAPP_URL` + `GAS_WEBAPP_TOKEN`) to see if a day's stream finished; if so, it posts a bilingual message to Facebook once per stream, tracked in `runtime/posted_streams.json`.
- **Utilities** (under `utils/`)
  - Image helpers (`check_missing_jpgs.py`, `check_sequence.py`, `crop_sources_to_16x9.py`, `jpeg_to_jpg.py`) and credential refresh scripts for Facebook/YouTube (`fb_refresh_page_token.py`, `refresh_youtube_token.py`).

## Data & Configuration
- Environment variables loaded from `.env` for API keys (`GEMINI_API_KEY`, playlist IDs, `PERSISTENT_STREAM_ID`, GAS tokens).
- YouTube OAuth credentials live in `config/client_secret_youtube.json` and `config/token_youtube.json`.
- Media paths assume the working tree resides at `~/projects/master_touch_meditation/` with sequence assets in the sibling `sequence/` folder.

## Typical Workflows
- **Generate a thumbnail**: `python generate_image_gemini.py <day>`.
- **Schedule a range**: `python schedule_range.py 285-300 --no-dry-run --stream-mode persistent --auto-start-stop` (adds playlists, uploads thumbnail, binds stream).
- **Plan a week**: `python schedule_week.py --days 7 --no-dry-run`.
- **Post after completion**: `python post_if_finished.py 2025-03-15 --dry-run` (checks GAS, optionally posts to Facebook).

## Known Conventions
- Day numbering is 1-based from 2025-02-20; titles follow `"<n>. Master's Touch Meditation — Day <n> of 1000"`.
- Sunday thumbnails force a red-only palette (handled in `prompt_generator.choose_palette`).
- DRY-RUN modes avoid YouTube writes and Gemini calls while printing planned actions.
