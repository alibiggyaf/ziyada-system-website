#!/usr/bin/env python3
"""
Send Ziyada automation blog to Gmail as a draft
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    import json
except ImportError:
    print("Installing required packages...")
    os.system("pip3 install google-api-python-client google-auth-httplib2 -q")
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    import json

# Email recipient
RECIPIENT = "ali.biggy.af@gmail.com"

def get_gmail_service():
    """Get authenticated Gmail service from token.json"""
    if not os.path.exists('token.json'):
        print("❌ No token.json found!")
        print("   Please complete OAuth authentication first.")
        print("   Run: python3 tools/populate_manual_auth.py")
        return None
    
    try:
        with open('token.json', 'r') as token_file:
            token_data = json.load(token_file)
        
        credentials = Credentials.from_authorized_user_info(token_data)
        return build('gmail', 'v1', credentials=credentials)
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def create_draft():
    """Create Gmail draft with blog content"""
    
    # Read blog content
    try:
        with open('ziyada_automation_blog.md', 'r', encoding='utf-8') as f:
            blog_content = f.read()
    except FileNotFoundError:
        print("❌ Blog file not found: ziyada_automation_blog.md")
        return False
    
    # Extract title
    title = blog_content.split('\n')[0].replace('# ', '').strip()
    
    # Get Gmail service
    print("\n🔐 Connecting to Gmail...")
    service = get_gmail_service()
    
    if not service:
        return False
    
    # Create email message
    message = MIMEMultipart('alternative')
    message['to'] = RECIPIENT
    message['subject'] = title
    
    # Plain text version
    text_part = MIMEText(blog_content, 'plain')
    message.attach(text_part)
    
    # HTML version
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                color: #0f172a; 
                line-height: 1.7;
                max-width: 650px;
            }}
            h1 {{ color: #3b82f6; font-size: 24px; margin-bottom: 10px; }}
            h2 {{ color: #3b82f6; margin-top: 25px; margin-bottom: 15px; }}
            h3 {{ color: #8b5cf6; margin-top: 15px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th {{ background-color: #f1f5f9; padding: 10px; text-align: left; border: 1px solid #e2e8f0; }}
            td {{ padding: 10px; border: 1px solid #e2e8f0; }}
            p {{ margin: 12px 0; }}
            strong {{ color: #0f172a; }}
            .signature {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 13px; }}
        </style>
    </head>
    <body>
        {blog_content.replace(chr(10), '<br>')}
        <div class="signature">
            <p><strong>Ziyada System</strong><br>
            Building Automation That Actually Works<br><br>
            <em>This email was auto-generated from your blog content.</em></p>
        </div>
    </body>
    </html>
    """
    
    html_part = MIMEText(html_content, 'html')
    message.attach(html_part)
    
    # Create draft
    try:
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft_body = {'message': {'raw': raw_message}}
        
        draft = service.users().drafts().create(userId='me', body=draft_body).execute()
        
        print("\n✅ SUCCESS! Draft created in Gmail")
        print(f"📧 Recipient: {RECIPIENT}")
        print(f"📧 Subject: {title}")
        print(f"\n🔗 Open Gmail to review and send")
        print(f"   → https://mail.google.com/mail/u/0/#drafts")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating draft: {e}")
        print("\n💡 Alternative: Copy the formatted email manually")
        print(f"   1. Open {RECIPIENT} in Gmail")
        print(f"   2. Open ziyada_blog_email_draft.html in browser")
        print(f"   3. Copy content → Paste into Gmail draft")
        return False

if __name__ == '__main__':
    success = create_draft()
    exit(0 if success else 1)
