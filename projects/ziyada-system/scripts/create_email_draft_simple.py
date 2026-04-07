#!/usr/bin/env python3
"""
Create Ziyada blog email draft - generates HTML file for copy-paste into Gmail
"""

import os
from datetime import datetime

# Read blog content
with open('ziyada_automation_blog.md', 'r', encoding='utf-8') as f:
    blog_content = f.read()

# Extract title
title = blog_content.split('\n')[0].replace('# ', '').strip()

# Create HTML version
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Draft: {title}</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #0f172a;
            line-height: 1.7;
            background-color: #f8fafc;
            margin: 0;
            padding: 20px;
        }}
        .email-container {{
            background: white;
            max-width: 650px;
            margin: 0 auto;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}
        .email-header {{
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .email-header h1 {{
            color: #3b82f6;
            margin: 0;
            font-size: 24px;
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
        }}
        h3 {{
            color: #8b5cf6;
            font-size: 15px;
            margin-top: 15px;
            margin-bottom: 10px;
        }}
        p {{
            margin: 15px 0;
            line-height: 1.7;
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
            text-align: left;
            font-weight: 600;
            border: 1px solid #e2e8f0;
        }}
        td {{
            padding: 12px;
            border: 1px solid #e2e8f0;
        }}
        strong {{
            color: #0f172a;
            font-weight: 600;
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
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 4px;
            font-size: 13px;
        }}
        .instructions strong {{
            color: #1e40af;
        }}
        ul {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        li {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="instructions">
            <strong>📧 Quick instructions:</strong><br>
            1. Copy all the content below<br>
            2. Open Gmail → Click "Compose"<br>
            3. Paste everything into the email body<br>
            4. Review and customize before sending
        </div>

        <div class="email-header">
            <h1>{title}</h1>
            <p>Subject line: {title}</p>
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
        if 'Before' in line or 'Metric' in line:  # Table header row
            html_content += '<table><tr>'
            for cell in line.split('|')[1:-1]:
                html_content += f'<th>{cell.strip()}</th>'
            html_content += '</tr>'
        elif line.startswith('|---'):
            continue
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
        # Look ahead to see if we should close ul
    else:
        if line.strip():
            html_content += f'<p>{line.strip()}</p>\n'

html_content += """
        </div>

        <div class="signature">
            <p><strong>Ziyada System</strong><br>
            Building Automation That Actually Works<br><br>
            <em>Note: This is draft content. Review and customize before sending.</em></p>
        </div>
    </div>

    <div style="text-align: center; margin-top: 40px; color: #94a3b8; font-size: 12px;">
        <p>Generated: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """</p>
    </div>
</body>
</html>
"""

# Save HTML file
output_file = 'ziyada_blog_email_draft.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

# Also create a plain text version for copy-paste
with open('ziyada_blog_email_draft.txt', 'w', encoding='utf-8') as f:
    f.write(f"Subject: {title}\n\n")
    f.write(blog_content)

print("\n✅ SUCCESS! Email draft files created:\n")
print(f"📄 HTML version: {output_file}")
print(f"   → Open in browser to see formatted version")
print(f"   → Copy from browser → Paste into Gmail compose\n")
print(f"📄 Text version: ziyada_blog_email_draft.txt")
print(f"   → Copy → Paste into Gmail compose\n")
print("📧 Next steps:")
print("   1. Open Gmail")
print("   2. Click 'Compose' (or press 'C')")
print(f"   3. Paste the subject: {title}")
print("   4. Copy content from the HTML file and paste into email body")
print("   5. Review and customize before sending\n")
print(f"✨ Your blog post is ready to send!")
