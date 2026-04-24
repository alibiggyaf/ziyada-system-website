import { useEffect } from "react";
import { useOutletContext, useParams, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { Calendar, ArrowLeft, ArrowRight, Clock } from "lucide-react";
import { staticPosts } from "./blogContent";
import useSEO from "@/lib/useSEO";
import { trackEvent } from "@/lib/analytics";

function getReadingTime(text) {
  const words = (text || '').split(/\s+/).length
  return Math.max(1, Math.ceil(words / 200))
}

const proseStyles = `
.blog-prose h1 { font-size: 2rem; font-weight: 800; margin: 1.6em 0 0.6em; line-height: 1.3; }
.blog-prose h2 { font-size: 1.6rem; font-weight: 700; margin: 1.4em 0 0.5em; line-height: 1.35; }
.blog-prose h3 { font-size: 1.3rem; font-weight: 700; margin: 1.2em 0 0.4em; line-height: 1.4; }
.blog-prose h4 { font-size: 1.1rem; font-weight: 600; margin: 1em 0 0.4em; }
.blog-prose p { margin: 0 0 1em; }
.blog-prose ul { list-style-type: disc; padding-inline-start: 1.8em; margin: 0 0 1em; }
.blog-prose ol { list-style-type: decimal; padding-inline-start: 1.8em; margin: 0 0 1em; }
.blog-prose li { margin: 0.3em 0; }
.blog-prose li > ul, .blog-prose li > ol { margin: 0.3em 0 0.3em; }
.blog-prose blockquote {
  border-inline-start: 4px solid var(--accent-primary, #7c3aed);
  padding: 0.6em 1.2em;
  margin: 1em 0;
  font-style: italic;
  opacity: 0.9;
  background: rgba(124,58,237,0.06);
  border-radius: 0 8px 8px 0;
}
.blog-prose code {
  font-family: 'Fira Code', 'Consolas', monospace;
  background: rgba(124,58,237,0.1);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
}
.blog-prose pre {
  background: rgba(15,23,42,0.85);
  border: 1px solid rgba(124,58,237,0.2);
  border-radius: 8px;
  padding: 1em 1.2em;
  overflow-x: auto;
  margin: 1em 0;
}
.blog-prose pre code {
  background: none;
  padding: 0;
  font-size: 0.88em;
  color: #e2e8f0;
}
.blog-prose a {
  color: var(--accent-primary, #7c3aed);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.blog-prose a:hover { opacity: 0.8; }
.blog-prose img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1em auto;
  display: block;
}
.blog-prose table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}
.blog-prose th, .blog-prose td {
  border: 1px solid rgba(124,58,237,0.2);
  padding: 0.5em 0.8em;
  text-align: start;
}
.blog-prose th {
  background: rgba(124,58,237,0.1);
  font-weight: 600;
}
.blog-prose hr {
  border: none;
  border-top: 1px solid rgba(124,58,237,0.2);
  margin: 2em 0;
}
.blog-prose strong { font-weight: 700; }
`;

export default function BlogPost() {
  const { lang } = useOutletContext();
  const isRTL = lang === "ar";

  // Support clean URLs (/blog/:slug) and legacy query params (/BlogPost?slug=xxx&id=xxx)
  const { slug: routeSlug } = useParams();
  const [searchParams] = useSearchParams();
  const slug = routeSlug || searchParams.get("slug");
  const id = searchParams.get("id");

  useEffect(() => {
    if (slug) {
      trackEvent('blog_read', { slug });
    }
  }, [slug]);

  const { data: dbPost, isLoading } = useQuery({
    queryKey: ["blog_post", id, slug],
    queryFn: async () => {
      if (id) {
        const res = await siteApi.entities.BlogPost.filter({ id });
        return res?.[0] || null;
      }
      if (slug) {
        const res = await siteApi.entities.BlogPost.filter({ slug });
        return res?.[0] || null;
      }
      return null;
    },
    enabled: !!id || !!slug,
  });

  // If no DB post found (or loading a slug), fall back to static content
  const staticPost = slug ? staticPosts.find(p => p.slug === slug) : null;
  const post = dbPost || staticPost;

  const Arrow = isRTL ? ArrowRight : ArrowLeft;

  // Compute reading time from the content that will be displayed
  const contentText = post ? (isRTL ? post.content_ar : post.content_en) : "";
  const readingTime = getReadingTime(contentText);

  // SEO metadata for the loaded post
  useSEO({
    title: post ? (lang === 'ar' ? post.title_ar : post.title_en) : (isRTL ? 'مقال — زيادة سيستم' : 'Article — Ziyada Systems'),
    titleEn: post ? post.title_en : 'Article — Ziyada Systems',
    description: post ? (lang === 'ar' ? post.excerpt_ar : post.excerpt_en) : '',
    descriptionEn: post ? post.excerpt_en : '',
    path: post ? `/blog/${post.slug}` : '/Blog',
    schema: post ? {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: post.title_en,
      description: post.excerpt_en,
      author: { '@type': 'Person', name: post.author || 'Ziyada' },
      datePublished: post.published_date,
      image: post.cover_image,
    } : undefined,
  });

  if (isLoading) return (
    <div style={{ maxWidth: 800, margin: "60px auto", padding: "0 24px" }}>
      <div className="glass-panel" style={{ padding: 40, height: 400 }} />
    </div>
  );

  if (!post) return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 800, margin: "60px auto", padding: "0 24px", textAlign: "center" }}>
      <p style={{ color: "var(--text-primary)", opacity: 0.82 }}>{isRTL ? "المقال غير موجود" : "Post not found"}</p>
      <Link to="/Blog"><button className="btn-outline-ziyada" style={{ marginTop: 20 }}>{isRTL ? "العودة للمدونة" : "Back to Blog"}</button></Link>
    </div>
  );

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 800, margin: "0 auto", padding: "60px 24px" }}>
      <style>{proseStyles}</style>

      <Link to="/Blog" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "var(--text-primary)", opacity: 0.78, textDecoration: "none", marginBottom: 32, fontSize: "0.9rem" }}>
        <Arrow size={16} /> {isRTL ? "العودة للمدونة" : "Back to Blog"}
      </Link>

      {post.cover_image && (
        <img src={post.cover_image} alt={isRTL ? post.title_ar : post.title_en} style={{ width: "100%", height: 320, objectFit: "cover", borderRadius: 12, marginBottom: 36 }} />
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
        {post.tags?.map(t => (
          <span key={t} style={{ background: "rgba(124,58,237,0.15)", color: "var(--accent-primary)", fontSize: "0.8rem", padding: "3px 10px", borderRadius: 999 }}>{t}</span>
        ))}
      </div>

      <h1 style={{ fontSize: "2.2rem", fontWeight: 900, marginBottom: 12, lineHeight: 1.3 }}>
        {isRTL ? post.title_ar : post.title_en}
      </h1>
      <div style={{ display: "flex", alignItems: "center", gap: 12, color: "var(--text-primary)", opacity: 0.72, fontSize: "0.85rem", marginBottom: 36, flexWrap: "wrap" }}>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
          <Calendar size={14} />{post.published_date}
        </span>
        {post.author && <span>— {post.author}</span>}
        <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
          <Clock size={14} />
          {isRTL ? `${readingTime} دقيقة قراءة` : `${readingTime} min read`}
        </span>
      </div>

      <div className="blog-prose" style={{ color: "var(--text-primary)", opacity: 0.86, lineHeight: 1.9, fontSize: "1.05rem" }}>
        <ReactMarkdown>{isRTL ? post.content_ar : post.content_en}</ReactMarkdown>
      </div>
    </div>
  );
}
