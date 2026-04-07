#!/usr/bin/env python3
"""
Create Ziyada Arabic blog email draft - generates HTML file for copy-paste into Gmail
"""

import os
from datetime import datetime

# Read Arabic blog content
with open('ziyada_automation_blog_ar.md', 'r', encoding='utf-8') as f:
    blog_content = f.read()

# Extract title
title = blog_content.split('\n')[0].replace('# ', '').strip()

# Create HTML version for Arabic (RTL)
html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مسودة البريد: {title}</title>
    <style>
        * {{
            direction: rtl;
            text-align: right;
        }}
        body {{
            font-family: 'Cairo', 'Segoe UI', Roboto, sans-serif;
            color: #0f172a;
            line-height: 1.8;
            background-color: #f8fafc;
            margin: 0;
            padding: 20px;
        }}
        .email-container {{
            background: white;
            max-width: 650px;
            direction: rtl;
            margin: 0 auto;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}
        .email-header {{
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .email-header h1 {{
            color: #3b82f6;
            margin: 0;
            font-size: 24px;
            font-weight: 700;
        }}
        .email-header p {{
            color: #64748b;
            margin: 5px 0 0 0;
            font-size: 13px;
        }}
        h2 {{
            color: #3b82f6;
            font-size: 18px;
            margin-top: 30px;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        h3 {{
            color: #8b5cf6;
            font-size: 15px;
            margin-top: 15px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        p {{
            margin: 15px 0;
            line-height: 1.8;
            font-size: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th {{
            background-color: #f1f5f9;
            color: #0f172a;
            padding: 12px;
            text-align: right;
            font-weight: 700;
            border: 1px solid #e2e8f0;
        }}
        td {{
            padding: 12px;
            border: 1px solid #e2e8f0;
            text-align: right;
        }}
        strong {{
            color: #0f172a;
            font-weight: 700;
        }}
        code {{
            background-color: #f1f5f9;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
        }}
        .signature {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            color: #64748b;
            font-size: 13px;
        }}
        .signature strong {{
            color: #0f172a;
        }}
        .instructions {{
            background-color: #eff6ff;
            border-right: 4px solid #3b82f6;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 4px;
            font-size: 13px;
        }}
        .instructions strong {{
            color: #1e40af;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-right: 20px;
        }}
        li {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="instructions">
            <strong>📧 تعليمات سريعة:</strong><br>
            1. انسخ كل المحتوى أدناه<br>
            2. افتح Gmail → انقر على "كتابة"<br>
            3. الصق كل شيء في نص البريد<br>
            4. راجع وخصص قبل الإرسال
        </div>

        <div class="email-header">
            <h1>{title}</h1>
            <p>سطر الموضوع: {title}</p>
        </div>

        <div class="email-body">
"""

# Convert markdown to HTML (simple version)
lines = blog_content.split('\n')
skip_first = True

for line in lines:
    if skip_first and line.startswith('#'):
        skip_first = False
        continue
    
    if line.startswith('## '):
        heading = line.replace('## ', '').strip()
        html_content += f'<h2>{heading}</h2>\n'
    elif line.startswith('### '):
        heading = line.replace('### ', '').strip()
        html_content += f'<h3>{heading}</h3>\n'
    elif line.startswith('| '):
        # Handle tables
        if 'المقياس' in line or '---' in line:
            if '---' in line:
                continue
            # This is a header row
            html_content += '<table><tr>'
            for cell in line.split('|')[1:-1]:
                html_content += f'<th>{cell.strip()}</th>'
            html_content += '</tr>'
        else:
            html_content += '<tr>'
            for cell in line.split('|')[1:-1]:
                html_content += f'<td>{cell.strip()}</td>'
            html_content += '</tr>'
    elif line.strip() == '':
        continue
    elif line.startswith('-'):
        # Bullet points
        if not html_content.rstrip().endswith('<ul>'):
            html_content += '<ul>\n'
        html_content += f'<li>{line.replace("- ", "").strip()}</li>\n'
    else:
        if line.strip():
            html_content += f'<p>{line.strip()}</p>\n'

html_content += """
        </div>

        <div class="signature">
            <p><strong>زيادة سستم للانظمة الذكية</strong><br>
            بناء نظم تشغيل آلي تعمل بالفعل<br><br>
            <em>ملاحظة: هذا محتوى مسودة. يرجى المراجعة والتخصيص قبل الإرسال.</em></p>
        </div>
    </div>

    <div style="text-align: center; margin-top: 40px; color: #94a3b8; font-size: 12px;">
        <p>تم الإنشاء: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """</p>
    </div>
</body>
</html>
"""

# Save HTML file
output_file = 'ziyada_blog_email_draft_ar.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

# Also create a plain text version for copy-paste
with open('ziyada_blog_email_draft_ar.txt', 'w', encoding='utf-8') as f:
    f.write(f"الموضوع: {title}\n\n")
    f.write(blog_content)

print("\n✅ نجح! تم إنشاء ملفات مسودة البريد:\n")
print(f"📄 النسخة الـ HTML: {output_file}")
print(f"   → افتح في المتصفح لرؤية النسخة المنسقة")
print(f"   → انسخ من المتصفح → الصق في مكتب Gmail\n")
print(f"📄 النسخة النصية: ziyada_blog_email_draft_ar.txt")
print(f"   → انسخ → الصق في مكتب Gmail\n")
print("📧 الخطوات التالية:")
print("   1. افتح Gmail")
print("   2. انقر على 'كتابة' (أو اضغط 'C')")
print(f"   3. الصق الموضوع: {title}")
print("   4. انسخ المحتوى من ملف HTML والصقه في نص البريد")
print("   5. راجع وخصص قبل الإرسال\n")
print(f"✨ مدونتك جاهزة للإرسال!")
