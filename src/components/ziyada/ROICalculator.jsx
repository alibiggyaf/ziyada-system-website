import { useState } from "react";
import { Link } from "react-router-dom";

function formatNum(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(0) + "K";
  return n.toLocaleString();
}

// ─── SVG Icons ────────────────────────────────────────────────────────────────
const IconCalc = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/>
    <line x1="8" y1="10" x2="10" y2="10"/><line x1="14" y1="10" x2="16" y2="10"/>
    <line x1="8" y1="14" x2="10" y2="14"/><line x1="14" y1="14" x2="16" y2="14"/>
    <line x1="8" y1="18" x2="10" y2="18"/><line x1="14" y1="18" x2="16" y2="18"/>
  </svg>
);
const IconUsers = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
);
const IconClock = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
  </svg>
);
const IconCoin = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><path d="M12 6v2m0 8v2m-4-6h8"/>
  </svg>
);
const IconTrend = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
  </svg>
);
const IconTarget = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
  </svg>
);
const IconZap = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
  </svg>
);
const IconStar = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
);
const IconMail = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
  </svg>
);

// ─── Service Type Configs ─────────────────────────────────────────────────────
const SERVICE_TYPES = {
  ar: [
    { id: "ops_automation", label: "أتمتة العمليات الداخلية", icon: "⚙️", desc: "CRM، إيميلات، تقارير، إدخال بيانات" },
    { id: "sales_crm",      label: "مبيعات وCRM",           icon: "🎯", desc: "توليد عملاء، متابعة، إغلاق صفقات" },
    { id: "marketing",      label: "تسويق رقمي وإعلانات",   icon: "📢", desc: "حملات، SEO، سوشيال ميديا" },
    { id: "web_dev",        label: "تطوير مواقع وتطبيقات",  icon: "🌐", desc: "موقع احترافي، صفحات هبوط" },
  ],
  en: [
    { id: "ops_automation", label: "Internal Ops Automation", icon: "⚙️", desc: "CRM, emails, reports, data entry" },
    { id: "sales_crm",      label: "Sales & CRM",             icon: "🎯", desc: "Lead gen, follow-up, closing deals" },
    { id: "marketing",      label: "Digital Marketing & Ads", icon: "📢", desc: "Campaigns, SEO, social media" },
    { id: "web_dev",        label: "Web & App Development",   icon: "🌐", desc: "Professional site, landing pages" },
  ]
};

