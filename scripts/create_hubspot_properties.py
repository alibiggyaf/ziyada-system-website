
import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Load your HubSpot Private App Token from environment variable
HUBSPOT_TOKEN = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN")

if not HUBSPOT_TOKEN:
    raise Exception("HUBSPOT_PRIVATE_APP_TOKEN not set in environment variables.")

API_URL = "https://api.hubapi.com/crm/v3/properties/contacts"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

PROPERTIES = [
    {
        "name": "service_interest",
        "label": "Service Interest",
        "groupName": "contactinformation",
        "type": "enumeration",
        "fieldType": "checkbox",
        "options": [
            {"label": "Automation", "value": "automation"},
            {"label": "CRM", "value": "crm"},
            {"label": "Lead Generation", "value": "lead-generation"},
            {"label": "Marketing", "value": "marketing"},
            {"label": "Web Development", "value": "web-development"},
            {"label": "Social Media", "value": "social-media"}
        ]
    },
    {
        "name": "budget_range",
        "label": "Budget Range",
        "groupName": "contactinformation",
        "type": "enumeration",
        "fieldType": "select",
        "options": [
            {"label": "<5000", "value": "<5000"},
            {"label": "5000-15000", "value": "5000-15000"},
            {"label": "15000-50000", "value": "15000-50000"},
            {"label": "50000+", "value": "50000+"}
        ]
    },
    {
        "name": "timeline",
        "label": "Timeline",
        "groupName": "contactinformation",
        "type": "enumeration",
        "fieldType": "select",
        "options": [
            {"label": "Immediate", "value": "immediate"},
            {"label": "1-3 Months", "value": "1-3months"},
            {"label": "3-6 Months", "value": "3-6months"},
            {"label": "Exploring", "value": "exploring"}
        ]
    },
    {
        "name": "source_page",
        "label": "Source Page",
        "groupName": "contactinformation",
        "type": "string",
        "fieldType": "text"
    },
    {
        "name": "language_preference",
        "label": "Language Preference",
        "groupName": "contactinformation",
        "type": "enumeration",
        "fieldType": "select",
        "options": [
            {"label": "Arabic", "value": "ar"},
            {"label": "English", "value": "en"}
        ]
    },
    {
        "name": "utm_source",
        "label": "UTM Source",
        "groupName": "contactinformation",
        "type": "string",
        "fieldType": "text"
    },
    {
        "name": "utm_medium",
        "label": "UTM Medium",
        "groupName": "contactinformation",
        "type": "string",
        "fieldType": "text"
    },
    {
        "name": "utm_campaign",
        "label": "UTM Campaign",
        "groupName": "contactinformation",
        "type": "string",
        "fieldType": "text"
    }
]

def create_property(prop):
    resp = requests.post(API_URL, headers=HEADERS, json=prop)
    if resp.status_code == 409:
        print(f"Property '{prop['name']}' already exists.")
    elif resp.status_code == 201:
        print(f"Property '{prop['name']}' created successfully.")
    else:
        print(f"Error creating '{prop['name']}': {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    for prop in PROPERTIES:
        create_property(prop)
