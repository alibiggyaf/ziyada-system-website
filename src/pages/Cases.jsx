import { useOutletContext } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { Link } from "react-router-dom";
import useSEO from '@/lib/useSEO';

const C = {
  ar: {
    title: "دراسات الحالة",
    sub: "نتائج حقيقية حققناها مع عملائنا",
    cta: "احجز استشارة مجانية",
    challenge: "التحدي",
    solution: "الحل",
    result: "النتيجة",
    empty: "دراسات الحالة قادمة قريباً...",
    static: [
      {
        title_ar: "أتمتة شركة عقارية توفّر 60 ساعة شهرياً",
        client: "شركة عقارية — الرياض",
        industry: "العقارات",
        challenge_ar: "الفريق كان يقضي 3 ساعات يومياً في إدخال بيانات العملاء يدوياً بين WhatsApp وGoogle Sheets وHubSpot",
        solution_ar: "بنينا سير عمل n8n يربط WhatsApp Business API بـ HubSpot تلقائياً مع تصنيف العملاء وتوزيعهم على المبيعات",
        result_ar: "توفير 60 ساعة شهرياً، زيادة 35% في معدل الاستجابة، وصفر أخطاء إدخال بيانات",
        metrics: [{ label: "ساعات موفّرة", value: "60/شهر" }, { label: "معدل الاستجابة", value: "+35%" }, { label: "أخطاء البيانات", value: "0%" }]
      },
      {
        title_ar: "توليد 120 عميل محتمل شهرياً لشركة استشارات",
        client: "شركة استشارات — جدة",
        industry: "الاستشارات",
        challenge_ar: "الشركة تعتمد على الإحالات فقط وليس لديها قناة رقمية منتظمة لتوليد العملاء",
        solution_ar: "بنينا ماكينة توليد عملاء B2B على LinkedIn مع أتمتة المتابعة وتأهيل العملاء عبر HubSpot",
        result_ar: "120 عميل محتمل مؤهّل شهرياً، تكلفة لكل عميل أقل من 150 ريال، وخط مبيعات يساوي 2 مليون ريال",
        metrics: [{ label: "عملاء محتملون", value: "120/شهر" }, { label: "تكلفة العميل", value: "150 ر" }, { label: "خط المبيعات", value: "2M ر" }]
      },
      {
        title_ar: "رفع مبيعات متجر إلكتروني 40% عبر Google Ads",
        client: "متجر إلكتروني — الخليج",
        industry: "التجارة الإلكترونية",
        challenge_ar: "حملات Google Ads غير محسّنة تستنزف الميزانية بدون نتائج ملموسة",
        solution_ar: "أعدنا هيكلة الحملات بالكامل مع تحسين صفحات الهبوط وبناء نظام تتبع تحويل شامل",
        result_ar: "نمو المبيعات 40% خلال 3 أشهر مع خفض تكلفة التحويل 50%",
        metrics: [{ label: "نمو المبيعات", value: "+40%" }, { label: "تكلفة التحويل", value: "-50%" }, { label: "المدة", value: "3 أشهر" }]
      }
    ]
  },
  en: {
    title: "Case Studies",
    sub: "Real results we achieved with our clients",
    cta: "Book a Free Consultation",
    challenge: "Challenge",
    solution: "Solution",
    result: "Result",
    empty: "Case studies coming soon...",
    static: [
      {
        title_en: "Real Estate Company Automation Saves 60 Hours/Month",
        client: "Real Estate Company — Riyadh",
        industry: "Real Estate",
        challenge_en: "The team spent 3 hours daily manually entering client data between WhatsApp, Google Sheets, and HubSpot",
        solution_en: "We built an n8n workflow connecting WhatsApp Business API to HubSpot automatically with client classification and sales assignment",
        result_en: "60 hours saved monthly, 35% increase in response rate, and zero data entry errors",
        metrics: [{ label: "Hours Saved", value: "60/mo" }, { label: "Response Rate", value: "+35%" }, { label: "Data Errors", value: "0%" }]
      },
      {
        title_en: "120 Qualified Leads/Month for a Consulting Firm",
        client: "Consulting Company — Jeddah",
        industry: "Consulting",
        challenge_en: "The company relied only on referrals with no regular digital channel for lead generation",
        solution_en: "We built a B2B lead generation machine on LinkedIn with automated follow-up and lead qualification via HubSpot",
        result_en: "120 qualified leads per month, cost per lead under $40, and a sales pipeline worth $533K",
        metrics: [{ label: "Leads/Month", value: "120" }, { label: "Cost/Lead", value: "$40" }, { label: "Pipeline Value", value: "$533K" }]
      },
      {
        title_en: "40% E-commerce Sales Growth via Google Ads",
        client: "E-commerce Store — Gulf",
        industry: "E-commerce",
        challenge_en: "Unoptimized Google Ads campaigns draining budget without tangible results",
        solution_en: "We restructured campaigns entirely, optimized landing pages, and built a comprehensive conversion tracking system",
        result_en: "40% sales growth in 3 months with 50% reduction in conversion costs",
        metrics: [{ label: "Sales Growth", value: "+40%" }, { label: "Conversion Cost", value: "-50%" }, { label: "Duration", value: "3 months" }]
      }
    ]
  }
};

