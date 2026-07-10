-- Adds a link table between user-owned search history and global company entities.
-- This keeps Company global while enabling per-user result views via SearchHistory.

CREATE TABLE IF NOT EXISTS search_history_companies (
    id SERIAL PRIMARY KEY,
    search_history_id INTEGER NOT NULL REFERENCES search_history(id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    confidence_score INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_search_history_company UNIQUE (search_history_id, company_id)
);

CREATE INDEX IF NOT EXISTS ix_search_history_companies_search_history_id
    ON search_history_companies (search_history_id);

CREATE INDEX IF NOT EXISTS ix_search_history_companies_company_id
    ON search_history_companies (company_id);
