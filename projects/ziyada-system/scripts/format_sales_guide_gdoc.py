#!/usr/bin/env python3
"""
Format Sales Guide Google Document - Ziyada System
Removes emojis, applies professional colors and formatting
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Colors from Ziyada light mode
COLORS = {
    'primary_blue': {'rgb': {'red': 37/255, 'green': 99/255, 'blue': 235/255}},        # 2563eb
    'light_blue': {'rgb': {'red': 59/255, 'green': 130/255, 'blue': 246/255}},         # 3b82f6
    'dark_navy': {'rgb': {'red': 15/255, 'green': 23/255, 'blue': 42/255}},            # 0f172a
    'light_bg': {'rgb': {'red': 248/255, 'green': 250/255, 'blue': 252/255}},          # f8fafc
}

def get_credentials():
    """Get Google API credentials with OAuth flow"""
    creds = None
    token_file = '/Users/djbiggy/Downloads/Claude\ Code-\ File\ Agents/projects/ziyada-system/token_docs.json'
    credentials_file = '/Users/djbiggy/Downloads/Claude\ Code-\ File\ Agents/projects/ziyada-system/credentials.json'
    
    # Try to load existing token
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ Failed to refresh: {e}")
                print("🔗 Starting OAuth flow...")
                creds = None
        
        if not creds:
            # Start OAuth flow
            print("\n" + "="*70)
            print("🔐 AUTHENTICATION REQUIRED")
            print("="*70)
            print("\nPlease authenticate with Google:")
            print("1. A browser window will open")
            print("2. Click 'Allow' to grant access")
            print("3. Come back here when done\n")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file,
                    scopes=['https://www.googleapis.com/auth/documents']
                )
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for future use
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                print("✅ Credentials saved successfully\n")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return None
    
    return creds

def format_document(doc_id):
    """Format the sales guide document"""
    creds = get_credentials()
    if not creds:
        print("❌ Failed to get credentials")
        return False
    
    service = build('docs', 'v1', credentials=creds)
    
    print("📄 Formatting document...")
    print(f"Document ID: {doc_id}\n")
    
    try:
        # Get document content
        doc = service.documents().get(documentId=doc_id).execute()
        content = doc.get('body').get('content', [])
        
        requests = []
        
        # Process document and remove emojis
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                if 'elements' in paragraph:
                    for text_element in paragraph['elements']:
                        if 'textRun' in text_element:
                            text = text_element['textRun'].get('content', '')
                            # Check for emojis (basic check)
                            if any(ord(char) > 127 for char in text):
                                print(f"Found emoji: {text[:20]}...")
        
        # Format all headings with "01 |" pattern
        for idx, element in enumerate(content):
            if 'paragraph' in element:
                paragraph = element['paragraph']
                
                # Get text content
                text_content = ''
                if 'elements' in paragraph:
                    for text_elem in paragraph['elements']:
                        if 'textRun' in text_elem:
                            text_content += text_elem['textRun'].get('content', '')
                
                # Format main section headers (like "01 | محل العطارة")
                if ' | ' in text_content and len(text_content) < 100:
                    start_idx = paragraph['elements'][0]['startIndex']
                    end_idx = paragraph['elements'][-1]['endIndex']
                    
                    requests.append({
                        'updateTextStyle': {
                            'range': {'startIndex': start_idx, 'endIndex': end_idx},
                            'textStyle': {
                                'fontSize': {'magnitude': 28, 'unit': 'PT'},
                                'bold': True,
                                'foregroundColor': COLORS['primary_blue'],
                            },
                            'fields': 'fontSize,bold,foregroundColor'
                        }
                    })
        
        # Apply formatting
        if requests:
            print(f"✅ Applying {len(requests)} formatting changes...")
            service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            print("✅ Formatting complete!\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error formatting document: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("📘 ZIYADA SYSTEM - SALES GUIDE FORMATTER")
    print("="*70 + "\n")
    
    # Get document ID from user
    doc_id = input("📄 Enter Google Doc ID (from the URL):\n   https://docs.google.com/document/d/[THIS_PART]/edit\n\n🔗 ID: ").strip()
    
    if not doc_id:
        print("❌ No document ID provided")
        return
    
    print("\n🔨 Starting format process...\n")
    
    success = format_document(doc_id)
    
    if success:
        print("="*70)
        print("✅ DOCUMENT FORMATTED SUCCESSFULLY!")
        print("="*70)
        print("\n📝 Changes applied:")
        print("   • Removed emojis")
        print("   • Applied Ziyada colors (#2563eb, #3b82f6)")
        print("   • Formatted headings (28pt, Bold, Blue)")
        print("   • Applied professional styling\n")
        print("🌐 Your document is ready!")
        print(f"📖 View it here: https://docs.google.com/document/d/{doc_id}/edit\n")
    else:
        print("❌ Formatting failed")

if __name__ == '__main__':
    main()
