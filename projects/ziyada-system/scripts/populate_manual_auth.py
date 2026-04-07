#!/usr/bin/env python3
"""OAuth flow for Google Slides with automatic localhost callback handling."""
import json
from pathlib import Path
import sys
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import urlopen

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DECK_ID = "1DtD9wyNWoJrOd1hj3AQXrOBSe2UNwAB70mRTlbtliNo"
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent


def load_client_config():
    """Load OAuth client config, preferring known-good desktop credentials file."""
    candidates = [
        PROJECT_DIR / "client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json",
        PROJECT_DIR / "credentials.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            raw = path.read_text().strip()
            if not raw:
                continue
            # Some files may contain trailing garbage after JSON. Keep only the JSON object.
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1 or end <= start:
                continue
            data = json.loads(raw[start:end + 1])
            if "installed" in data and data["installed"].get("client_id"):
                return "installed", data["installed"]
            if "web" in data and data["web"].get("client_id"):
                return "web", data["web"]
        except Exception:
            continue
    raise RuntimeError("No valid OAuth client configuration found.")


def build_auth_url(client_id, redirect_uri):
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    return "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)


def exchange_code_for_token(code, client_id, client_secret, redirect_uri):
    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    data = urlencode(payload).encode("utf-8")
    with urlopen("https://oauth2.googleapis.com/token", data=data) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_code(user_input):
    """Accept either a raw code or a full localhost callback URL and return code."""
    text = user_input.strip()
    if not text:
        return ""
    if "http://" in text or "https://" in text:
        try:
            parsed = urlparse(text)
            q = parse_qs(parsed.query)
            if "code" in q and q["code"]:
                return q["code"][0]
        except Exception:
            pass
    return text

def manual_auth():
    """Manual OAuth with explicit redirect_uri and code exchange only."""
    token_path = PROJECT_DIR / "token.json"
    redirect_uri = "http://localhost:8080/"
    client_type, client = load_client_config()
    client_id = client["client_id"]
    client_secret = client["client_secret"]
    
    # Check if we have valid token
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            if creds and creds.valid:
                return creds
        except:
            pass
    
    # Manual code exchange only (no local server, no browser auto-open).
    auth_url = build_auth_url(client_id, redirect_uri)
    
    print("\n" + "="*70)
    print("🔗 STEP 1: Copy this URL and open it in your browser:")
    print("="*70)
    print(auth_url)
    print("="*70)
    print("\n📋 STEP 2: After approval, browser may show localhost unreachable.")
    print("Copy the full URL from address bar OR copy only the 'code' parameter value.\n")
    
    code = extract_code(input("Paste the redirect URL or authorization code here: "))
    
    if not code:
        print("❌ No code provided")
        sys.exit(1)
    
    # Exchange code for token
    token = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
    if "access_token" not in token:
        print(f"❌ Failed to exchange code. Response: {token}")
        sys.exit(1)

    creds = Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    
    # Save token
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    
    print("✅ Token saved!")
    return creds

def populate():
    print("🔐 Authenticating with Google Slides...")
    creds = manual_auth()
    
    service = build("slides", "v1", credentials=creds)
    print("✅ Connected\n")
    
    # Get presentation
    pres = service.presentations().get(presentationId=DECK_ID).execute()
    slides = [s.get("objectId") for s in pres.get("slides", [])]
    
    print(f"📄 Presentation has {len(slides)} slides")
    print("📝 Adding content and colors...\n")
    
    # Colors
    COLORS = {
        "deepNavy": {"red": 23/255, "green": 28/255, "blue": 43/255},
        "midnightBlue": {"red": 20/255, "green": 29/255, "blue": 53/255},
    }
    
    # Slides content
    SLIDES = [
        {"bg": "deepNavy", "title": "Ziyada System", "subtitle": "نحن لا نبيع التقنية"},
        {"bg": "deepNavy", "title": "What We Build", "subtitle": "مزيج من البنية التحتية"},
        {"bg": "midnightBlue", "title": "What We're NOT", "subtitle": "نحن لسنا شركة تقليدية"},
        {"bg": "deepNavy", "title": "Services", "subtitle": "Strategy • Engineering • DevOps"},
        {"bg": "midnightBlue", "title": "Why Ziyada?", "subtitle": "لأننا مسؤولون لا هواة"},
        {"bg": "deepNavy", "title": "Approach", "subtitle": "منهجية واضحة وشفافة"},
        {"bg": "midnightBlue", "title": "Who We Serve", "subtitle": "المؤسسات التقنية والفرق"},
        {"bg": "deepNavy", "title": "Values", "subtitle": "المسؤولية • الشفافية"},
        {"bg": "midnightBlue", "title": "Social Proof", "subtitle": "عملاؤنا يشهدون"},
        {"bg": "deepNavy", "title": "Ready to Talk?", "subtitle": "هل أنت مستعد؟"},
        {"bg": "midnightBlue", "title": "Ziyada System", "subtitle": "built by operators"},
    ]
    
    batch_requests = []
    for idx, slide_id in enumerate(slides[:len(SLIDES)]):
        info = SLIDES[idx]
        color = COLORS[info["bg"]]
        
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
        batch_requests.append({"insertText": {"objectId": title_id, "insertionIndex": 0, "text": info["title"]}})
        batch_requests.append({"updateTextStyle": {"objectId": title_id, "textRange": {"type": "ALL"},
            "style": {"fontSize": {"magnitude": 60, "unit": "PT"}, "bold": True,
                      "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 230/255, "green": 233/255, "blue": 242/255}}}},
            "fields": "fontSize,bold,foregroundColor"}})
        
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
        batch_requests.append({"insertText": {"objectId": subtitle_id, "insertionIndex": 0, "text": info["subtitle"]}})
        batch_requests.append({"updateTextStyle": {"objectId": subtitle_id, "textRange": {"type": "ALL"},
            "style": {"fontSize": {"magnitude": 32, "unit": "PT"},
                      "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 230/255, "green": 233/255, "blue": 242/255}}}},
            "fields": "fontSize,foregroundColor"}})
    
    # Execute batch
    service.presentations().batchUpdate(presentationId=DECK_ID, body={"requests": batch_requests}).execute()
    
    print("✅ All 11 slides populated!\n")
    print(f"🔗 View your presentation:")
    print(f"   https://docs.google.com/presentation/d/{DECK_ID}/edit\n")

if __name__ == "__main__":
    populate()
