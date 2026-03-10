"""Extract slide images and text content from a PowerPoint file."""

import json
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches
from PIL import Image

from config import SLIDES_DIR, SCRIPTS_DIR, OUTPUT_DIR


def extract_text_content(pptx_path: str) -> list[dict]:
    """Extract title, body text, and speaker notes from each slide."""
    prs = Presentation(pptx_path)
    slides_data = []

    for i, slide in enumerate(prs.slides, start=1):
        title = ""
        body_lines = []

        for shape in slide.shapes:
            if shape.has_text_frame:
                if shape.shape_id == slide.shapes.title.shape_id if slide.shapes.title else False:
                    title = shape.text_frame.text.strip()
                else:
                    for paragraph in shape.text_frame.paragraphs:
                        text = paragraph.text.strip()
                        if text:
                            body_lines.append(text)

        notes = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()

        slides_data.append({
            "slide_number": i,
            "title": title,
            "body": "\n".join(body_lines),
            "notes": notes,
        })

    return slides_data


def export_slide_images(pptx_path: str) -> list[Path]:
    """Export slides as images using LibreOffice (fallback: placeholder)."""
    import subprocess

    pptx_abs = str(Path(pptx_path).resolve())
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)

    # Try LibreOffice conversion
    try:
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "png",
             "--outdir", str(SLIDES_DIR.resolve()), pptx_abs],
            check=True, capture_output=True, timeout=120,
        )
        return sorted(SLIDES_DIR.glob("*.png"))
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Fallback: try python-pptx + pillow to create simple slide images
    print("LibreOffice not found. Creating placeholder slide images.")
    prs = Presentation(pptx_path)
    images = []
    width = int(prs.slide_width.inches * 96)
    height = int(prs.slide_height.inches * 96)

    for i, slide in enumerate(prs.slides, start=1):
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        path = SLIDES_DIR / f"slide_{i:03d}.png"
        img.save(path)
        images.append(path)

    return images


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_slides.py <path-to-pptx>")
        sys.exit(1)

    pptx_path = sys.argv[1]
    print(f"Extracting from: {pptx_path}")

    # Extract text content
    slides_data = extract_text_content(pptx_path)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    content_file = SCRIPTS_DIR / "slides_content.json"
    content_file.write_text(json.dumps(slides_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved slide content to {content_file} ({len(slides_data)} slides)")

    # Export images
    images = export_slide_images(pptx_path)
    print(f"Exported {len(images)} slide images to {SLIDES_DIR}")


if __name__ == "__main__":
    main()
