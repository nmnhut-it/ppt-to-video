# PPT to Video

Turn your PowerPoint presentations into narrated videos — with AI-generated Vietnamese narration and natural-sounding speech.

## What It Does

Upload a `.pptx` file, and the app walks you through 5 simple steps:

1. **Upload** — drag and drop your PowerPoint file
2. **Pick slides** — choose which slides to include
3. **Narration** — let AI write a script, use your speaker notes, or type your own
4. **Audio** — convert the narration to natural speech
5. **Download** — get your finished MP4 video

## Narration Options

| Option | What it does | Best for |
|--------|-------------|----------|
| **Use notes** | Uses the speaker notes you already wrote in PowerPoint | You already have a script ready |
| **Generate** | AI writes a narration based on your slide content | You want a quick draft |
| **Manual** | You type the narration yourself | Full control over every word |

You can mix and match — use notes for some slides, generate for others, and edit anything before creating audio.

## Requirements

You'll need to install a few things before using the app. If you're not sure how, ask a developer friend or follow the links below.

- **Microsoft PowerPoint** — must be installed on your computer (used to export slide images)
- **Python 3.11 or newer** — [download here](https://www.python.org/downloads/) (check "Add to PATH" during install)
- **FFmpeg** — for video creation. Open a terminal and run: `winget install Gyan.FFmpeg`, then restart your terminal
- **Claude Code** — [install guide](https://docs.anthropic.com/en/docs/claude-code) (powers the AI narration)
- **Gemini API key** — free, follow the steps below

### How to Get a Gemini API Key (free)

1. Open [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Create API key"**
4. Copy the key — it looks like `AIzaSy...`

No credit card needed. The free plan is more than enough for personal use.

## Installation

Open a terminal (Command Prompt or PowerShell) and run these commands one by one:

```bash
git clone https://github.com/nmnhut-it/ppt-to-video.git
cd ppt-to-video
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart python-dotenv comtypes
```

Then set up your API key:

1. In the `ppt-to-video` folder, find the file `.env.example`
2. Make a copy and rename it to `.env`
3. Open `.env` with Notepad and replace `your-gemini-api-key` with your actual key
4. Save and close

## How to Start

Every time you want to use the app, open a terminal in the `ppt-to-video` folder and run:

```bash
python -m uvicorn app:app --port 8765
```

Then open your browser and go to **http://localhost:8765**

To stop the app, press `Ctrl+C` in the terminal.
