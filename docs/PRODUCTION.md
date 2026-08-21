# Production flow

The pipeline is designed as a gated sequence rather than one opaque AI call.

1. Topic selection
2. Research providers collect authoritative sources
3. Claims are linked to source IDs
4. Research quality gate rejects unsupported or review-required claims
5. Script engine creates a citation-aware writing brief
6. LLM provider generates narration only from the research packet
7. Scene planner maps narration to visual queries
8. Media providers search appropriate footage/images
9. Generated visuals are used only as a configured fallback
10. TTS produces measured narration durations
11. Scene timing is retimed to measured audio
12. Render plan targets 1920x1080 long-form or 1080x1920 Shorts
13. Captions, music and SFX are added by render adapters
14. Thumbnail brief is generated
15. Metadata is generated
16. Final quality gates run
17. YouTube upload/scheduling occurs only if every required gate passes

## Credentials

The repository contains no real secrets. Provider keys belong in GitHub Actions secrets or local environment variables. NASA Image & Video Library access is designed to remain keyless; optional APIs are added only when their integration is implemented.

## Current state

The repository currently contains the contracts and orchestration boundaries for research, scripting, visuals, narration, rendering, thumbnails and publication. External LLM/TTS/image-generation/YouTube credentials are deliberately not hard-coded.
