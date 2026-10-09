# API contracts (`/api/v1`)

- `GET /health` — health/version.
- `GET /demo-cases` — list controlled synthetic cases.
- `POST /documents` — multipart file field `file`; returns `document_id`, filename, size, SHA-256.
- `POST /documents/{id}/analyze` — analyze uploaded file.
- `GET /verifications/{id}` — result object.
- `GET /verifications/{id}/report` — same result with disclaimer.
- `GET /registry/search?q=...` — synthetic records only.

Finding format: category, title, severity, description, evidence, page numbers, confidence (null unless a defined metric exists), recommended action.

Error format: `{"error":{"code":"INVALID_FILE","message":"Unsupported file type."}}`.
