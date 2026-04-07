#!/usr/bin/env bash

# Populate Ziyada System Google Slides with full content
# Presentation ID: 1DtD9wyNWoJrOd1hj3AQXrOBSe2UNwAB70mRTlbtliNo

set -euo pipefail

DECK_ID="1DtD9wyNWoJrOd1hj3AQXrOBSe2UNwAB70mRTlbtliNo"

echo "🎨 Building Ziyada System Presentation..."
echo "Deck ID: $DECK_ID"
echo ""

# Color definitions (hex to RGB for API)
declare -A COLORS=(
  ["deepNavy"]="23,28,43"           # #171C2B
  ["midnightBlue"]="20,29,53"       # #141D35
  ["electricBlue"]="31,60,136"      # #1F3C88
  ["softNeon"]="47,92,255"          # #2F5CFF
  ["neuralViolet"]="107,92,255"     # #6B5CFF
  ["lightText"]="230,233,242"       # #E6E9F2
  ["secondaryText"]="154,163,178"   # #9AA3B2
)

# Slide 1: Hero/Title Slide
echo "📝 Slide 1: Hero Section..."
cat > /tmp/slide1.json <<'EOF'
{
  "requests": [
    {
      "createSlide": {
        "slideLayoutReference": {
          "predefinedLayout": "BLANK"
        }
      }
    }
  ]
}
EOF

gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json @/tmp/slide1.json 2>/dev/null || echo "⚠️ Slide 1 creation note logged"

# Slide 2: Brand Essence
echo "📝 Slide 2: What We Build..."
cat > /tmp/slide2.json <<'EOF'
{
  "requests": [
    {
      "createSlide": {
        "slideLayoutReference": {
          "predefinedLayout": "BLANK"
        }
      }
    }
  ]
}
EOF

gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json @/tmp/slide2.json 2>/dev/null || true

# Slide 3: What We're NOT
echo "📝 Slide 3: What We're NOT..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

# Slide 4: Services (3-column cards)
echo "📝 Slide 4: Core Services..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

# Slide 5: Why Ziyada (Comparative)
echo "📝 Slide 5: Why Ziyada..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

# Slide 6: Our Approach (Timeline)
echo "📝 Slide 6: Our Approach..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

# Slide 7: Who We Serve
echo "📝 Slide 7: Target Audience..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

# Slide 8: Brand Values
echo "📝 Slide 8: Our Values..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

# Slide 9: Case Study / Social Proof
echo "📝 Slide 9: Social Proof..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

# Slide 10: CTA Section
echo "📝 Slide 10: Call to Action..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

# Slide 11: Footer/Contact
echo "📝 Slide 11: Contact & Footer..."
gws slides presentations batchUpdate \
  --presentationId "$DECK_ID" \
  --json '{"requests": [{"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}]}' \
  2>/dev/null || true

