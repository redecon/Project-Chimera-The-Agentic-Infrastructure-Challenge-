Skill: download-video

Purpose
- Download a video file from a remote HTTP(S) URL and save it to local storage or a configured artifact store. Designed to be idempotent for repeated requests with the same `url`.

Schema
- Input / Output contract: [skills/skill-download-video/schema.json](skills/skill-download-video/schema.json)

Inputs
- `url` (string, required): HTTP(S) URL of the video to download.
- `headers` (object, optional): Additional HTTP headers to include (e.g., Authorization).
- `filename` (string, optional): Preferred filename for the saved asset.
- `timeout_seconds` (integer, optional): Request timeout in seconds (default: 60).

Outputs
- `success` (boolean): True on successful download.
- `file_path` (string): Path to the saved file when `success = true`.
- `content_type` (string): MIME type detected for the downloaded file.
- `content_length` (integer): Size in bytes if known.
- `duration_seconds` (number|null): Optional media duration if parsed.
- `error` (string|null): Error message when `success = false`.

Behavioral notes
- Implementations SHOULD perform streaming downloads to avoid high memory usage.
- Implementations SHOULD validate `content_type` against an allowed whitelist when necessary.
- Save locations SHOULD be deterministic (e.g., `./data/videos/<sha1(url)>-<filename>`), enabling idempotent fetches.

Traceability
- Contract schema: [skills/skill-download-video/schema.json](skills/skill-download-video/schema.json)
- Link this skill usage from ingestion workflows that require media capture or archival.
