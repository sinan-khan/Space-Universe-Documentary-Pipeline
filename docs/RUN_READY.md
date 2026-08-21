# Run-ready checklist

## Local prerequisites

1. Python 3.11+
2. FFmpeg available on PATH
3. Piper installed and a compatible `.onnx` voice model downloaded locally
4. `GEMINI_API_KEY` set only in the local environment or GitHub Actions secrets
5. `GEMINI_MODEL` set to a currently available Gemini Flash model

## Safe test

```bash
python -m pipeline.run_pipeline_v2 --topic "What Happens When a Star Dies?"
```

This performs research only and does not call Gemini, Piper, FFmpeg rendering, or YouTube.

## Live render

```bash
python -m pipeline.run_pipeline_v2 --topic "What Happens When a Star Dies?" --live
```

Live mode generates the script and narration, downloads NASA preview assets, renders a baseline documentary, and creates six vertical Shorts. It does **not** upload to YouTube.

## QA gate

Do not enable automated publishing until `documentary.mp4` and all Shorts have been watched. The current renderer is intentionally a baseline slideshow; scene-aware media matching, captions burned into video, music/SFX, thumbnails, and YouTube OAuth remain separate production upgrades.
