-- Reports extras migration
-- Add new columns to existing tables

ALTER TABLE report_templates ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE sentence_bank ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
