#!/usr/bin/env python3
"""
Diagnostic script: Check workflow vs sheet configuration mismatch
"""
import json
import sys
sys.path.insert(0, 'projects/ziyada-system/scripts')

print("="*70)
print("WORKFLOW COLUMN NAME DIAGNOSTIC")
print("="*70)

# Expected column names the workflow recognizes
EXPECTED_COLUMNS = [
    'trigger_status',
    'trigger status', 
    'send_status',
    'send status',
    'workflow_status',
    'workflow status',
    'status',
    'request_status',
    'request status'
]

print("\n1. WORKFLOW EXPECTATIONS:")
print("   The workflow looks for a STATUS column with one of these names:")
for i, col in enumerate(EXPECTED_COLUMNS, 1):
    print(f"     {i}. '{col}'")

print("\n2. REQUIRED VALUE:")
print("   The status column MUST contain one of these values (case-insensitive):")
print("     • 'start'")
print("     • 'continue'")

print("\n3. FLOW LOGIC IN 'Select New Intake Rows' node:")
print("   - Reads all rows from 'Content Intake' sheet")
print("   - Looks for status column (tries names in order above)")
print("   - Filters for rows WHERE status = 'start' OR 'continue'")
print("   - Excludes rows already marked 'done' or 'completed'")
print("   - Processes ONE row per minute (polling interval)")

print("\n4. COMMON ISSUES:")
print("   ✗ Column name is 'switch' - NOT recognized (needs to be one from list above)")
print("   ✗ Column name is 'active' or 'enabled' - NOT recognized")
print("   ✗ Value is 'yes', 'true', '1' - NOT recognized (must be 'start' or 'continue')")
print("   ✗ Extra spaces: ' start ' - Should work (trim is applied)")
print("   ✗ Case: 'START' - Should work (case-insensitive)")

print("\n5. SOLUTION:")
print("   In your 'Content Intake' sheet:")
print("   a) Rename your column FROM 'switch' TO 'trigger_status' (or one of the options)")
print("   b) Set values to exactly 'start' or 'continue'")
print("   c) Re-run test data")

print("\n6. ALTERNATIVE: Add custom column handler")
print("   If you want to keep 'switch' column name, modify the workflow:")
print("   - Edit 'Select New Intake Rows' code node")
print("   - Add: row.switch as another alias in the statusCandidate lookup")

print("\n" + "="*70)
print("TESTING WITH SHEET STRUCTURE CHECK")
print("="*70)

# Try to read the sheet structure without full auth
try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    
    # Try to use token without refresh
    token_file = 'projects/ziyada-system/token_sheets.json'
    with open(token_file, 'r') as f:
        token_data = json.load(f)
    
    print(f"\n✓ Token file found: {token_file}")
    print(f"  Scopes in token: {token_data.get('scopes', ['unknown'])}")
    
    # Note: We can't actually read the sheet without valid credentials
    # but we can at least verify the token structure
    
except FileNotFoundError:
    print(f"\n✗ Token file not found")
except Exception as e:
    print(f"\n  Error: {e}")

print("\n" + "="*70)
print("ACTION ITEMS FOR USER:")
print("="*70)
print("""
1. IMMEDIATE:
   - Open your 'Content Intake' sheet
   - Check the column headers
   - Find your "switch column" - what is it named?
   - Look for columns named: trigger_status, status, send_status, etc.

2. RENAME/UPDATE:
   - If column is named 'switch': RENAME to 'trigger_status'
   - If column is named something else: Add new column 'trigger_status'
   - Fill cells with 'start' (not 'yes', 'true', or '1')

3. RETEST:
   - Add a new test row with Ziyada System data
   - Set trigger_status='start'
   - Wait 1-2 minutes for polling trigger
   - Check 'ContentResults' sheet for output

4. DEBUGGING:
   - If still not working, share column names from your sheet
   - Let's update the workflow to recognize your custom column name
""")

print("="*70)
