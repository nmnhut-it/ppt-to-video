# PPT to Video

Turn PowerPoint slides into narrated videos. Upload a `.pptx` file, generate Vietnamese narration, convert to speech, and export as MP4.

## How It Works

1. **Upload** your `.pptx` file
2. **Pick slides** you want in the video
3. **Write narration** — auto-generate with AI, use your speaker notes, or type manually
4. **Generate audio** — text-to-speech via Google Gemini
5. **Export video** — slides + audio combined into a single MP4

## Setup

### Prerequisites

- **Python 3.11+**
- **FFmpeg** — [download here](https://ffmpeg.org/download.html), make sure `ffmpeg` is in your PATH
- **Claude Code** — [install here](https://docs.anthropic.com/en/docs/claude-code) (for AI narration generation)
- **Gemini API key** — free at [Google AI Studio](https://aistudio.google.com/apikey)

### Install

```bash
git clone https://github.com/nmnhut-it/ppt-to-video.git
cd ppt-to-video
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart python-dotenv
```

### Configure

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Run

```bash
python -m uvicorn app:app --port 8765
```

Open **http://localhost:8765** in your browser.

## Narration Options

| Option | How | Best for |
|--------|-----|----------|
| **Use notes** | Copies your PowerPoint speaker notes as-is | When you already wrote a script |
| **Generate** | AI writes narration from slide content | When you want a fresh script |
| **Manual** | Type directly in the text box | Full control |

You can mix and match — use notes for some slides, generate for others, and edit any of them before creating audio.

## Tech Stack

- **FastAPI** — web server
- **python-pptx** — slide extraction
- **Claude Code CLI** — narration generation
- **Google Gemini TTS** — text-to-speech
- **FFmpeg** — video composition
