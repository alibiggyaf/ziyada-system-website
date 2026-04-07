#!/usr/bin/env python3
"""Ingest weekly YouTube video data for selected channels."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from youtube_channel_discovery import discover_channels, save_discovery_output


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "outputs" / "market_intel" / "youtube"


def _api_get(url: str) -> Dict:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def _week_window(timezone_name: str, lookback_days: int) -> Tuple[datetime, datetime]:
    tz = ZoneInfo(timezone_name)
    now_local = datetime.now(tz)
    end_local = datetime(now_local.year, now_local.month, now_local.day, tzinfo=tz)
    start_local = end_local - timedelta(days=lookback_days)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _search_channel_videos(api_key: str, channel_id: str, published_after: str, max_results: int, youtube_service=None) -> List[str]:
    if youtube_service is not None:
        data = (
            youtube_service.search()
            .list(
                part="snippet",
                channelId=channel_id,
                order="date",
                type="video",
                publishedAfter=published_after,
                maxResults=max_results,
            )
            .execute()
        )
    else:
        qs = urllib.parse.urlencode(
            {
                "part": "snippet",
                "channelId": channel_id,
                "order": "date",
                "type": "video",
                "publishedAfter": published_after,
                "maxResults": str(max_results),
                "key": api_key,
            }
        )
        url = f"https://www.googleapis.com/youtube/v3/search?{qs}"
        data = _api_get(url)
    ids = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if video_id:
            ids.append(video_id)
    return ids


def _fetch_videos(api_key: str, video_ids: List[str], youtube_service=None) -> List[Dict]:
    if not video_ids:
        return []
    out = []
    chunks = [video_ids[i : i + 50] for i in range(0, len(video_ids), 50)]
    for chunk in chunks:
        if youtube_service is not None:
            data = (
                youtube_service.videos()
                .list(part="snippet,statistics,contentDetails", id=",".join(chunk), maxResults=50)
                .execute()
            )
        else:
            qs = urllib.parse.urlencode(
                {
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(chunk),
                    "maxResults": "50",
                    "key": api_key,
                }
            )
            url = f"https://www.googleapis.com/youtube/v3/videos?{qs}"
            data = _api_get(url)
        out.extend(data.get("items", []))
    return out


def _to_int(raw: str | None) -> int:
    if not raw:
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


def _language_hint(snippet: Dict) -> str:
    default_lang = snippet.get("defaultAudioLanguage") or snippet.get("defaultLanguage") or ""
    if default_lang:
        return str(default_lang)
    text = f"{snippet.get('title', '')} {snippet.get('description', '')}".lower()
    if any(ar in text for ar in ["ال", "في", "من", "على"]):
        return "ar"
    return "en"


def ingest_weekly_data(api_key: str, run_id: str, timezone_name: str, lookback_days: int, youtube_service=None) -> Dict:
    channels = discover_channels(
        api_key=api_key,
        target_min=int(os.getenv("REPORT_CHANNEL_TARGET_MIN", "20")),
        target_max=int(os.getenv("REPORT_CHANNEL_TARGET_MAX", "30")),
        ai_weight=0.7,
        youtube_service=youtube_service,
    )
    save_discovery_output(channels, run_id)

    max_videos_per_channel = int(os.getenv("REPORT_MAX_VIDEOS_PER_CHANNEL", "12"))
    start_utc, end_utc = _week_window(timezone_name, lookback_days)
    published_after = start_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    videos_out = []
    for ch in channels:
        video_ids = _search_channel_videos(
            api_key,
            ch["channel_id"],
            published_after,
            max_videos_per_channel,
            youtube_service=youtube_service,
        )
        video_items = _fetch_videos(api_key, video_ids, youtube_service=youtube_service)

        for item in video_items:
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            videos_out.append(
                {
                    "run_id": run_id,
                    "week_start": start_utc.isoformat(),
                    "week_end": end_utc.isoformat(),
                    "channel_id": ch["channel_id"],
                    "channel_title": ch["title"],
                    "category_label": ch["category_label"],
                    "video_id": item.get("id", ""),
                    "video_url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "views": _to_int(stats.get("viewCount")),
                    "likes": _to_int(stats.get("likeCount")),
                    "comments": _to_int(stats.get("commentCount")),
                    "duration": item.get("contentDetails", {}).get("duration", ""),
                    "language_hint": _language_hint(snippet),
                    "data_source": "youtube_api",
                }
            )

    return {
        "run_id": run_id,
        "timezone": timezone_name,
        "week_start": start_utc.isoformat(),
        "week_end": end_utc.isoformat(),
        "channels": channels,
        "videos": videos_out,
    }


def save_ingest_output(result: Dict) -> Path:
    out_dir = OUTPUT_DIR / result["run_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "weekly_ingest.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing YOUTUBE_API_KEY")

    timezone_name = os.getenv("REPORT_TIMEZONE", "Asia/Riyadh")
    lookback_days = int(os.getenv("REPORT_DEFAULT_LOOKBACK_DAYS", "7"))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    result = ingest_weekly_data(api_key, run_id, timezone_name, lookback_days)
    out_path = save_ingest_output(result)
    print(f"Ingested {len(result['channels'])} channels and {len(result['videos'])} videos")
    print(out_path)


if __name__ == "__main__":
    main()
