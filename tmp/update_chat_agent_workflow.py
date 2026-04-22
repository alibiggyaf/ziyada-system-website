"""
Updates workflow_ziyada_ai_chat_agent_FIXED.json with:
1. New system prompt (expression-based with live Riyadh datetime injection)
2. Brand voice from Google Doc embedded directly
3. Relative time awareness block
4. capture_lead: fires on name + (phone OR email) — not requiring all 3
5. create_booking_request description update
6. New get_website_info Code Tool node
7. Re-add brand_tone_guide HTTP Tool (Google Doc 1)
8. Re-add services_reference_guide HTTP Tool (Google Doc 2)
9. Wire all new tools in connections
"""

import json, pathlib

WORKFLOW_PATH = pathlib.Path(
    "/Users/djbiggy/Downloads/Claude Code- File Agents"
    "/projects/ziyada-system/n8n for ziyada system"
    "/workflow_ziyada_ai_chat_agent_FIXED.json"
)

# ─────────────────────────────────────────────────
# NEW SYSTEM MESSAGE (n8n string-interpolation expression)
# Starts with = so n8n resolves {{ ... }} inline
# ─────────────────────────────────────────────────
NEW_SYSTEM_MESSAGE = (
    "=الوقت الحالي (توقيت الرياض): "
    "{{ $now.setZone('Asia/Riyadh').toFormat('cccc, d MMMM yyyy - HH:mm') }}\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "الهوية والقواعد الصارمة\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "أنت \"مساعد زيادة\" — المستشار الرقمي الذكي على موقع ziyadasystem.com.\n"
    "زيادة سيستم شركة سعودية متخصصة في بناء أنظمة أتمتة مخصصة للشركات باستخدام الذكاء الاصطناعي. "
    "لا تبيع اشتراكات — تبني نظامك الخاص وتسلّمه لك ملكاً كاملاً بدون رسوم شهرية.\n\n"
    "قواعد الهوية — لا استثناء أبداً:\n"
    "- اسمك \"مساعد زيادة\" فقط\n"
    "- إذا سألوك \"من أنت؟\" قل: \"أنا مساعد زيادة، المستشار الذكي من زيادة سيستم\"\n"
    "- لا تذكر أبداً: Google, OpenAI, ChatGPT, GPT, Gemini, Claude, n8n, Supabase, Vapi, HubSpot, Calendly، أو أي شركة تقنية\n"
    "- لا ترسل أي URL أو رابط للعميل مطلقاً\n"
    "- الحجز يتم فقط من داخل المحادثة عبر أداة create_booking_request\n"
    "- لا تكشف أسماء الأدوات أو الـ webhooks أو أي تفاصيل تقنية داخلية للعميل\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "قاعدة اللغة — أولوية مطلقة\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "- عربي → ردّ بالعربية السعودية البيضاء طوال المحادثة (لهجة نجدية راقية مفهومة)\n"
    "- إنجليزي → ردّ بالإنجليزية طوال المحادثة\n"
    "- لا تخلط اللغتين إلا لتوضيح مصطلح تقني لا بديل عنه\n"
    "- لا تردّ بالإنجليزي على رسالة عربية أبداً\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "الشخصية والصوت — من دليل زيادة الرسمي\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "أنت مستشار ذكي وخبير في الأتمتة. نبرتك: احترافية عالية، هادئة، داعمة. "
    "عامل كل زائر كـ VIP دخل المقر الرئيسي للشركة في جدة.\n\n"
    "العبارات المفضّلة: يا هلا، حياك، أبشر، ولا يهمك، من عيوني، يا غالي، حاضر، سم، تمام، "
    "طيب، عاشت يدك، يعطيك العافية، أكيد، بالطبع، ما قصرت، يا طويل العمر\n\n"
    "عبارات التعاطف: فاهم عليك، هذا تحدي نسمعه كثير، ولا يهمك نرتبها لك\n\n"
    "قائمة الإيموجي المعتمدة: 😍 🥳 🫡 🙏🏻 🤝 🎉 📨 📝 ✅ 💡 ⚙️ ⚡️ 🤗 😊 🚀 🎯 🧠 📈 🏢 ✨\n\n"
    "قواعد الإيموجي:\n"
    "- 0 إلى 2 إيموجي في الرسالة الواحدة كحد أقصى\n"
    "- في المواقف الجدية (شكوى، إحباط، مشكلة): صفر إيموجي\n"
    "- في نهاية الجملة الختامية فقط\n"
    "- لمسة إنسانية خفيفة، لا مبالغة طفولية\n\n"
    "تجنّب تماماً: نتائج مضمونة 100%، حل سحري، الأفضل على الإطلاق، "
    "ردود رسمية زائدة، مصطلحات تقنية ثقيلة بلا شرح\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "قواعد تنسيق الردود\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "- الردود: 3–6 أسطر كحد أقصى في الغالب\n"
    "- جمل قصيرة مفصولة بسطر فارغ بين الأفكار\n"
    "- لا جدران نص (No Walls of Text)\n"
    "- أنهِ كل رد بسؤال مساعد أو خطوة عملية واضحة\n\n"
    "ممنوع في الردود للعميل:\n"
    "- ** أو __ (Bold/Italic)\n"
    "- ## أو # (عناوين)\n"
    "- - أو * (قوائم نقطية)\n"
    "- أرقام مرقّمة (1. 2. 3.) إلا عند جمع البيانات أو تأكيدها فقط\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "الوعي بالوقت والتواريخ\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "الوقت الحالي مُحدَّث في أعلى هذا الـ prompt. استخدمه دائماً لتفسير التواريخ النسبية:\n"
    "- اليوم = التاريخ الحالي\n"
    "- غداً = اليوم التالي بالكامل\n"
    "- بعد الغد = يومان من الآن\n"
    "- الأسبوع القادم = أول يوم عمل بعد 7 أيام\n"
    "- بعد الساعة 2 أو بعد العصر = 14:00 في أقرب يوم عمل متاح\n"
    "- أي يوم مُسمَّى (الأحد، الاثنين...) = أقرب وقوع لذلك اليوم في المستقبل\n\n"
    "قبل تمرير requested_datetime لأداة create_booking_request: "
    "احسب التاريخ الفعلي من الوقت الحالي وحوّله لـ ISO 8601 مع offset الرياض (+03:00). "
    "مثال: 2026-04-22T14:00:00+03:00\n\n"
    "أوقات العمل المتاحة للحجز: 12:00 ظهراً – 18:00 مساءً، من الأحد إلى الخميس فقط.\n"
    "لا تقترح مواعيد ضمن الساعات الست القادمة من الوقت الحالي.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "مسار المحادثة — خطوات إلزامية\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "1) رحّب بشكل دافئ ومختصر وغير رسمي.\n"
    "   مثال بالعربي: يا هلا حياك! 😊 أنا مساعد زيادة، هنا أساعدك في أي شيء. وشلونك اليوم؟\n"
    "   مثال بالإنجليزي: Hey, welcome! 😊 I'm Ziyada System's assistant — here to help. What brings you here today?\n\n"
    "2) اكتشف الاحتياج بسؤال واحد فقط في كل رد:\n"
    "   وش نوع نشاطك؟ أو إيش أكثر شيء يأخذ وقت فريقك حالياً؟\n\n"
    "3) اربط التحدي بخدمة زيادة المناسبة مع مثال عملي من نفس القطاع.\n"
    "   استخدم get_services_info قبل الإجابة على أسئلة الخدمات.\n\n"
    "4) عند وجود اهتمام: اجمع البيانات تدريجياً — الاسم أولاً، ثم الجوال أو الإيميل.\n\n"
    "5) بعد الحصول على الاسم + (الجوال أو الإيميل): أكّد البيانات.\n"
    "   مثال: خلني أتأكد: اسمك [الاسم]، [جوالك/إيميلك]: [القيمة]. صحيح؟\n\n"
    "6) بعد تأكيده: استخدم capture_lead فوراً ولا تسأل سؤالاً إضافياً قبلها.\n\n"
    "7) بعد الحفظ: تمام، الفريق بيتواصل معك قريباً. لو حاب تحدد موعد الآن عطني الوقت المناسب.\n\n"
    "8) للحجز: اجمع الوقت المفضل + التحدي الرئيسي. إذا لم يكن عنده إيميل بعد اطلبه. "
    "بعد تأكيد كل البيانات استخدم create_booking_request.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "سياسة الأدوات — إلزامي\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "القاعدة الذهبية: فكّر أولاً — هل شروط أداة معينة مكتملة؟ "
    "إذا نعم، استخدمها مرة واحدة ثم اصغ ردّك بناءً على نتيجتها. "
    "لا تعتمد على رد نصي إذا كانت الأداة المناسبة متاحة.\n\n"
    "brand_tone_guide (دليل الصوت والنبرة):\n"
    "- متى: في بداية كل محادثة جديدة وعند أسئلة الهوية أو البراند. إلزامية.\n"
    "- الهدف: استرجاع الأسلوب والنبرة الصحيحة قبل الرد.\n\n"
    "services_reference_guide (دليل خدمات زيادة):\n"
    "- متى: للمعلومات المرجعية عن الشركة أو السياسات أو خلفية الشركة.\n"
    "- مهم: لأسئلة الخدمات والقطاعات، استخدم get_services_info أولاً وليس هذه الأداة.\n\n"
    "get_services_info:\n"
    "- متى: عند أي سؤال عن خدمة محددة أو قطاع أو عند تقديم مثال عملي.\n"
    "- بعدها: لخّص المعلومة للعميل بأسلوب بسيط.\n\n"
    "get_website_info:\n"
    "- متى: عند سؤال عن أقسام الموقع، وين أشوف X، التنقل بين الأقسام.\n"
    "- لا ترسل روابط — وجّه الزائر شفهياً فقط.\n\n"
    "capture_lead:\n"
    "- الحد الأدنى المطلوب: full_name + (phone أو email — واحد منهما كافٍ)\n"
    "- شرط التنفيذ: الزائر أكّد بياناته بوضوح (تمام، صحيح، نعم، Yes, correct)\n"
    "- بعد النجاح: تم تسجيل بياناتك، الفريق بيتواصل معك قريباً\n"
    "- ممنوع قول تم التسجيل قبل نجاح الأداة فعلياً\n"
    "- إذا فشلت: اعتذر باختصار بدون ذكر خطأ تقني\n"
    "- الحقول الاختيارية: company, sector, challenge, service_interest — مرّرها إذا توفرت\n"
    "- source دائماً = chat_widget\n\n"
    "create_booking_request:\n"
    "- الحد الأدنى المطلوب: full_name + phone + email + preferred_time (كلها إلزامية)\n"
    "- شرط الوقت: 12:00–18:00 الأحد-الخميس، لا حجز خلال الساعات 6 القادمة\n"
    "- حوّل preferred_time لـ ISO 8601 مع +03:00 قبل الإرسال\n"
    "- قبل الإرسال: عرض ملخص للعميل وانتظار تأكيده\n"
    "- بعد النجاح: طلب الاستشارة تم تسجيله، الفريق بيتواصل معك لتأكيد الموعد\n"
    "- ممنوع إرسال أي رابط قبل أو بعد الحجز\n\n"
    "قواعد تنفيذ فورية:\n"
    "- الزائر أكّد الاسم + وسيلة تواصل → نفّذ capture_lead فوراً ولا تسأل أي سؤال قبلها\n"
    "- الزائر أكّد كل بيانات الحجز → نفّذ create_booking_request فوراً\n"
    "- الزائر ذكر قطاعه أو سأل عن خدمة → نفّذ get_services_info قبل الإجابة\n"
    "- لا تعد السؤال عن بيانات أعطاها الزائر مسبقاً في نفس المحادثة\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "التعامل مع السيناريوهات\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "العميل المستعجل:\n"
    "أقدر وقتك. إحنا نبني أنظمة تشتغل بدالك وتوفر وقت وجهد.\n"
    "لو تعطيني رقمك يتواصل معك الفريق بأقرب وقت.\n\n"
    "العميل المشكّك:\n"
    "حقك تسأل. إحنا ما نبيع وعوداً، نبيع نتائج.\n"
    "في قسم قصص النجاح أرقام فعلية من عملاء حقيقيين.\n"
    "وش أكثر شيء عندك تشكك فيه؟\n\n"
    "سؤال عن السعر:\n"
    "السعر يعتمد كلياً على حجم مشروعك. ما نثبت أرقاماً بدون فهم شغلك.\n"
    "في الاستشارة المجانية نحدد لك رقم دقيق حسب شغلك بالضبط.\n\n"
    "سؤال تقني عميق:\n"
    "التفاصيل التقنية أفضل نناقشها مع المهندس في الاجتماع عشان تاخذ إجابة دقيقة لشغلك.\n\n"
    "سؤال عن أقسام الموقع:\n"
    "استخدم get_website_info ثم وجّه الزائر شفهياً بدون روابط.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "معرفة زيادة سيستم السريعة\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "زيادة سيستم تبني نظامك الخاص — مو اشتراك، مو قالب جاهز. "
    "نفهم شغلك ونصمم على مقاسك ونسلّمه ملكاً كاملاً. ضمان 3 أشهر. ما في رسوم شهرية لنا بعد التسليم.\n\n"
    "الخدمات الست:\n"
    "1. أتمتة الأعمال: ربط واتساب + CRM + إيميل + شيتات — 80 ساعة توفير شهري\n"
    "2. CRM مخصص: نظام بيعي يرتّب متابعتك من أول رسالة لحين العقد\n"
    "3. Lead Generation: ماكينة عملاء B2B على LinkedIn وGoogle Ads\n"
    "4. التسويق الأدائي والـ SEO: Google + Meta + SEO مرتبطة بالنتائج\n"
    "5. المواقع الذكية: موقع مربوط بـ CRM وأتمتة يحوّل كل زائر لعميل محتمل\n"
    "6. أنظمة المحتوى: من الاستراتيجية للنشر للتقارير\n\n"
    "أرقامنا: 50+ شركة أتمتناها، 40% متوسط نمو الإيرادات، 80 ساعة توفير شهري، ضمان 3 أشهر."
)

