import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import ServiceDetailPage from "../components/ziyada/ServiceDetailPage.jsx";
import ROICalculator from "../components/ziyada/ROICalculator.jsx";
import { IconGlobe } from "../components/ziyada/BrandIcons.jsx";
import useSEO from "@/lib/useSEO";
import { trackEvent } from "@/lib/analytics";

const DATA = {
  ar: {
    icon: IconGlobe,
    tag: "أصول رقمية",
    title: "المواقع الذكية والمنصات الرقمية",
    desc: "الموقع المفروض ما يكون بس واجهة حلوة. المفروض يجمع لك عملاء، يسجّل بياناتهم، ويرتبط بنظامك. حنا نبني مواقع ومنصات رقمية مو بس حلوة بالشكل — مربوطة بإدارة العملاء والتقارير والأتمتة.",
    scope: [
      "مواقع ويب ذكية مرتبطة بالأنظمة",
      "صفحات هبوط للحملات والعروض",
      "بوابات خدمة وتطبيقات ويب",
      "ربط الأنظمة الحالية والبيانات",
      "أنظمة رقمية قابلة للتوسع",
      "تجهيز الموقع للإطلاق والتشغيل"
    ],
    features: [
      "واجهة مستخدم حديثة وسهلة",
      "سرعة تحميل عالية جداً",
      "أمان عالي مع تشفير SSL",
      "SEO محسّن من البداية",
      "تكامل مع CRM والأتمتة",
      "استجابة كاملة لكل الأجهزة (Mobile-First)"
    ],
    results: ["أساس رقمي أقوى", "رحلة عميل أفضل", "تكامل أعلى مع الأنظمة", "أصول رقمية أكثر فايدة", "مرونة أكبر"],
    case: {
      who: "شركة عقارية متوسطة تبي تحضير رقمي متكامل",
      what: "بوابة عقارية ذكية مرتبطة بـ CRM مع خريطة، بحث متقدم، وأتمتة الحجوزات",
      when: "3 أشهر من التطوير والتجهيز",
      where: "المملكة العربية السعودية",
      why: "زيادة البيعات الرقمية والتواصل المباشر مع المشترين — الموقع صار يجيب عملاء بدون ما أحد يسوق له"
    }
  },
  en: {
    icon: IconGlobe,
    tag: "Digital Assets",
    title: "Smart Websites & Digital Platforms",
    desc: "A website shouldn't just look good — it should collect leads, log data, and connect to your systems. We build websites and digital platforms that are tied to CRM, analytics, and automation.",
    scope: [
      "Smart websites connected to systems",
      "Campaign and offer landing pages",
      "Service portals and web applications",
      "Integration with existing systems and data",
      "Scalable digital systems",
      "Launch preparation and deployment"
    ],
    features: [
      "Modern, easy-to-use interface",
      "Ultra-fast loading speeds",
      "High security with SSL encryption",
      "SEO optimized from the start",
      "CRM and automation integration",
      "Fully responsive across all devices (Mobile-First)"
    ],
    results: ["Stronger digital foundation", "Better customer journey", "Higher system integration", "More useful digital assets", "Greater flexibility"],
    case: {
      who: "Mid-sized real estate company seeking full digital transformation",
      what: "Smart real estate portal connected to CRM with maps, advanced search, and automated bookings",
      when: "3 months of development and setup",
      where: "Saudi Arabia",
      why: "Increased digital sales and direct buyer communication — the site now generates leads on autopilot"
    }
  }
};

export default function ServiceWebDev() {
  const { lang } = useOutletContext();
  useSEO({ title: "المواقع الذكية والمنصات الرقمية — زيادة سيستم", titleEn: "Smart Websites & Digital Platforms", description: "مواقع مربوطة بإدارة العملاء والأتمتة مو بس واجهة حلوة", path: "/Services/web-development", keywords: "تطوير مواقع, منصات رقمية, مواقع ذكية, زيادة سيستم", schema: { "@context": "https://schema.org", "@type": "Service", name: "Smart Websites & Digital Platforms", provider: { "@type": "Organization", name: "Ziyada" }, description: "Websites and digital platforms connected to CRM, analytics, and automation systems" } });
  useEffect(() => { trackEvent('service_view', { service: 'web-development' }); }, []);
  return (
    <>
      <ServiceDetailPage data={DATA[lang] || DATA.ar} lang={lang} />
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px" }}>
        <ROICalculator lang={lang} />
      </div>
    </>
  );
}
