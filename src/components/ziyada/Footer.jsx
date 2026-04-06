import { Link } from "react-router-dom";
import { useState } from "react";
import { siteApi } from "@/api/siteApi";
import { checkRateLimit } from "@/lib/rateLimit";

export default function Footer({ lang }) {
  const [email, setEmail] = useState("");
  const [subStatus, setSubStatus] = useState(null);
  const [website, setWebsite] = useState("");
  const [formError, setFormError] = useState("");
  const isRTL = lang === "ar";

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (!email) return;
    setFormError("");

    // Honeypot check
    if (website) return;

    // Rate limit check
    const rl = checkRateLimit("newsletter");
    if (!rl.allowed) {
      setFormError(isRTL ? "عدد كبير من الطلبات. يرجى المحاولة مرة أخرى بعد بضع دقائق." : "Too many submissions. Please try again in a few minutes.");
      return;
    }

    setSubStatus("loading");
    try {
      const res = await siteApi.functions.invoke("subscribeEmail", { email, language: lang });
      setSubStatus(res.data?.success ? "success" : "error");
      if (!res.data?.success) {
        setFormError(isRTL ? "حدث خطأ أثناء الاشتراك. يرجى المحاولة مرة أخرى." : "Something went wrong. Please try again.");
      }
    } catch (err) {
      console.error(err);
      setSubStatus("error");
      setFormError(isRTL ? "حدث خطأ أثناء الاشتراك. يرجى المحاولة مرة أخرى." : "Something went wrong. Please try again.");
    }
  };

  return (
    <footer style={{ borderTop: "1px solid var(--border-glass)", padding: "60px 24px 30px", background: "var(--bg-deep)", position: "relative", zIndex: 1 }}
      dir={isRTL ? "rtl" : "ltr"}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 40, marginBottom: 40 }}>
          {/* Brand */}
          <div>
            <div className="gradient-text" style={{ fontSize: "1.4rem", fontWeight: 900, marginBottom: 12 }}>Ziyada Systems</div>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: 1.7 }}>
              {isRTL ? "تصميم وبناء الأنظمة التشغيلية والرقمية للشركات الطموحة." : "Building operational and digital systems for ambitious companies."}
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 style={{ marginBottom: 16, fontWeight: 700 }}>{isRTL ? "روابط سريعة" : "Quick Links"}</h4>
            {[
              { label: isRTL ? "الخدمات" : "Services", path: "/Services" },
              { label: isRTL ? "من نحن" : "About", path: "/About" },
              { label: isRTL ? "المدونة" : "Blog", path: "/Blog" },
              { label: isRTL ? "تواصل معنا" : "Contact", path: "/Contact" },
              { label: isRTL ? "الأسئلة الشائعة" : "FAQ", path: "/FAQ" },
            ].map(l => (
              <div key={l.path} style={{ marginBottom: 8 }}>
                <Link to={l.path} style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: "0.9rem" }}>{l.label}</Link>
              </div>
            ))}
          </div>

          {/* Newsletter */}
          <div>
            <h4 style={{ marginBottom: 16, fontWeight: 700 }}>{isRTL ? "النشرة البريدية" : "Newsletter"}</h4>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: 12 }}>
              {isRTL ? "اشترك للحصول على آخر المقالات والأفكار." : "Subscribe for latest articles and insights."}
            </p>
            {subStatus === "success" ? (
              <p style={{ color: "#22c55e", fontSize: "0.9rem" }}>
                {isRTL ? "شكراً! تم الاشتراك بنجاح ✓" : "Thank you! Subscribed successfully ✓"}
              </p>
            ) : (
              <form onSubmit={handleSubscribe} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
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
                <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder={isRTL ? "بريدك الإلكتروني" : "Your email"}
                  className="form-input-ziyada" style={{ flex: 1, minWidth: 160 }} required />
                <button type="submit" className="btn-primary-ziyada" style={{ padding: "10px 16px", fontSize: "0.85rem" }}
                  disabled={subStatus === "loading"}>
                  {subStatus === "loading" ? "..." : (isRTL ? "اشترك" : "Subscribe")}
                </button>
                {formError && <p style={{ color: "#ef4444", fontSize: "0.8rem", width: "100%", marginTop: 4 }}>{formError}</p>}
              </form>
            )}
          </div>
        </div>

        <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: 24, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>
            © 2026 Ziyada Systems. All Rights Reserved.
          </p>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.78rem", marginTop: 4 }}>
            ziyadasystem.com · info@ziyadasystem.com
          </p>
        </div>
        <div style={{ display: "flex", gap: 20 }}>
          <Link to="/Privacy" style={{ color: "var(--text-secondary)", fontSize: "0.8rem", textDecoration: "none" }}>{isRTL ? "سياسة الخصوصية" : "Privacy Policy"}</Link>
          <Link to="/Terms" style={{ color: "var(--text-secondary)", fontSize: "0.8rem", textDecoration: "none" }}>{isRTL ? "شروط الاستخدام" : "Terms of Use"}</Link>
        </div>
        </div>
      </div>
    </footer>
  );
}