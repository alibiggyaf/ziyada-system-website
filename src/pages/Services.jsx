import { useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import { IconZap, IconTarget, IconRocket, IconMegaphone, IconGlobe, IconShare } from "../components/ziyada/BrandIcons";
import useSEO from "@/lib/useSEO";
import { GlassButton } from "@/components/ui/glass-button";

const C = {
  ar: {
    title: "خدماتنا",
    sub: "منظومة متكاملة من الحلول الرقمية — نبنيها عشان شركتك تنمو بنظام، مو بجهد عشوائي",
    cta: "اطلب عرض سعر",
    learn_more: "اعرف أكثر",
    services: [
      { Icon: IconZap,       title: "أنظمة أتمتة الأعمال",              desc: "نحوّل الأعمال المتكررة إلى أنظمة ذكية تشتغل بسرعة واتساق — توفّر وقت الفريق وتقلّل الأخطاء وتخلّي كل شي مرتّب.", path: "/Services/automation",      sectors: ["التجزئة", "العقارات", "الرعاية الصحية", "التعليم"] },
      { Icon: IconTarget,    title: "أنظمة إدارة العملاء والمبيعات",    desc: "نبني لك نظام بيعي يرتّب المتابعة ويقفل الصفقات — من أول تواصل مع العميل لين يصير صفقة.", path: "/Services/crm",             sectors: ["الخدمات المهنية", "التجزئة", "B2B"] },
      { Icon: IconRocket,    title: "أنظمة اكتساب العملاء",             desc: "نلقط الفرص ونأهلها وندخلها مسار بيعي واضح — عشان ما تضيع فرصة واحدة.", path: "/Services/lead-generation",  sectors: ["التقنية", "الاستشارات", "الخدمات"] },
      { Icon: IconMegaphone, title: "التسويق الأدائي والظهور في البحث",  desc: "إعلانات + SEO مرتبطة بجودة العملاء مو بس المشاهدات — كل ريال تصرفه يرجع لك بنتيجة واضحة.", path: "/Services/marketing",        sectors: ["التجارة الإلكترونية", "التعليم", "العقارات"] },
      { Icon: IconGlobe,     title: "المواقع الذكية والمنصات الرقمية",   desc: "مواقع مربوطة بإدارة العملاء والأتمتة مو بس واجهة حلوة — موقعك يشتغل لك 24/7.", path: "/Services/web-development",  sectors: ["جميع القطاعات"] },
      { Icon: IconShare,     title: "أنظمة المحتوى ووسائل التواصل",     desc: "منظومة محتوى واضحة من الاستراتيجية للنشر للتقارير — حضورك الرقمي يخدم أهدافك التجارية.", path: "/Services/social-media",     sectors: ["التجزئة", "المطاعم", "الرياضة والترفيه"] },
    ]
  },
  en: {
    title: "Our Services",
    sub: "An integrated ecosystem of digital solutions — built so your company grows with systems, not scattered effort",
    cta: "Request a Proposal",
    learn_more: "Learn More",
    services: [
      { Icon: IconZap,       title: "Business Automation Systems",          desc: "Turn repetitive tasks into smart automated systems that run with speed and consistency — saving team time and eliminating errors.", path: "/Services/automation",      sectors: ["Retail", "Real Estate", "Healthcare", "Education"] },
      { Icon: IconTarget,    title: "CRM & Sales Systems",                  desc: "Build a complete sales system that organizes follow-ups and closes deals — from first contact to closed deal.", path: "/Services/crm",             sectors: ["Professional Services", "Retail", "B2B"] },
      { Icon: IconRocket,    title: "Customer Acquisition Systems",          desc: "Capture, qualify, and route leads into a clear sales path — so no opportunity is ever lost.", path: "/Services/lead-generation",  sectors: ["Tech", "Consulting", "Services"] },
      { Icon: IconMegaphone, title: "Performance Marketing & Search",        desc: "Ads + SEO tied to actual lead quality, not just impressions — every riyal spent returns a clear result.", path: "/Services/marketing",        sectors: ["E-commerce", "Education", "Real Estate"] },
      { Icon: IconGlobe,     title: "Smart Websites & Digital Platforms",    desc: "Websites connected to CRM and automation, not just a pretty frontend — your site works for you 24/7.", path: "/Services/web-development",  sectors: ["All Sectors"] },
      { Icon: IconShare,     title: "Content & Social Media Systems",        desc: "A clear content system from strategy to publishing to reports — your digital presence serves your business goals.", path: "/Services/social-media",     sectors: ["Retail", "Restaurants", "Sports & Entertainment"] },
    ]
  }
};

export default function Services() {
  const { lang } = useOutletContext();
  const c = C[lang] || C.ar;
  const isRTL = lang === "ar";

  useSEO({
    title: "خدماتنا — زيادة سيستم",
    titleEn: "Our Services — Ziyada Systems",
    description: "منظومة متكاملة من الحلول الرقمية: أتمتة، CRM، اكتساب عملاء، تسويق أدائي، مواقع ذكية، محتوى",
    path: "/Services",
    keywords: "خدمات زيادة سيستم, أتمتة أعمال, CRM, اكتساب عملاء, تسويق رقمي, مواقع ذكية, محتوى رقمي, السعودية"
  });

  return (
    <div dir={isRTL ? "rtl" : "ltr"} className="services-page" style={{ maxWidth: 1200, margin: "0 auto", padding: "28px 24px 56px" }}>
      <div style={{ textAlign: "center", maxWidth: 700, margin: "0 auto 60px" }}>
        <h1 className="gradient-text" style={{ fontSize: "2.5rem", fontWeight: 900, marginBottom: 16 }}>{c.title}</h1>
        <p>{c.sub}</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 28, marginBottom: 60 }}>
        {c.services.map((s, i) => (
          <div key={i} className="glass-panel glass-service-card" style={{ padding: 32, display: "flex", flexDirection: "column" }}>
            <div style={{ background: "linear-gradient(135deg,rgba(59,130,246,0.15),rgba(139,92,246,0.15))", borderRadius: 12, padding: 12, display: "inline-flex", marginBottom: 18, color: "var(--accent-primary)", width: "fit-content" }}>
              <s.Icon size={26} />
            </div>
            <h3 style={{ fontWeight: 800, fontSize: "1.2rem", marginBottom: 12, color: "var(--text-primary)" }}>{s.title}</h3>
            <p style={{ flexGrow: 1, marginBottom: 20 }}>{s.desc}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 20 }}>
              {s.sectors.map((sec, j) => (
                <span key={j} style={{ background: "rgba(59,130,246,0.1)", color: "var(--accent-primary)", fontSize: "0.75rem", padding: "3px 10px", borderRadius: 999, border: "1px solid rgba(59,130,246,0.2)" }}>{sec}</span>
              ))}
            </div>
            <Link to={s.path}>
              <GlassButton size="sm" className="w-full" contentClassName="justify-center font-semibold">
                {c.learn_more} ←
              </GlassButton>
            </Link>
          </div>
        ))}
      </div>

      <div style={{ textAlign: "center" }}>
        <Link to="/RequestProposal">
          <GlassButton size="lg" contentClassName="font-bold">
            {c.cta}
          </GlassButton>
        </Link>
      </div>
    </div>
  );
}