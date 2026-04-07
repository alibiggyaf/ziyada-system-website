#!/usr/bin/env python3
"""Score weekly YouTube channels and videos for trend relevance."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "outputs" / "market_intel" / "youtube"

# ── Niche relevance configuration ─────────────────────────────────────────────
# Balanced mode: broad enough for trend coverage, tight enough to exclude
# clearly off-niche content (e.g. Morocco horse-driving videos).

_POSITIVE_TERMS: List[str] = [
    # AI / automation / tech
    "ai", "artificial intelligence", "automation", "machine learning", "chatgpt",
    "generative", "llm", "gpt", "claude", "gemini", "openai", "langchain",
    "workflow", "n8n", "zapier", "no-code", "low-code", "agentic",
    # Marketing / business
    "marketing", "digital marketing", "brand", "branding", "social media",
    "content marketing", "seo", "growth hacking", "startup", "entrepreneur",
    "business", "strategy", "campaign", "roi", "funnel", "conversion",
    "saas", "b2b", "ecommerce", "monetization", "revenue", "sales",
    # Region: MENA / Saudi / Arab
    "saudi", "ksa", "riyadh", "mena", "arabic", "arab", "gulf",
    "خليج", "سعود",
    "عربي", "السعودية",
    "التسويق", "ريادة",
    # YouTube / creator economy
    "youtube", "creator", "subscribers", "video marketing",
    "influencer", "content creation", "podcast", "newsletter",
]

_NEGATIVE_TERMS: List[str] = [
    # Sports / automotive unrelated to business tech
    "horse", "equestrian", "horse racing", "horse driving",
    "camel racing", "formula 1", "f1 race", "nascar", "rally racing",
    # Cooking (unless marketing angle — caught by low positive count)
    "recipe", "cooking tutorial", "chef",
    # Pure gaming (unless esports business)
    "gameplay", "walkthrough", "playthrough", "lets play", "game review",
    "minecraft", "fortnite", "roblox", "gta v", "call of duty",
    # Pure entertainment
    "funny animals", "pet video", "prank video",
    "moroccan driving", "camel driving",
]

# Minimum relevance to keep a video (0.0–1.0). Configurable via env.
_RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.15"))


def _relevance_score(video: Dict) -> Tuple[float, str, str]:
    """Return (score, decision, reason). Score range 0.0 to 1.0."""
    text = " ".join([
        video.get("title", ""),
        video.get("description", "")[:400],
        video.get("channel_title", ""),
        video.get("category_label", ""),
    ]).lower()

    pos_hits = [t for t in _POSITIVE_TERMS if t in text]
    neg_hits = [t for t in _NEGATIVE_TERMS if t in text]

    pos_score = min(1.0, len(pos_hits) * 0.2)
    neg_penalty = min(0.9, len(neg_hits) * 0.35)
    raw = max(0.0, pos_score - neg_penalty)

    # Channel category can rescue borderline-but-legitimate channel videos
    cat = video.get("category_label", "").lower()
    if cat in ("ai_marketing", "saudi_tech", "mena_business", "arabic_content"):
        raw = max(raw, 0.25)

    if neg_hits and not pos_hits:
        decision = "dropped"
        reason = "off-niche: " + ", ".join(neg_hits[:3])
    elif raw < _RELEVANCE_THRESHOLD:
        decision = "dropped"
        reason = f"low_relevance({raw:.2f}) pos={pos_hits[:3]}"
    else:
        decision = "kept"
        reason = f"ok({raw:.2f}) matched={pos_hits[:4]}"

    return round(raw, 3), decision, reason


def _score_video(video: Dict) -> float:
    views = float(video.get("views", 0))
    likes = float(video.get("likes", 0))
    comments = float(video.get("comments", 0))
    engagement = likes * 2.0 + comments * 3.0
    return views * 0.25 + engagement


def score_ingest_payload(payload: Dict) -> Dict:
    videos = payload.get("videos", [])
    channels = payload.get("channels", [])

    channel_index = {c["channel_id"]: dict(c) for c in channels}
    channel_scores: Dict[str, Dict] = {}

    scored_videos: List[Dict] = []
    rejected_videos: List[Dict] = []

    for video in videos:
        rel_score, decision, reason = _relevance_score(video)
        row = dict(video)
        row["relevance_score"] = rel_score
        row["relevance_decision"] = decision
        row["relevance_reason"] = reason

        if decision == "dropped":
            rejected_videos.append(row)
            continue

        trend_score = _score_video(video)
        row["trend_score"] = round(trend_score, 2)
        scored_videos.append(row)

        cid = video.get("channel_id", "")
        if cid not in channel_scores:
            channel_scores[cid] = {"video_count": 0, "sum_trend": 0.0, "sum_views": 0}
        channel_scores[cid]["video_count"] += 1
        channel_scores[cid]["sum_trend"] += trend_score
        channel_scores[cid]["sum_views"] += int(video.get("views", 0))

    # Log acceptance/rejection sample
    kept_n = len(scored_videos)
    dropped_n = len(rejected_videos)
    print(f"[relevance] kept={kept_n} dropped={dropped_n} "
          f"threshold={_RELEVANCE_THRESHOLD}")
    if rejected_videos:
        sample = rejected_videos[:3]
        for s in sample:
            print(f"  dropped: {s.get('title','')[:60]} — {s.get('relevance_reason','')}")

    scored_channels = []
    for cid, stats in channel_scores.items():
        base = channel_index.get(cid, {})
        avg_trend = stats["sum_trend"] / max(1, stats["video_count"])
        final_score = avg_trend * 0.55 + float(base.get("final_score", 0.0)) * 0.45
        scored_channels.append(
            {
                "run_id": payload["run_id"],
                "week_start": payload["week_start"],
                "week_end": payload["week_end"],
                "channel_id": cid,
                "channel_title": base.get("title", ""),
                "subscriber_count": base.get("subscriber_count", 0),
                "category_label": base.get("category_label", "other"),
                "relevance_score": base.get("relevance_score", 0.0),
                "region_score": base.get("region_score", 0.0),
                "video_count": stats["video_count"],
                "sum_views": stats["sum_views"],
                "avg_trend_score": round(avg_trend, 2),
                "final_channel_score": round(final_score, 2),
                "data_source": "youtube_api",
            }
        )

    scored_channels.sort(key=lambda x: x["final_channel_score"], reverse=True)
    scored_videos.sort(key=lambda x: x["trend_score"], reverse=True)

    return {
        "run_id": payload["run_id"],
        "timezone": payload["timezone"],
        "week_start": payload["week_start"],
        "week_end": payload["week_end"],
        "channels": scored_channels,
        "videos": scored_videos,
        "rejected_videos": rejected_videos,
    }


def save_scored_output(result: Dict) -> Path:
    out_dir = OUTPUT_DIR / result["run_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "weekly_scored.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    in_path = OUTPUT_DIR / run_id / "weekly_ingest.json"
    if not in_path.exists():
        raise SystemExit(f"Missing ingest file: {in_path}")
    payload = json.loads(in_path.read_text(encoding="utf-8"))
    result = score_ingest_payload(payload)
    out_path = save_scored_output(result)
    print(out_path)


if __name__ == "__main__":
    main()
