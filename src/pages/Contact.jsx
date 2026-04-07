import { useState, useRef } from "react";
import { useOutletContext, useNavigate, Link } from "react-router-dom";
import { siteApi } from "@/api/siteApi";
import { ArrowRight, ArrowLeft } from "lucide-react";
import { contactSchema, validate } from "@/lib/validation";
import useSEO from "@/lib/useSEO";
import { getUTMParams, getSourcePage } from "@/lib/utm";
import { checkRateLimit } from "@/lib/rateLimit";
import { trackEvent, identifyUser } from "@/lib/analytics";

export default function Contact() {
  const { lang } = useOutletContext();
  const isRTL = lang === "ar";

  useSEO({
    title: "تواصل معنا — زيادة سيستم",
    titleEn: "Contact Us — Ziyada Systems",
    description: "تواصل مع فريق زيادة سيستم للاستفسارات العامة",
    path: "/Contact"
  });

  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", message: "", name: "" });
  const [loading, setLoading] = useState(false);
  const [website, setWebsite] = useState("");
  const [formError, setFormError] = useState("");
  const formStarted = useRef(false);

  const onFormFocus = () => {
    if (!formStarted.current) {
      formStarted.current = true;
      trackEvent('form_start', { form: 'contact' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    const v = validate(contactSchema, form);
    if (!v.ok) return;

    // Honeypot check
    if (website) return;

    // Rate limit check
    const rl = checkRateLimit("contact");
    if (!rl.allowed) {
      setFormError(isRTL ? "عدد كبير من الطلبات. يرجى المحاولة مرة أخرى بعد بضع دقائق." : "Too many submissions. Please try again in a few minutes.");
      return;
    }

    setLoading(true);
    try {
      const utmParams = getUTMParams();
      const sourcePage = getSourcePage();
      // Prepare payload
      const payload = { email: form.email, name: form.name, challenge: form.message, source: "contact", language: lang, ...utmParams, source_page: sourcePage };

      // Contact Form Submission Handler (workflow name: Contact Form Submission Handler, workflow ID: 0f30c293-c375-45a2-9cf6-d55208de387b)
      const contactFormWebhook = "https://n8n.srv953562.hstgr.cloud/webhook/0f30c293-c375-45a2-9cf6-d55208de387b";
      await fetch(contactFormWebhook, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      trackEvent('form_submit', { form: 'contact' });
      identifyUser(form.email);
      navigate("/ThankYou");
    } catch (err) {
      console.error(err);
      setFormError(isRTL ? "حدث خطأ أثناء الإرسال. يرجى المحاولة مرة أخرى." : "Something went wrong. Please try again.");
    }
    setLoading(false);
  };

  const inputStyle = { width: "100%", background: "rgba(255,255,255,0.06)", border: "1px solid var(--border-glass)", borderRadius: 8, padding: "12px 14px", color: "var(--text-primary)", fontFamily: "inherit", fontSize: "0.95rem", outline: "none", boxSizing: "border-box" };

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 600, margin: "0 auto", padding: "60px 24px" }}>
      <Link to="/Home" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "var(--text-secondary)", textDecoration: "none", fontSize: "0.9rem", marginBottom: 20 }}>
        {isRTL ? <ArrowRight size={16} /> : <ArrowLeft size={16} />}
        {isRTL ? "← العودة" : "← Back"}
      </Link>
      <div className="glass-panel" style={{ padding: 48, textAlign: "center" }}>
        <h1 className="gradient-text" style={{ fontSize: "2rem", fontWeight: 900, marginBottom: 12 }}>
          {isRTL ? "تواصل معنا" : "Contact Us"}
        </h1>
        <p style={{ color: "var(--text-secondary)", marginBottom: 32 }}>
          {isRTL ? "للاستفسارات العامة، يرجى ملء النموذج أدناه." : "For general inquiries, please fill out the form below."}
        </p>

        <form onSubmit={handleSubmit} style={{ textAlign: isRTL ? "right" : "left" }}>
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
            <div style={{ marginBottom: 16 }}>
              <input style={inputStyle} placeholder={isRTL ? "اسمك" : "Your name"} value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} onFocus={onFormFocus} />
            </div>
            <div style={{ marginBottom: 16 }}>
              <input type="email" style={inputStyle} placeholder={isRTL ? "بريدك الإلكتروني" : "Your email"} required value={form.email} onChange={e => setForm(f => ({...f, email: e.target.value}))} />
            </div>
            <div style={{ marginBottom: 20 }}>
              <textarea style={{ ...inputStyle, minHeight: 120, resize: "vertical" }} placeholder={isRTL ? "رسالتك..." : "Your message..."} required value={form.message} onChange={e => setForm(f => ({...f, message: e.target.value}))} />
            </div>
            {formError && <p style={{ color: "#ef4444", fontSize: "0.9rem", marginBottom: 12 }}>{formError}</p>}
            <button type="submit" className="btn-primary-ziyada" style={{ width: "100%", padding: "14px", fontSize: "1rem" }} disabled={loading}>
              {loading ? "..." : (isRTL ? "إرسال" : "Send")}
            </button>
        </form>
      </div>
    </div>
  );
}