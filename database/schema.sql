CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS documents (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(), original_filename TEXT NOT NULL,
 storage_key TEXT NOT NULL UNIQUE, mime_type TEXT NOT NULL, size_bytes BIGINT NOT NULL CHECK(size_bytes>0),
 sha256 CHAR(64) NOT NULL, page_count INTEGER, status TEXT NOT NULL DEFAULT 'uploaded',
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS verifications (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(), document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
 status TEXT NOT NULL DEFAULT 'completed', risk_score NUMERIC(5,2), risk_level TEXT,
 coverage_weight_percent NUMERIC(5,2), unavailable_categories JSONB NOT NULL DEFAULT '[]',
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS extracted_fields (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(), verification_id UUID NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
 field_name TEXT NOT NULL, field_value TEXT, page_number INTEGER, extraction_method TEXT NOT NULL,
 extraction_confidence NUMERIC(5,2)
);
CREATE TABLE IF NOT EXISTS findings (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(), verification_id UUID NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
 category TEXT NOT NULL, title TEXT NOT NULL, severity TEXT NOT NULL, description TEXT NOT NULL,
 evidence JSONB NOT NULL DEFAULT '{}', page_numbers INTEGER[] NOT NULL DEFAULT '{}',
 confidence NUMERIC(5,2), recommended_action TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS registry_records (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 source_label TEXT NOT NULL DEFAULT 'SYNTHETIC DEMO REGISTRY DATA — GovTech Sandbox',
 registration_number TEXT, owner_name TEXT, survey_number TEXT, khata_number TEXT,
 village TEXT, tehsil TEXT, district TEXT, area_hectares NUMERIC(12,4),
 is_synthetic BOOLEAN NOT NULL DEFAULT TRUE CHECK(is_synthetic=TRUE)
);
CREATE TABLE IF NOT EXISTS risk_categories (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(), verification_id UUID NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
 category_code TEXT NOT NULL, weight_percent NUMERIC(5,2) NOT NULL, available BOOLEAN NOT NULL,
 concern_score NUMERIC(5,2), reason_unavailable TEXT, evidence JSONB NOT NULL DEFAULT '{}',
 UNIQUE(verification_id, category_code)
);
