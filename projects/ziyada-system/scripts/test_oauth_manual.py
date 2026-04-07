#!/usr/bin/env python3
"""
Test Google API connections - Manual OAuth code exchange
"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
from pathlib import Path
import base64
from urllib.parse import urlencode, urlparse, parse_qs
import webbrowser

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.send"
]

# Load credentials
credentials_file = Path("credentials.json")
with open(credentials_file) as f:
    config = json.load(f)
    cred_config = config.get('web') or config.get('installed')
    client_id = cred_config['client_id']
    client_secret = cred_config['client_secret']
    redirect_uri = "http://localhost:8080/"

def get_auth_url():
    """Generate the authorization URL"""
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(SCOPES),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return 'https://accounts.google.com/o/oauth2/auth?' + urlencode(params)

def exchange_code_for_token(auth_code):
    """Exchange authorization code for access token"""
    import urllib.request
    
    params = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    url = 'https://oauth2.googleapis.com/token'
    data = urlencode(params).encode('utf-8')
    
    try:
        with urllib.request.urlopen(url, data) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"❌ Error exchanging code: {e}")
        return None

def create_test_doc(service):
    """Create a test Google Document"""
    print("\n📄 Creating test document...")
    try:
        doc = service.documents().create(body={
            "title": "Ziyada System - OAuth Test Doc"
        }).execute()
        doc_id = doc.get('documentId')
        print(f"✅ Document created: {doc_id}")
        print(f"   Link: https://docs.google.com/document/d/{doc_id}/edit")
        
        # Add content
        requests = [
            {
                "insertText": {
                    "text": "Ziyada System - OAuth Connection Test\n\n✓ This document was created automatically via Google Docs API\n✓ OAuth authentication is WORKING!"
                }
            }
        ]
        service.documents().batchUpdate(documentId=doc_id, body={
            "requests": requests
        }).execute()
        print("✅ Content added to document")
        return True
    except Exception as e:
        print(f"❌ Error with Docs API: {e}")
        return False

def send_test_email(service, recipient_email):
    """Send a test email"""
    print("\n📧 Sending test email...")
    try:
        message = f"""From: me
To: {recipient_email}
Subject: Ziyada System - OAuth Connection Test

✓ This email was sent automatically via Gmail API
✓ OAuth authentication is WORKING!

---
Test completed successfully
"""
        raw = base64.urlsafe_b64encode(message.encode()).decode()
        
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        print(f"✅ Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Error with Gmail API: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("🧪 ZIYADA SYSTEM - OAUTH CONNECTION TEST (MANUAL)")
    print("=" * 70)
    
    # Step 1: Get auth URL
    print("\n🔐 Step 1: Google OAuth Authorization")
    print("-" * 70)
    auth_url = get_auth_url()
    print("\n📋 Copy this URL and paste it into your browser:\n")
    print(auth_url)
    print("\n1. Open the URL above in your browser")
    print("2. Click 'Sign in with Google'")
    print("3. Allow access to Documents and Gmail")
    print("4. You'll see a URL in your browser - copy just the 'code' value")
    print("\nExample: If you see:")
    print("  http://localhost:8080/?code=4/0AY0e-g...")
    print("Copy only: 4/0AY0e-g...\n")
    
    auth_code = input("📝 Paste the authorization code here: ").strip()
    
    if not auth_code:
        print("❌ No code provided")
        return
    
    # Step 2: Exchange for token
    print("\n🔄 Exchanging code for access token...")
    token_response = exchange_code_for_token(auth_code)
    
    if not token_response or 'access_token' not in token_response:
        print("❌ Failed to get access token")
        print(f"   Response: {token_response}")
        return
    
    print("✅ Access token received")
    
    # Save token
    Path("token.json").write_text(json.dumps(token_response))
    print("✅ Token saved to token.json")
    
    # Step 3: Build credentials and test APIs
    print("\n📚 Step 2: Testing Google APIs")
    print("-" * 70)
    
    creds = Credentials(
        token=token_response['access_token'],
        refresh_token=token_response.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    
    # Test Docs
    try:
        docs_service = build("docs", "v1", credentials=creds)
        create_test_doc(docs_service)
    except Exception as e:
        print(f"❌ Docs API failed: {e}")
    
    # Test Gmail
    try:
        gmail_service = build("gmail", "v1", credentials=creds)
        profile = gmail_service.users().getProfile(userId="me").execute()
        user_email = profile.get('emailAddress')
        print(f"\n📧 Your email: {user_email}")
        send_test_email(gmail_service, user_email)
    except Exception as e:
        print(f"❌ Gmail API failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✨ CONNECTION TEST COMPLETE")
    print("=" * 70)
    print("\n✅ If you see both checkmarks above:")
    print("   • Document created successfully")
    print("   • Email sent successfully")
    print("   → Your OAuth is WORKING! Ready for slides!")
    print("\n🚀 Next steps:")
    print("   Run: cd projects/ziyada-system && python3 -B scripts/create_ziyada_presentation.py")
    print()

if __name__ == "__main__":
    main()
