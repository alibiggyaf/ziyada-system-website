import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import ServiceDetailPage from "../components/ziyada/ServiceDetailPage.jsx";
import ROICalculator from "../components/ziyada/ROICalculator.jsx";
import { IconRocket } from "../components/ziyada/BrandIcons.jsx";
import useSEO from "@/lib/useSEO";
import { trackEvent } from "@/lib/analytics";

const DATA = {
  ar: {
    icon: IconRocket,
    tag: "نتائج سريعة",
    title: "أنظمة اكتساب العملاء",
    desc: "مو بس تجيب استفسارات — المهم إن الاستفسار يوصل للشخص الصح، يتأهل بسرعة، ويدخل مسار بيعي واضح. كثير شركات تصرف على الإعلانات وبعدين الاستفسارات تضيع لأن ما فيه نظام يلقطها ويرتّبها. هنا يجي دور أنظمة الاكتساب حقتنا.",
    scope: [
      "أنظمة سرعة الاستجابة للعملاء الجدد",
      "أنظمة التواصل الخارجي بين الشركات (B2B Outreach)",
      "هندسة مسارات التحويل عشان ما يتسرب العميل",
      "تأهيل وتوزيع العملاء تلقائي",
      "استراتيجية اكتساب وصياغة العرض"
    ],
    features: [
      "+50 عميل مؤهل شهرياً",
      "نمو إيرادات 40%",
      "تحسين التحويل 35%",
      "تقليل تكلفة اكتساب العميل 60%",
      "تصنيف وتقييم الفرص آلياً"
    ],
    results: ["فرص أكثر بجودة أعلى", "استجابة أسرع", "مسار تحويل أوضح", "تنسيق أفضل بين التسويق والمبيعات", "استغلال أذكى للميزانية"],
    case: {
      who: "شركة SaaS تستهدف الشركات المتوسطة والكبيرة في السعودية",
      what: "نظام اكتساب يشمل LinkedIn + صفحة هبوط + CRM + سلسلة متابعة أتمتة",
      when: "خلال شهر من الإطلاق بدأت توصل فرص مؤهلة",
      where: "LinkedIn + Google Ads + HubSpot + البريد الإلكتروني",
      why: "المبيعات كانت تعتمد على العلاقات الشخصية فقط — الحين 60% من الصفقات تجي من الأنظمة الرقمية"
    }
  },
  en: {
    icon: IconRocket,
    tag: "Fast Results",
    title: "Customer Acquisition Systems",
    desc: "It's not just about getting inquiries — what matters is that each inquiry reaches the right person, gets qualified fast, and enters a clear sales path. We build acquisition systems that capture and organize every opportunity.",
    scope: [
      "Speed-to-lead response systems",
      "B2B outreach systems",
      "Conversion funnel engineering to prevent leaks",
      "Automated lead qualification and routing",
      "Acquisition strategy and offer framing"
    ],
    features: [
      "+50 qualified leads/month",
      "40% revenue growth",
      "35% conversion improvement",
      "60% reduction in acquisition cost",
      "Automated lead scoring and classification"
    ],
    results: ["More leads, higher quality", "Faster response", "Clearer conversion path", "Better marketing-sales alignment", "Smarter budget use"],
    case: {
      who: "SaaS company targeting mid and large enterprises in Saudi Arabia",
      what: "Acquisition system with LinkedIn + landing page + CRM + automated follow-up sequences",
      when: "Qualified leads started arriving within one month of launch",
      where: "LinkedIn + Google Ads + HubSpot + Email",
      why: "Sales relied only on personal connections — now 60% of deals come from digital systems"
    }
  }
};

export default function ServiceLeadGen() {
  const { lang } = useOutletContext();
  useSEO({ title: "أنظمة اكتساب العملاء — زيادة سيستم", titleEn: "Customer Acquisition Systems", description: "نلقط الفرص ونأهلها وندخلها مسار بيعي واضح", path: "/Services/lead-generation", keywords: "اكتساب عملاء, توليد عملاء, B2B, زيادة سيستم", schema: { "@context": "https://schema.org", "@type": "Service", name: "Customer Acquisition Systems", provider: { "@type": "Organization", name: "Ziyada" }, description: "Lead generation and qualification systems that capture every opportunity into a clear sales path" } });
  useEffect(() => { trackEvent('service_view', { service: 'lead-generation' }); }, []);
  return (
    <>
      <ServiceDetailPage data={DATA[lang] || DATA.ar} lang={lang} />
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px" }}>
        <ROICalculator lang={lang} />
      </div>
    </>
  );
}
