# BhuSatya 50-document synthetic reference dataset

## Safety label
All PDFs and records are fictional synthetic data. They are not government records, certified copies, or examples of real citizens' records. Each PDF visibly states `SYNTHETIC DEMO — NOT A GOVERNMENT RECORD`. Do not present matches as official verification.

## Contents
- `backend/reference_dataset/catalog.json`: canonical fields, displayed document fields, category labels, and PDF paths for all 50 records.
- `backend/reference_dataset/documents/`: 50 generated PDF documents.
- `database/seed_50_synthetic_documents.sql`: inserts canonical synthetic registry records and the reference-document catalogue. Run after `database/schema.sql`.

## Distribution
- 001–010: consistent baseline (10)
- 011–020: cross-field survey-number mismatch (10)
- 021–030: area discrepancy (10)
- 031–035: missing/incomplete field (5)
- 036–040: metadata/image-indicator benchmark labels (5). PDFs do not claim actual image-forensic detection; labels are benchmark metadata only.
- 041–050: mixed survey and area anomalies (10)

## Matching behavior
`POST /api/v1/documents` then `POST /api/v1/documents/{document_id}/analyze` runs text extraction and attempts identifier-based matching against this local synthetic catalogue. It returns a candidate and field comparisons when identifiers are extracted. This is a heuristic demonstration, not a robust OCR parser or government integration. A no-match result does not imply forgery.

## API
- `GET /api/v1/reference-documents` — list/search catalogue.
- `GET /api/v1/reference-documents/{reference_id}/download` — download one synthetic PDF.
- `GET /api/v1/registry/search?q=...` — search 50 canonical synthetic records.

## Test plan
Upload at least one clean PDF and one anomalous PDF from this folder. Confirm reference ID extraction, candidate matching, field comparison, and visible synthetic disclaimer. Also test unrelated documents, image-only scans without OCR, unsupported file types, and oversized uploads.
