# Convert to Audiobook (Kokoro TTS)

This project provides a **drag-and-drop audiobook converter** using [Kokoro TTS](https://github.com/nazdridoy/kokoro-tts) to transform text-based files (TXT, EPUB, PDF) into audio files.

Drag a file onto `convert_to_audiobook.bat` and the script handles the rest: it splits the book into chapters, renders speech on your GPU, merges the chunks into chapter files, and remembers the result so re-runs are instant.

---

## Features

- Supports **TXT, EPUB, and PDF** input files.
- Renders on **GPU via CUDA** (onnxruntime-gpu).
- Splits large files into chapters, then merges the chunks into final audio files.
- **Skips already-rendered books**: a `COMPLETE` sentinel stores a fingerprint of the voice, speed, format, model, and source content hash. Re-running a finished book returns instantly.
- **Re-renders automatically** when anything changes: edit the source file, or switch voice, speed, or format, and the next run rebuilds the audio.
- **Preflight validation**: unsupported file types, missing model files, or a broken venv are reported as friendly messages before rendering starts.
- Configurable **voice, speed, format, and model**.

---

## Prerequisites

1. **Python 3.9 - 3.12** (Kokoro TTS does not support 3.13+).
2. **Kokoro TTS CLI** installed into the project venv. From the project folder:

   ```bash
   python -m venv venv
   venv\Scripts\pip install kokoro-tts
   ```

   Install the GPU runtime (optional but recommended, version must match your CUDA toolkit):

   ```bash
   venv\Scripts\pip install onnxruntime-gpu coloredlogs sympy
   ```

   The dependency tree includes numba, which requires **numpy 2.4 or less**. If you install numpy manually, pin it: `venv\Scripts\pip install "numpy==2.4.6"`.

   > Never install kokoro-tts with `--no-deps`. The CLI imports every dependency at startup, even for plain TXT input, so a partial install fails at the first chunk.

3. Place the following files in the same folder as `convert_to_audiobook.py`:

   - `kokoro-v1.0.onnx` -> Kokoro TTS model file
   - `voices-v1.0.bin` -> Voice definitions
   - `convert_to_audiobook.bat` -> Optional BAT file for drag-and-drop execution

---

## Usage

### 1. Drag & Drop

- Drag a TXT, EPUB, or PDF file onto `convert_to_audiobook.bat`.
- Output lands in `audiobook_output/<book_name>/`: per-chapter folders hold the raw chunks, `Chapter N.wav` (or `.mp3`) files are the finished chapters, and a `COMPLETE` file marks the run as done.
- Drop the same file again and the script skips instantly. Change the source or a config value and it re-renders automatically. To force a re-render, delete the `COMPLETE` file.

### 2. Command Line (Optional)

```bash
python convert_to_audiobook.py <path_to_file>
python convert_to_audiobook.py "D:\Books\story.txt"
```

For command-line use, activate the venv first so `kokoro-tts` is on PATH: `call venv\Scripts\activate.bat`.

---

## Configuration

You can modify the following parameters in `convert_to_audiobook.py`:

```python
KOKORO = "kokoro-tts"              # Kokoro CLI command
VOICE = "bf_isabella"              # Default voice
SPEED = "1.0"                      # Speech speed
FORMAT = "wav"                     # Output audio format (wav or mp3)
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"
OUTPUT_ROOT = "audiobook_output"   # Root output folder
SUPPORTED_EXTS = {".txt", ".epub", ".pdf"}
```

Changing `VOICE`, `SPEED`, `FORMAT`, `MODEL_FILE`, or `VOICES_FILE`, or editing the source file, invalidates the stored fingerprint and triggers a re-render on the next run.

---

## Troubleshooting

- **"CLI 'kokoro-tts' not found on PATH"**: launch via the BAT file, or activate the venv first.
- **"The venv is missing dependencies"**: run `venv\Scripts\pip install --force-reinstall kokoro-tts` to re-resolve the full dependency tree.
- **"Unsupported file type"**: only TXT, EPUB, and PDF are accepted.
- **Render uses CPU instead of GPU**: make sure only `onnxruntime-gpu` is installed. The plain `onnxruntime` (CPU) package and the GPU build install files to the same paths, so the last one installed wins. Evict the CPU build with `venv\Scripts\pip uninstall -y onnxruntime` and reinstall `onnxruntime-gpu`.
