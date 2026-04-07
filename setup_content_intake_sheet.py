#!/usr/bin/env python3
"""
Setup Google Sheets with proper data validation for manual input
- Adds dropdown validators to trigger column
- Creates filter option columns for user selection
- No auto-filling of company information
"""
import json
from pathlib import Path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
REQUEST_TAB = "Content Intake"

def load_credentials():
    """Load OAuth credentials"""
    token_locations = [
        'projects/ziyada-system/token_sheets.json',
        'projects/ziyada-system/token.json',
    ]
    
    for token_path in token_locations:
        if Path(token_path).exists():
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            try:
                creds = Credentials.from_authorized_user_info(
                    token_data,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                if creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except:
                        pass
                return creds
            except:
                pass
    
    raise Exception("No valid Google Sheets token found")

def setup_sheet_structure():
    """Setup sheet with proper column headers and data validation"""
    print("="*70)
    print("SETTING UP CONTENT INTAKE SHEET")
    print("="*70)
    
    creds = load_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    # Step 1: Define proper header row
    print("\n1. Setting up sheet structure...")
    headers = [
        "request_id",           # A - Auto-generated or manually provided
        "company_name",         # B - User must enter (NO AUTO-FILL)
        "industry",             # C - Dropdown options
        "target_audience",      # D - Dropdown options
        "company_link",         # E - User must enter (NO AUTO-FILL)
        "writer_task",          # F - User input task/prompt
        "trigger_status"        # G - Dropdown: start/continue
    ]
    
    # Update header row
    header_values = [headers]
    body = {'values': header_values}
    
    try:
        result = service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"{REQUEST_TAB}!A1:G1",
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"   ✓ Headers set: {headers}")
    except Exception as e:
        print(f"   ✗ Error setting headers: {e}")
        return
    
    # Step 2: Add data validation dropdowns
    print("\n2. Adding dropdown validators...")
    
    requests = []
    
    # Dropdown for industry (Column C) - rows 2-1000
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": 0,  # First sheet
                "dimension": "ROWS",
                "startIndex": 1,  # Row 2
                "endIndex": 1000
            },
            "rule": {
                "condition": {
                    "type": "LIST",
                    "values": [
                        {"userEnteredValue": "Technology"},
                        {"userEnteredValue": "Software/SaaS"},
                        {"userEnteredValue": "E-Commerce"},
                        {"userEnteredValue": "Fashion"},
                        {"userEnteredValue": "Beauty"},
                        {"userEnteredValue": "Healthcare"},
                        {"userEnteredValue": "Finance"},
                        {"userEnteredValue": "Education"},
                        {"userEnteredValue": "Media/Publishing"},
                        {"userEnteredValue": "Other"}
                    ]
                },
                "inputMessage": "Select an industry",
                "strict": False,
                "showCustomUi": True
            },
            "range": {
                "sheetId": 0,
                "startRowIndex": 1,
                "endRowIndex": 1000,
                "startColumnIndex": 2,  # Column C
                "endColumnIndex": 3
            }
        }
    })
    
    # Dropdown for target_audience (Column D) - rows 2-1000
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": 0,
                "startRowIndex": 1,
                "endRowIndex": 1000,
                "startColumnIndex": 3,  # Column D
                "endColumnIndex": 4
            },
            "rule": {
                "condition": {
                    "type": "LIST",
                    "values": [
                        {"userEnteredValue": "Business Leaders"},
                        {"userEnteredValue": "Entrepreneurs"},
                        {"userEnteredValue": "Young Professionals"},
                        {"userEnteredValue": "Students"},
                        {"userEnteredValue": "Consumers"},
                        {"userEnteredValue": "Enterprise Customers"},
                        {"userEnteredValue": "Developers"},
                        {"userEnteredValue": "Designers"},
                        {"userEnteredValue": "Marketing Teams"},
                        {"userEnteredValue": "Other"}
                    ]
                },
                "inputMessage": "Select target audience",
                "strict": False,
                "showCustomUi": True
            }
        }
    })
    
    # Dropdown for trigger_status (Column G) - rows 2-1000
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": 0,
                "startRowIndex": 1,
                "endRowIndex": 1000,
                "startColumnIndex": 6,  # Column G
                "endColumnIndex": 7
            },
            "rule": {
                "condition": {
                    "type": "LIST",
                    "values": [
                        {"userEnteredValue": "start"},
                        {"userEnteredValue": "continue"},
                        {"userEnteredValue": "pause"}
                    ]
                },
                "inputMessage": "Select workflow trigger status",
                "strict": True,
                "showCustomUi": True
            }
        }
    })
    
    # Apply all validations
    try:
        body = {'requests': requests}
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body=body
        ).execute()
        print(f"   ✓ Data validation added:")
        print(f"     - Column C (industry): 10 predefined options")
        print(f"     - Column D (target_audience): 10 predefined options")
        print(f"     - Column G (trigger_status): start/continue/pause")
    except Exception as e:
        print(f"   ✗ Error adding validation: {e}")
        return
    
    # Step 3: Add example empty row with formatting
    print("\n3. Adding example row (empty for manual entry)...")
    example_row = [
        "REQ-2026-001",  # request_id - can be auto or manual
        "",              # company_name - EMPTY (user must fill)
        "",              # industry - dropdown
        "",              # target_audience - dropdown
        "",              # company_link - EMPTY (user must fill)
        "",              # writer_task - user enters prompt
        ""               # trigger_status - dropdown
    ]
    
    try:
        body = {'values': [example_row]}
        result = service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=f"{REQUEST_TAB}!A2:G2",
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"   ✓ Example row added (row 2)")
    except Exception as e:
        print(f"   ✗ Error adding example: {e}")
    
    print("\n" + "="*70)
    print("✓ SHEET SETUP COMPLETE")
    print("="*70)
    print("\nINSTRUCTIONS FOR MANUAL DATA ENTRY:")
    print("-" * 70)
    print("""
1. COLUMN A - request_id:
   - Optional: Generate your own ID or let system generate
   - Example: REQ-2026-001, REQ-AEONABAYA-001

2. COLUMN B - company_name (MANUAL ENTRY):
   - Type the actual company name
   - Example: "Aeonabaya", "Your Company Name"
   - NO AUTO-FILLING

3. COLUMN C - industry (DROPDOWN):
   - Click cell and select from dropdown list
   - Example: "Technology", "Fashion", "E-Commerce"

4. COLUMN D - target_audience (DROPDOWN):
   - Click cell and select from dropdown list
   - Example: "Business Leaders", "Entrepreneurs"

5. COLUMN E - company_link (MANUAL ENTRY):
   - Type the company website URL
   - Example: "https://aeonabaya.net"
   - NO AUTO-FILLING

6. COLUMN F - writer_task:
   - Type your custom task/prompt for AI writer
   - Example: "Write about Aeonabaya's luxury abayas and modern fashion"

7. COLUMN G - trigger_status (DROPDOWN):
   - Select "start" to trigger the workflow
   - Select "continue" for ongoing batch processing
   - Select "pause" to skip

WEBHOOK TRIGGER:
- The workflow also responds to direct webhook POST requests
- Send company data via Telegram bot @Aliabadi_Ai_Agent_bot
- Webhook will process immediately (no polling delay)

TESTING:
1. Fill in one complete row manually
2. Set trigger_status = "start"
3. Either:
   a) Wait 1-2 minutes for polling trigger, OR
   b) Send Telegram message to trigger webhook immediately
4. Check 'ContentResults' sheet for output within 2 minutes
    """)
    print("="*70)

if __name__ == "__main__":
    try:
        setup_sheet_structure()
    except Exception as e:
        print(f"\n✗ Setup error: {e}")
        import traceback
        traceback.print_exc()
