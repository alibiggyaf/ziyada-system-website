#!/usr/bin/env python3
"""Export latest trend-intelligence run into a frontend-friendly dashboard JSON."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "outputs" / "market_intel" / "youtube"
TARGET_PATH = PROJECT_DIR / "app" / "ziyada-system-website" / "public" / "niche-signal-intelligence-dashboard.json"


def _load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_run_dir() -> Optional[Path]:
    if not OUTPUT_DIR.exists():
        return None
    candidates: List[Path] = []
    for child in OUTPUT_DIR.iterdir():
        if not child.is_dir():
            continue
        if (child / "run_summary.json").exists() and (child / "weekly_scored.json").exists():
            candidates.append(child)
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.name)[-1]


def _build_history(limit: int = 8) -> List[Dict]:
    rows: List[Dict] = []
    if not OUTPUT_DIR.exists():
        return rows
    run_dirs = sorted([p for p in OUTPUT_DIR.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
    for run_dir in run_dirs:
        summary_path = run_dir / "run_summary.json"
        if not summary_path.exists():
            continue
        try:
            summary = _load_json(summary_path)
        except Exception:
            continue
        rows.append(
            {
                "run_id": summary.get("run_id", run_dir.name),
                "week_end": summary.get("week_end", ""),
                "channels_selected": int(summary.get("channels_selected", 0)),
                "videos_scored": int(summary.get("videos_scored", 0)),
                "run_cost_usd": float(summary.get("run_cost_usd", 0.0)),
            }
        )
        if len(rows) >= limit:
            break
    return list(reversed(rows))


def export_dashboard_json() -> Path:
    latest = _latest_run_dir()
    if latest is None:
        raise SystemExit(f"No run directories with summary/scored files found in: {OUTPUT_DIR}")

    summary = _load_json(latest / "run_summary.json")
    scored = _load_json(latest / "weekly_scored.json")

    insights_path = latest / "weekly_insights_bilingual.json"
    insights = _load_json(insights_path) if insights_path.exists() else {}

    videos = scored.get("videos", [])
    rejected = scored.get("rejected_videos", [])
    channels = scored.get("channels", [])

    kept_count = len(videos)
    dropped_count = len(rejected)
    total_considered = kept_count + dropped_count
    acceptance_rate = round((kept_count / total_considered) * 100.0, 1) if total_considered else 0.0

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_run_id": summary.get("run_id", latest.name),
        "summary": {
            "run_id": summary.get("run_id", latest.name),
            "timezone": summary.get("timezone", scored.get("timezone", "Asia/Riyadh")),
            "week_start": summary.get("week_start", scored.get("week_start", "")),
            "week_end": summary.get("week_end", scored.get("week_end", "")),
            "deck_url": summary.get("deck_url", ""),
            "sheet_url": summary.get("sheet_url", ""),
            "api_units_est": int(summary.get("api_units_est", 0)),
            "run_cost_usd": float(summary.get("run_cost_usd", 0.0)),
            "gmail_draft_id": summary.get("gmail_draft_id", ""),
            "report_recipient": summary.get("report_recipient", "ali.biggy.af@gmail.com"),
        },
        "kpis": {
            "channels_selected": int(summary.get("channels_selected", len(channels))),
            "videos_scored": int(summary.get("videos_scored", kept_count)),
            "videos_rejected": dropped_count,
            "acceptance_rate": acceptance_rate,
        },
        "top_channels": channels[:12],
        "top_videos": videos[:12],
        "rejected_samples": rejected[:8],
        "insights_en": insights.get("insights_en", ""),
        "insights_ar": insights.get("insights_ar", ""),
        "history": _build_history(limit=8),
    }

    TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    TARGET_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return TARGET_PATH


if __name__ == "__main__":
    out = export_dashboard_json()
    print(out)
