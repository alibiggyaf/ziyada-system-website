import { useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import { IconZap, IconTarget, IconRocket, IconMegaphone, IconGlobe, IconShare } from "../components/ziyada/BrandIcons";
import { GlassCard, GlassCardContent } from "@/components/ui/glass-card";
import useSEO from "@/lib/useSEO";

const SERVICES = {
  ar: [
  { Icon: IconZap, title: "أنظمة أتمتة الأعمال", desc: "نحوّل الأعمال المتكررة إلى أنظمة ذكية تشتغل بسرعة واتساق", path: "/Services/automation" },
  { Icon: IconTarget, title: "أنظمة إدارة العملاء والمبيعات", desc: "نبني لك نظام بيعي يرتّب المتابعة ويقفل الصفقات", path: "/Services/crm" },
  { Icon: IconRocket, title: "أنظمة اكتساب العملاء", desc: "نلقط الفرص ونأهلها وندخلها مسار بيعي واضح", path: "/Services/lead-generation" },
  { Icon: IconMegaphone, title: "التسويق الأدائي والظهور في البحث", desc: "إعلانات + SEO مرتبطة بجودة العملاء مو بس المشاهدات", path: "/Services/marketing" },
  { Icon: IconGlobe, title: "المواقع الذكية والمنصات الرقمية", desc: "مواقع مربوطة بإدارة العملاء والأتمتة مو بس واجهة حلوة", path: "/Services/web-development" },
  { Icon: IconShare, title: "أنظمة المحتوى ووسائل التواصل", desc: "منظومة محتوى واضحة من الاستراتيجية للنشر للتقارير", path: "/Services/social-media" }],

  en: [
  { Icon: IconZap, title: "Business Automation Systems", desc: "Turn repetitive tasks into smart automated systems that run with speed and consistency", path: "/Services/automation" },
  { Icon: IconTarget, title: "CRM & Sales Systems", desc: "Build a complete sales system that organizes follow-ups and closes deals", path: "/Services/crm" },
  { Icon: IconRocket, title: "Customer Acquisition Systems", desc: "Capture, qualify, and route leads into a clear sales path", path: "/Services/lead-generation" },
  { Icon: IconMegaphone, title: "Performance Marketing & Search", desc: "Ads + SEO tied to actual lead quality, not just impressions", path: "/Services/marketing" },
  { Icon: IconGlobe, title: "Smart Websites & Digital Platforms", desc: "Websites connected to CRM and automation, not just a pretty frontend", path: "/Services/web-development" },
  { Icon: IconShare, title: "Content & Social Media Systems", desc: "A clear content system from strategy to publishing to reports", path: "/Services/social-media" }]

};

const C = {
  ar: {
    hero_tag: "أنظمة زيادة — حيث يبدأ النمو المستدام",
    hero_title: "اجعل عملياتك تعمل بذكاء",
    hero_title2: "ليس بإجراءات تتكرّر",
    hero_eyebrow: "نبني الأساس. أنتَ تُعلي البناء.",
    hero_sub: "نبني لمنشأتك المنظومةَ الرقمية التي تُوحّد العمليات، وتُطلق كفاءة الفريق، وتمنح قيادتك سيطرةً تامة على الأداء — تحوّل هيكلي حقيقي، لا مجرد رقمنة.",
    hero_badges: ["كل مسار مُرتَّب", "كل مهمة مُؤتمَتة", "كل نتيجة قابلة للقياس والتطوير"],
    cta_primary: "ابنِ منظومتك معنا ←",
    cta_secondary: "اعرف كيف نعمل",
    services_title: "خدماتنا",
    services_sub: "منظومة متكاملة من الحلول الرقمية",
    stats: [
    { value: "50+", label: "شركة أتمتناها" },
    { value: "40%", label: "متوسط نمو الإيرادات" },
    { value: "80h", label: "توفير شهري لكل عميل" },
    { value: "3", label: "أشهر ضمان ما بعد التسليم" }],

    cta_section_title: "جاهز لبناء منظومة النمو الخاصة بك؟",
    cta_section_sub: "احجز استشارة مجانية مع فريقنا واكتشف كيف يمكننا مضاعفة إيراداتك"
  },
  en: {
    hero_tag: "Ziyada Systems — Where Sustainable Growth Begins",
    hero_title: "Leading Organizations Run on Systems That Think,",
    hero_title2: "Not Processes That Repeat",
    hero_eyebrow: "We Build the Foundation. You Scale the Vision.",
    hero_sub: "We build your integrated digital ecosystem — unifying operations, unlocking team capacity, and giving leadership full control over performance. Real structural transformation, not just digitization.",
    hero_badges: ["Every process structured", "Every task automated", "Every result measurable"],
    cta_primary: "Build Your System With Us →",
    cta_secondary: "See How We Work",
    services_title: "Our Services",
    services_sub: "An integrated ecosystem of digital solutions",
    stats: [
    { value: "50+", label: "Companies Automated" },
    { value: "40%", label: "Avg Revenue Growth" },
    { value: "80h", label: "Monthly Savings Per Client" },
    { value: "3", label: "Months Post-Delivery Guarantee" }],

    cta_section_title: "Ready to Build Your Growth System?",
    cta_section_sub: "Book a free consultation with our team and discover how we can multiply your revenue"
  }
};

export default function Home() {
  const { lang, theme } = useOutletContext();
  const c = C[lang] || C.ar;
  const services = SERVICES[lang] || SERVICES.ar;
  const isRTL = lang === "ar";

  useSEO({
    title: "زيادة سيستم — أنظمة نمو رقمية متكاملة",
    titleEn: "Ziyada Systems — Integrated Digital Growth Systems",
    description: "نبني لمنشأتك المنظومة الرقمية التي توحّد العمليات وتطلق كفاءة الفريق وتمنح قيادتك سيطرة كاملة على الأداء",
    path: "/Home",
    schema: { "@context": "https://schema.org", "@type": "Organization", name: "Ziyada Systems", url: "https://ziyadasystem.com", description: "Integrated digital growth systems for ambitious companies in Saudi Arabia" }
  });

  return (
    <div dir={isRTL ? "rtl" : "ltr"} className="page-fadein">
    <style>{`
      /* ── Hero entry animations ─────────────────────────── */
      @keyframes heroTitleReveal {
        from { opacity: 0; transform: translateY(32px) skewY(2deg); filter: blur(6px); }
        to   { opacity: 1; transform: translateY(0)   skewY(0deg); filter: blur(0); }
      }
      @keyframes heroFadeUp {
        from { opacity: 0; transform: translateY(22px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      @keyframes heroBadgePop {
        from { opacity: 0; transform: scale(0.8) translateY(10px); }
        to   { opacity: 1; transform: scale(1)   translateY(0); }
      }

      .hero-tag   { animation: heroFadeUp 0.6s cubic-bezier(.16,1,.3,1) both; }
      .hero-title { animation: heroTitleReveal 0.75s cubic-bezier(.16,1,.3,1) 0.1s both; }
      .hero-title2{ animation: heroTitleReveal 0.75s cubic-bezier(.16,1,.3,1) 0.22s both; }
      .hero-eyebrow{ animation: heroFadeUp 0.6s ease 0.35s both; }
      .hero-sub   { animation: heroFadeUp 0.6s ease 0.45s both; }
      .hero-badges span { animation: heroBadgePop 0.5s cubic-bezier(.34,1.56,.64,1) both; }
      .hero-badges span:nth-child(1) { animation-delay: 0.55s; }
      .hero-badges span:nth-child(2) { animation-delay: 0.65s; }
      .hero-badges span:nth-child(3) { animation-delay: 0.75s; }
      .hero-ctas  { animation: heroFadeUp 0.6s ease 0.85s both; }
      @media (max-width: 768px) {
        .hero-ctas { padding-bottom: 72px; }
      }

      .hero-subtitles-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(180px, 1fr));
        gap: 12px;
        max-width: 900px;
        margin: 0 auto 40px;
        align-items: start;
      }
      .hero-subtitle-card {
        border-color: rgba(255, 255, 255, 0.34) !important;
        background: linear-gradient(135deg, rgba(9, 18, 48, 0.62), rgba(14, 27, 60, 0.42));
      }
      .hero-subtitle-text {
        font-size: clamp(0.9rem, 1.5vw, 1rem);
        font-weight: 900;
        text-align: center;
        line-height: 1.45;
        color: #ffffff !important;
        opacity: 1 !important;
        text-shadow: 0 2px 16px rgba(2, 6, 23, 0.35);
      }
      .home-hero-shell {
        width: min(1100px, 100%);
        margin: 0 auto;
        padding: clamp(32px, 4vw, 54px) clamp(20px, 4vw, 48px);
        border-radius: 34px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        background:
          linear-gradient(160deg, rgba(8, 15, 34, 0.56), rgba(15, 23, 42, 0.34)),
          rgba(15, 23, 42, 0.22);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 22px 70px rgba(15, 23, 42, 0.22);
      }
      .home-hero-shell .hero-tag,
      .home-hero-shell .hero-eyebrow,
      .home-hero-shell .hero-sub,
      .home-hero-shell .hero-subtitle-text {
        color: var(--text-primary) !important;
      }
      .home-hero-shell .hero-eyebrow,
      .home-hero-shell .hero-sub,
      .home-hero-shell .hero-subtitle-text {
        text-shadow: 0 2px 18px rgba(2, 6, 23, 0.28);
      }
      .light-mode .home-hero-shell {
        border-color: rgba(37, 99, 235, 0.16);
        background:
          linear-gradient(160deg, rgba(255, 255, 255, 0.86), rgba(241, 245, 249, 0.74)),
          rgba(255, 255, 255, 0.7);
        box-shadow: 0 18px 54px rgba(15, 23, 42, 0.1);
      }
      .light-mode .home-hero-shell .hero-tag {
        background: rgba(37, 99, 235, 0.1) !important;
        border-color: rgba(37, 99, 235, 0.22) !important;
        color: #1d4ed8 !important;
      }
      .light-mode .home-hero-shell .hero-eyebrow,
      .light-mode .home-hero-shell .hero-sub,
      .light-mode .home-hero-shell .hero-subtitle-text {
        color: #0f172a !important;
        text-shadow: none;
        opacity: 1 !important;
      }
      .light-mode .hero-subtitle-card {
        border-color: rgba(37, 99, 235, 0.2) !important;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.88), rgba(239, 246, 255, 0.76));
      }
      .home-hero-secondary {
        color: var(--text-primary) !important;
      }
      .light-mode .home-hero-secondary {
        color: #0f172a !important;
        border-color: rgba(15, 23, 42, 0.14) !important;
        background: rgba(255, 255, 255, 0.58) !important;
      }
      .home-cta-card {
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        background:
          linear-gradient(160deg, rgba(8, 15, 34, 0.56), rgba(15, 23, 42, 0.34)),
          rgba(15, 23, 42, 0.22) !important;
        box-shadow: 0 22px 70px rgba(15, 23, 42, 0.22) !important;
      }
      .home-cta-title,
      .home-cta-sub {
        color: var(--text-primary) !important;
      }
      .light-mode .home-cta-card {
        border-color: rgba(37, 99, 235, 0.16) !important;
        background:
          linear-gradient(160deg, rgba(255, 255, 255, 0.86), rgba(241, 245, 249, 0.74)),
          rgba(255, 255, 255, 0.7) !important;
        box-shadow: 0 18px 54px rgba(15, 23, 42, 0.1) !important;
      }
      .light-mode .home-cta-title {
        color: #0f172a !important;
      }
      .light-mode .home-cta-sub {
        color: #1e293b !important;
        opacity: 1 !important;
      }

      @media (max-width: 980px) {
        .hero-subtitles-row {
          grid-template-columns: repeat(3, minmax(0, 1fr));
          max-width: 100%;
          gap: 8px;
        }
        .hero-subtitle-card {
          padding-top: 10px !important;
          padding-bottom: 10px !important;
        }
        .hero-subtitle-text {
          font-size: 0.82rem;
          line-height: 1.35;
        }
      }

      /* ── Animated gradient text ────────────────────────── */
      @keyframes gradientShiftHero {
        0%   { background-position: 0%   50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0%   50%; }
      }
      .gradient-text-hero {
        background: linear-gradient(270deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShiftHero 5s ease infinite;
      }
      @keyframes gradientShift {
        0%   { background-position: 0%   50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0%   50%; }
      }
      .gradient-text-anim {
        background: linear-gradient(270deg, #3b82f6, #8b5cf6, #3b82f6);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite;
      }

      /* ── CTA beam spin ─────────────────────────────────── */
      @keyframes ctaBeamSpin {
        from { --angle: 0deg; }
        to   { --angle: 360deg; }
      }
      @property --angle {
        syntax: '<angle>'; initial-value: 0deg; inherits: false;
      }
      .cta-beam-wrap {
        position: relative; border-radius: 60px; padding: 2px;
        background: conic-gradient(from var(--angle), transparent 60%, #3b82f6, #8b5cf6, transparent 80%);
        animation: ctaBeamSpin 3s linear infinite;
        display: inline-block;
      }
      .cta-beam-inner {
        border-radius: 58px; overflow: hidden;
      }

      /* ── Icon box hover ────────────────────────────────── */
      .icon-box-anim {
        transition: transform 0.35s cubic-bezier(.34,1.56,.64,1), box-shadow 0.3s;
      }
      .service-card:hover .icon-box-anim {
        transform: rotate(8deg) scale(1.18);
        box-shadow: 0 0 20px rgba(59,130,246,0.5);
      }

      /* ── Service card border glow ──────────────────────── */
      .service-card {
        transition: transform 0.3s cubic-bezier(.16,1,.3,1), box-shadow 0.3s, border-color 0.3s;
        border: 1px solid rgba(255,255,255,0.08);
      }
      .service-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 40px rgba(59,130,246,0.22);
        border-color: rgba(59,130,246,0.4) !important;
      }

      /* ── Stats counter pop ─────────────────────────────── */
      @keyframes statPop {
        from { opacity: 0; transform: scale(0.7) translateY(12px); }
        to   { opacity: 1; transform: scale(1)   translateY(0); }
      }
      .stat-item { animation: statPop 0.55s cubic-bezier(.34,1.56,.64,1) both; }
      .stat-item:nth-child(1) { animation-delay: 0.05s; }
      .stat-item:nth-child(2) { animation-delay: 0.15s; }
      .stat-item:nth-child(3) { animation-delay: 0.25s; }
      .stat-item:nth-child(4) { animation-delay: 0.35s; }

      /* ── Scroll reveal ─────────────────────────────────── */
      @keyframes revealUp {
        from { opacity: 0; transform: translateY(40px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      .reveal-section { animation: revealUp 0.7s cubic-bezier(.16,1,.3,1) both; }

      /* ── Page fade-in ──────────────────────────────────── */
      @keyframes pageFadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
      }
      .page-fadein { animation: pageFadeIn 0.5s ease both; }

      /* ── CTA section pulse glow ────────────────────────── */
      @keyframes ctaGlowPulse {
        0%, 100% { box-shadow: 0 0 30px rgba(59,130,246,0.15); }
        50%       { box-shadow: 0 0 60px rgba(139,92,246,0.3); }
      }
      .cta-section-card {
        animation: ctaGlowPulse 4s ease infinite;
      }
    `}</style>
      {/* Hero */}
      <section style={{ minHeight: "90vh", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "80px 24px 60px", position: "relative", overflow: "hidden" }}>
        <div className="home-hero-shell" style={{ position: "relative", zIndex: 1 }}>
          {/* Tag */}
          <div className="hero-tag" style={{ display: "inline-block", background: "rgba(59,130,246,0.12)", border: "1px solid rgba(59,130,246,0.3)", borderRadius: 999, padding: "6px 20px", marginBottom: 28, fontSize: "0.85rem", color: "var(--accent-primary)" }}>
            {c.hero_tag}
          </div>
          {/* Main headline */}
          <h1 className="hero-title" style={{ fontSize: "clamp(2.2rem, 5vw, 4rem)", fontWeight: 900, lineHeight: 1.25, marginBottom: 24 }}>
            <span style={{ background: "linear-gradient(270deg, #1e3a8a 0%, #3b82f6 40%, #7c3aed 70%, #1e3a8a 100%)", backgroundSize: "300% 300%", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text", animation: "gradientShiftHero 5s ease infinite" }}>
              {c.hero_title}
            </span>
          </h1>

          {/* Eyebrow */}
          <p className="hero-eyebrow" style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: 20 }}>
            {c.hero_eyebrow}
          </p>
          {/* Body */}
          <p className="hero-sub" style={{ fontSize: "clamp(0.95rem, 1.8vw, 1.05rem)", color: "var(--text-primary)", lineHeight: 1.85, marginBottom: 32, maxWidth: 680, margin: "0 auto 32px", opacity: 0.85 }}>
            {c.hero_sub}
          </p>
          {/* Horizontal subtitles */}
          <div className="hero-badges hero-subtitles-row">
            {c.hero_badges.map((badge, index) =>
            <GlassCard key={index} className="hero-subtitle-card py-4">
                <GlassCardContent className="px-4">
                  <p className="hero-subtitle-text">• {badge}</p>
                </GlassCardContent>
              </GlassCard>
            )}
          </div>
          {/* CTAs */}
          <div className="hero-ctas" style={{ display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}>
            <div className="cta-beam-wrap">
              <div className="cta-beam-inner">
                <Link to="/BookMeeting">
                  <button className="btn-primary-ziyada" style={{ padding: "15px 36px", fontSize: "1rem" }}>{c.cta_primary}</button>
                </Link>
              </div>
            </div>
            <Link to="/Why">
              <button className="btn-outline-ziyada home-hero-secondary" style={{ padding: "15px 36px", fontSize: "1rem" }}>{c.cta_secondary}</button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section style={{ padding: "40px 24px" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto" }}>
          <div className="glass-panel" style={{ padding: "32px 40px", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 24, textAlign: "center" }}>
            {c.stats.map((s, i) =>
            <div key={i} className="stat-item">
                <div className="gradient-text-anim" style={{ fontSize: "2.2rem", fontWeight: 900 }}>{s.value}</div>
                <div style={{ color: "var(--text-primary)", fontSize: "0.9rem", fontWeight: 600, marginTop: 4, opacity: 0.75 }}>{s.label}</div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Services */}
      <section className="reveal-section" style={{ padding: "80px 24px" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 56 }}>
            <div className="section-title-frame" style={{ marginBottom: 16 }}>
              <h2 style={{ fontSize: "2.6rem", fontWeight: 900, background: "linear-gradient(135deg, #1e3a8a, #7c3aed)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>{c.services_title}</h2>
            </div>
            <p style={{ color: "var(--text-primary)", opacity: 0.85 }}>{c.services_sub}</p>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 24 }}>
            {services.map((s, i) =>
            <Link key={i} to={s.path} style={{ textDecoration: "none" }}>
                <div className="glass-panel service-card" style={{ padding: 28, height: "100%", cursor: "pointer" }}>
                  <div className="icon-box-anim" style={{ background: "linear-gradient(135deg,rgba(109,40,217,0.15),rgba(124,58,237,0.2))", borderRadius: 12, padding: 12, display: "inline-flex", marginBottom: 16, color: "#7c3aed" }}>
                    <s.Icon size={24} />
                  </div>
                  <h3 style={{ fontWeight: 800, fontSize: "1.1rem", marginBottom: 10, color: "var(--text-primary)" }}>{s.title}</h3>
                  <p style={{ color: "var(--text-primary)", fontSize: "0.95rem", lineHeight: 1.75, opacity: 0.75 }}>{s.desc}</p>
                </div>
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="reveal-section" style={{ padding: "80px 24px" }}>
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <div className="glass-panel cta-section-card home-cta-card" style={{ padding: "60px 40px", textAlign: "center" }}>
            <h2 className="home-cta-title" style={{ fontSize: "2.4rem", fontWeight: 900, marginBottom: 16 }}>{c.cta_section_title}</h2>
            <p className="home-cta-sub" style={{ fontSize: "1.05rem", marginBottom: 36, lineHeight: 1.8, opacity: 0.88 }}>{c.cta_section_sub}</p>
            <Link to="/BookMeeting">
              <button className="btn-primary-ziyada" style={{ padding: "15px 40px", fontSize: "1rem" }}>{c.cta_primary}</button>
            </Link>
          </div>
        </div>
      </section>
    </div>);

}