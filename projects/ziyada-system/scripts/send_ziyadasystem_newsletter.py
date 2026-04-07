import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
SENDER_EMAIL = os.getenv('NEWSLETTER_SENDER_EMAIL', 'li.biggy.af@gmail.com')
SENDER_PASSWORD = os.getenv('NEWSLETTER_SENDER_PASSWORD', 'your_password')
RECIPIENT_EMAIL = os.getenv('NEWSLETTER_RECIPIENT_EMAIL', 'ali.biggy.af@gmail.com')

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

def send_newsletter():
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "🚀 Discover Ziyada System – Your Business Growth Partner!"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    part = MIMEText(NEWSLETTER_HTML, 'html')
    msg.attach(part)

    # Using Gmail SMTP (for test)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print(f"Test newsletter sent to {RECIPIENT_EMAIL}")

if __name__ == "__main__":
    send_newsletter()