// ─── Input definitions per service type ───────────────────────────────────────
const INPUTS_CONFIG = {
  ops_automation: {
    ar: [
      { key: "team_size",     label: "عدد الموظفين المتأثرين بالمهام اليدوية",      icon: <IconUsers />, min: 1,  max: 200, step: 1,  default: 5   },
      { key: "hours_wasted",  label: "ساعات يومية لكل موظف في مهام يدوية (إدخال، إيميلات، تقارير)", icon: <IconClock />, min: 0.5, max: 8, step: 0.5, default: 2 },
      { key: "hourly_cost",   label: "متوسط تكلفة ساعة العمل (ريال)",              icon: <IconCoin />,  min: 20, max: 500, step: 10, default: 80  },
      { key: "errors_monthly",label: "متوسط أخطاء بشرية شهرياً تسبب إعادة عمل",  icon: <IconZap />,  min: 0,  max: 100, step: 1,  default: 10  },
      { key: "error_fix_hrs", label: "ساعات لإصلاح كل خطأ",                       icon: <IconClock />, min: 0.5,max: 8,  step: 0.5, default: 1.5 },
    ],
    en: [
      { key: "team_size",     label: "Employees affected by manual tasks",                         icon: <IconUsers />, min: 1,   max: 200, step: 1,   default: 5   },
      { key: "hours_wasted",  label: "Daily hours per employee on manual tasks (data entry, emails, reports)", icon: <IconClock />, min: 0.5, max: 8, step: 0.5, default: 2 },
      { key: "hourly_cost",   label: "Average hourly cost (SAR)",                                  icon: <IconCoin />,  min: 20,  max: 500, step: 10,  default: 80  },
      { key: "errors_monthly",label: "Monthly human errors causing rework",                        icon: <IconZap />,  min: 0,   max: 100, step: 1,   default: 10  },
      { key: "error_fix_hrs", label: "Hours to fix each error",                                    icon: <IconClock />, min: 0.5, max: 8,   step: 0.5, default: 1.5 },
    ]
  },
  sales_crm: {
    ar: [
      { key: "monthly_leads",    label: "عدد العملاء المحتملين شهرياً",           icon: <IconUsers />, min: 5,    max: 2000, step: 5,    default: 40   },
      { key: "conversion_rate",  label: "معدل التحويل الحالي (%)",                icon: <IconTarget />, min: 1,   max: 50,  step: 1,    default: 10   },
      { key: "avg_deal",         label: "متوسط قيمة الصفقة (ريال)",              icon: <IconCoin />,  min: 1000, max: 500000, step: 1000, default: 15000 },
      { key: "lost_leads_pct",   label: "نسبة الليدز الضائعة بسبب بطء المتابعة (%)", icon: <IconTrend />, min: 5, max: 80, step: 5,   default: 35   },
      { key: "sales_team_size",  label: "عدد مندوبي المبيعات",                   icon: <IconUsers />, min: 1,    max: 50,  step: 1,    default: 3    },
    ],
    en: [
      { key: "monthly_leads",    label: "Monthly potential leads",                icon: <IconUsers />, min: 5,    max: 2000, step: 5,    default: 40   },
      { key: "conversion_rate",  label: "Current conversion rate (%)",            icon: <IconTarget />, min: 1,   max: 50,  step: 1,    default: 10   },
      { key: "avg_deal",         label: "Average deal value (SAR)",               icon: <IconCoin />,  min: 1000, max: 500000, step: 1000, default: 15000 },
      { key: "lost_leads_pct",   label: "Leads lost due to slow follow-up (%)",  icon: <IconTrend />, min: 5,    max: 80,  step: 5,    default: 35   },
      { key: "sales_team_size",  label: "Number of sales reps",                  icon: <IconUsers />, min: 1,    max: 50,  step: 1,    default: 3    },
    ]
  },
  marketing: {
    ar: [
      { key: "monthly_budget",   label: "الميزانية الإعلانية الشهرية (ريال)",     icon: <IconCoin />,  min: 1000, max: 200000, step: 1000, default: 10000 },
      { key: "current_roas",     label: "عائد الإعلان الحالي (ROAS) — ريال مقابل كل ريال مُنفق", icon: <IconTrend />, min: 0.5, max: 10, step: 0.5, default: 1.5 },
      { key: "monthly_visitors", label: "الزوار الشهريون على الموقع/الصفحة",     icon: <IconUsers />, min: 100,  max: 100000, step: 100,  default: 2000  },
      { key: "cvr",              label: "معدل التحويل الحالي من زائر لعميل (%)", icon: <IconTarget />, min: 0.1, max: 20,   step: 0.1,  default: 1     },
      { key: "avg_deal",         label: "متوسط قيمة العميل (ريال)",              icon: <IconCoin />,  min: 100,  max: 100000, step: 100,  default: 5000  },
    ],
    en: [
      { key: "monthly_budget",   label: "Monthly ad budget (SAR)",                icon: <IconCoin />,  min: 1000, max: 200000, step: 1000, default: 10000 },
      { key: "current_roas",     label: "Current ROAS (SAR earned per SAR spent)",icon: <IconTrend />, min: 0.5,  max: 10,    step: 0.5,  default: 1.5   },
      { key: "monthly_visitors", label: "Monthly visitors to site/page",          icon: <IconUsers />, min: 100,  max: 100000, step: 100,  default: 2000  },
      { key: "cvr",              label: "Current visitor-to-client rate (%)",     icon: <IconTarget />, min: 0.1, max: 20,    step: 0.1,  default: 1     },
      { key: "avg_deal",         label: "Average client value (SAR)",             icon: <IconCoin />,  min: 100,  max: 100000, step: 100,  default: 5000  },
    ]
  },
  web_dev: {
    ar: [
      { key: "monthly_visitors", label: "الزوار الشهريون الحاليون على الموقع",   icon: <IconUsers />, min: 100,  max: 100000, step: 100,  default: 1000  },
      { key: "current_cvr",      label: "معدل تحويل الزوار لعملاء حالياً (%)",  icon: <IconTarget />, min: 0.1, max: 20,    step: 0.1,  default: 0.5   },
      { key: "avg_deal",         label: "متوسط قيمة العميل (ريال)",              icon: <IconCoin />,  min: 100,  max: 100000, step: 100,  default: 3000  },
      { key: "sales_lost_pct",   label: "تقدير الفرص الضائعة بسبب ضعف الموقع (%)", icon: <IconZap />, min: 10, max: 80,    step: 5,    default: 40    },
    ],
    en: [
      { key: "monthly_visitors", label: "Current monthly website visitors",       icon: <IconUsers />, min: 100,  max: 100000, step: 100,  default: 1000  },
      { key: "current_cvr",      label: "Current visitor-to-client rate (%)",     icon: <IconTarget />, min: 0.1, max: 20,    step: 0.1,  default: 0.5   },
      { key: "avg_deal",         label: "Average client value (SAR)",             icon: <IconCoin />,  min: 100,  max: 100000, step: 100,  default: 3000  },
      { key: "sales_lost_pct",   label: "Estimated opportunities lost due to weak site (%)", icon: <IconZap />, min: 10, max: 80, step: 5, default: 40 },
    ]
  }
};

