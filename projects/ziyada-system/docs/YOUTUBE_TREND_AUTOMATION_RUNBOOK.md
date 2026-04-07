# Niche Signal Intelligence Workflow Runbook

## Purpose
Run a weekly and manual Niche Signal Intelligence workflow (YouTube-first source) that discovers top channels, scores trends, stores history in Google Sheets, builds bilingual Google Slides, and creates a Gmail draft for delivery.

## Prerequisites
- token.json exists in projects/ziyada-system with valid scopes for:
  - Slides
  - Sheets
  - Gmail compose
- credentials.json exists for OAuth refresh flow if needed.
- Environment variables loaded from .env (see .env.example).

## First Run Checklist
1. Set YOUTUBE_API_KEY in .env.
2. Set GOOGLE_SHEET_ID and tab names.
3. Confirm REPORT_RECIPIENT_EMAIL.
4. Ensure logos exist:
   - projects/ALI FALLATAH WEBSITE PORTOFOLIO/Ali website  2026/Ali Logos-02.png
   - projects/ALI FALLATAH WEBSITE PORTOFOLIO/Ali website  2026/Ali Logos-03.png

## Manual Run
python3 projects/ziyada-system/scripts/run_youtube_weekly_report.py --mode manual --timezone Asia/Riyadh --lookback-days 7

## Weekly Scheduled Run (Sunday)
python3 projects/ziyada-system/scripts/run_youtube_weekly_report.py --mode scheduled --timezone Asia/Riyadh --lookback-days 7

## Output Artifacts
Generated under:
- projects/ziyada-system/outputs/market_intel/youtube/<run_id>/

Files:
- discovered_channels.json
- weekly_ingest.json
- weekly_scored.json
- weekly_insights_bilingual.json
- run_summary.json

## Current MVP Behavior
- Uses YouTube Data API as primary source.
- Apify fallback is planned but not active in this MVP code path.
- Creates Google Slides deck with EN-first then AR section and thank-you slide.
- Creates Gmail draft with deck link.
- Appends weekly snapshots to Google Sheets tabs.

## Notes
- For production schedule, run via cron or an orchestrator every Sunday in Asia/Riyadh.
- If OAuth tokens expire, refresh using existing auth scripts in projects/ziyada-system/scripts.
