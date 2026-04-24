import { useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import { ChevronDown } from "lucide-react";
import { useState } from "react";
import useSEO from "@/lib/useSEO";

const C = {
  ar: {
    title: "الأسئلة الشائعة",
    subtitle: "إجابات على أكثر الأسئلة شيوعاً حول خدماتنا",
    cta: "احجز استشارة مجانية",
    faqs: [
      {
        q: "كم تكلفة الخدمات؟",
        a: "التسعير يعتمد على نطاق المشروع والخدمات المطلوبة. نقدم استشارة مجانية أولاً لفهم احتياجاتك وتقديم عرض سعر مخصص."
      },
      {
        q: "كم المدة الزمنية لتنفيذ المشروع؟",
        a: "تختلف المدة حسب نوع الخدمة: أتمتة العمل (3-4 أسابيع)، CRM (4-6 أسابيع)، توليد العملاء (4-8 أسابيع)، تطوير الموقع (6-8 أسابيع)."
      },
      {
        q: "هل تقدمون دعم ما بعد التسليم؟",
        a: "نعم، نقدم 3 أشهر ضمان ما بعد التسليم مع دعم فني شامل وتدريب الفريق."
      },
      {
        q: "ما الفرق بين الأتمتة و CRM؟",
        a: "الأتمتة تركز على تشغيل العمليات تلقائياً (n8n)، بينما CRM يركز على إدارة علاقات العملاء والمبيعات (HubSpot/Zoho)."
      },
      {
        q: "هل تعملون مع شركات صغيرة أم فقط الكبيرة؟",
        a: "نعمل مع جميع أحجام الشركات من الناشئة إلى الشركات الكبرى. كل خدمة قابلة للتطوير حسب احتياجاتك."
      },
      {
        q: "كيف تضمن جودة العمل؟",
        a: "نستخدم أدوات احترافية، متخصصين ذوي خبرة، واختبار شامل قبل التسليم، مع ضمان 3 أشهر."
      },
      {
        q: "هل يمكن تعديل الحل بعد التسليم؟",
        a: "نعم، نوفر دعم تعديلات في فترة الضمان. بعدها يمكن الاستفادة من خدمات الدعم المستمر."
      },
      {
        q: "ما أدوات وتقنيات تستخدمونها؟",
        a: "نستخدم: n8n (أتمتة)، HubSpot/Zoho (CRM)، Google Ads/Meta (إعلانات)، React (تطوير ويب)، وأدوات تحليل متقدمة."
      },
      {
        q: "هل تقدمون استشارات بدون التزام؟",
        a: "نعم! نقدم استشارة مجانية لفهم احتياجاتك وتقديم توصيات بدون التزام."
      },
      {
        q: "كيف أبدأ معكم؟",
        a: "اضغط على 'احجز استشارة مجانية' وحدد موعداً مناسباً. سنناقش احتياجاتك وتقديم حل مخصص."
      }
    ]
  },
  en: {
    title: "Frequently Asked Questions",
    subtitle: "Answers to the most common questions about our services",
    cta: "Book Free Consultation",
    faqs: [
      {
        q: "How much do your services cost?",
        a: "Pricing depends on project scope and required services. We provide a free initial consultation to understand your needs and give a customized quote."
      },
      {
        q: "How long does it take to implement a project?",
        a: "Timeline varies by service: Business Automation (3-4 weeks), CRM (4-6 weeks), Lead Generation (4-8 weeks), Web Development (6-8 weeks)."
      },
      {
        q: "Do you provide post-delivery support?",
        a: "Yes, we offer 3 months post-delivery warranty with comprehensive technical support and team training."
      },
      {
        q: "What's the difference between Automation and CRM?",
        a: "Automation focuses on running processes automatically (n8n), while CRM focuses on customer relationships and sales management (HubSpot/Zoho)."
      },
      {
        q: "Do you work with small companies or only large ones?",
        a: "We work with companies of all sizes from startups to enterprises. Every solution is scalable to your needs."
      },
      {
        q: "How do you ensure work quality?",
        a: "We use professional tools, experienced specialists, comprehensive testing before delivery, and offer a 3-month guarantee."
      },
      {
        q: "Can the solution be modified after delivery?",
        a: "Yes, we provide modifications during the warranty period. After that, you can use our ongoing support services."
      },
      {
        q: "What tools and technologies do you use?",
        a: "We use: n8n (automation), HubSpot/Zoho (CRM), Google Ads/Meta (advertising), React (web development), and advanced analytics tools."
      },
      {
        q: "Do you offer free consultations with no commitment?",
        a: "Yes! We provide a free consultation to understand your needs and give recommendations with no obligation."
      },
      {
        q: "How do I get started?",
        a: "Click on 'Book Free Consultation', choose a convenient time. We'll discuss your needs and provide a customized solution."
      }
    ]
  }
};

export default function FAQ() {
  const { lang } = useOutletContext();
  const c = C[lang] || C.ar;
  const isRTL = lang === "ar";

  const faqSchemaItems = (C.en.faqs || []).map(faq => ({
    "@type": "Question",
    name: faq.q,
    acceptedAnswer: { "@type": "Answer", text: faq.a }
  }));

  useSEO({
    title: "الأسئلة الشائعة — زيادة سيستم",
    titleEn: "FAQ — Ziyada Systems",
    description: "أجوبة لأكثر الأسئلة شيوعاً عن خدمات زيادة سيستم",
    descriptionEn: "Answers to the most common questions about Ziyada Systems services",
    path: "/FAQ",
    schema: {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      name: "Ziyada Systems FAQ",
      mainEntity: faqSchemaItems
    }
  });

  const [openIndex, setOpenIndex] = useState(null);

  return (
    <div dir={isRTL ? "rtl" : "ltr"} style={{ minHeight: "100vh", padding: "80px 24px 60px" }}>
      <div style={{ maxWidth: 900, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 60 }}>
          <div className="section-title-frame" style={{ display: "inline-block", marginBottom: 20 }}>
            <h1 className="gradient-text" style={{ fontSize: "2.2rem", fontWeight: 900, margin: 0 }}>
              {c.title}
            </h1>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem", opacity: 0.85, maxWidth: 600, margin: "0 auto" }}>
            {c.subtitle}
          </p>
        </div>

        {/* FAQs */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 60 }}>
          {c.faqs.map((faq, i) => (
            <div
              key={i}
              className="glass-panel"
              style={{
                padding: 0,
                cursor: "pointer",
                overflow: "hidden",
                transition: "all 0.3s ease"
              }}
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
            >
              {/* Question */}
              <div
                style={{
                  padding: "20px 24px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 16,
                  background: openIndex === i ? "rgba(59,130,246,0.08)" : "transparent",
                  transition: "background 0.3s ease"
                }}
              >
                <h3 style={{ margin: 0, fontWeight: 700, fontSize: "1rem", flex: 1, color: "var(--text-primary)" }}>
                  {faq.q}
                </h3>
                <ChevronDown
                  size={20}
                  style={{
                    color: "var(--accent-primary)",
                    transition: "transform 0.3s ease",
                    transform: openIndex === i ? "rotate(180deg)" : "rotate(0deg)",
                    flexShrink: 0
                  }}
                />
              </div>

              {/* Answer */}
              {openIndex === i && (
                <div
                  style={{
                    padding: "0 24px 20px",
                    borderTop: "1px solid rgba(59,130,246,0.2)",
                    color: "var(--text-secondary)",
                    fontSize: "0.95rem",
                    lineHeight: 1.8,
                    animation: "fadeIn 0.3s ease"
                  }}
                >
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="glass-panel" style={{ padding: 40, textAlign: "center", background: "linear-gradient(135deg, rgba(59,130,246,0.06) 0%, rgba(139,92,246,0.06) 100%)", borderColor: "rgba(124,58,237,0.3)" }}>
          <h2 className="gradient-text" style={{ fontSize: "1.6rem", fontWeight: 900, marginBottom: 12 }}>
            {isRTL ? "لديك المزيد من الأسئلة؟" : "More Questions?"}
          </h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: 28, opacity: 0.85 }}>
            {isRTL ? "تحدث مع فريقنا مباشرة واحصل على إجابات مفصلة." : "Talk to our team directly and get detailed answers."}
          </p>
          <Link to="/BookMeeting">
            <button className="btn-primary-ziyada" style={{ padding: "14px 36px", fontSize: "1rem" }}>
              {c.cta}
            </button>
          </Link>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `}</style>
    </div>
  );
}