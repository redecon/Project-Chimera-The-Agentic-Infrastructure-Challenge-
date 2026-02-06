Skill: transcribe-audio

Purpose
- Convert audio assets into machine-readable transcripts with optional speaker diarization and timecodes. Used by downstream enrichment and captioning workflows.

Schema
- Input / Output contract: [skills/skill-transcribe-audio/schema.json](skills/skill-transcribe-audio/schema.json)

Inputs
- `audio_file_path` (string) OR `audio_url` (string): Provide either a local path or a remote URL to the audio.
- `language` (string, optional): ISO language code hint (e.g., `en-US`).
- `model` (string, optional): Transcription model identifier.
- `diarize` (boolean, optional): Enable speaker diarization when true.

Outputs
- `success` (boolean): True when transcription completes.
- `transcript` (string): Complete transcript text.
- `format` (string): Format of returned transcript (e.g., `plain`, `srt`).
- `segments` (array): Optional array of `start_seconds`, `end_seconds`, `text`, `speaker`, `confidence` objects.
- `language` (string): Detected or used language code.
- `confidence` (number): Aggregate confidence score if available.
- `error` (string|null): Error message when `success = false`.

Behavioral notes
- Implementations SHOULD provide reasonable defaults for `model` and honor `language` hints when available.
- When `diarize=true`, include `speaker` labels in segments; otherwise `speaker` may be omitted or null.

Traceability
- Contract schema: [skills/skill-transcribe-audio/schema.json](skills/skill-transcribe-audio/schema.json)
- Link this skill in ingestion enrichment pipelines that require text extraction from media.
