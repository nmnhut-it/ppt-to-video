"""Generate audio from narration scripts using Gemini TTS API."""

import json
import sys
import wave
from pathlib import Path

from google import genai
from google.genai import types

from config import (
    AUDIO_DIR, AUDIO_SAMPLE_RATE, GEMINI_API_KEY,
    GEMINI_TTS_MODEL, GEMINI_VOICE_NAME, SCRIPTS_DIR,
)


def create_client() -> genai.Client:
    """Create Gemini API client."""
    if not GEMINI_API_KEY:
        print("Set GEMINI_API_KEY in environment or .env file.")
        sys.exit(1)
    return genai.Client(api_key=GEMINI_API_KEY)


def text_to_audio(client: genai.Client, text: str, output_path: Path) -> None:
    """Convert text to audio WAV file using Gemini TTS."""
    response = client.models.generate_content(
        model=GEMINI_TTS_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=GEMINI_VOICE_NAME,
                    )
                )
            ),
        ),
    )

    audio_data = response.candidates[0].content.parts[0].inline_data.data
    with wave.open(str(output_path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(AUDIO_SAMPLE_RATE)
        f.writeframes(audio_data)


def main():
    narrations_file = SCRIPTS_DIR / "narrations.json"
    if not narrations_file.exists():
        print("Run generate_narration.py first.")
        sys.exit(1)

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    narrations = json.loads(narrations_file.read_text(encoding="utf-8"))
    client = create_client()

    for item in narrations:
        slide_num = item["slide_number"]
        text = item["narration"]
        if not text:
            print(f"Skipping slide {slide_num} (empty narration)")
            continue

        output_path = AUDIO_DIR / f"slide_{slide_num:03d}.wav"
        print(f"Generating audio for slide {slide_num}...")
        text_to_audio(client, text, output_path)
        print(f"  Saved {output_path}")

    print(f"Generated {len(list(AUDIO_DIR.glob('*.wav')))} audio files")


if __name__ == "__main__":
    main()
