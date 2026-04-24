import { useState, useRef } from "react";
import { useOutletContext, useNavigate, Link } from "react-router-dom";
import { siteApi } from "@/api/siteApi";
import { Calendar, Clock, CheckCircle, ArrowRight, ArrowLeft } from "lucide-react";
import { bookingSchema, validate } from "@/lib/validation";
import useSEO from "@/lib/useSEO";
import { getUTMParams, getSourcePage } from "@/lib/utm";
import { checkRateLimit } from "@/lib/rateLimit";
import { trackEvent, identifyUser } from "@/lib/analytics";
import { setKnownIdentity } from "@/lib/contactIdentity";

const TIMES = ["09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00"];

const L = {
  ar: { title: "حجز جلسة استراتيجية", name: "الاسم الكامل", company: "اسم الشركة", email: "البريد الإلكتروني للعمل", phone: "رقم الهاتف", size: "حجم الشركة", industry: "القطاع", challenge: "ما هو التحدي الرئيسي الذي تواجهه حالياً؟", date_label: "اختر التاريخ", time_label: "اختر الوقت", consent: "أوافق على سياسة الخصوصية والتواصل معي.", submit: "تأكيد الحجز", loading: "جارٍ الحجز...", success_title: "تم الحجز بنجاح!", success_msg: "تحقق من بريدك الإلكتروني لتفاصيل الاجتماع.", meet_link: "رابط Google Meet", back: "العودة للرئيسية" },
  en: { title: "Book a Strategy Session", name: "Full Name", company: "Company Name", email: "Work Email", phone: "Phone Number", size: "Company Size", industry: "Industry", challenge: "What is your main challenge right now?", date_label: "Choose Date", time_label: "Choose Time", consent: "I agree to the privacy policy and being contacted.", submit: "Confirm Booking", loading: "Booking...", success_title: "Booking Confirmed!", success_msg: "Check your email for meeting details.", meet_link: "Google Meet Link", back: "Back to Home" }
};

