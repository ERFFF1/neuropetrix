-- Reports core migration
-- Core reports functionality

CREATE TABLE IF NOT EXISTS reports(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id TEXT NOT NULL,
  modality TEXT NOT NULL,
  version INTEGER NOT NULL,
  body TEXT NOT NULL,
  structured_json TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_reports_patient_modality ON reports(patient_id, modality);
