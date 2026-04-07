#!/usr/bin/env python3
"""
Test the workflow by sending a direct webhook request
This bypasses the polling mechanism
"""
import urllib.request
import json
import time

WEBHOOK_URL = "https://n8n.srv953562.hstgr.cloud/webhook/ziyada-blog-ingest"

# Create test payload similar to what would come from Telegram
test_payload = {
    "update_id": 123456789,
    "message": {
        "message_id": 1,
        "date": int(time.time()),
        "chat": {
            "id": -1001234567890,
            "type": "supergroup"
        },
        "text": "اسم الشركة: Ziyada System\nالمجال: Software/Tech\nالجمهور: Business Leaders\nالموقع: https://ziyada.com\nالموضوع: AI-powered content automation"
    }
}

# Then followup with trigger message
trigger_payload = {
    "update_id": 123456790,
    "message": {
        "message_id": 2,
        "date": int(time.time()),
        "chat": {
            "id": -1001234567890,
            "type": "supergroup"
        },
        "text": "ابدأ التنفيذ",
        "reply_to_message": test_payload["message"]
    }
}

def send_webhook(data, description):
    """Send data to webhook"""
    headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✓ {description}")
            print(f"  Status: {response.status}")
            print(f"  Response: {result[:200]}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"✗ {description} - HTTP {e.code}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"  Error: {error_body[:200]}")
        except:
            pass
        return False
    except Exception as e:
        print(f"✗ {description} - Error: {e}")
        return False

print("="*70)
print("TESTING ZIYADA SYSTEM WORKFLOW VIA WEBHOOK")
print("="*70)

print("\n1. Sending company details via Telegram simulation...")
send_webhook(test_payload, "Company details sent")

print("\n2. Waiting 5 seconds...")
time.sleep(5)

print("\n3. Sending trigger command (ابدأ التنفيذ - Start Execution)...")
send_webhook(trigger_payload, "Trigger command sent")

print("\n" + "="*70)
print("Webhook test complete!")
print("Check the n8n workflow editor to see if execution occurred")
print("="*70)
