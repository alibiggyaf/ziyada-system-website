import { useState, useRef } from "react";
import { useOutletContext, useNavigate, Link } from "react-router-dom";
import { siteApi } from "@/api/siteApi";
import { CheckCircle, ArrowRight, ArrowLeft } from "lucide-react";
import { proposalSchema, validate } from "@/lib/validation";
import { getUTMParams, getSourcePage } from "@/lib/utm";
import { checkRateLimit } from "@/lib/rateLimit";
import { trackEvent, identifyUser } from "@/lib/analytics";
import useSEO from '@/lib/useSEO';

const L = {
  ar: { title: "طلب عرض سعر", name: "الاسم", email: "البريد الإلكتروني للعمل", budget: "الميزانية المتوقعة", timeline: "الإطار الزمني", services_label: "الخدمات المطلوبة", consent: "أوافق على تخزين بياناتي للتواصل.", submit: "إرسال الطلب", loading: "جارٍ الإرسال...", success: "تم إرسال طلبك بنجاح! سنتواصل معك خلال 24 ساعة.", back: "العودة" },
  en: { title: "Request a Proposal", name: "Name", email: "Work Email", budget: "Expected Budget", timeline: "Timeline", services_label: "Services Needed", consent: "I agree to storing my data for contact purposes.", submit: "Send Request", loading: "Sending...", success: "Your request was sent successfully! We'll contact you within 24 hours.", back: "Go Back" }
};

const SERVICES = { ar: ["استراتيجية النمو","مسارات التحويل","تصميم CRM","إدارة الإعلانات","تحليل البيانات","أتمتة العمليات"], en: ["Growth Strategy","Conversion Funnels","CRM Design","Ad Management","Data Analytics","Process Automation"] };
const BUDGETS = { ar: [["Low","$5k - $10k"],["Mid","$10k - $25k"],["High","$25k+"]], en: [["Low","$5k - $10k"],["Mid","$10k - $25k"],["High","$25k+"]] };
const TIMELINES = { ar: [["ASAP","عاجل"],["1 Month","خلال شهر"],["3 Months","خلال 3 أشهر"]], en: [["ASAP","ASAP"],["1 Month","1 Month"],["3 Months","3 Months"]] };

