"""Run the full PPT-to-video pipeline."""

import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from extract_slides import main as extract
from generate_narration import main as narrate
from generate_audio import main as audio
from compose_video import main as compose


STEPS = {
    "extract": extract,
    "narrate": narrate,
    "audio": audio,
    "compose": compose,
    "all": None,
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <pptx-file> [step]")
        print(f"Steps: {', '.join(STEPS.keys())}")
        print("Default: all steps run sequentially")
        sys.exit(1)

    pptx_path = sys.argv[1]
    step = sys.argv[2] if len(sys.argv) > 2 else "all"

    if step not in STEPS:
        print(f"Unknown step: {step}. Choose from: {', '.join(STEPS.keys())}")
        sys.exit(1)

    # For extract step, we need to pass the pptx path via sys.argv
    sys.argv = [sys.argv[0], pptx_path]

    if step == "all":
        for name, fn in STEPS.items():
            if name == "all":
                continue
            print(f"\n{'='*50}")
            print(f"Step: {name}")
            print(f"{'='*50}")
            fn()
    else:
        STEPS[step]()


if __name__ == "__main__":
    main()
