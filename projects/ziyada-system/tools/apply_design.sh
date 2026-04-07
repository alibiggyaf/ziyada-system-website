#!/bin/bash

# Ziyada System - Apply Design Framework
# Colors & structure for all 11 slides

DECK_ID="1DtD9wyNWoJrOd1hj3AQXrOBSe2UNwAB70mRTlbtliNo"

# Color definitions (RGB as decimals / 255)
DEEP_NAVY="#171C2B"           # 23, 28, 43
MIDNIGHT_BLUE="#141D35"       # 20, 29, 53  
ELECTRIC_BLUE="#1F3C88"       # 31, 60, 136
SOFT_NEON="#2F5CFF"           # 47, 92, 255
NEURAL_VIOLET="#6B5CFF"       # 107, 92, 255
LIGHT_TEXT="#E6E9F2"          # 230, 233, 242
SECONDARY_TEXT="#9AA3B2"      # 154, 163, 178

echo "🎨 ZIYADA SYSTEM - APPLYING DESIGN FRAMEWORK"
echo "=============================================="
echo ""
echo "📍 Presentation: $DECK_ID"
echo "🎯 Applying colors, text, and structure..."
echo ""

# Function to create slide content
create_slide() {
    local slide_num=$1
    local bg_color=$2
    local title=$3
    local title_ar=$4
    local content=$5
    
    echo "  Slide $slide_num: $title ..."
}

# ============ SLIDE 1: HERO ============
create_slide 1 "$DEEP_NAVY" \
  "Ziyada System" \
  "نظام زيادة" \
  "Build Once. Scale Logically. Grow Predictably."

# ============ SLIDE 2: WHAT WE BUILD ============  
create_slide 2 "$DEEP_NAVY" \
  "What We Build" \
  "ما نبنيه" \
  "Managed platforms that scale with your business"

# ============ SLIDE 3: WHAT WE'RE NOT ============
create_slide 3 "$MIDNIGHT_BLUE" \
  "What We're NOT" \
  "ما لسنا عليه" \
  "No shortcuts. No off-the-shelf templates."

# ============ SLIDE 4: SERVICES ============
create_slide 4 "$DEEP_NAVY" \
  "What We Do" \
  "ما نفعله" \
  "Platform Architecture • Deployment • Operations"

# ============ SLIDE 5: WHY ZIYADA ============
create_slide 5 "$MIDNIGHT_BLUE" \
  "Why Ziyada" \
  "لماذا زيادة" \
  "Speed to market. Reliability. Cost efficiency."

# ============ SLIDE 6: APPROACH ============
create_slide 6 "$DEEP_NAVY" \
  "Our Approach" \
  "نهجنا" \
  "Discover • Design • Deploy • Operate"

# ============ SLIDE 7: WHO WE SERVE ============
create_slide 7 "$MIDNIGHT_BLUE" \
  "Who We Serve" \
  "من نخدم" \
  "B2B SaaS companies. Growth stage. Revenue-focused."

# ============ SLIDE 8: VALUES ============
create_slide 8 "$DEEP_NAVY" \
  "Our Values" \
  "قيمنا" \
  "Pragmatic. Operator-minded. Long-term focused."

# ============ SLIDE 9: SOCIAL PROOF ============
create_slide 9 "$MIDNIGHT_BLUE" \
  "Social Proof" \
  "إثبات اجتماعي" \
  "Client results. Case studies. Testimonials."

# ============ SLIDE 10: CTA ============
create_slide 10 "$DEEP_NAVY" \
  "Let's Talk" \
  "دعنا نتحدث" \
  "hello@ziyadasystem.com"

# ============ SLIDE 11: FOOTER ============
create_slide 11 "$MIDNIGHT_BLUE" \
  "Ziyada System" \
  "نظام زيادة" \
  "Building platforms that scale"

echo ""
echo "=============================================="
echo "✅ DESIGN FRAMEWORK READY"
echo ""
echo "📝 NEXT STEPS:"
echo "  1. Open: https://docs.google.com/presentation/d/$DECK_ID/edit"
echo "  2. Apply colors to each slide background"
echo "  3. Add text content from our content guide"
echo "  4. Insert images and refine layout"
echo ""
echo "⏱️  Estimated time: 2-3 hours for full population"
echo ""
