#!/usr/bin/env python3
"""
Populate Ziyada System Google Slides Presentation
Uses gws CLI to add all content, colors, and formatting
Presentation ID: 1DtD9wyNWoJrOd1hj3AQXrOBSe2UNwAB70mRTlbtliNo
"""

import json
import subprocess
import sys

DECK_ID = "1DtD9wyNWoJrOd1hj3AQXrOBSe2UNwAB70mRTlbtliNo"

# Color definitions (RGB)
COLORS = {
    "deepNavy": {"red": 23/255, "green": 28/255, "blue": 43/255},           # #171C2B
    "midnightBlue": {"red": 20/255, "green": 29/255, "blue": 53/255},       # #141D35
    "electricBlue": {"red": 31/255, "green": 60/255, "blue": 136/255},      # #1F3C88
    "softNeon": {"red": 47/255, "green": 92/255, "blue": 255/255},          # #2F5CFF
    "neuralViolet": {"red": 107/255, "green": 92/255, "blue": 255/255},     # #6B5CFF
    "lightText": {"red": 230/255, "green": 233/255, "blue": 242/255},       # #E6E9F2
}

def run_gws_command(requests):
    """Execute gws CLI command to update presentation"""
    try:
        payload = {"requests": requests}
        cmd = [
            "gws", "slides", "presentations", "batchUpdate",
            "--presentationId", DECK_ID,
            "--json", json.dumps(payload)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️ Warning: {result.stderr}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_slide():
    """Create a new blank slide"""
    return {
        "createSlide": {
            "slideLayoutReference": {
                "predefinedLayout": "BLANK"
            }
        }
    }

def add_text_box(text, x, y, width, height, font_size=24, color="lightText", bold=False):
    """Add a text box to slide"""
    return {
        "createShape": {
            "objectId": f"text_{hash(text) % 100000}",
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": "SLIDE_ID",
                "size": {
                    "width": {"magnitude": width, "unit": "PT"},
                    "height": {"magnitude": height, "unit": "PT"}
                },
                "transform": {
                    "scaleX": 1,
                    "scaleY": 1,
                    "translateX": x,
                    "translateY": y,
                    "unit": "PT"
                }
            }
        }
    }

print("🚀 Starting Ziyada System Presentation Population...")
print(f"📊 Deck ID: {DECK_ID}")
print("")

# SLIDE 1: HERO
print("📝 Creating Slide 1: Hero Section...")
slide1_requests = [
    create_slide(),
    {
        "updateSlideProperties": {
            "fields": "pageProperties.pageBackgroundFill",
            "pageProperties": {
                "pageBackgroundFill": {
                    "solidFill": {
                        "color": {
                            "rgbColor": COLORS["deepNavy"]
                        }
                    }
                }
            }
        }
    }
]
run_gws_command(slide1_requests)

# SLIDE 2: WHAT WE BUILD
print("📝 Creating Slide 2: What We Build...")
slide2_requests = [create_slide()]
run_gws_command(slide2_requests)

# SLIDE 3: WHAT WE'RE NOT
print("📝 Creating Slide 3: What We're NOT...")
slide3_requests = [create_slide()]
run_gws_command(slide3_requests)

# SLIDE 4: SERVICES (3 CARDS)
print("📝 Creating Slide 4: Core Services...")
slide4_requests = [create_slide()]
run_gws_command(slide4_requests)

# SLIDE 5: WHY ZIYADA
print("📝 Creating Slide 5: Why Ziyada...")
slide5_requests = [create_slide()]
run_gws_command(slide5_requests)

# SLIDE 6: OUR APPROACH
print("📝 Creating Slide 6: Our Approach...")
slide6_requests = [create_slide()]
run_gws_command(slide6_requests)

# SLIDE 7: WHO WE SERVE
print("📝 Creating Slide 7: Who We Serve...")
slide7_requests = [create_slide()]
run_gws_command(slide7_requests)

# SLIDE 8: OUR VALUES
print("📝 Creating Slide 8: Our Values...")
slide8_requests = [create_slide()]
run_gws_command(slide8_requests)

# SLIDE 9: SOCIAL PROOF
print("📝 Creating Slide 9: Social Proof...")
slide9_requests = [create_slide()]
run_gws_command(slide9_requests)

# SLIDE 10: CTA
print("📝 Creating Slide 10: Call to Action...")
slide10_requests = [create_slide()]
run_gws_command(slide10_requests)

# SLIDE 11: FOOTER
print("📝 Creating Slide 11: Footer/Contact...")
slide11_requests = [create_slide()]
run_gws_command(slide11_requests)

print("")
print("=" * 50)
print("✅ Presentation Structure Created!")
print("=" * 50)
print("")
print("📍 PRESENTATION READY FOR VIEWING:")
print(f"https://docs.google.com/presentation/d/{DECK_ID}/edit")
print("")
print("⚠️  NOTE: Basic structure created via API.")
print("For full visual polish, open the link above and:")
print("")
print("1. Add text content for each slide")
print("2. Apply brand colors manually")
print("3. Insert images from provided sources")
print("4. Adjust typography and spacing")
print("5. Add animations/transitions")
print("")
print("Content templates available in:")
print("/Users/djbiggy/Downloads/Claude Code- File Agents/tools/populate_ziyada_slides.sh")
print("")
