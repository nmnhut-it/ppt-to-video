"""Compose final video: slide image + audio per slide, concatenated via FFmpeg."""

import subprocess
import sys
import wave
from pathlib import Path

from config import AUDIO_DIR, FFMPEG_CMD, OUTPUT_DIR, SLIDES_DIR


def get_audio_duration(wav_path: Path) -> float:
    """Get duration in seconds of a WAV file."""
    with wave.open(str(wav_path), "rb") as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / rate


def create_slide_clip(slide_img: Path, audio_path: Path, output_path: Path) -> None:
    """Create a video clip: static slide image + audio."""
    duration = get_audio_duration(audio_path)

    subprocess.run([
        FFMPEG_CMD, "-y",
        "-loop", "1", "-i", str(slide_img),
        "-i", str(audio_path),
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),
        "-shortest",
        str(output_path),
    ], check=True, capture_output=True)


def concatenate_clips(clip_paths: list[Path], output_path: Path) -> None:
    """Concatenate video clips into final video."""
    list_file = OUTPUT_DIR / "clips_list.txt"
    list_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in clip_paths),
        encoding="utf-8",
    )

    subprocess.run([
        FFMPEG_CMD, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path),
    ], check=True, capture_output=True)

    list_file.unlink()


def main():
    slides = sorted(SLIDES_DIR.glob("*.png"))
    audios = sorted(AUDIO_DIR.glob("*.wav"))

    if not slides:
        print("No slide images found. Run extract_slides.py first.")
        sys.exit(1)
    if not audios:
        print("No audio files found. Run generate_audio.py first.")
        sys.exit(1)

    clips_dir = OUTPUT_DIR / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    clip_paths = []
    for slide_img, audio in zip(slides, audios):
        clip_path = clips_dir / f"{slide_img.stem}.mp4"
        print(f"Creating clip: {slide_img.name} + {audio.name}")
        create_slide_clip(slide_img, audio, clip_path)
        clip_paths.append(clip_path)

    final_output = OUTPUT_DIR / "final_video.mp4"
    print("Concatenating clips...")
    concatenate_clips(clip_paths, final_output)
    print(f"Done! Output: {final_output}")


if __name__ == "__main__":
    main()
