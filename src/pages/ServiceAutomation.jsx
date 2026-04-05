import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import ServiceDetailPage from "../components/ziyada/ServiceDetailPage.jsx";
import ROICalculator from "../components/ziyada/ROICalculator.jsx";
import { IconZap } from "../components/ziyada/BrandIcons.jsx";
import useSEO from "@/lib/useSEO";
import { trackEvent } from "@/lib/analytics";

const DATA = {
  ar: {
    icon: IconZap,
    tag: "الأكثر طلباً",
    title: "أنظمة أتمتة الأعمال",
    desc: "كثير من الشركات عندها شغل يتكرر كل يوم — إدخال بيانات، إرسال تقارير، متابعة رسائل. فريقك يقضي ساعات على أشياء المفروض تصير تلقائي. حنا في زيادة سيستم نحوّل هالأعمال المتكررة إلى أنظمة أتمتة ذكية تشتغل بسرعة واتساق، وتخلّي فريقك يركز على الشغل اللي فعلاً يحتاج تفكير.",
    scope: [
      "أتمتة سير العمل اليومي",
      "معالجة المستندات وإدخال البيانات تلقائي",
      "تقارير ذكية توصل الإدارة بدون ما أحد يجهّزها",
      "تحويل الجداول والإكسلات إلى نظام رقمي مرتّب",
      "مساعد ذكي يجاوب أسئلة الفريق من معرفة الشركة",
      "أنظمة توثيق وإجراءات تشغيل واضحة"
    ],
    features: [
      "أتمتة كاملة بـ n8n + ذكاء اصطناعي",
      "تكامل مع 300+ تطبيق (CRM، واتساب، إيميل)",
      "وكلاء ذكيون يشتغلون مع فريقك",
      "لوحة تحكم مركزية للمتابعة",
      "مراقبة فورية وتنبيهات لحظية",
      "تدريب الفريق على النظام الجديد"
    ],
    results: ["جهد يدوي أقل بـ 80%", "صفر أخطاء بشرية", "تنفيذ أسرع ٤ مرات", "وضوح أكبر للإدارة", "توسّع بدون توظيف إضافي"],
    case: {
      who: "شركة استشارات عقارية في الرياض تستقبل 200+ استفسار شهرياً",
      what: "نظام أتمتة يستقبل الاستفسارات من واتساب وإيميل، يصنّفها، يُرسل رد تلقائي، ويُسجّلها في CRM",
      when: "خلال 3 أسابيع تم التسليم",
      where: "واتساب + Gmail + HubSpot CRM + Google Sheets",
      why: "الفريق كان يضيع 3 ساعات يومياً في الردود اليدوية — الحين كل شي تلقائي 100%"
    }
  },
  en: {
    icon: IconZap,
    tag: "Most Requested",
    title: "Business Automation Systems",
    desc: "We turn repetitive daily tasks into smart automated systems that run with speed and consistency, so your team can focus on work that actually needs thinking.",
    scope: [
      "Daily workflow automation",
      "Document processing and auto data entry",
      "Smart reports delivered to management automatically",
      "Convert spreadsheets to organized digital systems",
      "AI assistant that answers team questions from company knowledge",
      "Clear documentation and operating procedures"
    ],
    features: [
      "Full automation with n8n + AI",
      "Integration with 300+ apps (CRM, WhatsApp, Email)",
      "AI agents working alongside your team",
      "Central monitoring dashboard",
      "Real-time alerts and notifications",
      "Team training on the new system"
    ],
    results: ["80% less manual effort", "Zero human errors", "4x faster execution", "Greater clarity for management", "Scale without extra hiring"],
    case: {
      who: "Real estate consulting firm in Riyadh receiving 200+ inquiries/month",
      what: "Automation system that receives inquiries from WhatsApp and email, classifies them, sends auto-replies, and logs them in CRM",
      when: "Delivered in 3 weeks",
      where: "WhatsApp + Gmail + HubSpot CRM + Google Sheets",
      why: "Team was losing 3 hours/day on manual replies — now 100% automated"
    }
  }
};

export default function ServiceAutomation() {
  const { lang } = useOutletContext();
  useSEO({ title: "أنظمة أتمتة الأعمال — زيادة سيستم", titleEn: "Business Automation Systems", description: "نحوّل الأعمال المتكررة إلى أنظمة ذكية تشتغل بسرعة واتساق", path: "/Services/automation", keywords: "أتمتة أعمال, n8n, أنظمة ذكية, زيادة سيستم, السعودية", schema: { "@context": "https://schema.org", "@type": "Service", name: "Business Automation Systems", provider: { "@type": "Organization", name: "Ziyada" }, description: "We turn repetitive daily tasks into smart automated systems using n8n and AI" } });
  useEffect(() => { trackEvent('service_view', { service: 'automation' }); }, []);
  return (
    <>
      <ServiceDetailPage data={DATA[lang] || DATA.ar} lang={lang} />
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px" }}>
        <ROICalculator lang={lang} />
      </div>
    </>
  );
}
