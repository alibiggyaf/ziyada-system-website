-- ═══════════════════════════════════════════════════════════
-- Ziyada System — Internal Guide Access Logs Table
-- Run this in: https://app.supabase.com/project/nuyscajjlhxviuyrxzyq/sql
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS guide_access_logs (
  id                   BIGSERIAL PRIMARY KEY,
  event_type           TEXT NOT NULL,
  event_label          TEXT,
  visitor_name         TEXT,
  ip_address           TEXT,
  country              TEXT,
  country_code         TEXT,
  city                 TEXT,
  region               TEXT,
  latitude             NUMERIC(10, 6),
  longitude            NUMERIC(10, 6),
  isp                  TEXT,
  timezone             TEXT,
  maps_link            TEXT,
  referrer             TEXT,
  utm_source           TEXT,
  user_agent           TEXT,
  screen_size          TEXT,
  platform             TEXT,
  page_url             TEXT,
  session_id           TEXT,
  attempt_number       INT,
  time_spent_seconds   INT,
  is_alert             BOOLEAN DEFAULT FALSE,
  extra_data           JSONB,
  created_at           TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast queries by event type and alert status
CREATE INDEX IF NOT EXISTS idx_guide_logs_event_type ON guide_access_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_guide_logs_is_alert ON guide_access_logs(is_alert);
CREATE INDEX IF NOT EXISTS idx_guide_logs_ip ON guide_access_logs(ip_address);
CREATE INDEX IF NOT EXISTS idx_guide_logs_created ON guide_access_logs(created_at DESC);

-- Disable public read (admin only via service_role key in N8N)
ALTER TABLE guide_access_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "No public access" ON guide_access_logs FOR ALL USING (false);
