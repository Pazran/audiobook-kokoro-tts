import sys
import os
import subprocess
import hashlib
import json
import shutil
from pathlib import Path
import logging

# Create a logger instance
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------- CONFIG ----------------
KOKORO = "kokoro-tts"            # CLI command
VOICE = "bf_isabella"               # default voice #bf_isabella #af_bella
SPEED = "1.0"                    # speech speed
FORMAT = "wav"                   # output format
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"
OUTPUT_ROOT = "audiobook_output"   # root output folder
SUPPORTED_EXTS = {".txt", ".epub", ".pdf"}
# ----------------------------------------

def run_kokoro(cmd):
    """Run Kokoro CLI with GPU + UTF-8 output environment"""
    env = os.environ.copy()
    env["ONNX_PROVIDER"] = "CUDAExecutionProvider"   # force GPU
    env["PYTHONIOENCODING"] = "utf-8"                # avoid cp1252 console crashes
    subprocess.run(cmd, check=True, env=env)

# ---------------- PREFLIGHT ----------------
def fail(msg):
    """Log an error and exit with a friendly message."""
    logger.error(msg)
    sys.exit(1)

def preflight_input(input_path):
    """Tier 0: free checks, always run before any work."""
    if input_path.suffix.lower() not in SUPPORTED_EXTS:
        fail(f"Unsupported file type '{input_path.suffix}'. Only TXT, EPUB, and PDF are supported.")
    if not input_path.is_file():
        fail(f"File not found: {input_path}")

def preflight_render():
    """Tier 1: checks that matter only when a render will happen."""
    for name in (MODEL_FILE, VOICES_FILE):
        if not Path(name).is_file():
            fail(f"Missing required file next to the script: {name}")
    cli = shutil.which(KOKORO)
    if cli is None:
        fail(f"CLI '{KOKORO}' not found on PATH. Launch via convert_to_audiobook.bat so the venv is active.")
    try:
        result = subprocess.run([cli, "--help"], capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        fail(f"CLI '{KOKORO}' hung during the boot check (30s timeout). The venv may be broken.")
    if result.returncode != 0:
        fail(f"CLI '{KOKORO}' crashed during boot check (exit {result.returncode}). "
             f"The venv is missing dependencies. Repair with: venv\\Scripts\\pip install --force-reinstall kokoro-tts")

# ---------------- RENDER STATE (completion sentinel) ----------------
SENTINEL_NAME = "COMPLETE"

def hash_file(path):
    """Streaming SHA-256 of a file, safe for large books."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def compute_fingerprint(input_path, config):
    """Deterministic fingerprint of every input that shapes the audio."""
    payload = json.dumps([
        config["voice"],
        config["speed"],
        config["format"],
        config["model"],
        config["voices"],
        hash_file(input_path),      # content, not mtime or size
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def should_render(output_dir, fingerprint):
    """Skip if a completed run with the same fingerprint already exists."""
    sentinel = output_dir / SENTINEL_NAME
    if sentinel.exists():
        try:
            data = json.loads(sentinel.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("Sentinel unreadable, re-rendering: %s", sentinel)
            return True
        if data.get("fingerprint") == fingerprint:
            logger.info("Output is up to date. Skipping render.")
            return False
        logger.info("Voice, speed, or source changed. Re-rendering.")
    return True

def clean_output_dir(output_dir):
    """Fresh start: a render always begins from an empty folder."""
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

def write_sentinel(output_dir, fingerprint):
    """Atomic sentinel write: temp file + os.replace, crash-safe."""
    sentinel = output_dir / SENTINEL_NAME
    tmp = output_dir / (SENTINEL_NAME + ".tmp")
    tmp.write_text(json.dumps({"fingerprint": fingerprint}, indent=2), encoding="utf-8")
    os.replace(tmp, sentinel)

def process_file(input_file):
    input_path = Path(input_file)
    preflight_input(input_path)   # tier 0: free checks, always

    book_name = input_path.stem
    output_dir = Path(OUTPUT_ROOT) / book_name

    config = {
        "voice": VOICE,
        "speed": SPEED,
        "format": FORMAT,
        "model": MODEL_FILE,
        "voices": VOICES_FILE,
    }
    logger.info(f"Processing '{input_file}'…")

    # Step 0: decide render vs. skip from the completion sentinel
    fingerprint = compute_fingerprint(input_path, config)
    if not should_render(output_dir, fingerprint):
        logger.info(f"Finished audiobook already in: {output_dir}")
        return

    # Step 0.5: render-only preflight (CLI must exist and boot)
    preflight_render()
    clean_output_dir(output_dir)

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

    # Step 3: mark the run complete (atomic write)
    write_sentinel(output_dir, fingerprint)

    logger.info(f"\n✔ Done! Final chapters saved in: {output_dir}")

def main():
    if len(sys.argv) < 2:
        print("Drag  & drop a TXT, EPUB, or PDF onto this script.")
        sys.exit(1)

    process_file(sys.argv[1])

if __name__ == "__main__":
    main()