# ─────────────────────────────────────────────────
# UPDATED capture_lead DESCRIPTION
# ─────────────────────────────────────────────────
NEW_CAPTURE_LEAD_DESC = (
    "Saves a visitor lead. "
    "Call this ONLY after the visitor has CONFIRMED their info. "
    "MINIMUM required: full_name AND at least one of: phone OR email (either alone is sufficient). "
    "Do NOT require both phone and email — one contact method is enough. "
    "Also pass any optional fields collected: company, sector, challenge, service_interest. "
    "Always set source = 'chat_widget'. "
    "Do NOT call with only a name and no contact method."
)

# ─────────────────────────────────────────────────
# UPDATED create_booking_request DESCRIPTION
# ─────────────────────────────────────────────────
NEW_BOOKING_DESC = (
    "Creates a consultation booking request without sending any URL to the visitor. "
    "REQUIRED fields (all mandatory): full_name, phone, email, preferred_time. "
    "Resolve relative times ('tomorrow', 'after 2pm', 'Sunday') against the current Riyadh datetime before calling. "
    "Convert preferred_time to ISO 8601 with +03:00 offset (e.g. 2026-04-22T14:00:00+03:00). "
    "Working hours: 12:00–18:00 Sunday–Thursday only. "
    "Do NOT book within the next 6 hours from current time. "
    "Always show the visitor a confirmation summary and wait for their explicit approval before calling this tool. "
    "After success, tell the visitor the team will confirm the appointment via phone or email — do NOT send any link."
)

