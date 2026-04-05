import { createClient } from '@supabase/supabase-js'
import { writeFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

const SITE_URL = 'https://www.ziyada-system.com'

// Try to read env vars (support both process.env and .env.local)
const supabaseUrl = process.env.VITE_SUPABASE_URL || 'https://nuyscajjlhxviuyrxzyq.supabase.co'
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY || ''

const staticPages = [
  { path: '/Home', priority: '1.0', changefreq: 'weekly' },
  { path: '/Services', priority: '0.9', changefreq: 'monthly' },
  { path: '/Services/automation', priority: '0.8', changefreq: 'monthly' },
  { path: '/Services/crm', priority: '0.8', changefreq: 'monthly' },
  { path: '/Services/lead-generation', priority: '0.8', changefreq: 'monthly' },
  { path: '/Services/marketing', priority: '0.8', changefreq: 'monthly' },
  { path: '/Services/web-development', priority: '0.8', changefreq: 'monthly' },
  { path: '/Services/social-media', priority: '0.8', changefreq: 'monthly' },
  { path: '/About', priority: '0.7', changefreq: 'monthly' },
  { path: '/Why', priority: '0.7', changefreq: 'monthly' },
  { path: '/Cases', priority: '0.7', changefreq: 'monthly' },
  { path: '/Blog', priority: '0.8', changefreq: 'weekly' },
  { path: '/BookMeeting', priority: '0.8', changefreq: 'monthly' },
  { path: '/RequestProposal', priority: '0.8', changefreq: 'monthly' },
  { path: '/Contact', priority: '0.7', changefreq: 'monthly' },
  { path: '/FAQ', priority: '0.6', changefreq: 'monthly' },
  { path: '/Privacy', priority: '0.3', changefreq: 'yearly' },
  { path: '/Terms', priority: '0.3', changefreq: 'yearly' },
]

async function generateSitemap() {
  const today = new Date().toISOString().split('T')[0]
  let blogPosts = []

  if (supabaseKey) {
    try {
      const supabase = createClient(supabaseUrl, supabaseKey)
      const { data } = await supabase
        .from('blog_posts')
        .select('slug, published_date, updated_at')
        .eq('published', true)
      blogPosts = data || []
    } catch (e) {
      console.warn('Could not fetch blog posts for sitemap:', e.message)
    }
  } else {
    console.warn('No Supabase key found, generating sitemap without blog posts')
  }

  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
  xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

  for (const page of staticPages) {
    xml += `  <url>\n`
    xml += `    <loc>${SITE_URL}${page.path}</loc>\n`
    xml += `    <lastmod>${today}</lastmod>\n`
    xml += `    <changefreq>${page.changefreq}</changefreq>\n`
    xml += `    <priority>${page.priority}</priority>\n`
    xml += `  </url>\n`
  }

  for (const post of blogPosts) {
    const lastmod = post.updated_at?.split('T')[0] || post.published_date || today
    xml += `  <url>\n`
    xml += `    <loc>${SITE_URL}/blog/${post.slug}</loc>\n`
    xml += `    <lastmod>${lastmod}</lastmod>\n`
    xml += `    <changefreq>monthly</changefreq>\n`
    xml += `    <priority>0.6</priority>\n`
    xml += `  </url>\n`
  }

  xml += '</urlset>\n'

  const outPath = resolve(__dirname, '..', 'public', 'sitemap.xml')
  writeFileSync(outPath, xml, 'utf-8')
  console.log(`Sitemap generated: ${outPath} (${staticPages.length + blogPosts.length} URLs)`)
}

generateSitemap()
