#!/usr/bin/env python3
"""
Clean up and reorganize Google Sheet
- Remove unnecessary columns
- Consolidate data
- Remove empty rows
- Create clean structure
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
        'projects/ziyada-system/token.json',
        'projects/ziyada-system/token_sheets.json',
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
                return creds
            except Exception as e:
                print(f"Warning: Could not use {token_path}: {e}")
                pass
    
    raise Exception("No valid Google Sheets token found")

def cleanup_sheet():
    """Reorganize and clean the sheet"""
    print("="*70)
    print("SHEET CLEANUP AND REORGANIZATION")
    print("="*70)
    
    creds = load_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    # Step 1: Read current data
    print("\n1. Reading current sheet structure...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{REQUEST_TAB}!A:I"
    ).execute()
    
    all_rows = result.get('values', [])
    headers = all_rows[0] if all_rows else []
    data_rows = all_rows[1:] if len(all_rows) > 1 else []
    
    print(f"   Found {len(all_rows)} rows total (including header)")
    print(f"   Headers: {len(headers)} columns")
    print(f"   Data rows: {len(data_rows)}")
    
    # Step 2: Filter out completely empty rows
    print("\n2. Removing completely empty rows...")
    non_empty_rows = []
    empty_count = 0
    
    for i, row in enumerate(data_rows, start=2):
        # Check if row has any non-empty values
        has_content = any(str(cell).strip() for cell in row if cell)
        if has_content:
            non_empty_rows.append(row)
        else:
            empty_count += 1
    
    print(f"   Removed {empty_count} empty rows")
    print(f"   Kept {len(non_empty_rows)} rows with data")
    
    # Step 3: Clean up data - ensure required columns have values
    print("\n3. Validating and cleaning data...")
    
    # Expected column indices (from your headers)
    col_names = {
        'request_id': 0,
        'company_name': 1,
        'industry': 2,
        'target_audience': 3,
        'company_link': 4,
        'topic': 5,
        'send_status': 6,
        'approval_status': 7,
        'writer_task': 8
    }
    
    cleaned_rows = []
    for row in non_empty_rows:
        # Expand row to 9 columns if needed
        while len(row) < 9:
            row.append("")
        
        # Ensure critical fields aren't empty
        company_name = str(row[col_names['company_name']]).strip()
        company_link = str(row[col_names['company_link']]).strip()
        
        if company_name and company_link:  # Only keep rows with both required fields
            cleaned_rows.append(row[:9])  # Keep only 9 columns
    
    print(f"   Kept {len(cleaned_rows)} rows with complete required data")
    
    # Step 4: Update the sheet
    print("\n4. Writing cleaned data back to sheet...")
    
    # Rebuild all data with header
    final_data = [headers] + cleaned_rows
    
    # Clear the sheet first
    service.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID,
        range=f"{REQUEST_TAB}!A:I"
    ).execute()
    
    # Write cleaned data
    body = {'values': final_data}
    result = service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"{REQUEST_TAB}!A1:I{len(final_data)}",
        valueInputOption="RAW",
        body=body
    ).execute()
    
    print(f"   ✓ Cleaned sheet written back")
    print(f"   Total rows (including header): {len(final_data)}")
    print(f"   Data rows: {len(cleaned_rows)}")
    
    # Step 5: Set column widths for better readability
    print("\n5. Setting column widths...")
    
    requests = [
        # request_id - A
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1
                },
                "properties": {
                    "pixelSize": 150
                },
                "fields": "pixelSize"
            }
        },
        # company_name - B
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": 2
                },
                "properties": {
                    "pixelSize": 150
                },
                "fields": "pixelSize"
            }
        },
        # industry - C
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 2,
                    "endIndex": 3
                },
                "properties": {
                    "pixelSize": 120
                },
                "fields": "pixelSize"
            }
        },
        # target_audience - D
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 3,
                    "endIndex": 4
                },
                "properties": {
                    "pixelSize": 150
                },
                "fields": "pixelSize"
            }
        },
        # company_link - E
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 4,
                    "endIndex": 5
                },
                "properties": {
                    "pixelSize": 180
                },
                "fields": "pixelSize"
            }
        },
        # topic - F
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 5,
                    "endIndex": 6
                },
                "properties": {
                    "pixelSize": 150
                },
                "fields": "pixelSize"
            }
        },
        # send_status - G
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 6,
                    "endIndex": 7
                },
                "properties": {
                    "pixelSize": 100
                },
                "fields": "pixelSize"
            }
        },
        # approval_status - H
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 7,
                    "endIndex": 8
                },
                "properties": {
                    "pixelSize": 120
                },
                "fields": "pixelSize"
            }
        },
        # writer_task - I
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 8,
                    "endIndex": 9
                },
                "properties": {
                    "pixelSize": 200
                },
                "fields": "pixelSize"
            }
        }
    ]
    
    try:
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body=body
        ).execute()
        print(f"   ✓ Column widths adjusted for readability")
    except Exception as e:
        print(f"   ⚠ Column width adjustment skipped: {e}")
    
    print("\n" + "="*70)
    print("✓ SHEET CLEANUP COMPLETE")
    print("="*70)
    
    print("""
IMPORTANT - FIX FOR ROW 17 (Ziyada System):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your row was removed if it was incomplete. Check these REQUIRED fields:
✓ Column B (company_name): Must have value - "Ziyada System"
✓ Column E (company_link): Must have value - "https://ziyada.com"  ← KEY!
✓ Column G (send_status): Must be "start" or "continue"

Add a new row with COMPLETE data:
1. request_id: ZIYADA-20260329
2. company_name: Ziyada System
3. industry: Software/AI
4. target_audience: Business Leaders
5. company_link: https://ziyada.com        ← MUST NOT BE EMPTY!
6. topic: AI content automation
7. send_status: start                       ← TRIGGER!
8. approval_status: approved (optional)
9. writer_task: (optional description)

Then wait 2 minutes for polling trigger.
    """)

if __name__ == "__main__":
    try:
        cleanup_sheet()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
