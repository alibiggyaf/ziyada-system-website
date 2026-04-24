import { useOutletContext } from "react-router-dom";
import useSEO from '@/lib/useSEO';

export default function Privacy() {
  const { lang } = useOutletContext();
  const isRTL = lang === "ar";

  useSEO({
    title: 'سياسة الخصوصية',
    titleEn: 'Privacy Policy',
    description: 'سياسة خصوصية زيادة - كيف نحمي بياناتك',
    descriptionEn: 'Ziyada privacy policy - how we protect your data',
    path: '/Privacy',
  });

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ maxWidth: 800, margin: "0 auto", padding: "60px 24px" }}>
      <h1 className="gradient-text" style={{ fontSize: "2rem", fontWeight: 900, marginBottom: 30 }}>{isRTL ? "سياسة الخصوصية" : "Privacy Policy"}</h1>
      <div className="glass-panel" style={{ padding: 36, color: "var(--text-secondary)", lineHeight: 1.9 }}>
        {isRTL ? (
          <>
            <p style={{marginBottom:16}}><strong style={{color:"var(--text-primary)"}}>آخر تحديث: مارس 2026</strong></p>
            <p style={{marginBottom:16}}>تلتزم زيادة للأنظمة المتقدمة بحماية خصوصيتك. توضح هذه السياسة كيفية جمع واستخدام وحفظ بياناتك الشخصية.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>البيانات التي نجمعها</h3>
            <p style={{marginBottom:16}}>نجمع البيانات التي تقدمها طوعاً عبر نماذج التواصل والحجز، بما فيها: الاسم، البريد الإلكتروني، رقم الهاتف، واسم الشركة.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>كيف نستخدم بياناتك</h3>
            <p style={{marginBottom:16}}>نستخدم بياناتك للتواصل معك، وتقديم الخدمات المطلوبة، وتحسين تجربتك معنا. نحن لا نبيع بياناتك لأطراف ثالثة.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>تكامل HubSpot</h3>
            <p style={{marginBottom:16}}>نستخدم HubSpot CRM لإدارة التواصل مع العملاء. بياناتك محفوظة بأمان ووفق معايير GDPR.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>حقوقك</h3>
            <p>يحق لك طلب حذف بياناتك أو تعديلها في أي وقت عبر التواصل معنا على info@ziyadasystems.com</p>
          </>
        ) : (
          <>
            <p style={{marginBottom:16}}><strong style={{color:"var(--text-primary)"}}>Last Updated: March 2026</strong></p>
            <p style={{marginBottom:16}}>Ziyada Advanced Systems is committed to protecting your privacy. This policy explains how we collect, use, and store your personal data.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>Data We Collect</h3>
            <p style={{marginBottom:16}}>We collect data you voluntarily provide through contact and booking forms, including: name, email, phone number, and company name.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>How We Use Your Data</h3>
            <p style={{marginBottom:16}}>We use your data to contact you, provide requested services, and improve your experience. We do not sell your data to third parties.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>HubSpot Integration</h3>
            <p style={{marginBottom:16}}>We use HubSpot CRM to manage client communications. Your data is securely stored in accordance with GDPR standards.</p>
            <h3 style={{color:"var(--text-primary)",marginBottom:8,marginTop:24}}>Your Rights</h3>
            <p>You may request deletion or modification of your data at any time by contacting us at info@ziyadasystems.com</p>
          </>
        )}
      </div>
    </div>
  );
}