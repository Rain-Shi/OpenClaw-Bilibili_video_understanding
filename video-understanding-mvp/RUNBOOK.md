# Runbook

## 1. For local file
```bash
python3 video-understanding-mvp/entries/run_mvp.py --video_file /path/to/video.mp4
```

## 2. For Bilibili URL
Requires `yt-dlp`.

```bash
python3 video-understanding-mvp/entries/run_mvp.py --bilibili_url "https://www.bilibili.com/video/BV..."
```

## 3. To unlock real transcript generation
Requires:
- `ffmpeg`
- `whisper` CLI

Suggested install:
```bash
sudo apt-get install ffmpeg
pip install yt-dlp openai-whisper
```

## 4. Outputs
Check the generated run directory for:
- `summary.md`
- `chapters.json`
- `result.json`
- `transcript.srt`
- `transcript.json`

## 5. Current known limitation
If dependencies are not installed, the app still runs but falls back to placeholder transcript / OCR hooks.
