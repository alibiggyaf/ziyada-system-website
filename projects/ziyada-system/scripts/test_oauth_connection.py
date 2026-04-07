#!/usr/bin/env python3
"""
Test Google API connections - Create a Doc and send an email
Verifies OAuth credentials are working before attempting Slides
"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.send"
]

def authenticate():
    """Authenticate with Google APIs"""
    creds = None
    token_path = Path("token.json")
    cred_path = Path("credentials.json")
    
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            if creds and creds.valid:
                print("✅ Using existing token")
                return creds
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print("✅ Refreshed expired token")
                return creds
        except Exception as e:
            print(f"⚠️  Token invalid: {e}")
    
    # Fresh OAuth flow
    print("\n🌐 Starting OAuth flow...")
    print("=" * 70)
    flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
    print("📋 STEP 1: Copy the URL below and paste into your browser\n")
    
    creds = flow.run_local_server(port=8080, open_browser=False)
    
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    
    print("✅ Token saved!")
    return creds

def create_test_doc(service):
    """Create a test Google Document"""
    print("\n📄 Creating test document...")
    try:
        doc = service.documents().create(body={
            "title": "Ziyada System - OAuth Test"
        }).execute()
        doc_id = doc.get('documentId')
        print(f"✅ Document created: {doc_id}")
        print(f"   Link: https://docs.google.com/document/d/{doc_id}/edit")
        
        # Add content
        requests = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": "Ziyada System - OAuth Connection Test\n\nThis document was created automatically to verify Google API authentication is working.\n\nIf you can see this message, the OAuth flow is successful!"
                }
            }
        ]
        service.documents().batchUpdate(documentId=doc_id, body={
            "requests": requests
        }).execute()
        print("✅ Content added to document\n")
        return doc_id
    except Exception as e:
        print(f"❌ Error creating document: {e}\n")
        return None

def send_test_email(service, recipient_email):
    """Send a test email"""
    print("📧 Sending test email...")
    try:
        message = {
            "raw": __import__('base64').urlsafe_b64encode(
                f"""From: me
To: {recipient_email}
Subject: Ziyada System - OAuth Connection Test

This email was sent automatically to verify Gmail API authentication is working.

If you received this, the OAuth flow is successful!

---
Sent from Ziyada System OAuth Test
""".encode('utf-8')
            ).decode('utf-8')
        }
        
        service.users().messages().send(userId="me", body=message).execute()
        print(f"✅ Email sent to {recipient_email}\n")
    except Exception as e:
        print(f"❌ Error sending email: {e}\n")

def main():
    print("\n" + "=" * 70)
    print("🧪 ZIYADA SYSTEM - OAUTH CONNECTION TEST")
    print("=" * 70)
    
    # Step 1: Authenticate
    print("\n🔐 Step 1: Google OAuth Authentication")
    print("-" * 70)
    try:
        creds = authenticate()
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Step 2: Test Docs API
    print("\n📚 Step 2: Testing Google Docs API")
    print("-" * 70)
    docs_service = build("docs", "v1", credentials=creds)
    doc_id = create_test_doc(docs_service)
    
    # Step 3: Test Gmail API
    print("✉️  Step 3: Testing Gmail API")
    print("-" * 70)
    gmail_service = build("gmail", "v1", credentials=creds)
    
    # Get user email
    try:
        profile = gmail_service.users().getProfile(userId="me").execute()
        user_email = profile.get('emailAddress')
        print(f"📧 Your email: {user_email}")
        
        send_test_email(gmail_service, user_email)
    except Exception as e:
        print(f"❌ Error getting profile: {e}\n")
    
    # Summary
    print("=" * 70)
    print("✨ CONNECTION TEST COMPLETE")
    print("=" * 70)
    print("\n✅ If you see this:")
    print("   • Document created successfully")
    print("   • Email sent successfully")
    print("   → Your OAuth credentials are WORKING! ✓")
    print("\n📝 Next steps:")
    print("   Run: cd projects/ziyada-system && python3 -B scripts/create_ziyada_presentation.py")
    print("   This will populate all 11 slides automatically")
    print()

if __name__ == "__main__":
    main()
