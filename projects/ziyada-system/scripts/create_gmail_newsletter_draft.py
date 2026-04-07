import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Google API credentials
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'path/to/service_account.json')
USER_EMAIL = os.getenv('NEWSLETTER_SENDER_EMAIL', 'ali.biggy.af@gmail.com')

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

# HTML newsletter content about Ziyada System
NEWSLETTER_HTML = '''
<html>
  <body style="font-family: Arial, sans-serif; background: #f9f9f9; padding: 20px;">
    <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #eee; padding: 32px;">
      <h2 style="color: #2a7ae2;">Discover Ziyada System</h2>
      <p>Welcome to <b>Ziyada System</b> – your all-in-one platform for business automation, analytics, and growth!</p>
      <ul>
        <li>🚀 <b>Automate</b> your workflows and save time</li>
        <li>📊 <b>Analyze</b> your data with powerful dashboards</li>
        <li>🤝 <b>Collaborate</b> with your team in real-time</li>
        <li>🔒 <b>Secure</b> and reliable cloud infrastructure</li>
      </ul>
      <p style="margin-top: 24px;">
        <a href="https://ziyadasystem.com" style="background: #2a7ae2; color: #fff; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: bold;">Try Ziyada System Now</a>
      </p>
      <hr style="margin: 32px 0;">
      <p style="font-size: 12px; color: #888;">You are receiving this email as a test newsletter for Ziyada System. If you wish to unsubscribe, simply ignore this message.</p>
    </div>
  </body>
</html>
'''

def create_gmail_draft():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=USER_EMAIL)
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEMultipart('alternative')
    message['to'] = USER_EMAIL
    message['from'] = USER_EMAIL
    message['subject'] = "🚀 Discover Ziyada System – Your Business Growth Partner!"
    part = MIMEText(NEWSLETTER_HTML, 'html')
    message.attach(part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'message': {'raw': raw_message}}
    draft = service.users().drafts().create(userId='me', body=create_message).execute()
    print(f"Draft created! View it in your Gmail drafts folder.")
    return draft

if __name__ == "__main__":
    create_gmail_draft()
