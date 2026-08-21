# Production v1

## What is implemented

- OpenAI Responses API script-generation adapter (`OPENAI_API_KEY`)
- NASA Image & Video Library discovery boundary
- Asset download + media manifest
- TTS provider contract + WAV timing probe
- Scene retiming from measured narration duration
- SRT caption generation
- FFmpeg mux/render adapter
- Thumbnail brief generation
- YouTube OAuth credential validation boundary
- Final publish gate

## Required local tools

- Python 3.11+
- FFmpeg on PATH for rendering

## Required credentials for live production

- `OPENAI_API_KEY` and optional `OPENAI_MODEL`
- A TTS provider key once a concrete TTS adapter is selected
- YouTube OAuth client ID, client secret and refresh token for publishing

NASA media discovery does not require a private API key in the current adapter.

## Safe execution order

1. Generate/retrieve research.
2. Verify claims and reject unsupported claims.
3. Generate the script from the verified packet.
4. Generate narration and measure its duration.
5. Retime scenes from measured audio.
6. Retrieve eligible media and write the manifest.
7. Generate captions and render the video.
8. Run quality/publish gates.
9. Keep YouTube uploads disabled until OAuth is configured and a human has inspected a test render.

The repository intentionally does not commit credentials and the YouTube adapter fails closed until a real OAuth implementation is connected.
