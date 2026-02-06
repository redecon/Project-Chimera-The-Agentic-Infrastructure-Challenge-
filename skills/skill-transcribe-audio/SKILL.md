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
- Success case: `success: true`, `transcript`, optional `segments`, `confidence`, `error: null`.
- Failure case: `success: false`, `error` (string) describing failure.

Error handling notes
- Possible error cases:
  - `InvalidInput`: missing both `audio_file_path` and `audio_url`.
  - `FileNotFound`: local path missing or remote URL returns 404.
  - `UnsupportedFormat`: audio codec/container unsupported.
  - `Timeout`: network fetch timed out or model decoding timed out.
  - `ModelError`: transcription model failed or returned invalid output.
  - `InsufficientPermissions`: cannot read file due to permissions.
  - `BudgetExceeded`: transcription token/billing budget exceeded.
- Behavior:
  - Use streaming downloads and intermediate file validation (ffmpeg probe) before sending to transcription model.
  - On transient model errors or network failures, retry with exponential backoff (max 3 attempts).
  - Return `success: false` with a concise `error` message and write detailed diagnostics to provenance logs.

Dependencies
- System: `ffmpeg` for audio probing and format conversion.
- Libraries/Models: `whisper`/OpenAI/Gemini adapter or internal ASR model, `pydub` or `ffmpeg-python` for pre-processing.
- MCP: must call transcription model through MCP adapter to ensure billing/accounting and policy checks.

Example error responses
- File not found (remote):

```json
{ "success": false, "error": "File not found (HTTP 404)" }
```

- Unsupported format:

```json
{ "success": false, "error": "Unsupported audio format: application/octet-stream" }
```

Behavioral notes
- Implementations SHOULD provide reasonable defaults for `model` and honor `language` hints when available.
- When `diarize=true`, include `speaker` labels in segments; otherwise `speaker` may be omitted or null.

Traceability
- Contract schema: [skills/skill-transcribe-audio/schema.json](skills/skill-transcribe-audio/schema.json)
- Link this skill in ingestion enrichment pipelines that require text extraction from media.
