# Production pipeline

## 1. Topic discovery

Generate candidate topics from evergreen astronomy questions, recent discoveries and high-interest concepts. Score each candidate for curiosity, factual support, visual availability and Shorts potential.

## 2. Research

Every factual claim should carry one or more source records. Prefer authoritative scientific sources. NASA is a media/research provider, not a blanket license for every item found on nasa.gov.

## 3. Story and script

Build a 25–35 minute narrative with a strong opening, clear progression and accessible explanations. Avoid fabricated quotes, unsupported certainty and repetitive filler.

## 4. Scene planning

Split narration into scenes and assign a visual query to each scene. Once TTS audio is generated, retime scenes from measured audio durations rather than estimated word counts.

## 5. Media

Retrieve eligible media and save a manifest containing URL, provider, title, attribution and license/usage notes. If no suitable source asset exists, queue a generated visual using the same scene query.

## 6. Rendering

A render adapter consumes the edit decision list and produces 16:9 long-form output and 9:16 Shorts. Captions should be derived from narration/audio timing, not manually typed.

## 7. Quality gates

Do not publish if the script is outside configured length, factual claims lack sources, scene timing is invalid, required media attribution is missing, or the timeline is empty.

## 8. Publishing

YouTube credentials remain in GitHub Actions secrets. Publishing should be a separate final stage so a failed research, render or quality stage cannot accidentally upload a bad video.

## 9. Scheduling model

The intended channel cadence is one Short per day and one long-form documentary every two days. A scheduler should create a queue rather than hard-code individual upload dates.