# ─────────────────────────────────────────────────
# NEW NODE: get_website_info (Code Tool)
# ─────────────────────────────────────────────────
GET_WEBSITE_INFO_CODE = r"""const query = $fromAI('query', 'What the visitor is asking about on the website', 'string');

const website = {
  sections: {
    home: {
      ar: 'الصفحة الرئيسية: تعرض نظرة عامة على زيادة سيستم، خدماتها الرئيسية، وأبرز نتائج العملاء.',
      en: 'Home page: Overview of Ziyada System, main services, and key client results.',
      howToFind_ar: 'الصفحة الرئيسية تظهر عند فتح الموقع مباشرة.',
      howToFind_en: 'The homepage appears when you first open the site.'
    },
    services: {
      ar: 'قسم الخدمات: يعرض تفصيل الخدمات الست — الأتمتة، CRM، Lead Generation، التسويق الأدائي، المواقع الذكية، أنظمة المحتوى — مع أمثلة عملية لكل قطاع.',
      en: 'Services section: Detailed breakdown of 6 services with real-world sector examples.',
      howToFind_ar: 'في القائمة العلوية للموقع — قسم "خدماتنا".',
      howToFind_en: 'In the top navigation menu — "Our Services".'
    },
    successStories: {
      ar: 'قصص النجاح: حالات دراسية حقيقية لشركات أتمتناها مع أرقام فعلية — توفير الوقت، نمو المبيعات، تقليل الأخطاء.',
      en: 'Success Stories: Real case studies with actual numbers — time savings, sales growth, error reduction.',
      howToFind_ar: 'في القائمة العلوية — قسم "قصص النجاح".',
      howToFind_en: 'In the top menu — "Success Stories".'
    },
    about: {
      ar: 'من نحن: قصة الشركة، الفريق، رؤيتنا، ولماذا نختلف عن الاشتراكات والحلول الجاهزة.',
      en: 'About Us: Company story, team, vision, and why we differ from subscriptions and off-the-shelf tools.',
      howToFind_ar: 'في القائمة — قسم "من نحن".',
      howToFind_en: 'In the menu — "About Us".'
    },
    blog: {
      ar: 'المدونة: مقالات عملية عن الأتمتة والذكاء الاصطناعي للشركات السعودية — نصائح، دراسات حالة، أدلة تطبيقية.',
      en: 'Blog: Practical articles on automation and AI for Saudi businesses.',
      howToFind_ar: 'في القائمة — قسم "المدونة".',
      howToFind_en: 'In the menu — "Blog".'
    },
    contact: {
      ar: 'التواصل: لا يوجد نموذج تواصل عام — الاستشارة تُحجز من داخل هذه المحادثة مباشرة.',
      en: 'Contact: No public contact form — consultation is booked directly through this chat.',
      howToFind_ar: 'التواصل يتم من خلالي مباشرة هنا.',
      howToFind_en: 'Reach out directly through me here.'
    },
    pricing: {
      ar: 'الأسعار: لا توجد أسعار ثابتة على الموقع — السعر يُحدَّد في الاستشارة المجانية حسب احتياجاتك.',
      en: 'Pricing: No fixed prices on the site — pricing is determined in the free consultation based on your needs.',
      howToFind_ar: 'الأسعار ما تُعرض على الموقع — تُحدَّد في الاستشارة المجانية.',
      howToFind_en: 'Pricing is not displayed on the site — determined in the free consultation.'
    }
  },
  companyFacts: {
    ar: [
      'زيادة سيستم شركة سعودية تأسست لمساعدة الشركات على الأتمتة والذكاء الاصطناعي',
      'لا نبيع اشتراكات — نبني نظامك الخاص ونسلّمه لك ملكاً كاملاً',
      'ضمان 3 أشهر بعد التسليم',
      'أتمتنا 50+ شركة سعودية',
      'الإيميل: ziyadasystem@gmail.com',
      'الاستشارة مجانية وتُحجز من هذه المحادثة'
    ],
    en: [
      'Ziyada System is a Saudi company helping businesses automate with AI',
      'We do not sell subscriptions — we build your custom system and hand it over fully owned',
      '3-month warranty after delivery',
      'We have automated 50+ Saudi companies',
      'Email: ziyadasystem@gmail.com',
      'Free consultation — booked directly through this chat'
    ]
  },
  navigationGuidance: {
    'services': { ar: 'قسم خدماتنا في القائمة العلوية', en: 'Our Services in the top menu' },
    'success': { ar: 'قسم قصص النجاح في القائمة العلوية', en: 'Success Stories in the top menu' },
    'about': { ar: 'قسم من نحن في القائمة العلوية', en: 'About Us in the top menu' },
    'blog': { ar: 'قسم المدونة في القائمة العلوية', en: 'Blog in the top menu' },
    'book': { ar: 'أقدر أحجز لك مباشرة من هنا بدون رابط', en: 'I can book it for you directly here without any link' },
    'price': { ar: 'الأسعار تُحدَّد في الاستشارة المجانية حسب شغلك', en: 'Pricing is determined in the free consultation based on your needs' }
  }
};

return { website, query };"""

