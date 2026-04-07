#!/usr/bin/env python3
"""
End-to-end test: Add Ziyada System data to Content Intake sheet and verify workflow output
"""
import os
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configuration
SHEET_ID = "1sUiWimjYYAn_vgVplotMPfKXqI2iuQBzwrAzxgMrW6s"
REQUEST_TAB = "Content Intake"
RESULTS_TAB = "ContentResults"
SA_FILE = "projects/ziyada-system/client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json"

def get_sheets_service():
    """Authenticate and get Google Sheets service"""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials as UserCredentials
    import json
    
    # Try token_sheets.json first (OAuth2 user token)
    token_file = "projects/ziyada-system/token_sheets.json"
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        creds = UserCredentials.from_authorized_user_info(
            token_data,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        # Refresh if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build('sheets', 'v4', credentials=creds)
    
    # Fallback to service account
    creds = Credentials.from_service_account_file(
        SA_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)

def add_test_row():
    """Add Ziyada System test row to Content Intake sheet"""
    service = get_sheets_service()
    
    test_row = [
        "ZIYADA-TEST-001",  # request_id
        "Ziyada System",     # company_name
        "Software/Tech",     # industry
        "Business Leaders, Entrepreneurs",  # target_audience
        "https://ziyada.com",  # company_link
        "Write about Ziyada System's AI-powered content automation platform and how it transforms workflow efficiency", # writer_task
        "start"  # trigger_status (THE KEY COLUMN)
    ]
    
    values = [test_row]
    body = {'values': values}
    
    result = service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{REQUEST_TAB}!A:G",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    print("✓ Added test row to Content Intake:")
    print(f"  Request ID: {test_row[0]}")
    print(f"  Company: {test_row[1]}")
    print(f"  Industry: {test_row[2]}")
    print(f"  Audience: {test_row[3]}")
    print(f"  Link: {test_row[4]}")
    print(f"  Task: {test_row[5][:60]}...")
    print(f"  Trigger Status: {test_row[6]}")
    print(f"  Updated cells: {result.get('updates', {}).get('updatedCells', 0)}")
    
    return test_row

def check_results(request_id):
    """Poll ContentResults for the test row"""
    service = get_sheets_service()
    
    print(f"\nWaiting for workflow to process (polling every 3 seconds)...")
    max_wait = 60  # 60 seconds
    elapsed = 0
    
    while elapsed < max_wait:
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=SHEET_ID,
                range=f"{RESULTS_TAB}!A:H"
            ).execute()
            
            values = result.get('values', [])
            
            # Search for our test row
            for i, row in enumerate(values[1:], start=2):  # Skip header
                if len(row) > 0 and request_id in str(row[0]):
                    print(f"✓ Found result row at line {i}!")
                    print(f"  Request ID: {row[0] if len(row) > 0 else 'N/A'}")
                    print(f"  Status: {row[1] if len(row) > 1 else 'N/A'}")
                    print(f"  Generated Content: {str(row[2])[:100] if len(row) > 2 else 'N/A'}...")
                    return True
            
            elapsed += 3
            print(f"  [{elapsed}s] No result yet, waiting...")
            time.sleep(3)
            
        except Exception as e:
            print(f"  Error checking results: {e}")
            time.sleep(3)
            elapsed += 3
    
    print(f"✗ No result found after {max_wait}s")
    return False

def main():
    print("="*70)
    print("ZIYADA SYSTEM WORKFLOW END-TO-END TEST")
    print("="*70)
    
    try:
        # Step 1: Add test row
        test_row = add_test_row()
        request_id = test_row[0]
        
        # Step 2: Wait and check for results
        time.sleep(2)  # Give workflow a chance to pick up the change
        success = check_results(request_id)
        
        if success:
            print("\n" + "="*70)
            print("✓ TEST PASSED: Workflow executed successfully!")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("✗ TEST FAILED: No output generated")
            print("="*70)
            print("\nDEBUGGING TIPS:")
            print("1. Check that trigger_status column is set to 'start' or 'continue'")
            print("2. Verify the Poll Intake Schedule is running (every 1 minute)")
            print("3. Check n8n logs for any workflow execution errors")
            print("4. Ensure all API credentials are valid")
            
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
