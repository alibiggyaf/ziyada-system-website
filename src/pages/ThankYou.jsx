import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import { CheckCircle } from "lucide-react";
import { trackEvent } from "@/lib/analytics";
import useSEO from '@/lib/useSEO';

export default function ThankYou() {
  const { lang } = useOutletContext();
  const isRTL = lang === "ar";

  useSEO({
    title: 'شكراً لك',
    titleEn: 'Thank You',
    description: 'شكراً لتواصلك مع زيادة',
    descriptionEn: 'Thank you for contacting Ziyada',
    path: '/ThankYou',
    noindex: true,
  });

  useEffect(() => {
    trackEvent('conversion', { type: 'form_submission' });
  }, []);

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ height: "70vh", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "0 24px" }}>
      <div className="glass-panel" style={{ padding: 60, maxWidth: 500 }}>
        <CheckCircle size={64} style={{ color: "var(--accent-primary)", margin: "0 auto 20px" }} />
        <h1 className="gradient-text" style={{ fontSize: "2rem", fontWeight: 900, marginBottom: 10 }}>
          {isRTL ? "شكراً لك!" : "Thank You!"}
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "1.1rem", marginBottom: 30 }}>
          {isRTL ? "تم استلام طلبك بنجاح. سنتواصل معك قريباً." : "Your request was received. We'll be in touch shortly."}
        </p>
        <Link to="/Home"><button className="btn-outline-ziyada">{isRTL ? "العودة للرئيسية" : "Back to Home"}</button></Link>
      </div>
    </div>
  );
}