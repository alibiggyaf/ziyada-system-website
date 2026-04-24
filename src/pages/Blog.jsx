import { useOutletContext } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { Link } from "react-router-dom";
import { Calendar } from "lucide-react";
import { staticPosts } from "./blogContent";
import useSEO from "@/lib/useSEO";

export default function Blog() {
  const { lang } = useOutletContext();
  const isRTL = lang === "ar";

  useSEO({
    title: "المدونة — زيادة سيستم",
    titleEn: "Blog — Ziyada Systems",
    description: "مقالات ورؤى حول الأتمتة والتسويق الرقمي وأنظمة النمو للشركات",
    path: "/Blog"
  });

  const { data: dbPosts = [], isLoading } = useQuery({
    queryKey: ["blog_posts"],
    queryFn: () => siteApi.entities.BlogPost.filter({ published: true }, "-published_date", 20)
  });

  // Use DB posts if available, otherwise fall back to static content file
  const posts = dbPosts.length > 0 ? dbPosts : staticPosts.filter(p => p.published);

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 1200, margin: "0 auto", padding: "60px 24px" }}>
      <div style={{ textAlign: "center", marginBottom: 60 }}>
        <h1 className="gradient-text" style={{ fontSize: "2.5rem", fontWeight: 900, marginBottom: 12 }}>
          {isRTL ? "المدونة" : "Blog"}
        </h1>
        <p style={{ color: "var(--text-primary)", opacity: 0.85 }}>
          {isRTL ? "أفكار وتحليلات من فريق زيادة" : "Insights and analysis from the Ziyada team"}
        </p>
      </div>

      {isLoading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 24 }}>
          {[1,2,3].map(i => (
            <div key={i} className="glass-panel" style={{ padding: 24, height: 260, animation: "pulse 1.5s infinite" }} />
          ))}
        </div>
      ) : posts.length === 0 ? (
        <div style={{ textAlign: "center", padding: "80px 0" }}>
          <div style={{ fontSize: "3rem", marginBottom: 16 }}>📝</div>
          <p style={{ color: "var(--text-primary)", opacity: 0.82, fontSize: "1.1rem" }}>
            {isRTL ? "المقالات قادمة قريباً..." : "Articles coming soon..."}
          </p>
          <p style={{ color: "var(--text-primary)", opacity: 0.75, fontSize: "0.85rem", marginTop: 8 }}>
            {isRTL ? "يمكن نشر المقالات تلقائياً عبر n8n" : "Articles can be auto-published via n8n workflow"}
          </p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 28 }}>
          {posts.map(post => (
            <Link key={post.id || post.slug} to={`/blog/${post.slug}`} style={{ textDecoration: "none" }}>
              <div className="glass-panel" style={{ overflow: "hidden", transition: "transform 0.2s, border-color 0.2s" }}
                onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-4px)"; e.currentTarget.style.borderColor = "var(--accent-primary)"; }}
                onMouseLeave={e => { e.currentTarget.style.transform = ""; e.currentTarget.style.borderColor = ""; }}>
                {post.cover_image && (
                  <img src={post.cover_image} alt={isRTL ? post.title_ar : post.title_en} style={{ width: "100%", height: 180, objectFit: "cover" }} />
                )}
                <div style={{ padding: 24 }}>
                  {post.tags?.length > 0 && (
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 10 }}>
                      {post.tags.slice(0, 3).map(t => (
                        <span key={t} style={{ background: "rgba(124,58,237,0.15)", color: "var(--accent-primary)", fontSize: "0.75rem", padding: "2px 8px", borderRadius: 999 }}>{t}</span>
                      ))}
                    </div>
                  )}
                  <h3 style={{ fontWeight: 800, fontSize: "1.1rem", marginBottom: 10, color: "var(--text-primary)" }}>
                    {isRTL ? post.title_ar : post.title_en}
                  </h3>
                  <p style={{ color: "var(--text-primary)", opacity: 0.82, fontSize: "0.9rem", lineHeight: 1.6, marginBottom: 14 }}>
                    {isRTL ? post.excerpt_ar : post.excerpt_en}
                  </p>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-primary)", opacity: 0.72, fontSize: "0.8rem" }}>
                    <Calendar size={12} />{post.published_date}
                    {post.author && <span style={{ marginRight: "auto", marginLeft: "auto" }}>— {post.author}</span>}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}