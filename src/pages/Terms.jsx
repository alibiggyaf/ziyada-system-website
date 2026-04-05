import { useOutletContext } from "react-router-dom";
import useSEO from '@/lib/useSEO';

export default function Terms() {
  const { lang } = useOutletContext();
  const isRTL = lang === "ar";

  useSEO({
    title: 'الشروط والأحكام',
    titleEn: 'Terms & Conditions',
    description: 'شروط وأحكام استخدام خدمات زيادة',
    descriptionEn: 'Terms and conditions for using Ziyada services',
    path: '/Terms',
  });

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 800, margin: "0 auto", padding: "60px 24px" }}>
      <h1 className="gradient-text" style={{ fontSize: "2rem", fontWeight: 900, marginBottom: 30 }}>{isRTL ? "شروط الاستخدام" : "Terms of Use"}</h1>
      <div className="glass-panel" style={{ padding: 36, color: "var(--text-secondary)", lineHeight: 1.9 }}>
        {isRTL ? (
          <>
            <p style={{marginBottom:16}}><strong style={{color:"var(--text-primary)"}}>آخر تحديث: مارس 2026</strong></p>
            <p style={{marginBottom:16}}>باستخدامك لموقع زيادة للأنظمة المتقدمة، فإنك توافق على الشروط والأحكام التالية.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>استخدام الموقع</h3>
            <p style={{marginBottom:16}}>يُسمح باستخدام هذا الموقع للأغراض التجارية والمعلوماتية المشروعة فقط. يُحظر استخدام الموقع لأي غرض غير قانوني.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>الملكية الفكرية</h3>
            <p style={{marginBottom:16}}>جميع المحتويات المنشورة على هذا الموقع — بما فيها النصوص والصور والشعارات — هي ملك حصري لزيادة للأنظمة المتقدمة.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>تحديد المسؤولية</h3>
            <p style={{marginBottom:16}}>لا تتحمل زيادة للأنظمة أي مسؤولية عن أي أضرار مباشرة أو غير مباشرة ناتجة عن استخدام الموقع.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>التعديلات</h3>
            <p>نحتفظ بالحق في تعديل هذه الشروط في أي وقت. الاستمرار في استخدام الموقع بعد أي تعديل يعني موافقتك على الشروط المحدثة.</p>
          </>
        ) : (
          <>
            <p style={{marginBottom:16}}><strong style={{color:"var(--text-primary)"}}>Last Updated: March 2026</strong></p>
            <p style={{marginBottom:16}}>By using the Ziyada Advanced Systems website, you agree to the following terms and conditions.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>Use of Site</h3>
            <p style={{marginBottom:16}}>This site may only be used for legitimate business and informational purposes. Use for any unlawful purpose is prohibited.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>Intellectual Property</h3>
            <p style={{marginBottom:16}}>All content published on this site — including text, images, and logos — is the exclusive property of Ziyada Advanced Systems.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>Limitation of Liability</h3>
            <p style={{marginBottom:16}}>Ziyada Systems is not liable for any direct or indirect damages resulting from use of this site.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>Modifications</h3>
            <p>We reserve the right to modify these terms at any time. Continued use of the site after any modification implies acceptance of the updated terms.</p>
          </>
        )}
      </div>
    </div>
  );
}