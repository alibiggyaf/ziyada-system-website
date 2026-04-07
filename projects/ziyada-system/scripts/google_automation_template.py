import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Google API credentials from .env
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')

# Path to your service account JSON (if using service account)
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'path/to/service_account.json')

# Scopes for Google APIs
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
]

# Authenticate with service account (recommended for automation)
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

def create_presentation(title):
    service = build('slides', 'v1', credentials=creds)
    presentation = service.presentations().create(body={
        'title': title
    }).execute()
    print('Created presentation:')
    print(f"Title: {presentation.get('title')}")
    print(f"URL: https://docs.google.com/presentation/d/{presentation.get('presentationId')}")
    return presentation.get('presentationId')

def create_document(title):
    service = build('docs', 'v1', credentials=creds)
    document = service.documents().create(body={
        'title': title
    }).execute()
    print('Created document:')
    print(f"Title: {document.get('title')}")
    print(f"URL: https://docs.google.com/document/d/{document.get('documentId')}")
    return document.get('documentId')

def create_sheet(title):
    service = build('sheets', 'v4', credentials=creds)
    spreadsheet = service.spreadsheets().create(body={
        'properties': {'title': title}
    }).execute()
    print('Created spreadsheet:')
    print(f"Title: {spreadsheet['properties']['title']}")
    print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet['spreadsheetId']}")
    return spreadsheet['spreadsheetId']

# Placeholder for Banana image generation
# def generate_image_with_banana(prompt):
#     # Call Banana API here
#     pass

if __name__ == "__main__":
    # Example usage
    create_presentation("My Automated Presentation")
    create_document("My Automated Document")
    create_sheet("My Automated Sheet")
