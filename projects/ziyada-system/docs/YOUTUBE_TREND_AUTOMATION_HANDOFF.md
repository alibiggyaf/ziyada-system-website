# Niche Signal Intelligence Workflow - Implementation Handoff

Date: 2026-03-20
Owner: Ali Fallatah workflow
Status: Ready for build

## Objective
Build a cost-optimized weekly Niche Signal Intelligence pipeline that:
- Auto-discovers top 20-30 YouTube channels in AI automation and marketing (70/30 AI-heavy mix).
- Analyzes previous 7 days (Asia/Riyadh) for Saudi, Egypt, MENA, and global signals.
- Generates Google Slides report in this exact order:
  1) English cover
  2) Full English section
  3) Arabic cover
  4) Full Arabic section
  5) Thank-you closing slide
- Uses fixed logos by language section:
  - English: projects/ALI FALLATAH WEBSITE PORTOFOLIO/Ali website  2026/Ali Logos-02.png
  - Arabic: projects/ALI FALLATAH WEBSITE PORTOFOLIO/Ali website  2026/Ali Logos-03.png
- Sends report by Gmail to ali.biggy.af@gmail.com.
- Stores historical weekly data in Google Sheets for trend tracking over multiple weeks.

## Source Strategy and Cost Policy
Primary source (default): YouTube Data API v3.
Fallback source (only when needed): Apify YouTube actor(s).

Rules:
- API-first always.
- Apify only if confidence/coverage thresholds fail.
- Enforce hard caps per run:
  - max_channels_selected = 30
  - min_channels_selected = 20
  - max_videos_per_channel = configurable (default 12)
  - max_apify_fallback_calls = configurable (default 5)
- Include source usage summary in run output and email (API-only or API+Apify).

## Scheduling Requirements
- Weekly scheduled run: every Sunday, Asia/Riyadh timezone.
- Window: previous 7 full days.
- Also support manual on-demand run with same default window and optional override.

## Bilingual Presentation Rules
- Build complete English deck content first.
- Then append complete Arabic section.
- Do not mix Arabic and English text in the same content block.
- Arabic slides must be RTL and use Cairo styling logic from brand note.
- Visual language should follow:
  - projects/ALI FALLATAH WEBSITE PORTOFOLIO/Ali website  2026/AF_Bilingual_BrandNote_SaudiMarket.html

## Existing Code to Reuse
- Slides API population baseline:
  - projects/ziyada-system/scripts/populate_slides_auth.py
- Bilingual slide structuring reference:
  - projects/ziyada-system/scripts/create_company_profile_slides.py
- Gmail sending pattern:
  - projects/ziyada-system/scripts/send_ziyada_blog_gmail.py
- Existing scoring/workflow patterns:
  - projects/ziyada-system/scripts/deploy_n8n_blog_workflow.py

## Implementation Deliverables
Create or update the following:
1. Data ingestion and ranking
- projects/ziyada-system/scripts/youtube_trend_ingest.py
- projects/ziyada-system/scripts/youtube_channel_discovery.py

2. Scoring and insights
- projects/ziyada-system/scripts/youtube_trend_scoring.py
- projects/ziyada-system/scripts/youtube_weekly_insights_bilingual.py

3. Google Sheets persistence
- projects/ziyada-system/scripts/youtube_trend_sheets_store.py

4. Slides generation (EN first, then AR)
- projects/ziyada-system/scripts/create_youtube_trend_slides.py

5. Email delivery
- projects/ziyada-system/scripts/send_youtube_trend_report.py

6. Orchestrator
- projects/ziyada-system/scripts/run_youtube_weekly_report.py

7. Configuration and docs
- projects/ziyada-system/.env.example (add new variables)
- projects/ziyada-system/docs/YOUTUBE_TREND_AUTOMATION_RUNBOOK.md

## Required Environment Variables
- YOUTUBE_API_KEY
- APIFY_TOKEN (optional fallback path)
- APIFY_YOUTUBE_ACTOR_ID (optional fallback path)
- REPORT_TIMEZONE=Asia/Riyadh
- REPORT_DEFAULT_LOOKBACK_DAYS=7
- REPORT_CHANNEL_TARGET_MIN=20
- REPORT_CHANNEL_TARGET_MAX=30
- REPORT_AI_MARKETING_SPLIT=70_30
- REPORT_MAX_VIDEOS_PER_CHANNEL=12
- REPORT_MAX_APIFY_FALLBACK_CALLS=5
- GOOGLE_SHEET_ID
- GOOGLE_SHEET_TAB_CHANNELS=WeeklyChannelSnapshot
- GOOGLE_SHEET_TAB_VIDEOS=WeeklyVideoSnapshot
- GOOGLE_SHEET_TAB_INSIGHTS=WeeklyInsightsSummary
- GOOGLE_SHEET_TAB_RUNS=RunsAudit
- REPORT_RECIPIENT_EMAIL=ali.biggy.af@gmail.com

## Google Sheets Schema (minimum)
WeeklyChannelSnapshot:
- run_id
- week_start
- week_end
- timezone
- channel_id
- channel_title
- subscribers
- category_label
- relevance_score
- regional_fit_score
- final_channel_score
- data_source

WeeklyVideoSnapshot:
- run_id
- week_start
- week_end
- video_id
- channel_id
- title
- published_at
- views
- likes
- comments
- duration_seconds
- language_hint
- trend_score
- region_bucket
- data_source

WeeklyInsightsSummary:
- run_id
- week_start
- week_end
- top_channel_count
- top_video_count
- key_findings_en
- key_findings_ar
- opportunities_en
- opportunities_ar

RunsAudit:
- run_id
- executed_at
- mode (manual|scheduled)
- week_start
- week_end
- timezone
- api_quota_units_est
- apify_calls_used
- channels_selected
- videos_scored
- status
- error_summary

## Acceptance Criteria
1. Auto-discovery returns 20-30 channels with AI-heavy 70/30 weighting.
2. Weekly date window is correct for Sunday runs in Asia/Riyadh.
3. API-first path completes successfully without Apify in normal cases.
4. Apify fallback is invoked only when configured thresholds fail.
5. Google Sheets receives append-only weekly snapshots for all tabs.
6. Slides order exactly matches required sequence.
7. EN slides use Ali Logos-02.png, AR slides use Ali Logos-03.png.
8. Arabic section is RTL and readable, with no mixed-language blocks.
9. Final thank-you slide exists at the very end.
10. Gmail delivery works for both manual and scheduled runs.

## Suggested Execution Order
1. Implement ingestion + discovery (API-first).
2. Implement ranking + trend scoring.
3. Implement Google Sheets persistence.
4. Implement slide generator with EN-first then AR flow.
5. Implement email sender and orchestrator.
6. Add schedule trigger.
7. Run end-to-end test with manual mode.
8. Run simulated Sunday weekly mode.

## Manual Run Command (target)
python3 projects/ziyada-system/scripts/run_youtube_weekly_report.py --mode manual --timezone Asia/Riyadh --lookback-days 7

## Weekly Scheduled Command (target)
python3 projects/ziyada-system/scripts/run_youtube_weekly_report.py --mode scheduled --timezone Asia/Riyadh --lookback-days 7

## Notes
- Keep the architecture direct API based for MVP.
- MCP and n8n expansion can follow once weekly stability is proven.
- Preserve existing OAuth/token flow already used by Docs/Slides/Gmail scripts.
