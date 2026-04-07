#!/usr/bin/env python3
"""Orchestrator: run weekly niche signal ingestion -> scoring -> insights -> sheets -> slides -> gmail."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from create_youtube_trend_slides import create_deck
from export_youtube_dashboard_data import export_dashboard_json
from send_youtube_trend_report import create_report_draft
from youtube_trend_ingest import ingest_weekly_data, save_ingest_output
from youtube_trend_scoring import save_scored_output, score_ingest_payload
from youtube_trend_sheets_store import store_weekly_snapshots
from youtube_weekly_insights_bilingual import build_bilingual_insights, save_insights


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "outputs" / "market_intel" / "youtube"
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"


def load_env_file() -> None:
    env_path = PROJECT_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly Niche Signal Intelligence report")
    parser.add_argument("--mode", choices=["manual", "scheduled"], default="manual")
    parser.add_argument("--timezone", default=os.getenv("REPORT_TIMEZONE", "Asia/Riyadh"))
    parser.add_argument("--lookback-days", type=int, default=int(os.getenv("REPORT_DEFAULT_LOOKBACK_DAYS", "7")))
    parser.add_argument("--from-run-id", default="", help="Reuse an existing run_id from outputs when API quota is exceeded")
    parser.add_argument("--sheet-id", default="", help="Override GOOGLE_SHEET_ID for this run")
    return parser.parse_args()


def _oauth_youtube_service_or_none():
    token_path = PROJECT_DIR / "token.json"
    if not token_path.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(token_path))
    scopes = set(creds.scopes or [])
    if YOUTUBE_SCOPE not in scopes:
        return None
    if not creds.valid and not creds.refresh_token:
        return None
    return build("youtube", "v3", credentials=creds)


def _estimate_api_units(scored: Dict) -> int:
    channels = len(scored.get("channels", []))
    videos = len(scored.get("videos", []))
    # Rough quota estimate: discovery/search dominates quota usage.
    discovery_units = 1800
    channel_video_search_units = channels * 100
    low_cost_calls = max(1, channels // 50) + max(1, videos // 50)
    return discovery_units + channel_video_search_units + low_cost_calls


def _estimate_run_cost_usd(api_units: int) -> float:
    # Cost is effectively zero while within standard free YouTube quota.
    return 0.0 if api_units <= 10000 else round(((api_units - 10000) / 1000.0) * 5.0, 2)


def _latest_cached_run_id() -> str:
    if not OUTPUT_DIR.exists():
        return ""
    candidates = []
    for child in OUTPUT_DIR.iterdir():
        if not child.is_dir():
            continue
        if (child / "weekly_scored.json").exists():
            candidates.append(child.name)
    candidates.sort(reverse=True)
    return candidates[0] if candidates else ""


def main() -> None:
    load_env_file()
    args = parse_args()
    if args.sheet_id:
        os.environ["GOOGLE_SHEET_ID"] = args.sheet_id.strip()
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    youtube_service = None
    if not api_key:
        youtube_service = _oauth_youtube_service_or_none()
    if not args.from_run_id and not api_key and youtube_service is None:
        raise SystemExit(
            "Missing YOUTUBE_API_KEY and OAuth token lacks youtube.readonly. "
            "Run scripts/setup_youtube_report_oauth.py first."
        )

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    source_run_id = args.from_run_id

    if source_run_id:
        source_dir = OUTPUT_DIR / source_run_id
        ingest_path = source_dir / "weekly_ingest.json"
        scored_path = source_dir / "weekly_scored.json"
        if not scored_path.exists():
            raise SystemExit(f"Missing cached scored file: {scored_path}")
        scored = json.loads(scored_path.read_text(encoding="utf-8"))
        insights = build_bilingual_insights(scored)
        insights["run_id"] = run_id
        insights_path = save_insights(insights)
    else:
        try:
            ingest = ingest_weekly_data(
                api_key,
                run_id,
                args.timezone,
                args.lookback_days,
                youtube_service=youtube_service,
            )
            ingest_path = save_ingest_output(ingest)

            scored = score_ingest_payload(ingest)
            scored_path = save_scored_output(scored)

            insights = build_bilingual_insights(scored)
            insights_path = save_insights(insights)
        except HttpError as exc:
            if "quotaExceeded" not in str(exc):
                raise
            fallback_id = _latest_cached_run_id()
            if not fallback_id:
                raise SystemExit("YouTube quota exceeded and no cached run is available for fallback.")
            source_run_id = fallback_id
            source_dir = OUTPUT_DIR / source_run_id
            ingest_path = source_dir / "weekly_ingest.json"
            scored_path = source_dir / "weekly_scored.json"
            scored = json.loads(scored_path.read_text(encoding="utf-8"))
            insights = build_bilingual_insights(scored)
            insights["run_id"] = run_id
            insights_path = save_insights(insights)

    api_units_est = _estimate_api_units(scored)
    run_cost_usd = _estimate_run_cost_usd(api_units_est)

    spreadsheet_id = store_weekly_snapshots(scored, insights, mode=args.mode, run_cost_usd=run_cost_usd)

    deck_id = create_deck(insights, scored, run_cost_usd)
    deck_url = f"https://docs.google.com/presentation/d/{deck_id}/edit"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

    recipient = os.getenv("REPORT_RECIPIENT_EMAIL", "ali.biggy.af@gmail.com")
    subject = f"Weekly Niche Signal Intelligence Report | {insights['week_start']} to {insights['week_end']}"

    top_video_links = "\n".join(
        [f"- {v.get('title', '')}: {v.get('video_url', '')}" for v in insights.get("top_videos", [])[:10]]
    )

    text_body = (
        "Dear Ali,\n\n"
        "Please find your weekly Niche Signal Intelligence report below.\n\n"
        f"Run ID: {run_id}\n"
        f"Reporting Window: {insights['week_start']} to {insights['week_end']} ({insights['timezone']})\n"
        f"Channels Analyzed: {len(scored['channels'])}\n"
        f"Videos Scored: {len(scored['videos'])}\n"
        f"Estimated API Units: {api_units_est}\n"
        f"Estimated Run Cost (USD): ${run_cost_usd:.2f}\n"
        f"Presentation: {deck_url}\n"
        f"Data Sheet: {sheet_url}\n\n"
        "Top video links:\n"
        f"{top_video_links}\n\n"
        "Prepared by Ali Fallatah Portfolio Insights Team.\n"
    )

    html_body = f"""
    <html><body>
    <h2>Weekly Niche Signal Intelligence Report</h2>
    <p>Dear Ali,</p>
    <p>Please find your weekly report prepared for your review.</p>
    <p><strong>Run ID:</strong> {run_id}</p>
    <p><strong>Reporting Window:</strong> {insights['week_start']} to {insights['week_end']} ({insights['timezone']})</p>
        <p><strong>Channels:</strong> {len(scored['channels'])} | <strong>Videos:</strong> {len(scored['videos'])}</p>
        <p><strong>Estimated API Units:</strong> {api_units_est}</p>
        <p><strong>Estimated Run Cost:</strong> ${run_cost_usd:.2f}</p>
      <p><a href=\"{deck_url}\">Open Google Slides Report</a></p>
            <p><a href=\"{sheet_url}\">Open Google Sheets History</a></p>
            <h3>Top Video Links</h3>
            <ul>
                {''.join([f"<li><a href='{v.get('video_url','')}'>{v.get('title','')}</a></li>" for v in insights.get('top_videos', [])[:10]])}
            </ul>
            <p style="margin-top:20px;">Prepared by Ali Fallatah Portfolio Insights Team.</p>
    </body></html>
    """

    draft_id = create_report_draft(recipient, subject, html_body, text_body)

    run_summary = {
        "run_id": run_id,
        "mode": args.mode,
        "timezone": args.timezone,
        "week_start": insights["week_start"],
        "week_end": insights["week_end"],
        "channels_selected": len(scored["channels"]),
        "videos_scored": len(scored["videos"]),
        "api_units_est": api_units_est,
        "run_cost_usd": run_cost_usd,
        "fallback_source_run_id": source_run_id,
        "ingest_path": str(ingest_path),
        "scored_path": str(scored_path),
        "insights_path": str(insights_path),
        "deck_url": deck_url,
        "sheet_url": sheet_url,
        "gmail_draft_id": draft_id,
    }

    out_dir = OUTPUT_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "run_summary.json"
    summary_path.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        dashboard_path = export_dashboard_json()
        run_summary["dashboard_payload_path"] = str(dashboard_path)
        summary_path.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        run_summary["dashboard_payload_warning"] = str(exc)
        summary_path.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(run_summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
