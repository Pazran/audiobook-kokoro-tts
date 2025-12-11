import sys
import os
import subprocess
from pathlib import Path
import logging

# Create a logger instance
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------- CONFIG ----------------
KOKORO = "kokoro-tts"            # CLI command
VOICE = "af_bella"               # default voice #bf_isabella
SPEED = "1.0"                    # speech speed
FORMAT = "wav"                   # output format
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"
OUTPUT_ROOT = "audiobook_output"   # root output folder
# ----------------------------------------

def run_kokoro(cmd):
    """Run Kokoro CLI with GPU environment"""
    env = os.environ.copy()
    env["ONNX_PROVIDER"] = "CUDAExecutionProvider"   # force GPU
    subprocess.run(cmd, check=True, env=env)

def process_file(input_file):
    input_path = Path(input_file)
    book_name = input_path.stem
    output_dir = Path(OUTPUT_ROOT) / book_name
    output_dir.mkdir(parents=True, exist_ok=True)

    ext = input_path.suffix.lower()
    logger.info(f"Processing '{input_file}'…")

    # Step 1: process file (split chapters into chunks)
    process_cmd = [
        KOKORO,
        str(input_path),
        "--split-output", str(output_dir),
        "--format", FORMAT,
        "--speed", SPEED,
        "--voice", VOICE,
        "--model", MODEL_FILE,
        "--voices", VOICES_FILE,
        "--debug"
    ]
    run_kokoro(process_cmd)

    # Step 2: merge chunks into chapter files
    logger.info("Merging chapter chunks…")
    merge_cmd = [
        KOKORO,
        "--merge-chunks",
        "--split-output", str(output_dir),
        "--format", FORMAT
    ]
    run_kokoro(merge_cmd)

    logger.info(f"\n✔ Done! Final chapters saved in: {output_dir}")

def main():
    if len(sys.argv) < 2:
        print("Drag  & drop a TXT, EPUB, or PDF onto this script.")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        logger.error("File not found:", input_file)
        sys.exit(1)

    process_file(input_file)

if __name__ == "__main__":
    main()