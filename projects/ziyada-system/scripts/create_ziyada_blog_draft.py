#!/usr/bin/env python3
"""
Create Gmail draft with Ziyada Automation blog post
Simple version - uses googleapiclient directly
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from googleapiclient.discovery import build
except ImportError:
    print("❌ googleapiclient not found. Installing...")
    os.system("pip3 install google-api-python-client -q")
    from googleapiclient.discovery import build

def get_authenticated_service():
    """Get authenticated Gmail service"""
    creds = None
    
    # Check if token already exists
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load client config
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found!")
                print("   Please download it from Google Cloud Console first.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save credentials for future use
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)
    
    # Import here after we have credentials
    from googleapiclient.discovery import build
    return build('gmail', 'v1', credentials=creds)

def create_draft_with_blog():
    """Create Gmail draft with blog content"""
    
    print("\n🔐 Authenticating with Gmail...")
    service = get_authenticated_service()
    
    if not service:
        print("❌ Authentication failed")
        return False
    
    # Read blog content
    try:
        with open('ziyada_automation_blog.md', 'r', encoding='utf-8') as f:
            blog_content = f.read()
    except FileNotFoundError:
        print("❌ Blog file not found: ziyada_automation_blog.md")
        return False
    
    # Extract title from first line
    title = blog_content.split('\n')[0].replace('# ', '').strip()
    
    # Create email
    message = MIMEMultipart('alternative')
    message['to'] = 'your-email@gmail.com'  # User's own email
    message['subject'] = f'[DRAFT] {title}'
    
    # Plain text version
    text_part = MIMEText(blog_content, 'plain')
    message.attach(text_part)
    
    # Create HTML version for better formatting
    html_content = blog_content.replace('\n## ', '<h2 style="color:#3b82f6; margin-top:20px;">') \
                                .replace('\n###', '<h3 style="color:#8b5cf6;">') \
                                .replace('\n\n', '</p><p>') \
                                .replace('\n', '<br>')
    
    html_part = MIMEText(f"""
    <html>
    <head>
        <style>
            body {{ font-family: Inter, Arial; color: #0f172a; line-height: 1.6; }}
            h1 {{ color: #3b82f6; font-size: 28px; }}
            h2 {{ color: #3b82f6; margin-top: 20px; }}
            h3 {{ color: #8b5cf6; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 10px; text-align: left; }}
            th {{ background-color: #f1f5f9; }}
            code {{ background-color: #f1f5f9; padding: 2px 4px; border-radius: 3px; }}
            strong {{ color: #0f172a; }}
            .signature {{ margin-top: 40px; color: #64748b; font-size: 12px; }}
        </style>
    </head>
    <body>
        {html_content}
        <div class="signature">
            <p><strong>Ziyada System</strong><br>
            Building Automation That Actually Works<br>
            <em>This is draft content - review and customize before sending</em></p>
        </div>
    </body>
    </html>
    """, 'html')
    message.attach(html_part)
    
    # Create draft
    try:
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft_body = {'message': {'raw': raw_message}}
        
        draft = service.users().drafts().create(userId='me', body=draft_body).execute()
        
        print("\n✅ SUCCESS! Draft created in Gmail")
        print(f"📧 Subject: {message['subject']}")
        print(f"📧 To: {message['to']}")
        print(f"\n🔗 Open Gmail to review and customize before sending")
        print(f"   → https://mail.google.com/mail/u/0/#drafts")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating draft: {e}")
        return False

if __name__ == '__main__':
    success = create_draft_with_blog()
    exit(0 if success else 1)
