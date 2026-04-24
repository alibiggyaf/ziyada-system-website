import { useEffect } from "react";

const SITE_URL = "https://ziyadasystem.com";
const DEFAULT_OG_IMAGE = "/og-image.png";

export default function useSEO({ title, titleEn, description, descriptionEn, keywords, path, schema, noindex }) {
  useEffect(() => {
    // Title
    document.title = titleEn ? `${title} | ${titleEn}` : title;

    // Meta tags
    const metas = {
      description: description,
      keywords: keywords || "زيادة سيستم, أتمتة أعمال, CRM, تسويق رقمي, اكتساب عملاء, مواقع ذكية, محتوى, السعودية",
      "geo.region": "SA",
      "geo.position": "24.7136;46.6753",
      "geo.placename": "Riyadh, Saudi Arabia",
      "og:title": title,
      "og:description": description,
      "og:type": "website",
      "og:url": `${SITE_URL}${path || ""}`,
      "og:image": DEFAULT_OG_IMAGE,
      "og:locale": "ar_SA",
      "og:site_name": "Ziyada Systems | زيادة سيستم",
      "twitter:card": "summary_large_image",
      "twitter:title": titleEn ? `${title} | ${titleEn}` : title,
      "twitter:description": descriptionEn || description,
      "twitter:image": `${SITE_URL}${DEFAULT_OG_IMAGE}`,
    };

    Object.entries(metas).forEach(([name, content]) => {
      if (!content) return;
      const attr = name.startsWith("og:") ? "property" : "name";
      let el = document.querySelector(`meta[${attr}="${name}"]`);
      if (!el) {
        el = document.createElement("meta");
        el.setAttribute(attr, name);
        document.head.appendChild(el);
      }
      el.setAttribute("content", content);
    });

    // Robots noindex
    if (noindex) {
      let robotsMeta = document.querySelector('meta[name="robots"]');
      if (!robotsMeta) {
        robotsMeta = document.createElement("meta");
        robotsMeta.setAttribute("name", "robots");
        document.head.appendChild(robotsMeta);
      }
      robotsMeta.setAttribute("content", "noindex,nofollow");
    } else {
      const robotsMeta = document.querySelector('meta[name="robots"]');
      if (robotsMeta) robotsMeta.remove();
    }

    // Canonical
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement("link");
      canonical.setAttribute("rel", "canonical");
      document.head.appendChild(canonical);
    }
    canonical.setAttribute("href", `${SITE_URL}${path || ""}`);

    // hreflang
    const hreflangs = [
      { lang: "ar", href: `${SITE_URL}${path || ""}` },
      { lang: "en", href: `${SITE_URL}${path || ""}` },
      { lang: "x-default", href: `${SITE_URL}${path || ""}` },
    ];
    document.querySelectorAll('link[rel="alternate"][hreflang]').forEach(el => el.remove());
    hreflangs.forEach(({ lang, href }) => {
      const link = document.createElement("link");
      link.setAttribute("rel", "alternate");
      link.setAttribute("hreflang", lang);
      link.setAttribute("href", href);
      document.head.appendChild(link);
    });

    // Schema.org JSON-LD
    if (schema) {
      let scriptEl = document.querySelector('script[data-seo="ziyada"]');
      if (!scriptEl) {
        scriptEl = document.createElement("script");
        scriptEl.setAttribute("type", "application/ld+json");
        scriptEl.setAttribute("data-seo", "ziyada");
        document.head.appendChild(scriptEl);
      }
      scriptEl.textContent = JSON.stringify(schema);
    }

    return () => {
      document.querySelectorAll('link[rel="alternate"][hreflang]').forEach(el => el.remove());
      const scriptEl = document.querySelector('script[data-seo="ziyada"]');
      if (scriptEl) scriptEl.remove();
      const robotsMeta = document.querySelector('meta[name="robots"]');
      if (robotsMeta) robotsMeta.remove();
    };
  }, [title, titleEn, description, descriptionEn, keywords, path, schema, noindex]);
}
