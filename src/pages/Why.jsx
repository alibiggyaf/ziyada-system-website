import { useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import { IconClockAlert, IconTrendingDown, IconEyeOff, IconUnlink } from "../components/ziyada/BrandIcons";
import useSEO from '@/lib/useSEO';

const C = {
  ar: {
    title: "لماذا زيادة؟",
    intro: "نحن لا نقدم استشارات نظرية — نبني أنظمة حقيقية تعمل وتُقاس وتُحسَّن باستمرار. كل مشروع نعمل عليه يُبنى على أساس بيانات وخبرة ميدانية لا على نظريات.",
    accreditations_title: "الاعتمادات المهنية",
    accreditations: ["HubSpot Certified Partner", "Google Ads Certified", "Meta Business Partner", "n8n Certified Automation Expert", "ClickUp Ambassador"],
    capabilities_title: "قدراتنا التخصصية",
    capabilities: ["بناء أنظمة أتمتة n8n متكاملة", "هندسة CRM وتصميم pipelines البيع", "توليد عملاء B2B بالأتمتة والبيانات", "إدارة حملات Google Ads + Meta Ads", "تطوير مواقع محوّلة مع تكاملات CRM"],
    operational_title: "قدراتنا التشغيلية",
    operational: ["فريق من الممارسين وليس النظريين", "تطبيق منهجية Agile في جميع المشاريع", "تسليم في الوقت المحدد مع ضمان الجودة", "دعم ما بعد التسليم لمدة 3 أشهر", "تقارير شفافة ومؤشرات أداء واضحة"],
    unique_title: "ما يميزنا",
    unique: ["نفهم السوق العربي بعمق", "نربط التسويق بالمبيعات بالتشغيل", "لا نعمل مع أكثر من 5 عملاء في آن واحد", "شفافية كاملة في التقارير والنتائج", "نُسلّم أنظمة حقيقية — لا توصيات فقط"],
    problem_title: "المشكلة التي تواجه الشركات",
    problems: [
      { Icon: IconClockAlert,   title: "ضياع الوقت في التكرار", desc: "ساعات يومية في إدخال البيانات، إرسال ردود، ونقل معلومات بين الأنظمة يدوياً" },
      { Icon: IconTrendingDown, title: "فقدان فرص البيع", desc: "العملاء المحتملون يُتركون دون متابعة سريعة فيذهبون للمنافس" },
      { Icon: IconEyeOff,       title: "قرارات بدون بيانات", desc: "غياب لوحات متابعة واضحة يجعل القرارات تعتمد على الحدس لا الأرقام" },
      { Icon: IconUnlink,       title: "أنظمة غير مترابطة", desc: "كل تطبيق يعمل بمعزل — CRM، بريد، واتساب، جوجل شيتس — بدون تكامل" },
    ],
    conclusion: "إذا كنت تبحث عن شريك يفهم عملك ويبني معك — لا مجرد مستشار يقدم توصيات — فزيادة هي الخيار الصح.",
    cta: "احجز استشارة مجانية"
  },
  en: {
    title: "Why Ziyada?",
    intro: "We don't offer theoretical consulting — we build real systems that work, are measured, and continuously improved. Every project we work on is built on data and field experience, not theories.",
    accreditations_title: "Professional Accreditations",
    accreditations: ["HubSpot Certified Partner", "Google Ads Certified", "Meta Business Partner", "n8n Certified Automation Expert", "ClickUp Ambassador"],
    capabilities_title: "Specialized Capabilities",
    capabilities: ["Building integrated n8n automation systems", "CRM engineering and sales pipeline design", "B2B lead generation with automation and data", "Google Ads + Meta Ads campaign management", "Conversion website development with CRM integrations"],
    operational_title: "Operational Capabilities",
    operational: ["A team of practitioners, not theorists", "Agile methodology across all projects", "On-time delivery with quality assurance", "3-month post-delivery support", "Transparent reports and clear KPIs"],
    unique_title: "What Makes Us Different",
    unique: ["Deep understanding of the Arab market", "We connect marketing, sales, and operations", "We work with no more than 5 clients at a time", "Full transparency in reports and results", "We deliver real systems — not just recommendations"],
    problem_title: "The Problem Companies Face",
    problems: [
      { Icon: IconClockAlert,   title: "Wasted Time on Repetition", desc: "Hours daily on data entry, sending replies, and manually transferring info between systems" },
      { Icon: IconTrendingDown, title: "Lost Sales Opportunities", desc: "Prospects left without quick follow-up end up going to competitors" },
      { Icon: IconEyeOff,       title: "Decisions Without Data", desc: "Lack of clear dashboards means decisions rely on intuition, not numbers" },
      { Icon: IconUnlink,       title: "Disconnected Systems", desc: "Every app works in isolation — CRM, email, WhatsApp, Google Sheets — without integration" },
    ],
    conclusion: "If you're looking for a partner who understands your business and builds with you — not just an advisor who gives recommendations — Ziyada is the right choice.",
    cta: "Book a Free Consultation"
  }
};

export default function Why() {
  const { lang } = useOutletContext();
  const c = C[lang] || C.ar;
  const isRTL = lang === "ar";

  useSEO({
    title: 'لماذا زيادة',
    titleEn: 'Why Ziyada',
    description: 'اكتشف لماذا زيادة هي الشريك المثالي لتحويل أعمالك رقمياً',
    descriptionEn: 'Discover why Ziyada is the ideal partner for your digital transformation',
    path: '/Why',
  });

  const ListCard = ({ title, items }) => (
    <div className="glass-panel" style={{ padding: 30 }}>
      <h3 className="gradient-text" style={{ fontWeight: 800, fontSize: "1.1rem", marginBottom: 20 }}>{title}</h3>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {items.map((item, i) => (
          <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 12, color: "var(--text-primary)", fontSize: "0.9rem" }}>
            <span style={{ color: "var(--accent-primary)", flexShrink: 0, marginTop: 2 }}>✓</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 1200, margin: "0 auto", padding: "60px 24px" }}>
      <div style={{ textAlign: "center", maxWidth: 800, margin: "0 auto 60px" }}>
        <h1 className="gradient-text" style={{ fontSize: "2.5rem", fontWeight: 900, marginBottom: 20 }}>{c.title}</h1>
        <p style={{ fontSize: "1.1rem", color: "var(--text-primary)", lineHeight: 1.8 }}>{c.intro}</p>
      </div>

      {/* Problems */}
      <div style={{ marginBottom: 48 }}>
        <h2 style={{ fontWeight: 800, fontSize: "1.5rem", marginBottom: 24, textAlign: "center" }}>{c.problem_title}</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          {c.problems.map((p, i) => (
            <div key={i} className="glass-panel" style={{ padding: 24 }}>
              <div style={{ color: "#ef4444", marginBottom: 12, display: "inline-flex", background: "rgba(239,68,68,0.1)", borderRadius: 10, padding: 10 }}>
                <p.Icon size={20} />
              </div>
              <h4 style={{ fontWeight: 700, marginBottom: 8, fontSize: "0.95rem" }}>{p.title}</h4>
              <p style={{ color: "var(--text-primary)", fontSize: "0.85rem", lineHeight: 1.6 }}>{p.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Capabilities */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 24, marginBottom: 24 }}>
        <ListCard title={c.accreditations_title} items={c.accreditations} />
        <ListCard title={c.capabilities_title} items={c.capabilities} />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 24, marginBottom: 40 }}>
        <ListCard title={c.operational_title} items={c.operational} />
        <ListCard title={c.unique_title} items={c.unique} />
      </div>

      {/* CTA */}
      <div className="glass-panel" style={{ padding: 40, textAlign: "center" }}>
        <p style={{ fontSize: "1.2rem", fontWeight: 700, lineHeight: 1.7, maxWidth: 800, margin: "0 auto 30px" }}>{c.conclusion}</p>
        <Link to="/BookMeeting">
          <button className="btn-primary-ziyada" style={{ padding: "14px 36px", fontSize: "1rem" }}>{c.cta}</button>
        </Link>
      </div>
    </div>
  );
}