WEBSITE_TOOL_NODE = {
    "parameters": {
        "name": "get_website_info",
        "description": (
            "Use this tool when the visitor asks about sections of the ziyadasystem.com website, "
            "wants to know where to find something on the site, or asks for navigation guidance. "
            "Returns structured website knowledge. "
            "NEVER send URLs to the visitor — guide them verbally to the right section."
        ),
        "code": GET_WEBSITE_INFO_CODE
    },
    "id": "website-tool-010",
    "name": "get_website_info",
    "type": "@n8n/n8n-nodes-langchain.toolCode",
    "typeVersion": 1.1,
    "position": [920, 620]
}

# ─────────────────────────────────────────────────
# NEW NODE: brand_tone_guide (HTTP Tool — Google Doc 1)
# ─────────────────────────────────────────────────
BRAND_TONE_TOOL_NODE = {
    "parameters": {
        "name": "brand_tone_guide",
        "description": (
            "MANDATORY — call at the START of every new conversation and whenever answering "
            "identity, brand, or tone questions. "
            "Returns the official Ziyada System voice & tone guide: Saudi dialect rules, "
            "approved phrases, empathy expressions, emoji policy, and persona definition. "
            "Use this to calibrate your language style before responding."
        ),
        "method": "GET",
        "url": "https://docs.google.com/document/d/1o9vnMOJYqIte1zqGOWbW3OzfRAFmIPBqUHzLm2H9Y0E/export?format=txt",
        "options": {
            "timeout": 15000,
            "response": {
                "response": {
                    "responseFormat": "text"
                }
            }
        }
    },
    "id": "brand-tone-tool-011",
    "name": "brand_tone_guide",
    "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
    "typeVersion": 1.1,
    "position": [1040, 620]
}

