-- ============================================================
-- Competitor Intelligence Tables for Ziyada System
-- Run in Supabase SQL Editor: https://supabase.com/dashboard
-- ============================================================

-- Table 1: Raw competitor data from scraping
CREATE TABLE IF NOT EXISTS competitor_intel (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  scraped_at timestamptz DEFAULT now(),
  source text NOT NULL CHECK (source IN ('website', 'instagram', 'tiktok', 'youtube')),
  content_type text CHECK (content_type IN ('article', 'post', 'video', 'reel', 'podcast')),
  original_url text,
  original_title text,
  topic text,
  keywords text[],
  writing_style_notes text,
  engagement_score int DEFAULT 0,
  raw_data jsonb,
  created_at timestamptz DEFAULT now()
);

-- Table 2: AI-generated content suggestions
CREATE TABLE IF NOT EXISTS content_suggestions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  competitor_intel_id uuid REFERENCES competitor_intel(id) ON DELETE SET NULL,
  platform text NOT NULL CHECK (platform IN ('blog', 'tiktok', 'instagram', 'facebook', 'linkedin')),
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'published')),
  title_ar text,
  title_en text,
  content_ar text,
  content_en text,
  hooks jsonb,
  banana_image_prompt text,
  carousel_prompt text,
  sora_video_prompt text,
  vue3_animation_prompt text,
  canva_brief text,
  blog_post_id uuid,
  approved_at timestamptz,
  created_at timestamptz DEFAULT now()
);

-- Table 3: Blog posts (drafts and published)
CREATE TABLE IF NOT EXISTS blog_posts (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title_ar text,
  title_en text,
  content_ar text,
  content_en text,
  excerpt_ar text,
  excerpt_en text,
  slug text UNIQUE,
  category text,
  tags text[],
  author text DEFAULT 'Ziyada',
  published boolean DEFAULT false,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'published', 'archived')),
  published_at timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_competitor_intel_scraped_at ON competitor_intel(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_competitor_intel_source ON competitor_intel(source);
CREATE INDEX IF NOT EXISTS idx_content_suggestions_status ON content_suggestions(status);
CREATE INDEX IF NOT EXISTS idx_content_suggestions_platform ON content_suggestions(platform);
CREATE INDEX IF NOT EXISTS idx_content_suggestions_created ON content_suggestions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_suggestions_intel_id ON content_suggestions(competitor_intel_id);
CREATE INDEX IF NOT EXISTS idx_blog_posts_slug ON blog_posts(slug);
CREATE INDEX IF NOT EXISTS idx_blog_posts_status ON blog_posts(status);
CREATE INDEX IF NOT EXISTS idx_blog_posts_created ON blog_posts(created_at DESC);

-- RLS Policies
ALTER TABLE competitor_intel ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;

-- Allow service_role full access (for n8n)
CREATE POLICY "service_role_competitor_intel" ON competitor_intel
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_content_suggestions" ON content_suggestions
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_blog_posts" ON blog_posts
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Allow anon read (for frontend)
CREATE POLICY "anon_read_competitor_intel" ON competitor_intel
  FOR SELECT TO anon USING (true);

CREATE POLICY "anon_read_content_suggestions" ON content_suggestions
  FOR SELECT TO anon USING (true);

CREATE POLICY "anon_read_blog_posts" ON blog_posts
  FOR SELECT TO anon USING (published = true);

-- Allow anon update suggestion status (for frontend approve/reject)
CREATE POLICY "anon_update_suggestion_status" ON content_suggestions
  FOR UPDATE TO anon
  USING (true)
  WITH CHECK (status IN ('pending', 'approved', 'rejected', 'published'));

-- Allow anon insert suggestions (for frontend generate button)
CREATE POLICY "anon_insert_content_suggestions" ON content_suggestions
  FOR INSERT TO anon WITH CHECK (true);

-- Helper function: auto-update updated_at on blog_posts
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_blog_posts_updated_at
  BEFORE UPDATE ON blog_posts
  FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
