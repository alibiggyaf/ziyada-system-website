---
description: How to write high-end Arabic internal documentation and guides for Ziyada System
---

# Ziyada System: Arabic Documentation Guidelines

When asked to write research, guidelines, or internal documentation for Ziyada System, ALWAY follow this styling and structural pattern to deliver a premium, brand-aligned experience.

## 1. Do NOT Use Emojis for Icons
Never use standard emojis (🌐, 📁, ⚙️, 🔒, etc.) for icons. 
**Instead, use SVG inline icons**, specifically matching the "Lucide Icons" standard (stroke-width: 2, fill: none, stroke: currentColor). They look infinitely more professional and premium.

## 2. Layout & Typography (The Vibe)
- **Language**: Always Arabic (RTL configuration: `dir="rtl" lang="ar"`).
- **Fonts**: Use `Noto Kufi Arabic` at weights 400 (normal), 600 (semibold), 800 (bold), 900 (black).
- **Sizes**: Keep base body text large for comfortable reading (e.g. `16px` to `17px` minimum), and headers large and punchy (`20px` to `42px`). Let information breathe logically.
- **Tone**: The language must be strong, professional, and confident, emphasizing growth, automation, analytics, and smart systems (e.g. "دليل المنظومة الرقمية", "التكامل المتقدم", "تحويل/Conversion", "رحلة العميل", "بثبات").

## 3. Brand Colors & UI Elements
Do not use flat generic colors. Base the UI on Ziyada System's brand guidelines:
- **Card/Glass Layout**: Give elements soft shadows (`box-shadow: 0 4px 6px rgba(0,0,0,0.05)`) and rounded corners (`border-radius: 12px` to `20px`).
- **Gradients**: The primary brand gradient must be present, usually in the header or as a text clip. 
  `linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)` (Purple to Blue).
- **Primary Text**: Dark Slate/Blue (`#1e293b`).
- **White Background for Docs**: If it's a deep read or internal guide, default to a Light Mode (bg: `#f8fafc`, cards: `#ffffff`) to reduce eye strain, contrary to the dark mode pitch-decks.

## 4. Components You Must Include
1. **The Hero Header**: A prominent header at the top with a subtle top-border gradient, the shield "Z" logo (built with CSS logic if SVGs aren't provided), the document title, and metadata tags (Date, Version, Target Audience).
2. **Table of Contents**: A clear TOC linking to sections using ID hashes.
3. **Structured Step-by-Step Sections**: Number steps beautifully with rounded or circular icons. Let the steps float clearly.
4. **Flow Diagrams**: Instead of bullet points for workflows, use CSS layout blocks (`.flow-box`) connected by arrows (→ or `lucide` arrow SVG) to visualize the data flow across services (e.g., Supabase → N8N → HubSpot).
5. **Notice Alerts**: Build custom alert boxes (Success, Info, Warning) with distinct background colors (e.g., `#eff6ff` for info, `#fffbeb` for warning, `#f0fdf4` for success) plus an embedded Lucide SVG to represent the alert icon.

## 5. The Signature (Crucial)
At the bottom of every such document, you MUST include the Founder's signature to signify quality control:
> تم التطوير والتأسيس والمراجعة والتدقيق וכتابة هذا الملف من قِبل:
> **علي فلاتة**
> مؤسس زيادة سيستم

## Example Implementation Note
For the HTML implementation, encapsulate the styling inline within `<style>` blocks to ensure portability without depending on external asset loaders besides Google Fonts for Noto Kufi Arabic. Always provide highly semantic tags (`ul`, `li`, `table`, `a`).
