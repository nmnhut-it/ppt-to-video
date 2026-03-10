"""FastAPI backend for PPT-to-video pipeline."""

import json
import os
import shutil
import subprocess
import uuid
import wave
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import (
    AUDIO_DIR, AUDIO_SAMPLE_RATE, CLAUDE_CMD, FFMPEG_CMD,
    GEMINI_TTS_MODEL, GEMINI_VOICE_NAME, NARRATION_SYSTEM_PROMPT,
    OUTPUT_DIR, SLIDES_DIR,
)
from extract_slides import export_slide_images, extract_text_content

load_dotenv()

app = FastAPI(title="PPT to Video")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = OUTPUT_DIR / "uploads"
CLIPS_DIR = OUTPUT_DIR / "clips"

for d in [UPLOAD_DIR, SLIDES_DIR, AUDIO_DIR, OUTPUT_DIR / "scripts", CLIPS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")


# --- Models ---

class NarrationRequest(BaseModel):
    slide_number: int
    title: str
    body: str
    notes: str


class NarrationEditRequest(BaseModel):
    slide_number: int
    narration: str


class AudioRequest(BaseModel):
    slide_number: int
    narration: str


class ComposeRequest(BaseModel):
    slides: list[int]


# --- Routes ---

@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.post("/api/upload")
async def upload_pptx(file: UploadFile = File(...)):
    """Upload PPTX and extract slide content + images."""
    if not file.filename.endswith((".pptx", ".ppt")):
        raise HTTPException(400, "Only .pptx files accepted")

    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    slides_data = extract_text_content(str(save_path))
    export_slide_images(str(save_path))

    return {"slides": slides_data, "total": len(slides_data)}


@app.post("/api/narration/generate")
async def generate_narration(req: NarrationRequest):
    """Generate narration for a single slide using claude -p."""
    prompt = (
        f"{NARRATION_SYSTEM_PROMPT}\n\n"
        f"--- Slide {req.slide_number} ---\n"
        f"Title: {req.title}\n"
        f"Content:\n{req.body}\n"
        f"Speaker Notes: {req.notes}\n"
    )

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        result = subprocess.run(
            [CLAUDE_CMD, "-p", prompt],
            capture_output=True, text=True, timeout=120, encoding="utf-8",
            env=env,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Claude CLI timed out")

    if result.returncode != 0:
        raise HTTPException(500, f"Claude error: {result.stderr[:300]}")

    return {"slide_number": req.slide_number, "narration": result.stdout.strip()}


@app.post("/api/audio/generate")
async def generate_audio(req: AudioRequest):
    """Generate TTS audio for a slide narration using Gemini."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise HTTPException(500, "GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=GEMINI_TTS_MODEL,
            contents=req.narration,
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
    except Exception as e:
        raise HTTPException(500, f"Gemini TTS error: {str(e)[:300]}")

    audio_data = response.candidates[0].content.parts[0].inline_data.data
    output_path = AUDIO_DIR / f"slide_{req.slide_number:03d}.wav"
    with wave.open(str(output_path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(AUDIO_SAMPLE_RATE)
        f.writeframes(audio_data)

    duration = len(audio_data) / (AUDIO_SAMPLE_RATE * 2)
    return {
        "slide_number": req.slide_number,
        "audio_url": f"/output/audio/slide_{req.slide_number:03d}.wav",
        "duration": round(duration, 1),
    }


@app.post("/api/video/compose")
async def compose_video(req: ComposeRequest):
    """Compose final video from selected slides + audio."""
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    clip_paths = []

    for slide_num in req.slides:
        slide_img = SLIDES_DIR / f"slide_{slide_num:03d}.png"
        audio_path = AUDIO_DIR / f"slide_{slide_num:03d}.wav"

        if not slide_img.exists():
            raise HTTPException(400, f"Slide image {slide_num} not found")
        if not audio_path.exists():
            raise HTTPException(400, f"Audio for slide {slide_num} not found")

        with wave.open(str(audio_path), "rb") as wf:
            duration = wf.getnframes() / wf.getframerate()

        clip_path = CLIPS_DIR / f"slide_{slide_num:03d}.mp4"
        subprocess.run([
            FFMPEG_CMD, "-y",
            "-loop", "1", "-i", str(slide_img),
            "-i", str(audio_path),
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration), "-shortest",
            str(clip_path),
        ], check=True, capture_output=True)
        clip_paths.append(clip_path)

    final_output = OUTPUT_DIR / "final_video.mp4"

    if len(clip_paths) == 1:
        shutil.copy2(clip_paths[0], final_output)
    else:
        list_file = OUTPUT_DIR / "clips_list.txt"
        list_file.write_text(
            "\n".join(f"file '{p.resolve()}'" for p in clip_paths),
            encoding="utf-8",
        )
        subprocess.run([
            FFMPEG_CMD, "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file), "-c", "copy", str(final_output),
        ], check=True, capture_output=True)
        list_file.unlink()

    return {"video_url": "/output/final_video.mp4"}


@app.get("/api/audio/{slide_number}")
async def get_audio(slide_number: int):
    """Serve audio file for playback."""
    path = AUDIO_DIR / f"slide_{slide_number:03d}.wav"
    if not path.exists():
        raise HTTPException(404, "Audio not found")
    return FileResponse(path, media_type="audio/wav")


@app.get("/api/video/download")
async def download_video():
    """Download the final composed video."""
    path = OUTPUT_DIR / "final_video.mp4"
    if not path.exists():
        raise HTTPException(404, "Video not found. Compose first.")
    return FileResponse(path, media_type="video/mp4", filename="presentation.mp4")
