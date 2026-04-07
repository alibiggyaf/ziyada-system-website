#!/usr/bin/env python3
"""
Direct cleanup of Google Sheet - bypasses Google auth refresh issues
Uses raw values and direct API calls
"""
import urllib.parse
import json
import urllib.request
import urllib.error
from pathlib import Path

SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
REQUEST_TAB = "Content Intake"

def load_token():
    """Load access token directly"""
    token_path = Path('projects/ziyada-system/token_sheets.json')
    if token_path.exists():
        with open(token_path, 'r') as f:
            return json.load(f)['token']
    raise Exception("Token not found")

def make_sheets_request(url, data=None, method='GET'):
    """Make direct request to Google Sheets API"""
    token = load_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    if data:
        body = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} {e.reason}")
        print(e.read().decode())
        raise

def cleanup_sheet():
    """Clean up the sheet"""
    print("="*70)
    print("SHEET CLEANUP AND REORGANIZATION (Direct)")
    print("="*70)
    
    # Step 1: Read current data
    print("\n1. Reading current sheet data...")
    tab_encoded = urllib.parse.quote(REQUEST_TAB)
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{tab_encoded}!A:I?valueRenderOption=UNFORMATTED_VALUE"
    
    result = make_sheets_request(url)
    rows = result.get('values', [])
    
    if not rows:
        print("✗ No data found")
        return
    
    print(f"✓ Found {len(rows)} rows")
    
    # Step 2: Identify header and data rows
    print("\n2. Processing data...")
    headers = rows[0] if rows else []
    print(f"  Headers: {headers}")
    
    # Find indices for required fields
    try:
        company_name_idx = headers.index('company_name') if 'company_name' in headers else 1
        company_link_idx = headers.index('company_link') if 'company_link' in headers else 4
        send_status_idx = headers.index('send_status') if 'send_status' in headers else 6
    except ValueError:
        company_name_idx = 1
        company_link_idx = 4
        send_status_idx = 6
    
    print(f"  company_name column: {company_name_idx}")
    print(f"  company_link column: {company_link_idx}")
    print(f"  send_status column: {send_status_idx}")
    
    # Step 3: Filter data - keep only non-empty rows with required fields
    print("\n3. Filtering empty rows...")
    cleaned_rows = [headers]  # Keep header
    
    removed_count = 0
    for i, row in enumerate(rows[1:], 1):
        # Ensure row has enough columns
        while len(row) < len(headers):
            row.append('')
        
        # Check if row has required fields
        company_name = row[company_name_idx].strip() if company_name_idx < len(row) else ''
        company_link = row[company_link_idx].strip() if company_link_idx < len(row) else ''
        
        # Keep row if it has company_name AND company_link
        if company_name and company_link:
            cleaned_rows.append(row[:len(headers)])  # Trim to header length
            print(f"  ✓ Row {i}: {company_name}")
        else:
            removed_count += 1
    
    print(f"\n✓ Removed {removed_count} empty rows")
    print(f"✓ Kept {len(cleaned_rows)-1} valid rows")
    
    # Step 4: Write cleaned data back
    print("\n4. Writing cleaned data back to sheet...")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{tab_encoded}!A:I?valueInputOption=RAW_INPUT"
    
    # First clear the range
    clear_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{tab_encoded}!A:I:clear"
    make_sheets_request(clear_url, {}, method='POST')
    
    # Then write the cleaned data
    data = {
        'values': cleaned_rows
    }
    result = make_sheets_request(url, data, method='PUT')
    
    print(f"✓ Updated sheet with {result.get('updatedRows', 0)} rows")
    
    # Step 5: Set column widths
    print("\n5. Setting column widths...")
    batch_update_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}:batchUpdate"
    
    batch_data = {
        "requests": [
            {
                "updateSheetProperties": {
                    "fields": "gridProperties.columnCount",
                    "properties": {
                        "sheetId": 0,
                        "gridProperties": {"columnCount": 9}
                    }
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": 0,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 9
                    },
                    "properties": {
                        "pixelSize": 150
                    },
                    "fields": "pixelSize"
                }
            }
        ]
    }
    
    make_sheets_request(batch_update_url, batch_data, method='POST')
    print("✓ Column widths optimized")
    
    print("\n" + "="*70)
    print("✓ CLEANUP COMPLETE!")
    print("="*70)
    print(f"\nSummary:")
    print(f"  - Removed: {removed_count} empty rows")
    print(f"  - Kept: {len(cleaned_rows)-1} valid rows (with company_name & company_link)")
    print(f"  - Ready for new data entry")

if __name__ == '__main__':
    try:
        cleanup_sheet()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
