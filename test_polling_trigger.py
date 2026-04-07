#!/usr/bin/env python3
"""
Test the polling trigger path (Google Sheets)
Add test data directly to the sheet with trigger_status='start'
"""
import json
import time
import os
from pathlib import Path

# Try multiple token locations
token_locations = [
    'projects/ziyada-system/token_sheets.json',
    'projects/ziyada-system/token.json',
    'token_sheets.json'
]

def load_credentials():
    """Load OAuth credentials from token file"""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    
    for token_path in token_locations:
        if Path(token_path).exists():
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            try:
                creds = Credentials.from_authorized_user_info(
                    token_data,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                # Only attempt refresh if we have a refresh token
                if creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"  Warning: Could not refresh token ({e}), using cached token")
                return creds
            except Exception as e:
                pass
    
    raise Exception("No valid Google Sheets token found")

def main():
    from googleapiclient.discovery import build
    
    print("="*70)
    print("TESTING POLLING TRIGGER PATH (Google Sheets)")
    print("="*70)
    
    SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
    REQUEST_TAB = "Content Intake"
    RESULTS_TAB = "ContentResults"
    
    try:
        print("\n1. Loading Google Sheets credentials...")
        creds = load_credentials()
        print("   ✓ Credentials loaded")
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Read current state
        print("\n2. Checking current sheet state...")
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=f"{REQUEST_TAB}!A1:H"
        ).execute()
        
        rows = result.get('values', [])
        print(f"   Sheet '{ REQUEST_TAB}' has {len(rows)} rows")
        if len(rows) > 0:
            print(f"   Headers: {rows[0]}")
        
        # Append test row with trigger_status
        print("\n3. Adding Ziyada System test row with trigger_status='start'...")
        test_row = [
            "ZIYADA-TEST-POLL" + str(int(time.time())),  # request_id
            "Ziyada System",                                # company_name
            "Software/Tech/AI",                            # industry
            "Entrepreneurs, Business Leaders",            # target_audience
            "https://ziyada.com",                          # company_link
            "Write about Ziyada System's AI platform transforming content creation automation for brands", # writer_task
            "start"                                        # trigger_status (CRITICAL)
        ]
        
        values = [test_row]
        body = {'values': values}
        
        append_result = service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=f"{REQUEST_TAB}!A:G",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        
        print(f"   ✓ Row added")
        print(f"   Request ID: {test_row[0]}")
        print(f"   Trigger Status: {test_row[6]}")
        
        request_id = test_row[0]
        
        # Wait for workflow to poll and process
        print("\n4. Waiting for polling trigger to pick up the row...")
        print("   (Polls happen every 1 minute - monitoring for 90 seconds)")
        
        max_wait = 90  # 90 seconds
        check_interval = 5  # Check every 5 seconds
        elapsed = 0
        found = False
        
        while elapsed < max_wait and not found:
            try:
                # Check ContentResults for our output
                result = service.spreadsheets().values().get(
                    spreadsheetId=SHEET_ID,
                    range=f"{RESULTS_TAB}!A:H"
                ).execute()
                
                result_rows = result.get('values', [])
                
                # Search for our request_id
                for i, row in enumerate(result_rows[1:], start=2):  # Skip header
                    if len(row) > 0 and request_id in str(row[0]):
                        found = True
                        print(f"\n   ✓✓✓ RESULT FOUND AT ROW {i}!")
                        print(f"   Request ID: {row[0] if len(row) > 0 else 'N/A'}")
                        print(f"   Status: {row[1] if len(row) > 1 else 'N/A'}")
                        if len(row) > 2:
                            content = str(row[2])[:150]
                            print(f"   Generated Content: {content}...")
                        break
                
                if not found:
                    elapsed += check_interval
                    print(f"   [{elapsed}s] No result yet...")
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"   Error checking results: {e}")
                time.sleep(check_interval)
                elapsed += check_interval
        
        if found:
            print("\n" + "="*70)
            print("✓ SUCCESS: Polling trigger worked!")
            print("  The workflow picked up the row and generated output")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("✗ FAILED: No output generated after 90 seconds")
            print("="*70)
            print("\nDEBUGGING: Possible issues:")
            print("1. Polling schedule not running (needs workflow active=true)")
            print("2. Column name mismatch - workflow expects 'trigger_status', 'send_status', etc")
            print("3. Value not exactly 'start' or 'continue' (case sensitive)")
            print("4. Workflow encountered an error - check n8n logs")
            print("5. Google Sheets credentials expired or insufficient permissions")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
