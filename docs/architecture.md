# Architecture

Browser (React/Vite) → Flask REST API → validation/hash → OCR adapter → consistency rules → synthetic registry matcher → deterministic risk engine → JSON report.

- OCR/AI is not the final authority for scoring.
- API keys belong only in backend environment variables.
- Synthetic registry source label must remain visible.
- Unavailable checks are excluded from denominator and listed in the report.
- Uploaded files use generated names and are size/type limited.
