"""Configuration constants for PPT-to-video pipeline."""

import os
from pathlib import Path

# Directories
OUTPUT_DIR = Path("output")
SLIDES_DIR = OUTPUT_DIR / "slides"
AUDIO_DIR = OUTPUT_DIR / "audio"
SCRIPTS_DIR = OUTPUT_DIR / "scripts"

# Gemini TTS
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_TTS_MODEL = "gemini-2.5-flash-preview-tts"
GEMINI_VOICE_NAME = "Kore"
AUDIO_SAMPLE_RATE = 24000

# Claude CLI
CLAUDE_CMD = "claude"

# FFmpeg
FFMPEG_CMD = "ffmpeg"
VIDEO_FPS = 1  # static slides, 1 fps is enough

# Narration style prompt
NARRATION_SYSTEM_PROMPT = (
    "You are a Vietnamese narrator for educational presentations. "
    "Given slide content (title, bullet points, speaker notes), "
    "write a natural, engaging Vietnamese narration script. "
    "The script should sound like a teacher explaining to students. "
    "Output ONLY the narration text, no markdown, no labels."
)
