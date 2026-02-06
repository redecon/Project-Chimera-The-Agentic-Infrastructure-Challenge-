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
- Success case (schema): `success: true`, `file_path`, `content_type`, `content_length`, `duration_seconds`, `error: null`.
- Failure case (schema): `success: false`, `error` (string) describing the failure.

Error handling notes
- Possible error cases:
  - `InvalidInput`: missing or malformed `url`.
  - `HTTPError`: non-2xx response from remote (404/403/500).
  - `Timeout`: remote request timed out.
  - `DiskError`: insufficient disk space or permissions to write file.
  - `UnsupportedMedia`: downloaded content is not a supported video format.
  - `BudgetExceeded`: token/compute budget exceeded for this operation (if enforced).
- Behavior:
  - On transient network errors, perform a bounded retry with exponential backoff (max 3 attempts) before returning `success: false` with `error` describing the last error.
  - Never write secrets to logs. If authentication headers are used, mask sensitive values in logs.
  - Return structured errors (single-line `error` string) and write a detailed diagnostic entry to provenance/audit logs.

Dependencies
- System: `ffmpeg` installed for media probing (duration, format).
- Libraries: `requests` or `aiohttp`, `python-magic` (for MIME detection), `hashlib` (for deterministic filenames).
- MCP / services: Access to artifact storage service (S3 or internal object store) via MCP adapter; access to Redis for stream ack.

Example error responses
- File not found (HTTP 404):

```json
{ "success": false, "error": "HTTP 404 Not Found" }
```

- Timeout:

```json
{ "success": false, "error": "Timeout after 60s while downloading https://..." }
```

Behavioral notes
- Implementations SHOULD perform streaming downloads to avoid high memory usage.
- Implementations SHOULD validate `content_type` against an allowed whitelist when necessary.
- Save locations SHOULD be deterministic (e.g., `./data/videos/<sha1(url)>-<filename>`), enabling idempotent fetches.

Traceability
- Contract schema: [skills/skill-download-video/schema.json](skills/skill-download-video/schema.json)
- Link this skill usage from ingestion workflows that require media capture or archival.
