## Plan: Ziyada System AI Content Marketing Team

Build a bilingual (Arabic primary + English secondary) multi-agent content marketing system using existing n8n + Google + OpenAI + Apify integrations, and deliver a standalone bilingual dashboard with filtering and manual competitor input.

**Steps**
1. Foundation data layer: create master Google Sheet "Ziyada Content Hub 2026" with tabs `TrendScout`, `Scripts`, `Thumbnails`, `Competitors`, `BrandIntelligence`, `VideoProduction`, `DailyReport`, `Config`.
2. Brand Analyst agent (`01_Ziyada_Brand_Analyst`): ingest Ziyada brand docs + discover competitors (auto + manual list), analyze messaging and strategy, write to `BrandIntelligence`.
3. Trend Scout agent (`02_Ziyada_Trend_Scout_Daily`): run daily across YouTube, TikTok, Instagram, X, LinkedIn via Apify; compute outlier score \(\frac{48h\ engagement}{channel\ average\ 48h}\times100\); store top outliers in `TrendScout`.
4. Script Writer agent (`03_Ziyada_Script_Writer`): for top trends generate AR hook + 30s intro + outline + titles + EN matched version; enforce Ziyada voice; store in `Scripts`.
5. Thumbnail Designer agent (`04_Ziyada_Thumbnail_Designer`): generate 2-3 thumbnail concepts per script (DALL-E/OpenAI image) and save links in `Thumbnails`.
6. Video Producer agent (`05_Ziyada_Video_Producer`): automate editing via Shotstack/Creatomate (not Descript API), remove filler words, keep pauses <0.5s, animated layered intro, intro-only captions, subtle intro music, brand bumpers, optional AI B-roll; write status to `VideoProduction`.
7. Daily Reporter agent (`06_Ziyada_Daily_Reporter`): compile bilingual daily digest from all tabs and email to `ali.biggy.af@gmail.com`; log in `DailyReport`.
8. Competitor Monitor webhook (`07_Ziyada_Competitor_Monitor`): accept manual competitor input from dashboard, scrape/analyze, append to `Competitors`.
9. Dashboard build: create standalone React app in `projects/ziyada-system/app/ziyada-content-hub/` with AR/EN toggle, RTL/LTR switching, platform/date filters, trend cards, script viewer, thumbnail gallery, competitor input, report view.
10. Verification: run each workflow manually first, validate sheet outputs, email delivery, dashboard filters/toggle, and ensure existing workflow 62 remains operational.

**Relevant files**
- `projects/ziyada-system/docs/ZIYADA_VOICE_PROMPT_SYSTEM.txt` — canonical Arabic voice and style constraints.
- `projects/ziyada-system/docs/ZIYADA_GUIDELINES.md` — brand palette, identity, and messaging.
- `projects/ziyada-system/docs/SERVICES_CATALOG_AR_EN.md` — bilingual service framing.
- `projects/ziyada-system/workflows/workflow_62_snapshot.json` — baseline YouTube trend workflow to extend.
- `projects/ziyada-system/assets/ziyada_brand_book.html` — visual language reference for dashboard styling.

**Verification**
1. Create sheet tabs and validate schema.
2. Run Brand Analyst and confirm `BrandIntelligence` rows.
3. Run Trend Scout and confirm multi-platform outliers.
4. Run Script Writer and confirm separate AR + EN outputs.
5. Run Thumbnail Designer and confirm generated assets.
6. Run Video Producer test and verify timing/captions/music constraints.
7. Run Daily Reporter and verify Gmail delivery.
8. Test dashboard language toggle, RTL/LTR, platform/date filters, and manual competitor submission.

**Decisions**
- Dashboard is a new standalone React app.
- Social research uses Apify across all requested platforms.
- Video automation uses Shotstack or Creatomate due Descript API limits.
- Output remains fully bilingual with Arabic primary voice.
- Competitor list combines automatic discovery and manual user inputs.
