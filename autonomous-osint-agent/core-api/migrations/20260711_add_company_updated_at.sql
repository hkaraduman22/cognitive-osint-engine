ALTER TABLE companies
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

UPDATE companies
SET updated_at = created_at
WHERE updated_at IS NULL;

ALTER TABLE companies
ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE companies
ALTER COLUMN updated_at SET NOT NULL;
