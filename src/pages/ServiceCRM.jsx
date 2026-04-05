import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import ServiceDetailPage from "../components/ziyada/ServiceDetailPage.jsx";
import ROICalculator from "../components/ziyada/ROICalculator.jsx";
import { IconTarget } from "../components/ziyada/BrandIcons.jsx";
import useSEO from "@/lib/useSEO";
import { trackEvent } from "@/lib/analytics";

const DATA = {
  ar: {
    icon: IconTarget,
    tag: "الأعلى عائد",
    title: "أنظمة إدارة العملاء والمبيعات",
    desc: "تعرف إن كثير من الشركات ما تخسر عملاء لأن الطلب ضعيف — تخسرهم لأن المتابعة مو مرتّبة. العميل يسأل ويتأخر الرد، أو يدخل النظام وما أحد يرجع له. حنا نبني لك نظام بيعي يرتّب كل شي — من أول ما العميل يتواصل معك لين ما تقفل الصفقة.",
    scope: [
      "إعداد نظام إدارة العملاء (CRM) وهندسة مسارات البيع",
      "تسلسلات متابعة ورعاية العملاء",
      "مسارات واتساب للمبيعات وخدمة العملاء",
      "مكالمات ذكية وحجز مواعيد أوتوماتيكي",
      "إعادة تنشيط عملاء قدامى",
      "لوحات متابعة وتقارير بيعية واضحة"
    ],
    features: [
      "مسارات بيع مخصصة لنشاطك التجاري",
      "تقييم وتحويل آلي للعملاء المحتملين",
      "متابعة بريد + واتساب أوتوماتيك",
      "تقارير مبيعات + توقعات دقيقة",
      "تكامل كامل مع كل القنوات",
      "تدريب فريق المبيعات على النظام"
    ],
    results: ["ما يضيع عليك ولا عميل", "دورة بيع أقصر بـ 25%", "توقعات إيرادات دقيقة", "إنتاجية فريق أعلى", "استفادة من كل عميل قديم"],
    case: {
      who: "شركة مقاولات متوسطة بفريق مبيعات من 5 أشخاص",
      what: "نظام HubSpot مع مسارات مخصصة وأتمتة متابعة لكل مرحلة بيع",
      when: "تم التسليم خلال 4 أسابيع",
      where: "HubSpot + موقع الشركة + إيميل + واتساب",
      why: "كانوا يفقدون 40% من العملاء بسبب عدم المتابعة — الأتمتة حلّت المشكلة بالكامل"
    }
  },
  en: {
    icon: IconTarget,
    tag: "Highest ROI",
    title: "CRM & Sales Systems",
    desc: "Many companies don't lose clients because demand is low — they lose them because follow-up is disorganized. We build a complete sales system that organizes everything from first contact to closing the deal.",
    scope: [
      "CRM setup and sales pipeline engineering",
      "Follow-up and nurture sequences",
      "WhatsApp flows for sales and customer service",
      "Smart calls and automatic appointment booking",
      "Reactivating old customer databases",
      "Tracking dashboards and clear sales reports"
    ],
    features: [
      "Custom sales pipelines for your business",
      "Automated lead scoring and routing",
      "Auto email + WhatsApp follow-ups",
      "Sales reports + accurate forecasts",
      "Full omni-channel integration",
      "Sales team training on the system"
    ],
    results: ["Zero missed opportunities", "25% shorter sales cycle", "Accurate revenue forecasts", "Higher team productivity", "Value from every existing customer"],
    case: {
      who: "Mid-size contracting company with a 5-person sales team",
      what: "HubSpot system with custom pipelines and follow-up automation for every sales stage",
      when: "Delivered in 4 weeks",
      where: "HubSpot + Company website + Email + WhatsApp",
      why: "They were losing 40% of leads from lack of follow-up — automation solved this completely"
    }
  }
};

export default function ServiceCRM() {
  const { lang } = useOutletContext();
  useSEO({ title: "أنظمة إدارة العملاء والمبيعات — زيادة سيستم", titleEn: "CRM & Sales Systems", description: "نبني لك نظام بيعي يرتّب المتابعة ويقفل الصفقات", path: "/Services/crm", keywords: "CRM, إدارة عملاء, مبيعات, HubSpot, زيادة سيستم", schema: { "@context": "https://schema.org", "@type": "Service", name: "CRM & Sales Systems", provider: { "@type": "Organization", name: "Ziyada" }, description: "Complete CRM and sales pipeline systems that organize follow-up and close deals" } });
  useEffect(() => { trackEvent('service_view', { service: 'crm' }); }, []);
  return (
    <>
      <ServiceDetailPage data={DATA[lang] || DATA.ar} lang={lang} />
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px" }}>
        <ROICalculator lang={lang} />
      </div>
    </>
  );
}