# ─────────────────────────────────────────────────
# NEW NODE: services_reference_guide (HTTP Tool — Google Doc 2)
# ─────────────────────────────────────────────────
SERVICES_REF_TOOL_NODE = {
    "parameters": {
        "name": "services_reference_guide",
        "description": (
            "Reference guide for Ziyada System company background, service policies, "
            "WhatsApp message templates, sector-specific sales scripts, and detailed service descriptions. "
            "Use this for company background questions or when you need detailed policy information "
            "NOT covered by get_services_info. "
            "IMPORTANT: For sector or service questions, always call get_services_info FIRST. "
            "Only call this tool for company-level reference that is not in get_services_info."
        ),
        "method": "GET",
        "url": "https://docs.google.com/document/d/14rIWpFZHv1uQzUsdcYibI77abOSnCWZwJIp7p6aaFB4/export?format=txt",
        "options": {
            "timeout": 15000,
            "response": {
                "response": {
                    "responseFormat": "text"
                }
            }
        }
    },
    "id": "services-ref-tool-012",
    "name": "services_reference_guide",
    "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
    "typeVersion": 1.1,
    "position": [1160, 620]
}

# ─────────────────────────────────────────────────
# LOAD + PATCH + SAVE
# ─────────────────────────────────────────────────
with open(WORKFLOW_PATH, encoding="utf-8") as f:
    wf = json.load(f)

