import { useState, useCallback } from 'react';

export const translations = {
  ar: {
    nav: { home: 'الرئيسية', why: 'لماذا زيادة', services: 'خدماتنا', about: 'من نحن', cases: 'قصص النجاح', blog: 'المدونة', contact: 'تواصل', admin: 'لوحة التحكم' },
    hero: {
      title: 'أنظمة نمو متكاملة',
      subtitle: 'نساعدك في بناء منظومة متكاملة تربط التسويق بالمبيعات بالنتائج. منهجيات تنفيذية دقيقة مبنية على الخبرة العملية.',
      trust: 'نطبق منهجيات مجربة — لا شعارات رنانة — نتائج حقيقية'
    },
    cta: { book: 'احجز استشارة', meeting: 'احجز جلسة استراتيجية', proposal: 'اطلب عرض سعر' },
    services: {
      title: 'حلولنا العملية',
      intro: 'نقدم حلولاً عملية تشمل تصميم الأنظمة التشغيلية، تطوير البنية الرقمية، وبناء أنظمة البيانات.',
      items: [
        { icon: '🎯', title: 'استراتيجية النمو', desc: 'نبني خارطة طريق واضحة لنمو أعمالك بناءً على بيانات حقيقية.' },
        { icon: '🔄', title: 'مسارات التحويل', desc: 'تصميم وتحسين مسارات المبيعات لزيادة معدلات التحويل.' },
        { icon: '🤝', title: 'تصميم CRM', desc: 'بناء وتخصيص أنظمة إدارة علاقات العملاء لتناسب احتياجاتك.' },
        { icon: '📊', title: 'إدارة الإعلانات', desc: 'حملات إعلانية مدروسة على جميع المنصات بعائد استثمار محسوب.' },
        { icon: '📈', title: 'تحليل البيانات', desc: 'لوحات تحكم ذكية تحول بياناتك إلى قرارات استراتيجية.' },
        { icon: '⚡', title: 'أتمتة العمليات', desc: 'أتمتة المهام المتكررة لتحرير فريقك للعمل الاستراتيجي.' }
      ]
    },
    about: {
      title: 'من نحن',
      p1: 'زيادة للأنظمة المتقدمة هي شركة متخصصة في تصميم وبناء أنظمة النمو المتكاملة للشركات الطموحة.',
      p2: 'نجمع بين الخبرة التشغيلية العميقة والتقنيات الحديثة لنقدم حلولاً عملية قابلة للتنفيذ والقياس.',
      p3: 'فريقنا يضم خبراء في التسويق الرقمي، تحليل البيانات، أتمتة العمليات، وتصميم تجربة العميل.',
      vision_title: 'رؤيتنا',
      vision_desc: 'أن نكون الشريك الاستراتيجي المفضل للشركات العربية الطموحة في رحلة نموها الرقمي.',
      method_title: 'منهجيتنا',
      method_desc: 'نعتمد منهجية "النظام أولاً" — ننظر إلى عملك ككل قبل أن نقترح أي حل، مما يضمن تناسق جميع المكونات وتحقيق النتائج المرجوة.'
    },
    why: {
      title: 'لماذا زيادة؟',
      intro: 'نحن لا نبيع خدمات — نبني أنظمة. الفرق جوهري.',
      accreditations_title: 'الاعتمادات المهنية',
      accreditations: ['HubSpot Certified Partner', 'Google Ads Certified', 'Meta Business Partner', 'Salesforce Consulting'],
      capabilities_title: 'قدراتنا التخصصية',
      capabilities: ['استراتيجية النمو الكاملة', 'تصميم مسارات المبيعات', 'أتمتة CRM والتسويق', 'تحليل البيانات والتقارير', 'إدارة الإعلانات المدفوعة'],
      operational_title: 'قدراتنا التشغيلية',
      operational: ['فريق متكامل من 8+ متخصصين', 'تسليم خلال 30 يوماً', 'دعم مستمر بعد التسليم', 'تقارير أسبوعية شفافة'],
      unique_title: 'ما يميزنا',
      unique: ['نفهم السوق العربي', 'ننفذ بدلاً من أن نستشير فقط', 'نقيس كل شيء', 'نبني معك لا لك'],
      conclusion: 'إذا كنت جاداً في النمو، فنحن جاهزون للعمل.'
    },
    meeting: { title: 'احجز جلسة استراتيجية', subtitle: 'جلسة مجانية لمدة 45 دقيقة مع خبرائنا' },
    proposal: { title: 'طلب عرض سعر' },
    contact: { title: 'تواصل معنا', desc: 'للاستفسارات العامة، يرجى ملء النموذج أدناه.' },
    form: {
      name: 'الاسم الكامل', company: 'اسم الشركة', email: 'البريد الإلكتروني للعمل',
      phone: 'رقم الهاتف', size: 'حجم الشركة', industry: 'القطاع',
      challenge: 'ما هو التحدي الرئيسي الذي تواجهه؟', budget: 'الميزانية المتوقعة',
      timeline: 'الإطار الزمني', services_needed: 'الخدمات المطلوبة',
      consent: 'أوافق على سياسة الخصوصية والتواصل معي.',
      submit_meeting: 'تأكيد الحجز', submit_proposal: 'إرسال الطلب', submit_contact: 'إرسال',
      date: 'اختر تاريخ الجلسة', time: 'اختر الوقت'
    },
    thanks: { title: 'شكراً لك!', msg: 'تم استلام طلبك بنجاح. سنتواصل معك قريباً.' },
    blog: { title: 'المدونة', subtitle: 'أفكار وتحليلات من فريق زيادة', read_more: 'اقرأ المزيد' },
    cases: { title: 'قصص النجاح', subtitle: 'نتائج حقيقية لعملاء حقيقيين' },
    footer: { desc: 'تصميم وبناء الأنظمة التشغيلية والرقمية للشركات الطموحة.', links: 'روابط', legal: 'قانوني', rights: 'جميع الحقوق محفوظة' },
    loading: 'جاري التحميل...', error: 'حدث خطأ', success: 'تم بنجاح'
  },
  en: {
    nav: { home: 'Home', why: 'Why Ziyada', services: 'Services', about: 'About', cases: 'Case Studies', blog: 'Blog', contact: 'Contact', admin: 'Dashboard' },
    hero: {
      title: 'Integrated Growth Systems',
      subtitle: 'We help you build a complete system connecting marketing, sales, and results. Precise execution methodologies built on real-world experience.',
      trust: 'Proven methodologies — no buzzwords — real results'
    },
    cta: { book: 'Book a Consultation', meeting: 'Book a Strategy Session', proposal: 'Request a Proposal' },
    services: {
      title: 'Our Practical Solutions',
      intro: 'We offer practical solutions including operational system design, digital infrastructure development, and data system building.',
      items: [
        { icon: '🎯', title: 'Growth Strategy', desc: 'We build a clear roadmap for your business growth based on real data.' },
        { icon: '🔄', title: 'Conversion Funnels', desc: 'Design and optimize sales funnels to increase conversion rates.' },
        { icon: '🤝', title: 'CRM Design', desc: 'Build and customize CRM systems tailored to your needs.' },
        { icon: '📊', title: 'Ads Management', desc: 'Strategic advertising campaigns across all platforms with measured ROI.' },
        { icon: '📈', title: 'Data Analytics', desc: 'Smart dashboards that turn your data into strategic decisions.' },
        { icon: '⚡', title: 'Process Automation', desc: 'Automate repetitive tasks to free your team for strategic work.' }
      ]
    },
    about: {
      title: 'About Us',
      p1: 'Ziyada Advanced Systems specializes in designing and building integrated growth systems for ambitious companies.',
      p2: 'We combine deep operational expertise with modern technologies to deliver practical, measurable solutions.',
      p3: 'Our team includes experts in digital marketing, data analytics, process automation, and customer experience design.',
      vision_title: 'Our Vision',
      vision_desc: 'To be the preferred strategic partner for ambitious Arab companies on their digital growth journey.',
      method_title: 'Our Methodology',
      method_desc: 'We follow a "System First" approach — we look at your business as a whole before proposing any solution, ensuring all components align and results are achieved.'
    },
    why: {
      title: 'Why Ziyada?',
      intro: "We don't sell services — we build systems. The difference is fundamental.",
      accreditations_title: 'Professional Certifications',
      accreditations: ['HubSpot Certified Partner', 'Google Ads Certified', 'Meta Business Partner', 'Salesforce Consulting'],
      capabilities_title: 'Specialized Capabilities',
      capabilities: ['Full Growth Strategy', 'Sales Funnel Design', 'CRM & Marketing Automation', 'Data Analytics & Reporting', 'Paid Advertising Management'],
      operational_title: 'Operational Capabilities',
      operational: ['Integrated team of 8+ specialists', '30-day delivery timeline', 'Ongoing post-delivery support', 'Transparent weekly reports'],
      unique_title: 'What Sets Us Apart',
      unique: ['We understand the Arab market', 'We execute, not just consult', 'We measure everything', 'We build with you, not for you'],
      conclusion: "If you're serious about growth, we're ready to work."
    },
    meeting: { title: 'Book a Strategy Session', subtitle: 'Free 45-minute session with our experts' },
    proposal: { title: 'Request a Proposal' },
    contact: { title: 'Contact Us', desc: 'For general inquiries, please fill the form below.' },
    form: {
      name: 'Full Name', company: 'Company Name', email: 'Work Email',
      phone: 'Phone Number', size: 'Company Size', industry: 'Industry',
      challenge: 'What is your main challenge?', budget: 'Expected Budget',
      timeline: 'Timeline', services_needed: 'Services Needed',
      consent: 'I agree to the privacy policy and to be contacted.',
      submit_meeting: 'Confirm Booking', submit_proposal: 'Send Request', submit_contact: 'Send',
      date: 'Choose session date', time: 'Choose time'
    },
    thanks: { title: 'Thank You!', msg: 'Your request was received successfully. We will contact you shortly.' },
    blog: { title: 'Blog', subtitle: 'Insights and analysis from the Ziyada team', read_more: 'Read More' },
    cases: { title: 'Case Studies', subtitle: 'Real results for real clients' },
    footer: { desc: 'Designing and building operational and digital systems for ambitious companies.', links: 'Links', legal: 'Legal', rights: 'All Rights Reserved' },
    loading: 'Loading...', error: 'An error occurred', success: 'Success'
  }
};

export function useTranslation() {
  const [lang, setLang] = useState(() => localStorage.getItem('ziyada_lang') || 'ar');
  const t = translations[lang];
  const isRTL = lang === 'ar';

  const toggleLang = useCallback(() => {
    const newLang = lang === 'ar' ? 'en' : 'ar';
    setLang(newLang);
    localStorage.setItem('ziyada_lang', newLang);
    document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = newLang;
  }, [lang]);

  return { lang, t, isRTL, toggleLang };
}