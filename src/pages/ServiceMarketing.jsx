import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import ServiceDetailPage from "../components/ziyada/ServiceDetailPage.jsx";
import ROICalculator from "../components/ziyada/ROICalculator.jsx";
import { IconMegaphone } from "../components/ziyada/BrandIcons.jsx";
import useSEO from "@/lib/useSEO";
import { trackEvent } from "@/lib/analytics";

const DATA = {
  ar: {
    icon: IconMegaphone,
    tag: "إعلانات + SEO",
    title: "التسويق الأدائي والظهور في البحث",
    desc: "الإعلانات بدون نظام تحليل ومتابعة تصير مصروف بدون وضوح. حنا ندير الحملات المدفوعة والظهور في البحث بطريقة مرتبطة بجودة العملاء — مو بس كم واحد ضغط على الإعلان، لكن كم واحد فعلاً صار عميل.",
    scope: [
      "إعلانات مدفوعة (Google Ads + Meta Ads + Snapchat)",
      "تحسين الظهور في محركات البحث (SEO)",
      "إعلانات البحث المدفوعة (SEM)",
      "تحليلات ونسب النتائج وتقارير شاملة",
      "أبحاث السوق وتحليل المنافسين",
      "تحسين مستمر للحملات والصفحات"
    ],
    features: [
      "Google Ads + Meta Ads + Snapchat",
      "استهداف دقيق للجمهور المثالي",
      "A/B testing للإعلانات والصفحات",
      "تقارير ROAS واضحة للإدارة",
      "SEO تقني + محتوى محسّن للبحث",
      "ربط أداء القنوات بجودة العملاء"
    ],
    results: ["طلب أجود", "إنفاق أكفأ بـ 2-4x", "وضوح أكبر بالأداء", "حضور أقوى بالبحث", "قرارات تسويقية أدق"],
    case: {
      who: "مطوّر عقاري في جدة يطلق مشروع سكني 150 وحدة",
      what: "حملة Google + Meta + تحسين SEO لصفحات المشروع مع صفحة هبوط محسّنة",
      when: "حملة 3 أشهر بميزانية 50,000 ريال شهرياً",
      where: "Google Search + Meta (Facebook/Instagram) + SEO + صفحة هبوط مخصصة",
      why: "المبيعات بالأدوات التقليدية كانت بطيئة — الحملة الرقمية + SEO أنتجوا 80 عميل مؤهّل في الشهر الأول"
    }
  },
  en: {
    icon: IconMegaphone,
    tag: "Ads + SEO",
    title: "Performance Marketing & Search Visibility",
    desc: "Ads without analytics and follow-up become spend without clarity. We manage paid campaigns and search visibility tied to actual lead quality — not just clicks, but real customers.",
    scope: [
      "Paid ads (Google Ads + Meta Ads + Snapchat)",
      "Search engine optimization (SEO)",
      "Paid search advertising (SEM)",
      "Analytics, attribution, and comprehensive reports",
      "Market research and competitor analysis",
      "Continuous optimization of campaigns and pages"
    ],
    features: [
      "Google Ads + Meta Ads + Snapchat",
      "Precise target audience segmentation",
      "A/B testing for ads and landing pages",
      "Clear ROAS reports for management",
      "Technical SEO + search-optimized content",
      "Channel performance tied to lead quality"
    ],
    results: ["Higher quality demand", "2-4x more efficient spending", "Greater performance clarity", "Stronger search presence", "Sharper marketing decisions"],
    case: {
      who: "Real estate developer in Jeddah launching a 150-unit residential project",
      what: "Google + Meta campaign + SEO optimization for project pages with optimized landing page",
      when: "3-month campaign at 50,000 SAR/month budget",
      where: "Google Search + Meta (Facebook/Instagram) + SEO + Custom landing page",
      why: "Traditional sales were slow — the digital campaign + SEO generated 80 qualified leads in the first month"
    }
  }
};

export default function ServiceMarketing() {
  const { lang } = useOutletContext();
  useSEO({ title: "التسويق الأدائي والظهور في البحث — زيادة سيستم", titleEn: "Performance Marketing & Search", description: "إعلانات + SEO مرتبطة بجودة العملاء مو بس المشاهدات", path: "/Services/marketing", keywords: "تسويق رقمي, Google Ads, Meta Ads, SEO, SEM, زيادة سيستم", schema: { "@context": "https://schema.org", "@type": "Service", name: "Performance Marketing & Search Visibility", provider: { "@type": "Organization", name: "Ziyada" }, description: "Paid advertising and SEO campaigns tied to actual lead quality and business results" } });
  useEffect(() => { trackEvent('service_view', { service: 'marketing' }); }, []);
  return (
    <>
      <ServiceDetailPage data={DATA[lang] || DATA.ar} lang={lang} />
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px" }}>
        <ROICalculator lang={lang} />
      </div>
    </>
  );
}