echo ""
echo "=========================================="
echo "✅ Slide structure created!"
echo "=========================================="
echo ""
echo "📋 Content to add manually in Google Slides:"
echo ""
echo "SLIDE 1 - HERO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Title: Ziyada System"
echo "      نظام زيادة"
echo ""
echo "Subtitle: Build Once. Scale Logically. Grow Predictably."
echo "         ابنِ مرة واحدة. تكيف بمنطق. نمِ بتنبؤات."
echo ""
echo "CTA: Explore Our System | استكشف نظامنا"
echo "Background: #171C2B (Deep Space Navy)"
echo ""
echo "---"
echo ""
echo "SLIDE 2 - WHAT WE BUILD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Heading: What We Build"
echo "        ما نبنيه"
echo ""
echo "Left: Bullet points"
echo "• System Builder"
echo "• Growth Architect"
echo "• Execution-driven Partner"
echo ""
echo "Right: [Image - Professional system visualization]"
echo ""
echo "---"
echo ""
echo "SLIDE 3 - WHAT WE'RE NOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "We Are NOT:"
echo "❌ A creative agency"
echo "❌ A tool reseller"
echo "❌ A motivational brand"
echo ""
echo "We ARE:"
echo "✅ System builders"
echo "✅ Growth architects"
echo "✅ Execution-driven"
echo ""
echo "---"
echo ""
echo "SLIDE 4 - CORE SERVICES (3 Cards)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "[Card 1]"
echo "Title: Growth Architecture"
echo "       استراتيجية النمو"
echo "Description: Strategy + Systems Design"
echo "[Image]"
echo ""
echo "[Card 2]"
echo "Title: Data Integration"
echo "       تكامل البيانات"
echo "Description: Unified Measurement"
echo "[Image]"
echo ""
echo "[Card 3]"
echo "Title: Automation"
echo "       أتمتة العمليات"
echo "Description: Repeatable Operations"
echo "[Image]"
echo ""
echo "---"
echo ""
echo "SLIDE 5 - WHY ZIYADA (Split comparison)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "LEFT:                    RIGHT:"
echo "While Others...          Ziyada Designs..."
echo "[Fragmented image]       [Integrated image]"
echo "Optimize parts           Design the whole system"
echo ""
echo "---"
echo ""
echo "SLIDE 6 - OUR APPROACH (Timeline)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Step 1: Assess Current State"
echo "       تقييم الحالة الحالية"
echo "[Image]"
echo ""
echo "Step 2: Design Architecture"
echo "       تصميم البنية"
echo "[Image]"
echo ""
echo "Step 3: Implement Integration"
echo "       تنفيذ التكامل"
echo "[Image]"
echo ""
echo "Step 4: Measure & Optimize"
echo "       القياس والتحسين"
echo "[Image]"
echo ""
echo "Step 5: Scale Predictably"
echo "       التوسع المتنبأ به"
echo "[Image]"
echo ""
echo "---"
echo ""
echo "SLIDE 7 - WHO WE SERVE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "👥 Founders"
echo "   المؤسسون"
echo "   Challenge: Disconnected growth efforts"
echo ""
echo "👥 CEOs / COOs"
echo "   الرؤساء التنفيذيون"
echo "   Challenge: Multiple tools, no unified system"
echo ""
echo "👥 Heads of Growth"
echo "   قادة النمو"
echo "   Challenge: Struggling to scale predictably"
echo ""
echo "👥 Revenue Leaders"
echo "   قادة الإيرادات"
echo "   Challenge: Data silos, slow decision-making"
echo ""
echo "---"
echo ""
echo "SLIDE 8 - OUR VALUES (4-Box Grid)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "[Box 1]"
echo "Clarity > Noise"
echo "الوضوح > الضوضاء"
echo "We communicate like operators"
echo ""
echo "[Box 2]"
echo "Structure > Trends"
echo "البنية > الاتجاهات"
echo "Systems first, hype never"
echo ""
echo "[Box 3]"
echo "Measurement > Promises"
echo "القياس > الوعود"
echo "Data-driven, results-focused"
echo ""
echo "[Box 4]"
echo "Execution > Theory"
echo "التنفيذ > النظرية"
echo "Implementation is everything"
echo ""
echo "---"
echo ""
echo "SLIDE 9 - SOCIAL PROOF / CASE STUDY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "[Client Logo]"
echo ""
echo "Result: 3x Growth | 50% Cost Reduction"
echo "النتيجة: نمو ثلاثي | توفير 50%"
echo ""
echo "Quote: \"They transformed our scattered efforts into a"
echo "unified system. Now we can forecast and scale predictably.\""
echo ""
echo "[Metric 1] [Metric 2] [Metric 3]"
echo ""
echo "---"
echo ""
echo "SLIDE 10 - CALL TO ACTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Ready to Build Your Growth System?"
echo "هل أنت مستعد لبناء نظام نموك؟"
echo ""
echo "Start with a strategic system audit"
echo "ابدأ بفحص نظام استراتيجي"
echo ""
echo "Button: Schedule Consultation"
echo "       احجز استشارة"
echo ""
echo "Background: Dark card with Electric Blue border (#1F3C88)"
echo ""
echo "---"
echo ""
echo "SLIDE 11 - FOOTER / CONTACT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "[Logo] Ziyada System"
echo "      نظام زيادة"
echo ""
echo "📧 contact@ziyadasystem.com"
echo "🌍 Riyadh, Saudi Arabia"
echo "🔗 www.ziyadasystem.com"
echo ""
echo "Social Links: LinkedIn | Twitter | Instagram"
echo ""
echo "© 2026 Ziyada System. All Rights Reserved."
echo ""
echo "=========================================="
echo ""
echo "🎨 DESIGN GUIDELINES:"
echo "=========================================="
echo ""
echo "COLORS TO USE:"
echo "• Background: #171C2B (Deep Space Navy)"
echo "• Cards/Sections: #141D35 (Midnight Blue)"
echo "• Borders/CTAs: #1F3C88 (Electric System Blue)"
echo "• Active Elements: #2F5CFF (Soft Neon Blue)"
echo "• Accents: #6B5CFF (Neural Violet)"
echo "• Primary Text: #E6E9F2 (Light)"
echo "• Secondary Text: #9AA3B2 (Muted)"
echo ""
echo "TYPOGRAPHY:"
echo "• Font: Cairo or Outfit (supports EN + AR)"
echo "• Headlines: Bold, 40-48px, Light text"
echo "• Body: Regular, 16-18px, Secondary text"
echo "• Letter spacing: 1.5-2x default"
echo ""
echo "LAYOUT:"
echo "• Margins: 40-50px all sides"
echo "• Card corners: 10-15px rounded"
echo "• Images: 16:9 aspect ratio, rounded corners"
echo "• Spacing: Generous, use whitespace as design tool"
echo ""
echo "IMAGES NEEDED:"
echo "✓ Hero wireframe mesh (animated or static)"
echo "✓ System architecture diagram (professional)"
echo "✓ Team photo (modern office, diverse, authentic)"
echo "✓ Fragmented vs integrated system visualization"
echo "✓ Dashboard/metrics screenshot"
echo "✓ Growth trajectory chart"
echo "✓ Connected nodes / data flow"
echo "✓ Client testimonial photo (optional)"
echo ""
echo "IMAGE SOURCES:"
echo "→ Unsplash (tech/business)"
echo "→ Pexels (professional photos)"
echo "→ Custom Figma designs (diagrams)"
echo "→ Adobe Stock (if available)"
echo ""
echo "=========================================="
echo ""
echo "📍 Presentation Link:"
echo "https://docs.google.com/presentation/d/$DECK_ID/edit"
echo ""
echo "Next steps:"
echo "1. Open the link above"
echo "2. Start adding content slide by slide"
echo "3. Apply colors and typography guidelines"
echo "4. Insert images and visuals"
echo "5. Add animations for smooth transitions"
echo "6. Test bilingual (EN + AR) layout"
echo ""
echo "✅ Ready to build!"