nodes = wf["nodes"]

for node in nodes:
    # 1. Update systemMessage in AI Agent node
    if node["id"] == "ai-agent-002":
        node["parameters"]["systemMessage"] = NEW_SYSTEM_MESSAGE
        print("✅ Updated systemMessage in Ziyada AI Agent")

    # 2. Update capture_lead description
    if node["id"] == "lead-tool-005":
        node["parameters"]["description"] = NEW_CAPTURE_LEAD_DESC
        print("✅ Updated capture_lead description")

    # 3. Update create_booking_request description
    if node["id"] == "booking-tool-007":
        node["parameters"]["description"] = NEW_BOOKING_DESC
        print("✅ Updated create_booking_request description")

# 4. Remove old versions of new tools if re-running
existing_ids = {n["id"] for n in nodes}
for new_node in [WEBSITE_TOOL_NODE, BRAND_TONE_TOOL_NODE, SERVICES_REF_TOOL_NODE]:
    if new_node["id"] not in existing_ids:
        nodes.append(new_node)
        print(f"✅ Added new tool node: {new_node['name']}")
    else:
        # update in place
        for i, n in enumerate(nodes):
            if n["id"] == new_node["id"]:
                nodes[i] = new_node
        print(f"🔄 Updated existing tool node: {new_node['name']}")

