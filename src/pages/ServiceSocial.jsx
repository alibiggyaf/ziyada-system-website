import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import ServiceDetailPage from "../components/ziyada/ServiceDetailPage.jsx";
import ROICalculator from "../components/ziyada/ROICalculator.jsx";
import { IconShare } from "../components/ziyada/BrandIcons.jsx";
import useSEO from "@/lib/useSEO";
import { trackEvent } from "@/lib/analytics";

const DATA = {
  ar: {
    icon: IconShare,
    tag: "حضور مميز",
    title: "أنظمة المحتوى ووسائل التواصل",
    desc: "وسائل التواصل بدون نظام واضح تتحول لجهد متفرّق — تنشر بدون ما تعرف وش يشتغل ووش لا. حنا نبني لك منظومة محتوى واضحة من الاستراتيجية للإنتاج للنشر للتقارير، عشان حضورك الرقمي يخدم أهدافك التجارية فعلاً.",
    scope: [
      "استراتيجية المحتوى والرسائل الرئيسية",
      "إنتاج المحتوى والتصميم",
      "إنتاج فيديو ومحتوى إبداعي بالذكاء الاصطناعي",
      "النشر وإدارة المجتمع",
      "أنظمة تشغيل وسائل التواصل للفرق",
      "لوحات متابعة وتقارير آلية للإدارة",
      "تحسين مستمر لأداء المحتوى"
    ],
    features: [
      "محتوى موجّه لجمهورك المثالي",
      "تصميم يعكس هوية علامتك",
      "نشر منتظم على كل المنصات",
      "رد سريع على الجمهور",
      "إنتاج إبداعي بالذكاء الاصطناعي",
      "تقارير نمو واضحة للإدارة"
    ],
    results: ["حضور أقوى للعلامة", "تنظيم أفضل للمحتوى", "وضوح أكبر للإدارة", "ارتباط أوضح بالأهداف التجارية", "تطوير مستمر"],
    case: {
      who: "مكتب عقاري ناشئ يبي يبني حضور رقمي قوي في جدة",
      what: "إدارة Instagram + LinkedIn مع 20 منشور شهري، تصاميم احترافية، واستراتيجية محتوى تعليمي",
      when: "بدأنا من الصفر ووصلنا 5,000 متابع في 4 أشهر",
      where: "Instagram + LinkedIn + إنتاج إبداعي بالذكاء الاصطناعي",
      why: "المكتب كان يعتمد على الإحالات فقط — المحتوى الرقمي صار مصدر مستقل للعملاء"
    }
  },
  en: {
    icon: IconShare,
    tag: "Distinctive Presence",
    title: "Content & Social Media Systems",
    desc: "Social media without a clear system becomes scattered effort. We build a complete content ecosystem from strategy to production to publishing to reports, so your digital presence truly serves your business goals.",
    scope: [
      "Content strategy and key messaging",
      "Content production and design",
      "AI-powered video and creative production",
      "Publishing and community management",
      "Social media operating systems for teams",
      "Automated dashboards and reports for management",
      "Continuous content performance optimization"
    ],
    features: [
      "Content targeted to your ideal audience",
      "Design reflecting your brand identity",
      "Regular publishing across all platforms",
      "Fast audience response",
      "AI-powered creative production",
      "Clear growth reports for management"
    ],
    results: ["Stronger brand presence", "Better content organization", "Greater clarity for management", "Clearer tie to business goals", "Continuous improvement"],
    case: {
      who: "Emerging real estate office building a strong digital presence in Jeddah",
      what: "Instagram + LinkedIn management with 20 posts/month, professional designs, and educational content strategy",
      when: "Started from zero and reached 5,000 followers in 4 months",
      where: "Instagram + LinkedIn + AI-powered creative production",
      why: "The office relied only on referrals — digital content became an independent client source"
    }
  }
};

export default function ServiceSocial() {
  const { lang } = useOutletContext();
  useSEO({ title: "أنظمة المحتوى ووسائل التواصل — زيادة سيستم", titleEn: "Content & Social Media Systems", description: "منظومة محتوى واضحة من الاستراتيجية للنشر للتقارير", path: "/Services/social-media", keywords: "محتوى, وسائل تواصل, إدارة حسابات, زيادة سيستم", schema: { "@context": "https://schema.org", "@type": "Service", name: "Content & Social Media Systems", provider: { "@type": "Organization", name: "Ziyada" }, description: "Complete content ecosystem from strategy to production to publishing and reporting" } });
  useEffect(() => { trackEvent('service_view', { service: 'social-media' }); }, []);
  return (
    <>
      <ServiceDetailPage data={DATA[lang] || DATA.ar} lang={lang} />
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px" }}>
        <ROICalculator lang={lang} />
      </div>
    </>
  );
}
