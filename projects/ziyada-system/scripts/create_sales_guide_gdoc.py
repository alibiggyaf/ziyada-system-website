#!/usr/bin/env python3
"""
Create professional sales guide Google Document for Ziyada System
Targets: محل العطارة (Spice Shop) & محل العبايات (Abaya Shop)
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


TOKEN_FILE = '/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/token_docs.json'

# Brand colors
C_NAVY = {'red': 15/255, 'green': 23/255, 'blue': 42/255}
C_BLUE = {'red': 37/255, 'green': 99/255, 'blue': 235/255}
C_LIGHT_BLUE = {'red': 59/255, 'green': 130/255, 'blue': 246/255}
C_MUTED = {'red': 51/255, 'green': 65/255, 'blue': 85/255}
C_WHITE = {'red': 1, 'green': 1, 'blue': 1}
C_LIGHT_BG = {'red': 248/255, 'green': 250/255, 'blue': 252/255}


def get_credentials():
    if not os.path.exists(TOKEN_FILE):
        print("No token file found at", TOKEN_FILE)
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
    return creds


def styled_text(text, idx, font_size=11, bold=False, color=None, italic=False):
    """Return insert + style requests, returns (requests_list, new_index)."""
    reqs = []
    reqs.append({'insertText': {'text': text, 'location': {'index': idx}}})
    end = idx + len(text)
    style = {'fontSize': {'magnitude': font_size, 'unit': 'PT'}}
    fields = ['fontSize']
    if bold:
        style['bold'] = True
        fields.append('bold')
    if italic:
        style['italic'] = True
        fields.append('italic')
    if color:
        style['foregroundColor'] = {'color': {'rgbColor': color}}
        fields.append('foregroundColor')
    reqs.append({
        'updateTextStyle': {
            'range': {'startIndex': idx, 'endIndex': end},
            'textStyle': style,
            'fields': ','.join(fields)
        }
    })
    return reqs, end


def heading(text, idx, level=1):
    """Insert text and apply heading style."""
    full = text + '\n'
    reqs = [{'insertText': {'text': full, 'location': {'index': idx}}}]
    end = idx + len(full)
    sizes = {1: 28, 2: 22, 3: 18}
    colors = {1: C_NAVY, 2: C_BLUE, 3: C_LIGHT_BLUE}
    reqs.append({
        'updateTextStyle': {
            'range': {'startIndex': idx, 'endIndex': end - 1},
            'textStyle': {
                'fontSize': {'magnitude': sizes.get(level, 18), 'unit': 'PT'},
                'bold': True,
                'foregroundColor': {'color': {'rgbColor': colors.get(level, C_NAVY)}}
            },
            'fields': 'fontSize,bold,foregroundColor'
        }
    })
    named = {1: 'HEADING_1', 2: 'HEADING_2', 3: 'HEADING_3'}
    reqs.append({
        'updateParagraphStyle': {
            'range': {'startIndex': idx, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': named.get(level, 'HEADING_1')},
            'fields': 'namedStyleType'
        }
    })
    return reqs, end


def body_text(text, idx, font_size=12, color=None):
    """Insert body text paragraph."""
    full = text + '\n'
    reqs = [{'insertText': {'text': full, 'location': {'index': idx}}}]
    end = idx + len(full)
    if text:  # only style non-empty text
        style = {'fontSize': {'magnitude': font_size, 'unit': 'PT'}}
        fields = ['fontSize']
        if color:
            style['foregroundColor'] = {'color': {'rgbColor': color}}
            fields.append('foregroundColor')
        reqs.append({
            'updateTextStyle': {
                'range': {'startIndex': idx, 'endIndex': end - 1},
                'textStyle': style,
                'fields': ','.join(fields)
            }
        })
    return reqs, end


def separator(idx):
    full = '━' * 50 + '\n'
    reqs = [{'insertText': {'text': full, 'location': {'index': idx}}}]
    end = idx + len(full)
    reqs.append({
        'updateTextStyle': {
            'range': {'startIndex': idx, 'endIndex': end - 1},
            'textStyle': {
                'fontSize': {'magnitude': 8, 'unit': 'PT'},
                'foregroundColor': {'color': {'rgbColor': C_BLUE}}
            },
            'fields': 'fontSize,foregroundColor'
        }
    })
    return reqs, end


def page_break(idx):
    reqs = [
        {'insertText': {'text': '\n', 'location': {'index': idx}}},
        {'insertPageBreak': {'location': {'index': idx + 1}}}
    ]
    return reqs, idx + 2


def build_all_requests():
    """Build all document content requests sequentially."""
    reqs = []
    idx = 1  # Google Docs starts at index 1

    # ═══════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════
    r, idx = heading('دليل المبيعات الميداني', idx, level=1)
    reqs.extend(r)

    r, idx = body_text('', idx, 12)
    reqs.extend(r)

    r, idx = heading('زيادة سيستم | Ziyada System', idx, level=2)
    reqs.extend(r)

    r, idx = body_text('', idx, 12)
    reqs.extend(r)

    r, idx = body_text('محل العطارة والعبايات — نموذج مبيعات 2026', idx, 16, C_MUTED)
    reqs.extend(r)

    r, idx = body_text('', idx, 12)
    reqs.extend(r)

    r, idx = body_text('"Build once. Scale logically. Grow predictably."', idx, 14, C_BLUE)
    reqs.extend(r)

    r, idx = body_text('', idx, 12)
    reqs.extend(r)

    r, idx = body_text('تاريخ الوثيقة: 5 أبريل 2026  |  النسخة: 1.0', idx, 11, C_MUTED)
    reqs.extend(r)

    r, idx = page_break(idx)
    reqs.extend(r)

    # ═══════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════
    r, idx = heading('فهرس المحتويات', idx, level=1)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)

    toc_items = [
        '1. محل العطارة — النموذج الأول (فرعين)',
        '   المشاكل والفرص  |  خطوات كسب الصفقة  |  الخدمات والحل',
        '',
        '2. محل العبايات — النموذج الثاني (8 فروع)',
        '   التحديات العميقة  |  استراتيجية البيع  |  الحل المخصص',
        '',
        '3. الباقات والتسعير',
        '   الأساسية  |  المتكاملة  |  الاحترافية',
        '',
        '4. التواصل والخطوة التالية',
    ]
    for item in toc_items:
        r, idx = body_text(item, idx, 13, C_NAVY if item.startswith(('1.', '2.', '3.', '4.')) else C_MUTED)
        reqs.extend(r)

    r, idx = page_break(idx)
    reqs.extend(r)

    # ═══════════════════════════════════════
    # SECTION 1: SPICE SHOP
    # ═══════════════════════════════════════
    r, idx = heading('01 | محل العطارة — النموذج الأول (فرعين)', idx, level=1)
    reqs.extend(r)

    r, idx = separator(idx)
    reqs.extend(r)

    r, idx = heading('الحالة الحالية', idx, level=2)
    reqs.extend(r)

    current_state = [
        'فرعين بدون ربط رقمي',
        'كاشير منفصل لكل فرع',
        'إدارة مخزون يدوية 100%',
        'رسائل واتساب فوضى — ما في نظام للردود',
        'لا موقع إلكتروني',
    ]
    for item in current_state:
        r, idx = body_text('  •  ' + item, idx, 12)
        reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)

    r, idx = heading('الفرص', idx, level=2)
    reqs.extend(r)

    opportunities = [
        'زيادة المبيعات 20-50% بعد الرقمنة (Salesforce 2024)',
        'توفير 60-80% من وقت إدارة المخزون (McKinsey 2023)',
        '80% من الاستفسارات يمكن حلها بـ Bot (IBM Watson)',
        'عملاء 24/7 من موقع إلكتروني',
    ]
    for item in opportunities:
        r, idx = body_text('  •  ' + item, idx, 12, C_BLUE)
        reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)
    r, idx = separator(idx)
    reqs.extend(r)

    # Sales steps
    r, idx = heading('خطوات كسب الصفقة (خطوة بخطوة)', idx, level=2)
    reqs.extend(r)

    steps = [
        ('الخطوة 1: افتح بسؤال يكشف الوجع',
         '"لو الفرع الثاني نفد منه صنف الحين — كيف تعرف؟ وكم وقت يأخذ؟"',
         'من يسأل الأسئلة الصح يتحكم بالمحادثة.'),

        ('الخطوة 2: حسسه بحجم الخسارة بأرقام واقعية',
         '"لو في 10 رسائل واتساب يومياً ما تردّون — كم عميل تخسر في الأسبوع؟"',
         'أن يحس بالمشكلة، يحس بالحاجة.'),

        ('الخطوة 3: اعرض الحل بلغة وجعه',
         '"بعد ما نشتغل وياك — أي رسالة واتساب تجي، النظام يرد لحاله. كل صباح تجيك رسالة: الفرع الأول باع كذا، الفرع الثاني عنده نقص"',
         'ربط الحل بالوجع مباشرة.'),

        ('الخطوة 4: أزل الخوف — ابدأ بباقة صغيرة',
         '"خلنا نبدأ بموقع + بوت واتساب بس. بعد شهر تشوف النتيجة"',
         'جرّب أول، بدون التزام كبير.'),

        ('الخطوة 5: اختم بخطوة سهلة',
         '"وش رايك نرتب جلسة 15 دقيقة أونلاين — نحلل وضعك وأوريك الحل؟ بدون أي التزام."',
         'احصل على "نعم" صغيرة، على خطوة سهلة.'),
    ]

    for title, script, tip in steps:
        r, idx = heading(title, idx, level=3)
        reqs.extend(r)
        r, idx = body_text(script, idx, 12, C_NAVY)
        reqs.extend(r)
        r, idx = body_text('الفكرة: ' + tip, idx, 11, C_MUTED)
        reqs.extend(r)
        r, idx = body_text('', idx)
        reqs.extend(r)

    r, idx = separator(idx)
    reqs.extend(r)

    # Services
    r, idx = heading('الخدمات المقترحة', idx, level=2)
    reqs.extend(r)

    services = [
        ('كاشير + إدارة مخزون الفرعين',
         'نظام منفصل — ما يوصل المعلومة بين الفرعين',
         'نظام POS موحد يربط الفرعين مع تنبيهات على الهاتف',
         'لا نفاد مفاجئ للأصناف'),

        ('داشبورد مركزي — تحكم من مكان واحد',
         'صاحب المحل ما يعرف أداء الفرعين إلا لو اتصل',
         'شاشة واحدة تعرض المبيعات والمخزون والتقارير من الجوال',
         'تحكم أينما كنت'),

        ('موقع إلكتروني احترافي',
         'لا موقع — عميل يشوف الصنف بالموقع ما يقدر يطلبه',
         'موقع سريع يعرض الأصناف مع بحث وفلترة، متصل بالواتس والخرائط',
         'مبيعات 24/7'),

        ('بوت واتساب ذكي',
         'رسائل واتساب يأكل وقت الموظف — نفس الأسئلة عشرات المرات',
         'البوت يرد تلقائياً، يرسل الأصناف والأسعار، يحول للموظف عند الحاجة',
         'خدمة 24/7 + توفير وقت الفريق'),
    ]

    for title, problem, solution, result in services:
        r, idx = heading(title, idx, level=3)
        reqs.extend(r)
        r, idx = body_text('المشكلة: ' + problem, idx, 11, C_MUTED)
        reqs.extend(r)
        r, idx = body_text('الحل: ' + solution, idx, 12, C_BLUE)
        reqs.extend(r)
        r, idx = body_text('النتيجة: ' + result, idx, 12, C_NAVY)
        reqs.extend(r)
        r, idx = body_text('', idx)
        reqs.extend(r)

    r, idx = page_break(idx)
    reqs.extend(r)

    # ═══════════════════════════════════════
    # SECTION 2: ABAYA SHOP
    # ═══════════════════════════════════════
    r, idx = heading('02 | محل العبايات — النموذج الثاني (8 فروع)', idx, level=1)
    reqs.extend(r)

    r, idx = separator(idx)
    reqs.extend(r)

    r, idx = heading('الحالة الحالية', idx, level=2)
    reqs.extend(r)

    abaya_state = [
        '8 فروع متفرقة في المملكة',
        'كاشير + مخزون موجود — لكن بدون ربط مركزي',
        'لا تقارير يومية',
        'لا قاعدة بيانات للعملاء',
        'تنسيق الفروع يدوي ومرهق (مكالمات، رسائل)',
        'لا متابعة لأداء الموظفين',
        'غياب شبه كامل عن الفضاء الرقمي',
    ]
    for item in abaya_state:
        r, idx = body_text('  •  ' + item, idx, 12)
        reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)

    r, idx = heading('الفرصة الذهبية', idx, level=2)
    reqs.extend(r)

    r, idx = body_text(
        'تخيل عندك 8 فروع — وكل واحد فيهم يحمل بيانات ذهب: من الأكثر بيع؟ '
        'أي موسم أرباح أحسن؟ أي عميل محتاج متابعة؟ كم مرة عميل من الرياض '
        'شاف عبايتك على إنستغرام لكن ما قدر يطلبها؟',
        idx, 13, C_NAVY)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)

    r, idx = body_text(
        'هذي نحن نبني لك النظام اللي يحول ضغط وفوضى 8 فروع لـ نظام منظم '
        'وفرص بيع كبيرة.',
        idx, 13, C_BLUE)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)
    r, idx = separator(idx)
    reqs.extend(r)

    # Challenges
    r, idx = heading('التحديات العميقة الحقيقية', idx, level=2)
    reqs.extend(r)

    challenges = [
        ('تحدي 1: لا رؤية شاملة',
         'صاحب المحل ما يعرف أي فرع أداؤه أحسن — المقارنة تأخذ ساعات.',
         'داشبورد موحد في لحظة واحدة.'),
        ('تحدي 2: ضياع المبيعات بسبب عدم التنسيق',
         'عرض في فرع ما. عميل في فرع ثاني ما يعرف عنه.',
         'نظام موحد لكل العروض والتنبيهات.'),
        ('تحدي 3: لا قاعدة بيانات للعملاء',
         'كل عملية بيع تضيع — ما في سجل لعادات الشراء أو المقاسات المفضلة.',
         'CRM مركزي — كل عميل له بصمة.'),
        ('تحدي 4: فرص الموسم تضيع',
         'حين يجي رمضان أو العيد، الاتصالات والمكالمات — ما في تخطيط.',
         'حملات واتساب موسمية مؤتمتة = بيع أكثر.'),
        ('تحدي 5: لا متجر أونلاين',
         'عميل من أبها يشوف التصميم على إنستغرام لكن يجد طريق مسدود.',
         'متجر أونلاين + توصيل لكل المملكة.'),
    ]

    for title, problem, solution in challenges:
        r, idx = heading(title, idx, level=3)
        reqs.extend(r)
        r, idx = body_text(problem, idx, 12, C_MUTED)
        reqs.extend(r)
        r, idx = body_text('الحل: ' + solution, idx, 12, C_BLUE)
        reqs.extend(r)
        r, idx = body_text('', idx)
        reqs.extend(r)

    r, idx = separator(idx)
    reqs.extend(r)

    # Phased solution
    r, idx = heading('الحل المتدرج', idx, level=2)
    reqs.extend(r)

    phases = [
        ('الأولوية الأولى — الربط المركزي',
         [
             'داشبورد موحد: اعرض أداء كل 8 فروع لحظياً',
             'تقرير يومي: بيانات المبيعات، أكثر الأصناف، أداء الكاشيرين',
             'تنبيهات ذكية: نقص في صنف يحتاج إعادة طلب قبل نفاده',
         ],
         'قرارات مبنية على بيانات، مو تخمين.'),
        ('الأولوية الثانية — النمو والمبيعات',
         [
             'متجر إلكتروني: عميل من أبها يشتري من محلك في الرياض',
             'نظام ولاء + حملات: رسائل واتساب موسمية قبل رمضان والعيد',
             'بوت واتساب: يرد على الاستفسارات، يحول للموظف عند الحاجة',
         ],
         'عملاء قدامى يشترون أكثر، عملاء جدد من كل المملكة.'),
        ('الأولوية الثالثة — تحسين العمليات',
         [
             'إدارة سوشيال ميديا: محتوى شهري لإنستغرام وسناب',
             'حملات مدفوعة: إعلانات في المواسم الذروة',
             'تقارير أداء الموظفين: من يبيع أكثر؟ من يحتاج تدريب؟',
         ],
         'موظفين منتجين أكثر، صورة علامة قوية.'),
    ]

    for title, items, result in phases:
        r, idx = heading(title, idx, level=3)
        reqs.extend(r)
        for item in items:
            r, idx = body_text('  •  ' + item, idx, 12)
            reqs.extend(r)
        r, idx = body_text('النتيجة: ' + result, idx, 12, C_NAVY)
        reqs.extend(r)
        r, idx = body_text('', idx)
        reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)

    # Golden sales tip
    r, idx = body_text(
        'نصيحة ذهبية: "ركّز أول كلامك على الداشبورد — هذا الشيء اللي يحسها صاحب المحل كل يوم. '
        'بعد ما يوافق على الفكرة، تكمل معه بالباقي. ما تعرض كل شيء من أول مرة."',
        idx, 13, C_BLUE)
    reqs.extend(r)

    r, idx = page_break(idx)
    reqs.extend(r)

    # ═══════════════════════════════════════
    # SECTION 3: PACKAGES
    # ═══════════════════════════════════════
    r, idx = heading('03 | الباقات والتسعير', idx, level=1)
    reqs.extend(r)

    r, idx = separator(idx)
    reqs.extend(r)

    r, idx = body_text('الفلسفة: ابدأ صغير وكبّر — كل باقة تضيف قيمة حقيقية على السابقة.', idx, 13, C_MUTED)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)

    # Package 1
    r, idx = heading('الباقة الأساسية | البدء السريع', idx, level=2)
    reqs.extend(r)

    r, idx = body_text('مناسبة لـ: محل عطارة يريد البدء / محل عبايات يريد تجربة النظام', idx, 12, C_MUTED)
    reqs.extend(r)

    pkg1 = [
        'موقع إلكتروني احترافي — متجر للعرض، تصاميم احترافية، سرعة عالية',
        'بوت واتساب للردود التلقائية — يرد 24/7، يحول للموظف عند الحاجة',
        'قائمة منتجات تفاعلية — بحث وفلترة سهلة، عرض جغرافي للفروع',
        'متصل بالخرائط والواتساب — عميل يعرف الفرع الأقرب',
        'دعم فني الشهر الأول — تنصيب + تدريب',
    ]
    for item in pkg1:
        r, idx = body_text('  •  ' + item, idx, 12)
        reqs.extend(r)

    r, idx = body_text('المدة: شهر أول  |  تحديث: يومي', idx, 11, C_MUTED)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)
    r, idx = separator(idx)
    reqs.extend(r)

    # Package 2
    r, idx = heading('الباقة المتكاملة | الحل الأمثل (الأفضل للأغلبية)', idx, level=2)
    reqs.extend(r)

    r, idx = body_text('مناسبة لـ: محل بفروع متعددة يريد ربط مركزي وتحكم كامل', idx, 12, C_MUTED)
    reqs.extend(r)

    r, idx = body_text('كل ما بالباقة الأساسية +', idx, 12, C_BLUE)
    reqs.extend(r)

    pkg2 = [
        'داشبورد موحد لكل الفروع — مبيعات، أداء، معلومات موظفين',
        'قاعدة بيانات العملاء (CRM) — ملف لكل عميل، السجل الشرائي، التفضيلات',
        'تقارير مبيعات يومية وشهرية — على الجوال تلقائياً',
        'نظام الطلبات والتوصيل — اتصال بشركات شحن، إدارة مركزية',
        'دعم فني 3 أشهر على WhatsApp',
    ]
    for item in pkg2:
        r, idx = body_text('  •  ' + item, idx, 12)
        reqs.extend(r)

    r, idx = body_text('المدة: 3 أشهر أول  |  تحديث: يومي', idx, 11, C_MUTED)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)
    r, idx = separator(idx)
    reqs.extend(r)

    # Package 3
    r, idx = heading('الباقة الاحترافية | نمو شامل', idx, level=2)
    reqs.extend(r)

    r, idx = body_text('مناسبة لـ: محل عبايات يريد التوسع لكل المملكة مع أتمتة كاملة', idx, 12, C_MUTED)
    reqs.extend(r)

    r, idx = body_text('كل ما بالباقة المتكاملة +', idx, 12, C_BLUE)
    reqs.extend(r)

    pkg3 = [
        'نظام ولاء العملاء — مستويات VIP، نقاط شراء، كوبونات حصرية',
        'إدارة سوشيال ميديا شهرية — محتوى إنستغرام وسناب شات احترافي',
        'حملات واتساب و SMS — رسائل موسمية رمضان والعيد، عروض حصرية',
        'تحليل متقدم للبيانات — Insights عميقة، توقع الاتجاهات، توصيات نمو',
        'دعم فني 24/7 + استشارات نمو مستمرة',
    ]
    for item in pkg3:
        r, idx = body_text('  •  ' + item, idx, 12)
        reqs.extend(r)

    r, idx = body_text('المدة: اشتراك مستمر  |  تحديث: يومي + اجتماعات شهرية', idx, 11, C_MUTED)
    reqs.extend(r)

    r, idx = page_break(idx)
    reqs.extend(r)

    # ═══════════════════════════════════════
    # SECTION 4: CTA & CONTACT
    # ═══════════════════════════════════════
    r, idx = heading('04 | الخطوة التالية — تواصل معنا اليوم', idx, level=1)
    reqs.extend(r)

    r, idx = separator(idx)
    reqs.extend(r)

    r, idx = heading('لماذا نختلف؟', idx, level=2)
    reqs.extend(r)

    differentiators = [
        'نفهم السوق السعودي — خبرة مع محلات وشركات سعودية فعلية',
        'نبني حسب احتياجك — ما في حل كوبي-بيست، كل محل فريد',
        'ضمان النتيجة — إذا ما عمل كما وعدنا، نصلحه مجاناً',
        'دعم مستمر — فريق على WhatsApp، سؤالك يجيبه أحد في نفس اليوم',
    ]
    for item in differentiators:
        r, idx = body_text('  •  ' + item, idx, 13)
        reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)
    r, idx = separator(idx)
    reqs.extend(r)

    r, idx = heading('تواصل معنا الآن', idx, level=2)
    reqs.extend(r)

    r, idx = body_text('البريد الإلكتروني: ziyadasystem@gmail.com — نرد عليك في نفس اليوم', idx, 13)
    reqs.extend(r)
    r, idx = body_text('الموقع: https://ziyada.sa', idx, 13)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)
    r, idx = separator(idx)
    reqs.extend(r)

    r, idx = heading('العرض الخاص', idx, level=2)
    reqs.extend(r)

    r, idx = body_text('جلسة استراتيجية مجانية (15 دقيقة) — نحلل وضعك الحالي ونوريك كيف النظام يناسبك بالضبط. بدون التزام.', idx, 13, C_NAVY)
    reqs.extend(r)

    r, idx = body_text('30 يوم تجريبي على الباقة الأساسية — جرّب النظام على حقيقته وشوف النتائج بنفسك.', idx, 13, C_BLUE)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)

    r, idx = heading('خطواتك الثلاث من الآن:', idx, level=3)
    reqs.extend(r)

    r, idx = body_text('1.  اتصل بنا', idx, 14, C_NAVY)
    reqs.extend(r)
    r, idx = body_text('2.  احجز جلسة 15 دقيقة', idx, 14, C_NAVY)
    reqs.extend(r)
    r, idx = body_text('3.  تبدأ معنا (بدون التزام)', idx, 14, C_NAVY)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)
    r, idx = separator(idx)
    reqs.extend(r)

    r, idx = body_text('', idx)
    reqs.extend(r)
    r, idx = body_text('2026 ZIYADA SYSTEM', idx, 11, C_MUTED)
    reqs.extend(r)
    r, idx = body_text('"Build once. Scale logically. Grow predictably."', idx, 11, C_BLUE)
    reqs.extend(r)
    r, idx = body_text('للمزيد من المعلومات: ziyadasystem@gmail.com', idx, 11, C_MUTED)
    reqs.extend(r)

    return reqs


def main():
    print("Creating Sales Guide Google Document...")
    print("=" * 60)

    creds = get_credentials()
    if not creds:
        return

    docs = build('docs', 'v1', credentials=creds)
    drive = build('drive', 'v3', credentials=creds)

    # 1. Create the document
    title = 'دليل المبيعات | زيادة سيستم - محل العطارة والعبايات'
    doc = docs.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']
    print(f"Document created: {doc_id}")

    # 2. Set margins
    margin_req = [{
        'updateDocumentStyle': {
            'documentStyle': {
                'marginBottom': {'magnitude': 36, 'unit': 'PT'},
                'marginTop': {'magnitude': 36, 'unit': 'PT'},
                'marginLeft': {'magnitude': 54, 'unit': 'PT'},
                'marginRight': {'magnitude': 54, 'unit': 'PT'},
            },
            'fields': 'marginBottom,marginTop,marginLeft,marginRight'
        }
    }]
    docs.documents().batchUpdate(documentId=doc_id, body={'requests': margin_req}).execute()

    # 3. Insert all content
    content_requests = build_all_requests()
    # Google Docs has a limit of ~200 requests per batch, split if needed
    batch_size = 150
    for i in range(0, len(content_requests), batch_size):
        batch = content_requests[i:i + batch_size]
        docs.documents().batchUpdate(documentId=doc_id, body={'requests': batch}).execute()
        print(f"  Batch {i // batch_size + 1} applied ({len(batch)} requests)")

    # 4. Share publicly
    drive.permissions().create(
        fileId=doc_id,
        body={'role': 'reader', 'type': 'anyone'},
        fields='id'
    ).execute()

    doc_link = f'https://docs.google.com/document/d/{doc_id}/edit?usp=sharing'

    print()
    print("=" * 60)
    print("SUCCESS! Sales Guide created and shared.")
    print("=" * 60)
    print()
    print(f"Link: {doc_link}")
    print()

    return doc_id, doc_link


if __name__ == '__main__':
    main()
