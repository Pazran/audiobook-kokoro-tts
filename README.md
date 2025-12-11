# Convert to Audiobook (Kokoro TTS)

This project provides a **drag-and-drop audiobook converter** using [Kokoro TTS](https://github.com/nazdridoy/kokoro-tts) to transform text-based files (TXT, EPUB, PDF) into audio files.

The main script, `convert_to_audiobook.py`, is designed to be run via a BAT file: you simply **drag and drop a file** onto the BAT file, and the script will process it automatically.

---

## Features

- Supports **TXT, EPUB, and PDF** input files.
- Converts text into audio using Kokoro TTS.
- Splits large files into chapters, then merges them into final audio files.
- Configurable **voice, speed, format, and model**.
- Outputs audio into `audiobook_output/<book_name>/` folder.

---

## Prerequisites

1. **Python 3.8+** installed.
2. **Kokoro TTS CLI** installed:  
   Follow the official repository instructions: [Kokoro TTS GitHub](https://github.com/your-kokoro-git-link)

3. Place the following files in the same folder as `convert_to_audiobook.py`:

   - `kokoro-v1.0.onnx` → Kokoro TTS model file  
   - `voices-v1.0.bin` → Voice definitions  
   - `convert_to_audiobook.bat` → Optional BAT file for drag-and-drop execution

---

## Usage

### 1. Drag & Drop

- Drag a TXT, EPUB, or PDF file onto `convert_to_audiobook.bat`.
- The script will automatically process the file and create audio chapters in: audiobook_output/<book_name>/

### 2. Command Line (Optional)

```bash
python convert_to_audiobook.py <path_to_file>
python convert_to_audiobook.py "D:\Books\story.txt"
```

## Configuration

You can modify the following parameters in `convert_to_audiobook.py`:

```python
KOKORO = "kokoro-tts"          # Kokoro CLI command
VOICE = "af_bella"             # Default voice
SPEED = "1.0"                  # Speech speed
FORMAT = "wav"                 # Output audio format
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"
OUTPUT_ROOT = "audiobook_output"  # Root output folder
```
