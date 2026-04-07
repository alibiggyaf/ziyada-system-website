#!/usr/bin/env python3
"""
Populate Ziyada System Google Slides using OAuth2 authentication
"""
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DECK_ID = "1DtD9wyNWoJrOd1hj3AQXrOBSe2UNwAB70mRTlbtliNo"
SCOPES = ["https://www.googleapis.com/auth/presentations"]

COLORS = {
    "deepNavy": {"red": 23/255, "green": 28/255, "blue": 43/255},
    "midnightBlue": {"red": 20/255, "green": 29/255, "blue": 53/255},
}

SLIDES = [
    {"bg": "deepNavy", "title": "Ziyada System", "subtitle": "نحن لا نبيع التقنية، نحن نبسط أعمالك"},
    {"bg": "deepNavy", "title": "What We Build", "subtitle": "مزيج من بنية تحتية مرنة"},
    {"bg": "midnightBlue", "title": "What We're NOT", "subtitle": "نحن لسنا شركة 'نظم معلومات' تقليدية"},
    {"bg": "deepNavy", "title": "Services", "subtitle": "Strategy, Engineering, DevOps"},
    {"bg": "midnightBlue", "title": "Why Ziyada?", "subtitle": "لأننا مسؤولون لا هواة"},
    {"bg": "deepNavy", "title": "Approach", "subtitle": "منهجية واضحة، شفافة"},
    {"bg": "midnightBlue", "title": "Who We Serve", "subtitle": "المؤسسات التقنية والفرق الصغيرة"},
    {"bg": "deepNavy", "title": "Values", "subtitle": "قيمنا: المسؤولية، الشفافية"},
    {"bg": "midnightBlue", "title": "Social Proof", "subtitle": "عملاؤنا يشهدون بجودتنا"},
    {"bg": "deepNavy", "title": "Ready to Talk?", "subtitle": "هل أنت مستعد؟"},
    {"bg": "midnightBlue", "title": "Ziyada System", "subtitle": "built by operators for operators"},
]

def authenticate():
    creds = None
    token_path = Path("token.json")
    cred_path = Path("credentials.json")
    
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
    
    # Fresh OAuth flow - use fixed port 8080
    flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
    print("\n🌐 Opening browser for authorization...")
    print("If browser doesn't open, copy this URL and paste it manually:\n")
    creds = flow.run_local_server(port=8080, open_browser=False)
    
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    
    return creds

def populate():
    print("🔐 Authenticating with Google Slides...")
    creds = authenticate()
    
    service = build("slides", "v1", credentials=creds)
    print("✅ Authenticated\n")
    
    # Get presentation
    pres = service.presentations().get(presentationId=DECK_ID).execute()
    slides = [s.get("objectId") for s in pres.get("slides", [])]
    
    if len(slides) < len(SLIDES):
        print(f"Creating {len(SLIDES) - len(slides)} more slides...")
        reqs = []
        for i in range(len(slides), len(SLIDES)):
            reqs.append({
                "createSlide": {
                    "insertionIndex": i,
                    "slideLayoutReference": {"predefinedLayout": "BLANK"}
                }
            })
        service.presentations().batchUpdate(presentationId=DECK_ID, body={"requests": reqs}).execute()
        pres = service.presentations().get(presentationId=DECK_ID).execute()
        slides = [s.get("objectId") for s in pres.get("slides", [])]
    
    # Add content to each slide
    batch_requests = []
    for idx, slide_id in enumerate(slides[:len(SLIDES)]):
        slide_info = SLIDES[idx]
        color = COLORS[slide_info["bg"]]
        
        # Set background
        batch_requests.append({
            "updateSlideProperties": {
                "objectId": slide_id,
                "fields": "pageProperties.pageBackgroundFill.solidFill.color",
                "pageProperties": {
                    "pageBackgroundFill": {
                        "solidFill": {"color": {"rgbColor": color}}
                    }
                }
            }
        })
        
        # Add title
        title_id = f"title_{idx}"
        batch_requests.append({
            "createShape": {
                "objectId": title_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": 900, "unit": "PT"},
                             "height": {"magnitude": 150, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1,
                                   "translateX": 50, "translateY": 100, "unit": "PT"}
                }
            }
        })
        batch_requests.append({
            "insertText": {
                "objectId": title_id,
                "insertionIndex": 0,
                "text": slide_info["title"]
            }
        })
        batch_requests.append({
            "updateTextStyle": {
                "objectId": title_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontSize": {"magnitude": 60, "unit": "PT"},
                    "bold": True,
                    "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 230/255, "green": 233/255, "blue": 242/255}}}
                },
                "fields": "fontSize,bold,foregroundColor"
            }
        })
        
        # Add subtitle
        subtitle_id = f"subtitle_{idx}"
        batch_requests.append({
            "createShape": {
                "objectId": subtitle_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": 900, "unit": "PT"},
                             "height": {"magnitude": 100, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1,
                                   "translateX": 50, "translateY": 280, "unit": "PT"}
                }
            }
        })
        batch_requests.append({
            "insertText": {
                "objectId": subtitle_id,
                "insertionIndex": 0,
                "text": slide_info["subtitle"]
            }
        })
        batch_requests.append({
            "updateTextStyle": {
                "objectId": subtitle_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontSize": {"magnitude": 32, "unit": "PT"},
                    "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 230/255, "green": 233/255, "blue": 242/255}}}
                },
                "fields": "fontSize,foregroundColor"
            }
        })
    
    # Execute batch
    print(f"📝 Updating {len(slides)} slides...")
    service.presentations().batchUpdate(
        presentationId=DECK_ID,
        body={"requests": batch_requests}
    ).execute()
    
    print("✅ All slides populated!\n")
    print(f"🔗 View your presentation:")
    print(f"   https://docs.google.com/presentation/d/{DECK_ID}/edit\n")

if __name__ == "__main__":
    populate()
