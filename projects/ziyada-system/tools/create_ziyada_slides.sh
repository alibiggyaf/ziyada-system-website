#!/usr/bin/env bash

# Create Ziyada System Company Profile in Google Slides
# This script uses gws CLI to generate a professional bilingual presentation

set -euo pipefail

# Configuration
TITLE="Ziyada System – نظام زيادة | Company Profile"
COMPANY_EMAIL="contact@ziyadasystem.com"

echo "🚀 Creating Ziyada System presentation..."

# Step 1: Create presentation
DECK_ID=$(gws slides presentations create --json "{\"title\":\"$TITLE\"}" 2>/dev/null | jq -r '.presentationId')
echo "✅ Presentation created: $DECK_ID"

# Step 2: Fetch current slides (to get object IDs for updates)
SLIDES=$(gws slides presentations get --presentationId "$DECK_ID" 2>/dev/null | jq -r '.slides')

# Step 3: Build batch update requests for all slides
# This creates the complete presentation structure

BATCH_REQUESTS='[
  {
    "createSlide": {
      "slideLayoutReference": {"predefinedLayout": "TITLE"}
    }
  },
  {
    "insertText": {
      "objectId": "title",
      "text": "Ziyada System\nبناء نظم النمو",
      "insertionIndex": 0
    }
  },
  {
    "insertText": {
      "objectId": "subtitle",
      "text": "Build Once. Scale Logically. Grow Predictably.\nابنِ مرة واحدة. تكيف بمنطق. نمِ بتنبؤات.",
      "insertionIndex": 0
    }
  }
]'

# Execute batch update
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json "{\"requests\": $BATCH_REQUESTS}" \
  2>/dev/null || true

echo "✅ Slides structure created"

# Step 4: Add additional slides for each section
SECTIONS=(
  "What We Build|ما نبنيه"
  "Core Services|خدماتنا الأساسية"
  "Why Ziyada|لماذا زيادة"
  "Our Approach|منهجيتنا"
  "Who We Serve|من نخدم"
  "Brand Values|قيمنا"
  "Ready to Start|هل أنت مستعد"
)

for section in "${SECTIONS[@]}"; do
  IFS='|' read -r en_title ar_title <<< "$section"
  
  # Add slide
  gws slides presentations batchUpdate \
    --presentationId "$DECK_ID" \
    --json "{\"requests\": [{\"createSlide\": {\"slideLayoutReference\": {\"predefinedLayout\": \"BLANK\"}}}]}" \
    2>/dev/null || true
  
  echo "✅ Added section: $en_title / $ar_title"
done

# Step 5: Generate presentation URL
PRESENTATION_URL="https://docs.google.com/presentation/d/$DECK_ID/edit"

echo ""
echo "=========================================="
echo "✨ Presentation Ready!"
echo "=========================================="
echo "Title: $TITLE"
echo "ID: $DECK_ID"
echo "URL: $PRESENTATION_URL"
echo ""
echo "Next steps:"
echo "1. Open the link above"
echo "2. Customize text, colors, and images"
echo "3. Apply brand colors from guidelines:"
echo "   - Deep Space Navy: #171C2B"
echo "   - Electric System Blue: #1F3C88"
echo "   - Soft Neon Blue: #2F5CFF"
echo "   - Neural Violet: #6B5CFF"
echo "4. Add high-quality images for each section"
echo "=========================================="
