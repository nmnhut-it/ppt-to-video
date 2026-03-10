"""Generate Vietnamese narration scripts using Claude CLI (claude -p)."""

import json
import os
import subprocess
import sys
from pathlib import Path

from config import CLAUDE_CMD, NARRATION_SYSTEM_PROMPT, SCRIPTS_DIR


def generate_script_for_slide(slide_data: dict) -> str:
    """Call claude -p to generate narration for a single slide."""
    prompt = (
        f"{NARRATION_SYSTEM_PROMPT}\n\n"
        f"--- Slide {slide_data['slide_number']} ---\n"
        f"Title: {slide_data['title']}\n"
        f"Content:\n{slide_data['body']}\n"
        f"Speaker Notes: {slide_data['notes']}\n"
    )

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    result = subprocess.run(
        [CLAUDE_CMD, "-p", prompt],
        capture_output=True, text=True, timeout=120, encoding="utf-8",
        env=env,
    )

    if result.returncode != 0:
        print(f"  Error on slide {slide_data['slide_number']}: {result.stderr}")
        return ""

    return result.stdout.strip()


def main():
    content_file = SCRIPTS_DIR / "slides_content.json"
    if not content_file.exists():
        print("Run extract_slides.py first.")
        sys.exit(1)

    slides_data = json.loads(content_file.read_text(encoding="utf-8"))
    narrations = []

    for slide in slides_data:
        print(f"Generating narration for slide {slide['slide_number']}...")
        script = generate_script_for_slide(slide)
        narrations.append({
            "slide_number": slide["slide_number"],
            "narration": script,
        })
        print(f"  Done ({len(script)} chars)")

    output_file = SCRIPTS_DIR / "narrations.json"
    output_file.write_text(json.dumps(narrations, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved narrations to {output_file}")


if __name__ == "__main__":
    main()