export default function BookMeeting() {
  const { lang } = useOutletContext();
  const l = L[lang] || L.ar;
  const isRTL = lang === "ar";

  useSEO({
    title: "احجز استشارة مجانية — زيادة سيستم",
    titleEn: "Book Free Consultation — Ziyada Systems",
    description: "احجز جلسة استراتيجية مجانية مع فريق زيادة سيستم واكتشف كيف نضاعف نمو شركتك",
    path: "/BookMeeting"
  });

  const navigate = useNavigate();

  const [form, setForm] = useState({ lead_name: "", lead_email: "", lead_phone: "", company: "", industry: "", company_size: "", challenge: "", booking_date: "", booking_time: "" });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [availableSlots, setAvailableSlots] = useState(TIMES);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [errors, setErrors] = useState({});
  const [website, setWebsite] = useState("");
  const [formError, setFormError] = useState("");
  const formStarted = useRef(false);

  const onFormFocus = () => {
    if (!formStarted.current) {
      formStarted.current = true;
      trackEvent('form_start', { form: 'booking' });
    }
  };

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleDateChange = async (date) => {
    update("booking_date", date);
    update("booking_time", "");
    if (!date) return;
    setLoadingSlots(true);
    const res = await siteApi.functions.invoke("getAvailableSlots", { date });
    setAvailableSlots(res.data?.available_slots || TIMES);
    setLoadingSlots(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    const v = validate(bookingSchema, form);
    if (!v.ok) { setErrors(v.errors); return; }
    setErrors({});

    // Honeypot check
    if (website) return;

    // Rate limit check
    const rl = checkRateLimit("booking");
    if (!rl.allowed) {
      setFormError(isRTL ? "عدد كبير من الطلبات. يرجى المحاولة مرة أخرى بعد بضع دقائق." : "Too many submissions. Please try again in a few minutes.");
      return;
    }

    setLoading(true);
    try {
      const utmParams = getUTMParams();
      const sourcePage = getSourcePage();
      const res = await siteApi.functions.invoke("bookMeeting", { ...form, ...utmParams, source_page: sourcePage, language: lang });
      if (res?.data && !res?.error) {
        trackEvent('form_submit', { form: 'booking' });
        identifyUser(form.lead_email);
        setKnownIdentity({ email: form.lead_email, phone: form.lead_phone, name: form.lead_name });
        window.scrollTo(0, 0);
        navigate("/ThankYou");
      }
    } catch (err) {
      console.error("Booking error:", err);
      setFormError(isRTL ? "حدث خطأ أثناء الحجز. يرجى المحاولة مرة أخرى." : "Something went wrong. Please try again.");
    }
    setLoading(false);
  };

  // Get min date (tomorrow)
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().split("T")[0];

  if (result) {
    return (
      <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 600, margin: "60px auto", padding: "0 24px", textAlign: "center" }}>
        <div className="glass-panel" style={{ padding: 60 }}>
          <CheckCircle size={64} style={{ color: "var(--accent-primary)", margin: "0 auto 20px" }} />
          <h1 className="gradient-text" style={{ fontSize: "2rem", fontWeight: 900, marginBottom: 12 }}>{l.success_title}</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem", marginBottom: 20 }}>{l.success_msg}</p>
          {result.google_meet_link && (
            <a href={result.google_meet_link} target="_blank" rel="noreferrer"
              style={{ display: "inline-block", marginBottom: 24, padding: "10px 24px", background: "var(--gradient-main)", color: "white", borderRadius: 8, textDecoration: "none", fontWeight: 700 }}>
              {l.meet_link} →
            </a>
          )}
          <br />
          <button onClick={() => navigate("/Home")} className="btn-outline-ziyada">{l.back}</button>
        </div>
      </div>
    );
  }

  const inputStyle = { width: "100%", background: "rgba(255,255,255,0.06)", border: "1px solid var(--border-glass)", borderRadius: 8, padding: "12px 14px", color: "var(--text-primary)", fontFamily: "inherit", fontSize: "0.95rem", outline: "none", boxSizing: "border-box" };
  const labelStyle = { display: "block", marginBottom: 6, color: "var(--text-secondary)", fontSize: "0.85rem", fontWeight: 600 };

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 800, margin: "0 auto", padding: "60px 24px" }}>
      <Link to="/Home" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "var(--text-secondary)", textDecoration: "none", fontSize: "0.9rem", marginBottom: 20 }}>
        {isRTL ? <ArrowRight size={16} /> : <ArrowLeft size={16} />}
        {isRTL ? "← العودة" : "← Back"}
      </Link>
      <div className="glass-panel" style={{ padding: "40px 36px" }}>
        <h1 className="gradient-text" style={{ textAlign: "center", fontSize: "2rem", fontWeight: 900, marginBottom: 36 }}>{l.title}</h1>
        <form onSubmit={handleSubmit}>
          <div
            style={{
              position: "absolute",
              width: 1,
              height: 1,
              padding: 0,
              margin: -1,
              overflow: "hidden",
              clip: "rect(0, 0, 0, 0)",
              whiteSpace: "nowrap",
              border: 0,
            }}
            aria-hidden="true"
          >
            <input
              type="text"
              name="website"
              value={website}
              onChange={e => setWebsite(e.target.value)}
              tabIndex={-1}
              autoComplete="off"
            />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
            <div><label style={labelStyle}>{l.name}</label><input style={inputStyle} value={form.lead_name} onChange={e => update("lead_name", e.target.value)} required onFocus={onFormFocus} /></div>
            <div><label style={labelStyle}>{l.company}</label><input style={inputStyle} value={form.company} onChange={e => update("company", e.target.value)} required /></div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
            <div><label style={labelStyle}>{l.email}</label><input type="email" style={inputStyle} value={form.lead_email} onChange={e => update("lead_email", e.target.value)} required /></div>
            <div><label style={labelStyle}>{l.phone}</label><input type="tel" style={inputStyle} value={form.lead_phone} onChange={e => update("lead_phone", e.target.value)} /></div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
            <div>
              <label style={labelStyle}>{l.size}</label>
              <select style={inputStyle} value={form.company_size} onChange={e => update("company_size", e.target.value)}>
                <option value="">—</option>
                {["1-50","51-200","201-500","500+"].map(v => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>{l.industry}</label>
              <select style={inputStyle} value={form.industry} onChange={e => update("industry", e.target.value)}>
                <option value="">—</option>
                {["SaaS","E-commerce","B2B Services","Retail","Other"].map(v => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle}>{l.challenge}</label>
            <textarea style={{ ...inputStyle, minHeight: 90, resize: "vertical" }} value={form.challenge} onChange={e => update("challenge", e.target.value)} />
          </div>

          {/* Date & Time picker */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
            <div>
              <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: 6 }}><Calendar size={14} />{l.date_label}</label>
              <input type="date" style={inputStyle} min={minDate} value={form.booking_date} onChange={e => handleDateChange(e.target.value)} required />
            </div>
            <div>
              <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: 6 }}><Clock size={14} />{l.time_label}</label>
              <select style={inputStyle} value={form.booking_time} onChange={e => update("booking_time", e.target.value)} required disabled={!form.booking_date || loadingSlots}>
                <option value="">—</option>
                {availableSlots.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <div style={{ marginBottom: 24, display: "flex", gap: 10, alignItems: "flex-start" }}>
            <input type="checkbox" id="consent" required style={{ marginTop: 3 }} />
            <label htmlFor="consent" style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>{l.consent}</label>
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