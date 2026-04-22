#!/usr/bin/env python3
import json
import subprocess

VOICE = "https://n8n.srv953562.hstgr.cloud/webhook/voice-ingress-webhook"


def post(payload):
    cmd = [
        "curl",
        "-s",
        "-X",
        "POST",
        VOICE,
        "-H",
        "Content-Type: application/json",
        "-d",
        json.dumps(payload, ensure_ascii=False),
    ]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


payload1 = {
    "message": {
        "toolCallList": [
            {
                "id": "tc9",
                "function": {
                    "name": "save_lead",
                    "arguments": json.dumps({
                        "name": "سعود التست",
                        "phone": "0551230099",
                        "service_interest": "CRM",
                    }, ensure_ascii=False),
                },
            }
        ]
    }
}

payload2 = {
    "message": {
        "toolCallList": [
            {
                "id": "tc10",
                "function": {
                    "name": "create_booking_request",
                    "arguments": json.dumps({
                        "name": "سعود التست",
                        "phone": "0551230099",
                        "service": "Business Automation",
                        "preferred_datetime": "الاثنين 10:30",
                        "notes": "اختبار",
                    }, ensure_ascii=False),
                },
            }
        ]
    }
}

payload3 = {
    "voice": {
        "session_id": "phone-0551230099",
        "transcript": "وش خدماتكم؟",
        "language": "ar",
        "provider": "vapi",
    }
}

payload4 = {
    "message": {
        "toolCallList": [
            {
                "id": "tc11",
                "function": {
                    "name": "get_conversation_history",
                    "arguments": json.dumps({"phone": "0551230099"}, ensure_ascii=False),
                },
            }
        ]
    }
}

print("save_lead test:")
print(post(payload1))
print("\ncreate_booking_request test:")
print(post(payload2))
print("\nvoice transcript test:")
print(post(payload3))
print("\nget_conversation_history test:")
print(post(payload4))