// ─── Calculation logic per service ────────────────────────────────────────────
function calcResults(serviceId, inputs) {
  if (serviceId === "ops_automation") {
    const { team_size, hours_wasted, hourly_cost, errors_monthly, error_fix_hrs } = inputs;
    const days_per_month = 22;
    const monthly_hours_saved = team_size * hours_wasted * days_per_month * 0.70; // 70% automation rate
    const annual_hours_saved = monthly_hours_saved * 12;
    const cost_saved = annual_hours_saved * hourly_cost;
    const rework_saved = errors_monthly * error_fix_hrs * hourly_cost * 12 * 0.80;
    const total = Math.round(cost_saved + rework_saved);
    return { annual_hours_saved: Math.round(annual_hours_saved), cost_saved: Math.round(cost_saved), bonus: Math.round(rework_saved), total, roi_x: (total / (team_size * 1500 * 12) || 1).toFixed(1), type: "ops" };
  }
  if (serviceId === "sales_crm") {
    const { monthly_leads, conversion_rate, avg_deal, lost_leads_pct, sales_team_size } = inputs;
    const recovered_leads = monthly_leads * (lost_leads_pct / 100) * 0.40;
    const new_conversion = Math.min(conversion_rate * 1.35, 100);
    const extra_from_recovery = recovered_leads * (conversion_rate / 100) * avg_deal * 12;
    const extra_from_cvr = monthly_leads * ((new_conversion - conversion_rate) / 100) * avg_deal * 12;
    const sales_time_saved = sales_team_size * 40 * 12 * 80;
    const total = Math.round(extra_from_recovery + extra_from_cvr + sales_time_saved);
    return { extra_from_recovery: Math.round(extra_from_recovery), extra_from_cvr: Math.round(extra_from_cvr), sales_time_saved: Math.round(sales_time_saved), total, roi_x: (total / (sales_team_size * 1500 * 12) || 1).toFixed(1), type: "sales" };
  }
  if (serviceId === "marketing") {
    const { monthly_budget, current_roas, monthly_visitors, cvr, avg_deal } = inputs;
    const new_roas = current_roas * 2.2;
    const roas_gain = (new_roas - current_roas) * monthly_budget * 12;
    const new_cvr = Math.min(cvr * 1.5, 100);
    const extra_clients = monthly_visitors * ((new_cvr - cvr) / 100) * 12;
    const cvr_gain = extra_clients * avg_deal;
    const total = Math.round(roas_gain + cvr_gain);
    return { roas_gain: Math.round(roas_gain), cvr_gain: Math.round(cvr_gain), total, roi_x: (total / (monthly_budget * 12 * 0.15) || 1).toFixed(1), type: "marketing" };
  }
  if (serviceId === "web_dev") {
    const { monthly_visitors, current_cvr, avg_deal, sales_lost_pct } = inputs;
    const new_cvr = Math.min(current_cvr * 2.5, 100);
    const extra_clients = monthly_visitors * ((new_cvr - current_cvr) / 100) * 12;
    const cvr_gain = extra_clients * avg_deal;
    const recovered = monthly_visitors * (sales_lost_pct / 100) * (current_cvr / 100) * 0.30 * avg_deal * 12;
    const total = Math.round(cvr_gain + recovered);
    return { cvr_gain: Math.round(cvr_gain), recovered: Math.round(recovered), total, roi_x: (total / 25000 || 1).toFixed(1), type: "web" };
  }
  return null;
}

