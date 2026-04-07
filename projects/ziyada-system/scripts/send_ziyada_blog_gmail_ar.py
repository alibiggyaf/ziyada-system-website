#!/usr/bin/env python3
"""
Send Arabic Ziyada blog as Gmail draft to ali.biggy.af@gmail.com
"""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json

RECIPIENT = "ali.biggy.af@gmail.com"

# Load credentials from token.json (must be present)
def get_gmail_service():
    if not os.path.exists('token.json'):
        print("❌ No token.json found! Run OAuth first.")
        return None
    with open('token.json', 'r') as token_file:
        token_data = json.load(token_file)
    credentials = Credentials.from_authorized_user_info(token_data)
    return build('gmail', 'v1', credentials=credentials)

def create_draft():
    # Read Arabic blog content
    with open('ziyada_automation_blog_ar.md', 'r', encoding='utf-8') as f:
        blog_content = f.read()
    title = blog_content.split('\n')[0].replace('# ', '').strip()
    # Create email message
    message = MIMEMultipart('alternative')
    message['to'] = RECIPIENT
    message['subject'] = title
    text_part = MIMEText(blog_content, 'plain', 'utf-8')
    message.attach(text_part)
    # HTML version
    with open('ziyada_blog_email_draft_ar.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_part = MIMEText(html_content, 'html', 'utf-8')
    message.attach(html_part)
    # Create draft
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {'message': {'raw': raw_message}}
    service = get_gmail_service()
    if not service:
        return False
    draft = service.users().drafts().create(userId='me', body=draft_body).execute()
    print(f"\n✅ Draft created for {RECIPIENT} with subject: {title}")
    print("Open Gmail drafts to review and send.")
    return True

if __name__ == '__main__':
    create_draft()
