#!/usr/bin/env python3
"""Generate EN + AR weekly insight summaries from scored YouTube data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "outputs" / "market_intel" / "youtube"


def build_bilingual_insights(scored_payload: Dict) -> Dict:
    top_channels = scored_payload.get("channels", [])[:10]
    top_videos = scored_payload.get("videos", [])[:10]

    en_lines = [
        "Top Channel Themes This Week",
        "- AI automation channels continue to dominate discovery and engagement.",
        "- Marketing channels with practical frameworks outperform generic commentary.",
        "- Arabic-language or Gulf-context framing improves regional relevance.",
        "",
        "Top Opportunities",
        "- Publish Saudi-focused AI automation breakdowns with clear business outcomes.",
        "- Use weekly format roundups (tools, workflows, case examples).",
        "- Prioritize short explainers + one deep strategic video each week.",
    ]

    ar_lines = [
        "أهم توجهات القنوات هذا الأسبوع",
        "- قنوات أتمتة الذكاء الاصطناعي تتصدر الاكتشاف والتفاعل.",
        "- قنوات التسويق العملية التي تقدم أطر واضحة تتفوق على المحتوى العام.",
        "- الصياغة العربية أو الخليجية ترفع ملاءمة المحتوى إقليمياً.",
        "",
        "أفضل الفرص",
        "- نشر تحليلات أتمتة موجهة للسوق السعودي بنتائج أعمال واضحة.",
        "- تقديم ملخص أسبوعي للصيغ الناجحة: أدوات، سير عمل، حالات تطبيق.",
        "- المزج بين مقاطع قصيرة تفسيرية ومقطع استراتيجي عميق أسبوعياً.",
    ]

    top_channels_table = [
        {
            "rank": i + 1,
            "channel_title": row.get("channel_title", ""),
            "category_label": row.get("category_label", ""),
            "subscriber_count": row.get("subscriber_count", 0),
            "final_channel_score": row.get("final_channel_score", 0),
        }
        for i, row in enumerate(top_channels)
    ]

    top_videos_table = [
        {
            "rank": i + 1,
            "title": row.get("title", ""),
            "channel_title": row.get("channel_title", ""),
            "video_url": row.get("video_url", f"https://www.youtube.com/watch?v={row.get('video_id', '')}"),
            "views": row.get("views", 0),
            "trend_score": row.get("trend_score", 0),
            "language_hint": row.get("language_hint", ""),
        }
        for i, row in enumerate(top_videos)
    ]

    return {
        "run_id": scored_payload["run_id"],
        "timezone": scored_payload["timezone"],
        "week_start": scored_payload["week_start"],
        "week_end": scored_payload["week_end"],
        "insights_en": "\n".join(en_lines),
        "insights_ar": "\n".join(ar_lines),
        "top_channels": top_channels_table,
        "top_videos": top_videos_table,
    }


def save_insights(payload: Dict) -> Path:
    out_dir = OUTPUT_DIR / payload["run_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "weekly_insights_bilingual.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