// ─── Main Component ────────────────────────────────────────────────────────────
export default function ROICalculator({ lang = "ar" }) {
  const isRTL = lang === "ar";
  const serviceTypes = SERVICE_TYPES[lang] || SERVICE_TYPES.ar;
  const [selectedService, setSelectedService] = useState(null);
  const [inputs, setInputs] = useState({});
  const [result, setResult] = useState(null);

  const selectService = (id) => {
    setSelectedService(id);
    setResult(null);
    const cfg = INPUTS_CONFIG[id]?.[lang] || INPUTS_CONFIG[id]?.ar || [];
    const defaults = {};
    cfg.forEach(c => { defaults[c.key] = c.default; });
    setInputs(defaults);
  };

  const currentInputs = selectedService ? (INPUTS_CONFIG[selectedService]?.[lang] || INPUTS_CONFIG[selectedService]?.ar || []) : [];

  const calculate = () => {
    if (!selectedService) return;
    setResult(calcResults(selectedService, inputs));
  };

  const reset = () => { setSelectedService(null); setResult(null); setInputs({}); };

  const sar = isRTL ? "ريال" : "SAR";

  const renderResults = () => {
    if (!result) return null;
    let items = [];
    if (result.type === "ops") {
      items = [
        { label: isRTL ? "ساعات عمل موفّرة سنوياً" : "Work hours saved/year",        value: `${formatNum(result.annual_hours_saved)} h`, color: "#06b6d4" },
        { label: isRTL ? "توفير في رواتب وتكاليف العمل" : "Labor cost savings",        value: `${formatNum(result.cost_saved)} ${sar}`,   color: "#a78bfa" },
        { label: isRTL ? "توفير من تقليل الأخطاء وإعادة العمل" : "Rework elimination savings", value: `${formatNum(result.bonus)} ${sar}`, color: "#34d399" },
        { label: isRTL ? "إجمالي التوفير السنوي" : "Total annual savings",             value: `${formatNum(result.total)} ${sar}`,       color: "#f59e0b", big: true },
      ];
    } else if (result.type === "sales") {
      items = [
        { label: isRTL ? "إيرادات من استرداد الليدز الضائعة" : "Revenue from recovered leads", value: `${formatNum(result.extra_from_recovery)} ${sar}`, color: "#06b6d4" },
        { label: isRTL ? "زيادة إيرادات من تحسين التحويل" : "Revenue from better conversion",  value: `${formatNum(result.extra_from_cvr)} ${sar}`,      color: "#a78bfa" },
        { label: isRTL ? "توفير وقت فريق المبيعات" : "Sales team time savings",               value: `${formatNum(result.sales_time_saved)} ${sar}`,    color: "#34d399" },
        { label: isRTL ? "إجمالي العائد السنوي المتوقع" : "Total expected annual return",      value: `${formatNum(result.total)} ${sar}`,               color: "#f59e0b", big: true },
      ];
    } else if (result.type === "marketing") {
      items = [
        { label: isRTL ? "زيادة العائد من تحسين ROAS" : "Revenue gain from improved ROAS",    value: `${formatNum(result.roas_gain)} ${sar}`,    color: "#06b6d4" },
        { label: isRTL ? "زيادة العملاء من تحسين معدل التحويل" : "Revenue from improved CVR", value: `${formatNum(result.cvr_gain)} ${sar}`,     color: "#a78bfa" },
        { label: isRTL ? "إجمالي النمو السنوي المتوقع" : "Total expected annual growth",       value: `${formatNum(result.total)} ${sar}`,        color: "#f59e0b", big: true },
      ];
    } else if (result.type === "web") {
      items = [
        { label: isRTL ? "إيرادات إضافية من تحسين التحويل" : "Revenue from better CVR",  value: `${formatNum(result.cvr_gain)} ${sar}`, color: "#06b6d4" },
        { label: isRTL ? "إيرادات مستردة من الفرص الضائعة" : "Recovered lost opportunities", value: `${formatNum(result.recovered)} ${sar}`, color: "#a78bfa" },
        { label: isRTL ? "إجمالي العائد السنوي" : "Total annual return",                  value: `${formatNum(result.total)} ${sar}`,    color: "#f59e0b", big: true },
      ];
    }
    return items;
  };

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ marginTop: 80, marginBottom: 20 }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 10, background: "rgba(124,58,237,0.12)", border: "1px solid rgba(124,58,237,0.3)", borderRadius: 999, padding: "6px 18px", marginBottom: 16 }}>
          <span style={{ color: "var(--accent-primary)" }}><IconCalc /></span>
          <span style={{ color: "var(--accent-primary)", fontSize: "0.85rem", fontWeight: 700 }}>
            {isRTL ? "حاسبة العائد على الاستثمار" : "ROI Calculator"}
          </span>
        </div>
        <h2 className="gradient-text" style={{ fontSize: "2rem", fontWeight: 900, marginBottom: 10 }}>
          {isRTL ? "اكتشف كم ستوفّر وتكسب مع زيادة" : "Discover Your ROI with Ziyada"}
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "1rem" }}>
          {isRTL ? "اختر الخدمة التي تهمّك وأدخل أرقامك للحصول على تقدير حقيقي" : "Select the service you're interested in and get a real estimate"}
        </p>
      </div>

      <div className="glass-panel" style={{ padding: "36px 32px" }}>

        {/* Step 1: Service selection */}
        {!selectedService && (
          <div>
            <p style={{ textAlign: "center", fontWeight: 700, fontSize: "1rem", marginBottom: 24, color: "var(--text-secondary)" }}>
              {isRTL ? "أي خدمة تهمّك أكثر؟" : "Which service are you most interested in?"}
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
              {serviceTypes.map(st => (
                <button key={st.id} onClick={() => selectService(st.id)} style={{
                  background: "rgba(124,58,237,0.06)", border: "1px solid rgba(124,58,237,0.2)",
                  borderRadius: 12, padding: "20px 16px", cursor: "pointer", textAlign: isRTL ? "right" : "left",
                  transition: "all 0.2s", color: "var(--text-primary)", fontFamily: "inherit"
                }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = "var(--accent-primary)"; e.currentTarget.style.background = "rgba(124,58,237,0.12)"; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(124,58,237,0.2)"; e.currentTarget.style.background = "rgba(124,58,237,0.06)"; }}>
                  <div style={{ fontSize: "1.8rem", marginBottom: 10 }}>{st.icon}</div>
                  <div style={{ fontWeight: 700, fontSize: "0.95rem", marginBottom: 6 }}>{st.label}</div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{st.desc}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Sliders */}
        {selectedService && !result && (
          <div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28, flexWrap: "wrap", gap: 12 }}>
              <div>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{isRTL ? "الخدمة المختارة:" : "Selected:"} </span>
                <span style={{ fontWeight: 700, color: "var(--accent-primary)" }}>
                  {serviceTypes.find(s => s.id === selectedService)?.label}
                </span>
              </div>
              <button onClick={reset} style={{ background: "none", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, padding: "6px 14px", color: "var(--text-secondary)", cursor: "pointer", fontSize: "0.82rem", fontFamily: "inherit" }}>
                {isRTL ? "← تغيير الخدمة" : "← Change service"}
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 28, marginBottom: 32 }}>
              {currentInputs.map(({ key, label, min, max, step, icon }) => (
                <div key={key}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-secondary)", fontSize: "0.82rem", fontWeight: 600 }}>
                      <span style={{ color: "var(--accent-primary)" }}>{icon}</span>
                      <span style={{ lineHeight: 1.4 }}>{label}</span>
                    </div>
                    <span style={{ fontWeight: 800, fontSize: "0.95rem", color: "var(--text-primary)", background: "rgba(124,58,237,0.12)", padding: "2px 10px", borderRadius: 6, flexShrink: 0, marginInlineStart: 8 }}>
                      {(inputs[key] || 0).toLocaleString()}
                    </span>
                  </div>
                  <input type="range" min={min} max={max} step={step} value={inputs[key] || min}
                    onChange={e => setInputs(p => ({ ...p, [key]: Number(e.target.value) }))}
                    style={{ width: "100%", accentColor: "var(--accent-primary)", cursor: "pointer", height: 4 }} />
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "var(--text-secondary)", marginTop: 4 }}>
                    <span>{min.toLocaleString()}</span><span>{max.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ textAlign: "center" }}>
              <button className="btn-primary-ziyada" onClick={calculate} style={{ padding: "14px 48px", fontSize: "1rem", display: "inline-flex", alignItems: "center", gap: 8 }}>
                <IconCalc /> {isRTL ? "احسب العائد" : "Calculate ROI"}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Results */}
        {result && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28, flexWrap: "wrap", gap: 12 }}>
              <h3 style={{ fontWeight: 800, fontSize: "1.1rem", color: "var(--text-secondary)" }}>
                {isRTL ? "النتائج التقديرية لعملك" : "Estimated results for your business"}
              </h3>
              <button onClick={reset} style={{ background: "none", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, padding: "6px 14px", color: "var(--text-secondary)", cursor: "pointer", fontSize: "0.82rem", fontFamily: "inherit" }}>
                {isRTL ? "← إعادة الحساب" : "← Recalculate"}
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16, marginBottom: 20 }}>
              {renderResults()?.map((item, i) => (
                <div key={i} className="glass-panel" style={{ padding: "20px 16px", textAlign: "center", borderColor: `${item.color}33` }}>
                  <div style={{ fontSize: item.big ? "1.9rem" : "1.5rem", fontWeight: 900, color: item.color, marginBottom: 6 }}>{item.value}</div>
                  <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>{item.label}</div>
                </div>
              ))}
            </div>

            <div style={{ textAlign: "center", padding: "16px", background: "rgba(124,58,237,0.08)", borderRadius: 10, border: "1px solid rgba(124,58,237,0.2)", marginBottom: 16 }}>
              <span style={{ fontSize: "1rem", color: "var(--text-secondary)" }}>
                {isRTL ? "مضاعف العائد على الاستثمار: " : "ROI Multiple: "}
              </span>
              <span className="gradient-text" style={{ fontSize: "1.6rem", fontWeight: 900 }}>{result.roi_x}x</span>
            </div>

            <p style={{ textAlign: "center", fontSize: "0.75rem", color: "var(--text-secondary)", opacity: 0.6, marginBottom: 24 }}>
              {isRTL ? "* الأرقام تقديرية بناءً على متوسط نتائج عملائنا الفعلية" : "* Figures are estimates based on actual client averages"}
            </p>

            <div style={{ textAlign: "center" }}>
              <Link to="/BookMeeting">
                <button className="btn-primary-ziyada" style={{ padding: "14px 36px", fontSize: "1rem" }}>
                  {isRTL ? "احجز جلسة لتحقيق هذا العائد ←" : "Book a Session to Achieve This ROI →"}
                </button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}