export default function RequestProposal() {
  const { lang } = useOutletContext();
  const l = L[lang] || L.ar;
  const isRTL = lang === "ar";
  const navigate = useNavigate();

  useSEO({
    title: 'طلب عرض',
    titleEn: 'Request Proposal',
    description: 'احصل على عرض مخصص لتنمية أعمالك مع زيادة',
    descriptionEn: 'Get a custom proposal to grow your business with Ziyada',
    path: '/RequestProposal',
  });

  const [form, setForm] = useState({ name: "", email: "", budget: "", timeline: "" });
  const [selectedServices, setSelectedServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [website, setWebsite] = useState("");
  const [formError, setFormError] = useState("");
  const formStarted = useRef(false);

  const onFormFocus = () => {
    if (!formStarted.current) {
      formStarted.current = true;
      trackEvent('form_start', { form: 'proposal' });
    }
  };

  const toggleService = (s) => setSelectedServices(p => p.includes(s) ? p.filter(x => x !== s) : [...p, s]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    const v = validate(proposalSchema, form);
    if (!v.ok) return;

    // Honeypot check
    if (website) return;

    // Rate limit check
    const rl = checkRateLimit("proposal");
    if (!rl.allowed) {
      setFormError(isRTL ? "عدد كبير من الطلبات. يرجى المحاولة مرة أخرى بعد بضع دقائق." : "Too many submissions. Please try again in a few minutes.");
      return;
    }

    setLoading(true);
    try {
      const utmParams = getUTMParams();
      const sourcePage = getSourcePage();
      await siteApi.functions.invoke("submitLead", { ...form, source: "proposal", services_requested: selectedServices, language: lang, ...utmParams, source_page: sourcePage });
      trackEvent('form_submit', { form: 'proposal' });
      identifyUser(form.email);
      navigate("/ThankYou");
    } catch (err) {
      console.error(err);
      setFormError(isRTL ? "حدث خطأ أثناء الإرسال. يرجى المحاولة مرة أخرى." : "Something went wrong. Please try again.");
    }
    setLoading(false);
  };

  const inputStyle = { width: "100%", background: "rgba(255,255,255,0.06)", border: "1px solid var(--border-glass)", borderRadius: 8, padding: "12px 14px", color: "var(--text-primary)", fontFamily: "inherit", fontSize: "0.95rem", outline: "none", boxSizing: "border-box" };
  const labelStyle = { display: "block", marginBottom: 6, color: "var(--text-secondary)", fontSize: "0.85rem", fontWeight: 600 };

  if (success) return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 500, margin: "60px auto", padding: "0 24px", textAlign: "center" }}>
      <div className="glass-panel" style={{ padding: 60 }}>
        <CheckCircle size={64} style={{ color: "var(--accent-primary)", margin: "0 auto 20px" }} />
        <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", marginBottom: 24 }}>{l.success}</p>
        <button onClick={() => navigate("/Home")} className="btn-outline-ziyada">{l.back}</button>
      </div>
    </div>
  );

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 720, margin: "0 auto", padding: "60px 24px" }}>
      <Link to="/Home" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "var(--text-secondary)", textDecoration: "none", fontSize: "0.9rem", marginBottom: 20 }}>
        {isRTL ? <ArrowRight size={16} /> : <ArrowLeft size={16} />}
        {isRTL ? "← العودة" : "← Back"}
      </Link>
      <div className="glass-panel" style={{ padding: "40px 36px" }}>
        <h1 className="gradient-text" style={{ textAlign: "center", fontSize: "2rem", fontWeight: 900, marginBottom: 36 }}>{l.title}</h1>
        <form onSubmit={handleSubmit}>
          <div style={{ position: "absolute", left: "-9999px", opacity: 0 }} aria-hidden="true">
            <input
              type="text"
              name="website"
              value={website}
              onChange={e => setWebsite(e.target.value)}
              tabIndex={-1}
              autoComplete="off"
            />
          </div>
          <div style={{ marginBottom: 20 }}><label style={labelStyle}>{l.name}</label><input style={inputStyle} value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required onFocus={onFormFocus} /></div>
          <div style={{ marginBottom: 20 }}><label style={labelStyle}>{l.email}</label><input type="email" style={inputStyle} value={form.email} onChange={e => setForm(f => ({...f, email: e.target.value}))} required /></div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
            <div>
              <label style={labelStyle}>{l.budget}</label>
              <select style={inputStyle} value={form.budget} onChange={e => setForm(f => ({...f, budget: e.target.value}))}>
                <option value="">—</option>
                {BUDGETS[lang].map(([v, label]) => <option key={v} value={v}>{label}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>{l.timeline}</label>
              <select style={inputStyle} value={form.timeline} onChange={e => setForm(f => ({...f, timeline: e.target.value}))}>
                <option value="">—</option>
                {TIMELINES[lang].map(([v, label]) => <option key={v} value={v}>{label}</option>)}
              </select>
            </div>
          </div>
          <div style={{ marginBottom: 24 }}>
            <label style={labelStyle}>{l.services_label}</label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              {SERVICES[lang].map((s, i) => (
                <label key={i} style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", padding: "8px 12px", borderRadius: 6, background: selectedServices.includes(s) ? "rgba(124,58,237,0.15)" : "rgba(255,255,255,0.03)", border: `1px solid ${selectedServices.includes(s) ? "var(--accent-primary)" : "var(--border-glass)"}`, transition: "all 0.2s" }}>
                  <input type="checkbox" checked={selectedServices.includes(s)} onChange={() => toggleService(s)} style={{ accentColor: "var(--accent-primary)" }} />
                  <span style={{ fontSize: "0.9rem" }}>{s}</span>
                </label>
              ))}
            </div>
          </div>
          <div style={{ marginBottom: 24, display: "flex", gap: 10, alignItems: "flex-start" }}>
            <input type="checkbox" id="consent2" required style={{ marginTop: 3 }} />
            <label htmlFor="consent2" style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>{l.consent}</label>
          </div>
          {formError && <p style={{ color: "#ef4444", fontSize: "0.9rem", marginBottom: 12 }}>{formError}</p>}
          <button type="submit" className="btn-primary-ziyada" style={{ width: "100%", padding: "14px", fontSize: "1rem" }} disabled={loading}>
            {loading ? l.loading : l.submit}
          </button>
        </form>
      </div>
    </div>
  );
}