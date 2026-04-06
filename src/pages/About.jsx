import { useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import { IconCrosshair, IconHandshake, IconTrendingUp, IconRefresh } from "../components/ziyada/BrandIcons";
import useSEO from "@/lib/useSEO";

const C = {
  ar: {
    title: "من نحن",
    p1: "زيادة للأنظمة المتقدمة هي شركة متخصصة في تصميم وبناء أنظمة النمو الرقمية للشركات الطموحة — من الأتمتة والـ CRM إلى توليد العملاء والتسويق الرقمي.",
    p2: "نؤمن بأن النمو الحقيقي يبدأ ببناء الأنظمة الصحيحة — كل شيء متصل ومبني على منطق تجاري واضح وقياس دقيق.",
    p3: "فريقنا يجمع بين خبرة التسويق الرقمي والهندسة التشغيلية لتقديم حلول شاملة تساعدك على التوسع دون فوضى.",
    founder: "علي فلاتة — مؤسس زيادة سيستم",
    founder_title: "خبرة 10+ سنوات في بناء أنظمة النمو وأتمتة الأعمال",
    vision_title: "رؤيتنا",
    vision_desc: "أن نكون الشريك التشغيلي المفضل للشركات الطموحة في المنطقة العربية، ونساعدها على بناء أنظمة نمو متكاملة وقابلة للتوسع.",
    method_title: "منهجيتنا",
    method_desc: "نبدأ بفهم عميق لوضعك الحالي، ثم نصمم حلولاً مخصصة، ونطبقها بشكل تدريجي مع قياس النتائج في كل مرحلة.",
    stats: [
      { value: "50+", label: "عميل أتمتنا" },
      { value: "40%", label: "متوسط نمو الإيرادات" },
      { value: "10+", label: "سنوات خبرة" },
      { value: "80h", label: "متوسط التوفير الشهري" },
    ],
    values_title: "قيمنا",
    values: [
      { Icon: IconCrosshair,  label: "الدقة", desc: "نبني على البيانات، لا على التخمين" },
      { Icon: IconHandshake,  label: "الشراكة الحقيقية", desc: "نعمل كجزء من فريقك" },
      { Icon: IconTrendingUp, label: "النتائج أولاً", desc: "كل قرار مرتبط بمؤشر أداء" },
      { Icon: IconRefresh,    label: "التحسين المستمر", desc: "لا نتوقف عند التسليم" },
    ],
    cta: "تعرّف على خدماتنا"
  },
  en: {
    title: "About Us",
    p1: "Ziyada Advanced Systems specializes in designing and building digital growth systems for ambitious companies — from automation and CRM to lead generation and digital marketing.",
    p2: "We believe real growth starts with building the right systems — everything connected and built on clear business logic with precise measurement.",
    p3: "Our team combines digital marketing expertise and operational engineering to deliver comprehensive solutions that help you scale without chaos.",
    founder: "Ali Fallatah — Founder, Ziyada System",
    founder_title: "10+ years of experience building growth systems and business automation",
    vision_title: "Our Vision",
    vision_desc: "To be the preferred operational partner for ambitious companies in the Arab region, helping them build integrated and scalable growth systems.",
    method_title: "Our Methodology",
    method_desc: "We start with a deep understanding of your current situation, then design customized solutions, and implement them gradually while measuring results at every stage.",
    stats: [
      { value: "50+", label: "Clients Automated" },
      { value: "40%", label: "Avg Revenue Growth" },
      { value: "10+", label: "Years Experience" },
      { value: "80h", label: "Avg Monthly Savings" },
    ],
    values_title: "Our Values",
    values: [
      { Icon: IconCrosshair,  label: "Precision", desc: "We build on data, not guesswork" },
      { Icon: IconHandshake,  label: "True Partnership", desc: "We work as part of your team" },
      { Icon: IconTrendingUp, label: "Results First", desc: "Every decision tied to a KPI" },
      { Icon: IconRefresh,    label: "Continuous Improvement", desc: "We don't stop at delivery" },
    ],
    cta: "Explore Our Services"
  }
};

export default function About() {
  const { lang } = useOutletContext();
  const c = C[lang] || C.ar;
  const isRTL = lang === "ar";

  useSEO({
    title: "من نحن — زيادة سيستم",
    titleEn: "About Us — Ziyada Systems",
    description: "تعرّف على فريق زيادة سيستم وكيف نبني أنظمة نمو رقمية للشركات الطموحة في السعودية",
    path: "/About"
  });

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 1200, margin: "0 auto", padding: "60px 24px" }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 40, alignItems: "start", marginBottom: 50 }}>
        <div>
          <div className="section-title-frame" style={{ marginBottom: 30 }}>
            <h1 className="gradient-text" style={{ fontSize: "2.5rem", fontWeight: 900 }}>{c.title}</h1>
          </div>
          <div className="glass-panel" style={{ padding: 34 }}>
            <p style={{ fontSize: "1.05rem", lineHeight: 1.9, marginBottom: 18, color: "var(--text-primary)", opacity: 0.85 }}>{c.p1}</p>
            <p style={{ fontSize: "1.05rem", lineHeight: 1.9, marginBottom: 18, color: "var(--text-primary)", opacity: 0.85 }}>{c.p2}</p>
            <p style={{ fontSize: "1.05rem", lineHeight: 1.9, marginBottom: 26, color: "var(--text-primary)", opacity: 0.85 }}>{c.p3}</p>
            <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: 20 }}>
              <p style={{ fontWeight: 700, fontSize: "1.05rem" }}>{c.founder}</p>
              <p style={{ fontSize: "0.9rem", marginTop: 6, color: "var(--text-primary)", opacity: 0.75 }}>{c.founder_title}</p>
            </div>
          </div>
        </div>
        <div>
          <div className="glass-panel" style={{ padding: 36, marginBottom: 24 }}>
            <h3 className="gradient-text" style={{ fontSize: "1.4rem", fontWeight: 800, marginBottom: 14 }}>{c.vision_title}</h3>
            <p style={{ fontSize: "1.02rem", lineHeight: 1.85, marginBottom: 28, color: "var(--text-primary)", opacity: 0.85 }}>{c.vision_desc}</p>
            <h3 className="gradient-text" style={{ fontSize: "1.4rem", fontWeight: 800, marginBottom: 14 }}>{c.method_title}</h3>
            <p style={{ fontSize: "1.02rem", lineHeight: 1.85, color: "var(--text-primary)", opacity: 0.85 }}>{c.method_desc}</p>
          </div>
          {/* Stats */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            {c.stats.map((s, i) => (
              <div key={i} className="glass-panel" style={{ padding: "16px", textAlign: "center" }}>
                <div className="gradient-text" style={{ fontSize: "1.8rem", fontWeight: 900 }}>{s.value}</div>
                <div style={{ fontSize: "0.85rem", fontWeight: 600, marginTop: 6, color: "var(--text-primary)", opacity: 0.75 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ textAlign: "center", marginBottom: 36 }}>
        <div className="section-title-frame" style={{ display: "inline-block" }}>
          <h2 style={{ fontWeight: 800, fontSize: "2rem", color: "var(--text-primary)", margin: 0 }}>{c.values_title}</h2>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 20, marginBottom: 60 }}>
        {c.values.map((v, i) => (
          <div key={i} className="glass-panel" style={{ padding: 28, textAlign: "center" }}>
            <div style={{ color: "var(--accent-primary)", marginBottom: 16, display: "flex", justifyContent: "center" }}>
              <div style={{ background: "rgba(124,58,237,0.12)", borderRadius: 12, padding: 14, display: "inline-flex" }}>
                <v.Icon size={26} />
              </div>
            </div>
            <h4 style={{ fontWeight: 700, fontSize: "1.05rem", marginBottom: 10 }}>{v.label}</h4>
            <p style={{ fontSize: "0.95rem", lineHeight: 1.7, color: "var(--text-primary)", opacity: 0.8 }}>{v.desc}</p>
          </div>
        ))}
      </div>

      <div style={{ textAlign: "center" }}>
        <Link to="/Services">
          <button className="btn-primary-ziyada" style={{ padding: "14px 36px", fontSize: "1rem" }}>{c.cta}</button>
        </Link>
      </div>
    </div>
  );
}
