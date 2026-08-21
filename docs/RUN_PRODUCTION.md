# End-to-end production run

## Prerequisites

- Python 3.11+
- FFmpeg installed and available on PATH
- Piper installed and available on PATH
- A compatible Piper English voice model
- Gemini API key in `GEMINI_API_KEY`

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell use `.venv\Scripts\Activate.ps1`.

Copy `.env.example` to `.env` and set:

```text
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
PIPER_EXECUTABLE=piper
PIPER_MODEL=/path/to/voice.onnx
```

## Dry run

```bash
python -m pipeline --topic "What Happens When a Star Dies?"
```

## Full local production

```bash
python -m pipeline --topic "What Happens When a Star Dies?" --live
```

The run creates:

- `research.json`
- `script.txt`
- `narration.wav`
- `media-manifest.json`
- `visuals.mp4`
- `documentary.mp4`
- `captions.srt`
- `shorts/short-01.mp4` ...
- `production.json`

The output is **never automatically published**. `production.json` records `publishable: false` until a human reviews the render. This is intentional.

## Visual behavior

The current free-first renderer uses downloaded NASA Image and Video Library preview assets as a deterministic slideshow with slow zoom. It is a working baseline renderer, not the final cinematic visual system. The next visual iteration should add asset-level video retrieval, scene-specific ranking, motion graphics and generated-visual fallback.
