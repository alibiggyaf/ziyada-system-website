-- Ziyada System - Supabase Database Schema
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor > New Query)

CREATE TABLE IF NOT EXISTS public.leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text, email text, phone text, company text, company_size text,
  industry text, challenge text, services_requested text[] DEFAULT '{}',
  budget text, timeline text, source text DEFAULT 'contact',
  language text DEFAULT 'ar', status text DEFAULT 'new',
  utm_source text, utm_medium text, utm_campaign text, utm_term text, utm_content text,
  source_page text, hubspot_contact_id text, created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.bookings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_name text, lead_email text, lead_phone text, company text,
  company_size text, industry text, challenge text,
  booking_date text, booking_time text, status text DEFAULT 'pending',
  google_meet_link text, hubspot_deal_id text, language text DEFAULT 'ar',
  utm_source text, utm_medium text, utm_campaign text, utm_content text,
  source_page text, created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.blog_posts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug text UNIQUE, title_ar text, title_en text,
  excerpt_ar text, excerpt_en text, content_ar text, content_en text,
  category text, tags text[] DEFAULT '{}', author text, cover_image text,
  seo_title text, meta_description text, language text DEFAULT 'ar',
  status text DEFAULT 'draft', published boolean DEFAULT false,
  published_date text, created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.case_studies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title_ar text, title_en text, client text, industry text,
  challenge_ar text, challenge_en text, solution_ar text, solution_en text,
  result_ar text, result_en text, cover_image text, metrics jsonb DEFAULT '{}',
  published boolean DEFAULT true, display_order int DEFAULT 0, created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.subscribers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE, name text, language text DEFAULT 'ar',
  status text DEFAULT 'active', welcome_email_sent boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.faq_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  question_ar text, question_en text, answer_ar text, answer_en text,
  category text, display_order int DEFAULT 0, published boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.services (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug text UNIQUE, title_ar text, title_en text,
  description_ar text, description_en text, icon text, features jsonb DEFAULT '[]',
  display_order int DEFAULT 0, published boolean DEFAULT true, created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.settings (
  key text PRIMARY KEY, value jsonb, updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  role text DEFAULT 'developer' CHECK (role IN ('owner', 'developer')),
  display_name text, created_at timestamptz DEFAULT now()
);

-- RLS
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.case_studies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.faq_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.services ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Leads: public insert, authenticated read/update/delete
CREATE POLICY "leads_insert" ON public.leads FOR INSERT WITH CHECK (true);
CREATE POLICY "leads_select" ON public.leads FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "leads_update" ON public.leads FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "leads_delete" ON public.leads FOR DELETE USING (auth.role() = 'authenticated');

-- Bookings: public insert, authenticated read/update/delete
CREATE POLICY "bookings_insert" ON public.bookings FOR INSERT WITH CHECK (true);
CREATE POLICY "bookings_select" ON public.bookings FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "bookings_update" ON public.bookings FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "bookings_delete" ON public.bookings FOR DELETE USING (auth.role() = 'authenticated');

-- Blog: public read published, authenticated CRUD
CREATE POLICY "blog_select" ON public.blog_posts FOR SELECT USING (published = true OR auth.role() = 'authenticated');
CREATE POLICY "blog_insert" ON public.blog_posts FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "blog_update" ON public.blog_posts FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "blog_delete" ON public.blog_posts FOR DELETE USING (auth.role() = 'authenticated');

-- Cases: public read published, authenticated CRUD
CREATE POLICY "cases_select" ON public.case_studies FOR SELECT USING (published = true OR auth.role() = 'authenticated');
CREATE POLICY "cases_insert" ON public.case_studies FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "cases_update" ON public.case_studies FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "cases_delete" ON public.case_studies FOR DELETE USING (auth.role() = 'authenticated');

-- Subscribers: public insert, authenticated read/update/delete
CREATE POLICY "subs_insert" ON public.subscribers FOR INSERT WITH CHECK (true);
CREATE POLICY "subs_select" ON public.subscribers FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "subs_update" ON public.subscribers FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "subs_delete" ON public.subscribers FOR DELETE USING (auth.role() = 'authenticated');

-- FAQ: public read published, authenticated CRUD
CREATE POLICY "faq_select" ON public.faq_items FOR SELECT USING (published = true OR auth.role() = 'authenticated');
CREATE POLICY "faq_insert" ON public.faq_items FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "faq_update" ON public.faq_items FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "faq_delete" ON public.faq_items FOR DELETE USING (auth.role() = 'authenticated');

-- Services: public read published, authenticated CRUD
CREATE POLICY "services_select" ON public.services FOR SELECT USING (published = true OR auth.role() = 'authenticated');
CREATE POLICY "services_insert" ON public.services FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "services_update" ON public.services FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "services_delete" ON public.services FOR DELETE USING (auth.role() = 'authenticated');

-- Settings: authenticated only
CREATE POLICY "settings_select" ON public.settings FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "settings_insert" ON public.settings FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "settings_update" ON public.settings FOR UPDATE USING (auth.role() = 'authenticated');

-- Profiles: authenticated read, update own
CREATE POLICY "profiles_select" ON public.profiles FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "profiles_update" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "profiles_insert" ON public.profiles FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, display_name, role)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email), 'developer');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Default settings
INSERT INTO public.settings (key, value) VALUES
  ('company', '{"name_ar": "زيادة", "name_en": "Ziyada", "email": "ziyadasystem@gmail.com"}'),
  ('social_links', '{"twitter": "", "linkedin": "", "instagram": "", "whatsapp": ""}'),
  ('integrations', '{"n8n_webhook_url": "", "hubspot_enabled": false, "blog_api_key": ""}')
ON CONFLICT (key) DO NOTHING;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_leads_status ON public.leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created ON public.leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON public.bookings(booking_date);
CREATE INDEX IF NOT EXISTS idx_blog_posts_slug ON public.blog_posts(slug);
CREATE INDEX IF NOT EXISTS idx_blog_posts_published ON public.blog_posts(published);
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON public.subscribers(email);
CREATE INDEX IF NOT EXISTS idx_faq_items_order ON public.faq_items(display_order);
CREATE INDEX IF NOT EXISTS idx_services_order ON public.services(display_order);
