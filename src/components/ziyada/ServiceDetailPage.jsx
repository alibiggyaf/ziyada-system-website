import { Link } from "react-router-dom";
import { ArrowRight, ArrowLeft } from "lucide-react";
import { IconZap, IconTarget, IconClock, IconUser, IconMapPin, IconCheck } from "./BrandIcons";

const IconDot = () => (
  <svg width="8" height="8" viewBox="0 0 8 8" fill="currentColor"><circle cx="4" cy="4" r="4" /></svg>
);

export default function ServiceDetailPage({ data, lang }) {
  const isRTL = lang === "ar";
  const Icon = data.icon;

  const caseLabels = {
    ar: { who: { icon: IconUser,   text: "من"    }, what: { icon: IconZap,    text: "ماذا"  }, when: { icon: IconClock,  text: "متى"   }, where: { icon: IconMapPin, text: "أين"   }, why: { icon: IconTarget, text: "لماذا" } },
    en: { who: { icon: IconUser,   text: "Who"   }, what: { icon: IconZap,    text: "What"  }, when: { icon: IconClock,  text: "When"  }, where: { icon: IconMapPin, text: "Where" }, why: { icon: IconTarget, text: "Why"   } }
  };
  const labels = caseLabels[lang] || caseLabels.ar;

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 1100, margin: "0 auto", padding: "60px 24px 80px" }}>
      {/* Back */}
      <div style={{ marginBottom: 32 }}>
        <Link to="/Services" style={{ textDecoration: "none" }}>
          <button className="btn-outline-ziyada" style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "10px 20px", fontSize: "0.88rem" }}>
            {isRTL ? <ArrowRight size={14} /> : <ArrowLeft size={14} />}
            {isRTL ? "← العودة للخدمات" : "← Back to Services"}
          </button>
        </Link>
      </div>

      {/* Hero */}
      <div style={{ textAlign: "center", marginBottom: 60 }}>
        <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 80, height: 80, background: "rgba(124,58,237,0.12)", border: "1px solid rgba(124,58,237,0.3)", borderRadius: 20, marginBottom: 24, color: "var(--accent-primary)" }}>
          <Icon size={36} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <span style={{ background: "rgba(124,58,237,0.15)", color: "var(--accent-primary)", padding: "4px 14px", borderRadius: 999, fontSize: "0.8rem", fontWeight: 700, border: "1px solid rgba(124,58,237,0.3)" }}>{data.tag}</span>
        </div>
        <h1 className="gradient-text" style={{ fontSize: "2.2rem", fontWeight: 900, marginBottom: 16, lineHeight: 1.3 }}>{data.title}</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "1.1rem", maxWidth: 680, margin: "0 auto", lineHeight: 1.7 }}>{data.desc}</p>
      </div>

      {/* Scope + Features */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 24, marginBottom: 24 }}>
        <div className="glass-panel" style={{ padding: 30 }}>
          <h3 style={{ color: "var(--accent-primary)", fontWeight: 700, marginBottom: 20, fontSize: "1rem" }}>
            {isRTL ? "نطاق العمل" : "Scope of Work"}
          </h3>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {data.scope.map((item, i) => (
              <li key={i} style={{ display: "flex", gap: 10, padding: "7px 0", color: "var(--text-secondary)", fontSize: "0.9rem", alignItems: "flex-start" }}>
                <span style={{ color: "var(--accent-primary)", flexShrink: 0, marginTop: 3 }}><IconCheck size={14} /></span>{item}
              </li>
            ))}
          </ul>
        </div>
        <div className="glass-panel" style={{ padding: 30 }}>
          <h3 style={{ color: "var(--accent-primary)", fontWeight: 700, marginBottom: 20, fontSize: "1rem" }}>
            {isRTL ? "المميزات" : "Features"}
          </h3>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {data.features.map((item, i) => (
              <li key={i} style={{ display: "flex", gap: 10, padding: "7px 0", color: "var(--text-secondary)", fontSize: "0.9rem", alignItems: "flex-start" }}>
                <span style={{ color: "#06b6d4", flexShrink: 0, marginTop: 6 }}><IconDot /></span>{item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Results */}
      <div className="glass-panel" style={{ padding: 30, marginBottom: 24 }}>
        <h3 style={{ color: "var(--accent-primary)", fontWeight: 700, marginBottom: 20, fontSize: "1rem" }}>
          {isRTL ? "النتائج المتوقعة" : "Expected Results"}
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
          {data.results.map((r, i) => (
            <div key={i} style={{ background: "rgba(124,58,237,0.08)", border: "1px solid rgba(124,58,237,0.2)", borderRadius: 10, padding: "14px 16px", fontWeight: 700, fontSize: "0.9rem", textAlign: "center", color: "var(--text-primary)" }}>
              {r}
            </div>
          ))}
        </div>
      </div>

      {/* Case Study */}
      <div className="glass-panel" style={{ padding: 30, marginBottom: 40, borderColor: "rgba(6,182,212,0.2)" }}>
        <h3 style={{ color: "#06b6d4", fontWeight: 700, marginBottom: 20, fontSize: "1rem" }}>
          {isRTL ? "مثال واقعي — قصة نجاح" : "Real Case Study — Success Story"}
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          {[
            { label: labels.who, value: data.case.who, bg: "rgba(59,130,246,0.08)", color: "var(--accent-primary)" },
            { label: labels.what, value: data.case.what, bg: "rgba(139,92,246,0.08)", color: "var(--accent-secondary)" },
            { label: labels.when, value: data.case.when, bg: "rgba(16,185,129,0.08)", color: "#10b981" },
            { label: labels.where, value: data.case.where, bg: "rgba(245,158,11,0.08)", color: "#f59e0b" },
            { label: labels.why, value: data.case.why, bg: "rgba(239,68,68,0.08)", color: "#ef4444" },
          ].map((item, i) => {
            const LabelIcon = item.label.icon;
            return (
            <div key={i} style={{ background: item.bg, borderRadius: 10, padding: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 700, color: item.color, marginBottom: 8, fontSize: "0.82rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                <LabelIcon size={14} />{item.label.text}
              </div>
              <p style={{ color: "var(--text-secondary)", margin: 0, fontSize: "0.9rem", lineHeight: 1.5 }}>{item.value}</p>
            </div>
            );
          })}
        </div>
      </div>

      {/* CTA */}
      <div className="glass-panel" style={{ padding: 40, textAlign: "center", background: "linear-gradient(135deg, rgba(59,130,246,0.06) 0%, rgba(139,92,246,0.06) 100%)", borderColor: "rgba(124,58,237,0.3)" }}>
        <h2 className="gradient-text" style={{ fontSize: "1.8rem", fontWeight: 900, marginBottom: 12 }}>
          {isRTL ? "مستعد تبدأ معنا؟" : "Ready to Get Started?"}
        </h2>
        <p style={{ color: "var(--text-secondary)", maxWidth: 480, margin: "0 auto 28px", lineHeight: 1.7 }}>
          {isRTL ? "احجز جلسة استراتيجية مجانية الآن ونبني معك خارطة طريق واضحة." : "Book a free strategy session now and we'll build a clear roadmap together."}
        </p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
          <Link to="/BookMeeting">
            <button className="btn-primary-ziyada" style={{ padding: "14px 36px", fontSize: "1rem" }}>
              {isRTL ? "احجز جلسة مجانية" : "Book Free Session"}
            </button>
          </Link>
          <Link to="/RequestProposal">
            <button className="btn-outline-ziyada" style={{ padding: "14px 28px", fontSize: "0.95rem" }}>
              {isRTL ? "طلب عرض سعر" : "Request Proposal"}
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}