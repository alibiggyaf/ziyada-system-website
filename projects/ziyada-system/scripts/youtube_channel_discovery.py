#!/usr/bin/env python3
"""Auto-discover top YouTube channels for AI automation and marketing."""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "outputs" / "market_intel" / "youtube"

AI_TERMS = [
    "ai automation",
    "workflow automation",
    "n8n automation",
    "zapier automation",
    "no-code ai",
    "agentic ai",
    "ai tools",
    "أتمتة الذكاء الاصطناعي",
    "أتمتة الأعمال",
    "وكلاء الذكاء الاصطناعي",
]

MARKETING_TERMS = [
    "digital marketing",
    "b2b marketing",
    "content marketing",
    "lead generation",
    "growth marketing",
    "التسويق الرقمي",
    "التسويق بالمحتوى",
    "توليد العملاء المحتملين",
]

SAUDI_EGYPT_HINTS = [
    "saudi",
    "ksa",
    "riyadh",
    "jeddah",
    "egypt",
    "cairo",
    "السعود",
    "السعودية",
    "الرياض",
    "جدة",
    "مصر",
    "القاهرة",
]


@dataclass
class ChannelCandidate:
    channel_id: str
    title: str
    description: str
    subscriber_count: int
    video_count: int
    view_count: int
    ai_score: float
    marketing_score: float
    region_score: float
    relevance_score: float
    category_label: str
    final_score: float


def _api_get(url: str) -> Dict:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def _keyword_score(text: str, terms: List[str]) -> float:
    normalized = text.lower()
    score = 0.0
    for term in terms:
        if term.lower() in normalized:
            score += 1.0
    return score


def _classify_channel(title: str, description: str) -> Tuple[float, float, float, str]:
    text = f"{title} {description}"
    ai = _keyword_score(text, AI_TERMS)
    marketing = _keyword_score(text, MARKETING_TERMS)
    region = _keyword_score(text, SAUDI_EGYPT_HINTS)

    if ai >= marketing:
        label = "ai_automation"
    else:
        label = "marketing"

    relevance = ai * 1.3 + marketing * 1.0 + region * 0.6
    return ai, marketing, region, label if relevance > 0 else "other"


def _extract_subscriber(stats: Dict) -> int:
    raw = stats.get("subscriberCount")
    if raw is None:
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


def _extract_int(stats: Dict, key: str) -> int:
    raw = stats.get(key)
    if raw is None:
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


def _search_channels(api_key: str, query: str, max_results: int = 25, youtube_service=None) -> List[str]:
    if youtube_service is not None:
        data = (
            youtube_service.search()
            .list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=max_results,
                regionCode="SA",
            )
            .execute()
        )
    else:
        qs = urllib.parse.urlencode(
            {
                "part": "snippet",
                "q": query,
                "type": "channel",
                "maxResults": str(max_results),
                "regionCode": "SA",
                "key": api_key,
            }
        )
        url = f"https://www.googleapis.com/youtube/v3/search?{qs}"
        data = _api_get(url)
    items = data.get("items", [])
    ids = []
    for item in items:
        cid = item.get("snippet", {}).get("channelId")
        if cid:
            ids.append(cid)
    return ids


def _fetch_channel_details(api_key: str, channel_ids: List[str], youtube_service=None) -> Dict[str, Dict]:
    if not channel_ids:
        return {}
    chunks = [channel_ids[i : i + 50] for i in range(0, len(channel_ids), 50)]
    result: Dict[str, Dict] = {}
    for chunk in chunks:
        if youtube_service is not None:
            data = (
                youtube_service.channels()
                .list(part="snippet,statistics", id=",".join(chunk), maxResults=50)
                .execute()
            )
        else:
            qs = urllib.parse.urlencode(
                {
                    "part": "snippet,statistics",
                    "id": ",".join(chunk),
                    "maxResults": "50",
                    "key": api_key,
                }
            )
            url = f"https://www.googleapis.com/youtube/v3/channels?{qs}"
            data = _api_get(url)
        for item in data.get("items", []):
            result[item.get("id", "")] = item
    return result


def discover_channels(
    api_key: str,
    target_min: int = 20,
    target_max: int = 30,
    ai_weight: float = 0.7,
    youtube_service=None,
) -> List[Dict]:
    marketing_weight = 1.0 - ai_weight

    pool_ids: List[str] = []
    for term in AI_TERMS + MARKETING_TERMS:
        pool_ids.extend(_search_channels(api_key, term, max_results=15, youtube_service=youtube_service))

    deduped = list(dict.fromkeys(pool_ids))
    details = _fetch_channel_details(api_key, deduped, youtube_service=youtube_service)

    candidates: List[ChannelCandidate] = []
    for channel_id, item in details.items():
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        title = snippet.get("title", "")
        description = snippet.get("description", "")
        ai_score, marketing_score, region_score, category = _classify_channel(title, description)
        subscribers = _extract_subscriber(stats)

        # Log-scale preference for channel size.
        size_score = 0.0
        if subscribers > 0:
            size_score = min(10.0, len(str(subscribers)) * 1.5)

        weighted_category = ai_score * ai_weight + marketing_score * marketing_weight
        relevance = weighted_category + region_score * 0.6
        final_score = size_score * 0.55 + relevance * 0.45

        candidates.append(
            ChannelCandidate(
                channel_id=channel_id,
                title=title,
                description=description,
                subscriber_count=subscribers,
                video_count=_extract_int(stats, "videoCount"),
                view_count=_extract_int(stats, "viewCount"),
                ai_score=ai_score,
                marketing_score=marketing_score,
                region_score=region_score,
                relevance_score=relevance,
                category_label=category,
                final_score=final_score,
            )
        )

    # Keep top channels by score, then enforce 70/30 preference where possible.
    candidates.sort(key=lambda c: c.final_score, reverse=True)
    ai_channels = [c for c in candidates if c.category_label == "ai_automation"]
    marketing_channels = [c for c in candidates if c.category_label == "marketing"]

    target = max(target_min, min(target_max, len(candidates)))
    ai_target = int(round(target * ai_weight))
    mk_target = target - ai_target

    selected = ai_channels[:ai_target] + marketing_channels[:mk_target]
    if len(selected) < target:
        selected_ids = {c.channel_id for c in selected}
        for c in candidates:
            if c.channel_id not in selected_ids:
                selected.append(c)
            if len(selected) >= target:
                break

    return [c.__dict__ for c in selected[:target_max]]


def save_discovery_output(channels: List[Dict], run_id: str) -> Path:
    out_dir = OUTPUT_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "discovered_channels.json"
    payload = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "channels": channels,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing YOUTUBE_API_KEY")

    target_min = int(os.getenv("REPORT_CHANNEL_TARGET_MIN", "20"))
    target_max = int(os.getenv("REPORT_CHANNEL_TARGET_MAX", "30"))
    ai_weight = 0.7

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    channels = discover_channels(api_key, target_min=target_min, target_max=target_max, ai_weight=ai_weight)
    out_path = save_discovery_output(channels, run_id)
    print(f"Discovered {len(channels)} channels")
    print(out_path)


if __name__ == "__main__":
    main()
