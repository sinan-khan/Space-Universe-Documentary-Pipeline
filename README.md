# Space-Universe-Documentary-Pipeline

Automated production engine for cinematic Space & Universe documentaries and Shorts.

## Goals

- Research-first, factual documentary generation
- 25–35 minute long-form videos
- Automatic extraction of multiple Shorts from every documentary
- NASA/public-domain media discovery with source attribution and usage checks
- Timestamped story-to-visual synchronization
- TTS narration, captions, music/SFX, thumbnails and YouTube metadata
- Dry-run mode for safe testing before publishing
- GitHub Actions orchestration

## Architecture

```text
Topic Discovery → Research → Story/Script → Scene Plan → Media Retrieval
                                      ↓
                         Narration + Timeline Sync
                                      ↓
                         Captions + Music + SFX
                                      ↓
                     Long-form → Shorts → Thumbnail
                                      ↓
                              Quality Gates
                                      ↓
                           YouTube Scheduling
```

The project deliberately separates providers from the pipeline so APIs can be swapped without rewriting the workflow.

## Safety and rights

NASA material is not automatically equivalent to NASA branding. The pipeline records source URLs, credits, usage notes and provider metadata. It should not use NASA insignia/logos to imply endorsement. Third-party material is never assumed to be reusable merely because it appears on a NASA page.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pipeline.cli run --topic "What Happens When a Star Dies?" --dry-run
```

See `docs/PIPELINE.md` and `.env.example` for configuration.

## Status

Foundation build: configuration, schemas, research/asset provider interfaces, deterministic scene planning, media manifests, rendering abstractions, Shorts extraction, metadata, quality gates, CLI, tests and CI are included. Provider credentials are intentionally not committed.