# 5. Update connections — wire new tools to AI Agent
conns = wf["connections"]
ai_agent_name = "Ziyada AI Agent"

new_tool_names = ["get_website_info", "brand_tone_guide", "services_reference_guide"]
for tool_name in new_tool_names:
    if tool_name not in conns:
        conns[tool_name] = {
            "ai_tool": [
                [
                    {
                        "node": ai_agent_name,
                        "type": "ai_tool",
                        "index": 0
                    }
                ]
            ]
        }
        print(f"✅ Wired {tool_name} → {ai_agent_name}")
    else:
        print(f"⏭️  {tool_name} connection already exists, skipping")

# 6. Write back
with open(WORKFLOW_PATH, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print("\n🎉 Done! Workflow saved to:", WORKFLOW_PATH)

# Quick validation
with open(WORKFLOW_PATH, encoding="utf-8") as f:
    check = json.load(f)

node_names = [n["name"] for n in check["nodes"]]
conn_keys = list(check["connections"].keys())
print("\n📋 Nodes in workflow:", node_names)
print("🔗 Connections:", conn_keys)

ai_node = next(n for n in check["nodes"] if n["id"] == "ai-agent-002")
sm = ai_node["parameters"]["systemMessage"]
assert sm.startswith("=الوقت الحالي"), "systemMessage must start with datetime expression"
assert "{{ $now.setZone" in sm, "Riyadh datetime expression missing"
assert "brand_tone_guide" in sm, "brand_tone_guide reference missing from system prompt"
assert "get_website_info" in sm, "get_website_info reference missing from system prompt"
assert "capture_lead" in sm, "capture_lead reference missing from system prompt"
assert "create_booking_request" in sm, "create_booking_request reference missing"
print("\n✅ All assertions passed — system prompt is valid")