export default function Cases() {
  const { lang } = useOutletContext();
  const c = C[lang] || C.ar;
  const isRTL = lang === "ar";

  useSEO({
    title: 'دراسات الحالة',
    titleEn: 'Case Studies',
    description: 'تعرف على قصص نجاح عملائنا ونتائجنا المحققة',
    descriptionEn: 'Explore our client success stories and proven results',
    path: '/Cases',
  });

  const { data: dbCases = [] } = useQuery({
    queryKey: ["case_studies"],
    queryFn: () => siteApi.entities.CaseStudy.filter({ published: true }, "order", 20)
  });

  const cases = dbCases.length > 0 ? dbCases : c.static;

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 1200, margin: "0 auto", padding: "60px 24px" }}>
      <div style={{ textAlign: "center", maxWidth: 700, margin: "0 auto 60px" }}>
        <h1 className="gradient-text" style={{ fontSize: "2.5rem", fontWeight: 900, marginBottom: 16 }}>{c.title}</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem" }}>{c.sub}</p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 32, marginBottom: 60 }}>
        {cases.map((cs, i) => (
          <div key={i} className="glass-panel" style={{ padding: 36 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12, marginBottom: 24 }}>
              <div>
                <span style={{ background: "rgba(59,130,246,0.12)", color: "var(--accent-primary)", fontSize: "0.78rem", padding: "3px 12px", borderRadius: 999, border: "1px solid rgba(59,130,246,0.2)", marginBottom: 12, display: "inline-block" }}>
                  {cs.industry}
                </span>
                <h3 style={{ fontWeight: 800, fontSize: "1.25rem", marginTop: 8 }}>{isRTL ? cs.title_ar : cs.title_en}</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginTop: 4 }}>{cs.client}</p>
              </div>
              {cs.metrics && (
                <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
                  {cs.metrics.map((m, j) => (
                    <div key={j} style={{ textAlign: "center", background: "rgba(139,92,246,0.1)", borderRadius: 12, padding: "12px 20px", border: "1px solid rgba(139,92,246,0.2)" }}>
                      <div className="gradient-text" style={{ fontSize: "1.5rem", fontWeight: 900 }}>{m.value}</div>
                      <div style={{ color: "var(--text-secondary)", fontSize: "0.75rem", marginTop: 2 }}>{m.label}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20 }}>
              {[
                { label: c.challenge, text: isRTL ? cs.challenge_ar : cs.challenge_en, color: "#ef4444" },
                { label: c.solution,  text: isRTL ? cs.solution_ar  : cs.solution_en,  color: "#3b82f6" },
                { label: c.result,    text: isRTL ? cs.result_ar    : cs.result_en,    color: "#22c55e" },
              ].map((item, j) => (
                <div key={j} style={{ background: "rgba(255,255,255,0.03)", borderRadius: 12, padding: "16px 20px", borderRight: `3px solid ${item.color}`, borderLeft: "none" }}>
                  <div style={{ color: item.color, fontWeight: 700, fontSize: "0.85rem", marginBottom: 8 }}>{item.label}</div>
                  <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: 1.6 }}>{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div style={{ textAlign: "center" }}>
        <Link to="/BookMeeting">
          <button className="btn-primary-ziyada" style={{ padding: "15px 40px", fontSize: "1rem" }}>{c.cta}</button>
        </Link>
      </div>
    </div>
  );
}