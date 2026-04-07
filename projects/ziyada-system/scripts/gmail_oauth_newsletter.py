import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.send']

# Path to your client secret file
CLIENT_SECRET_FILE = 'client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json'

# The email you want to send from (must match the authenticated account)
SENDER_EMAIL = 'ali.biggy.af@gmail.com'
RECIPIENT_EMAIL = 'ali.biggy.af@gmail.com'

# Load Ziyada guidelines
with open('ZIYADA_GUIDELINES.md', 'r', encoding='utf-8') as f:
    guidelines = f.read()

# Placeholder for Banana image generation (customize with your Banana API)
def generate_banana_image(prompt):
    # Example: Call Banana API here and return image URL
    # return banana.generate_image(prompt)
    return 'https://your-banana-image-url.com/ziyadasaudi.jpg'

# Example prompt for Banana image
banana_prompt = 'Modern Saudi business team collaborating, Ziyada System branding, blue and gold colors, technology, automation, professional, culturally appropriate.'
banana_image_url = generate_banana_image(banana_prompt)

# Subject for the email (Saudi Arabic, no emoji, per guidelines)
SUBJECT = "دليل علامة زيادة | Ziyada Brand Book (Draft)"

# Blog-style newsletter content (Arabic, Saudi tone, creative layout)
with open('ziyada_brand_book.html', 'r', encoding='utf-8') as f:
    NEWSLETTER_HTML = f.read()

def get_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080, prompt='consent')
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_draft_with_attachment(service, sender, to, subject, body_text, attachment_path):
    from email.mime.base import MIMEBase
    from email import encoders
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    # Attach the body text
    message.attach(MIMEText(body_text, 'plain'))
    # Attach the PDF
    with open(attachment_path, 'rb') as f:
        mime = MIMEBase('application', 'pdf')
        mime.set_payload(f.read())
        encoders.encode_base64(mime)
        mime.add_header('Content-Disposition', 'attachment', filename='ziyada_brand_book.pdf')
        message.attach(mime)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'message': {'raw': raw_message}}
    draft = service.users().drafts().create(userId='me', body=create_message).execute()
    print(f"Draft with PDF created! View it in your Gmail drafts folder.")
    return draft

def send_email(service, sender, to, subject, html_content):
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    part = MIMEText(html_content, 'html')
    message.attach(part)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = {'raw': raw_message}
    sent = service.users().messages().send(userId='me', body=send_message).execute()
    print(f"Email sent! Message ID: {sent['id']}")
    return sent

def create_html_draft(service, sender, to, subject, html_content):
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    part = MIMEText(html_content, 'html')
    message.attach(part)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'message': {'raw': raw_message}}
    draft = service.users().drafts().create(userId='me', body=create_message).execute()
    print(f"HTML draft created! View it in your Gmail drafts folder.")
    return draft

if __name__ == "__main__":
    if SENDER_EMAIL == 'your_email@gmail.com' or RECIPIENT_EMAIL == 'your_email@gmail.com':
        print("Please set your real email in the ZIYADA_EMAIL environment variable or directly in the script before sending.")
    else:
        service = get_gmail_service()
        # Send the real PDF as an attachment
        body_text = "Please find attached the Ziyada System Brand Book (PDF).\n\nPath to open in Finder: /Users/djbiggy/Downloads/Claude Code- File Agents/ziyada_brand_book.pdf"
        create_draft_with_attachment(service, SENDER_EMAIL, RECIPIENT_EMAIL, SUBJECT, body_text, 'ziyada_brand_book.pdf')
        print("Draft with the PDF attached has been sent to your Gmail drafts folder.")
        # Create an HTML draft with the brand guidelines
        create_html_draft(service, SENDER_EMAIL, RECIPIENT_EMAIL, SUBJECT, NEWSLETTER_HTML)
        print("HTML draft with the brand guidelines has been sent to your Gmail drafts folder.")
