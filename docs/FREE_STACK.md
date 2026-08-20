# Free-first production stack

The default stack is designed to run without paid LLM/TTS subscriptions:

- **LLM:** Gemini Flash through `GEMINI_API_KEY`.
- **TTS:** local Piper through `PIPER_EXECUTABLE` and `PIPER_MODEL`.
- **Space media:** NASA Image and Video Library provider.
- **Rendering:** FFmpeg.
- **Captions:** local caption pipeline.

## Secrets

Never commit API keys. Add `GEMINI_API_KEY` and YouTube OAuth credentials to the runtime environment or GitHub Actions Secrets.

## Gemini limits

The free tier is rate-limited and model availability can change. The provider therefore retries transient failures and keeps the model configurable through `GEMINI_MODEL`.

## Piper

Install Piper separately and download a compatible English voice model. Point `PIPER_MODEL` at that local model. The repository intentionally does not vendor voice binaries.

## Publishing

`PUBLISH_ENABLED=false` and `DRY_RUN=true` are the defaults. Enable YouTube only after a successful local render and manual QA of the first production sample.
