CREATE TABLE IF NOT EXISTS bookmarks (
  id SERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  title TEXT,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'processing', 'done', 'failed')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
