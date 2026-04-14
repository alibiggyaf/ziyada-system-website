from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parent
REFERENCE_IMAGE = ROOT / "Ziyada inspairations" / "Screenshot 2026-04-09 at 11.52.16 PM.png"

# Select model: "wan-2-7-video" (Wan 2.7 Video) or "kling-3-motion-control" (Kling 3.0 Motion Control)
MODEL_NAME = os.environ.get("KIE_VIDEO_MODEL", "wan-2-7-video")
OUTPUT_DIR = ROOT / "outputs" / "ziyada-video"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT = (
    "Use the reference image as the character and scene anchor. Preserve the same Saudi man, "
    "same face, same expression, same shemagh, same side-profile composition, same premium cinematic "
    "lighting, and same futuristic transparent screen interaction. Generate a 16:9 corporate awareness "
    "reel where he scrolls elegant enterprise software interface elements with his finger. Show advanced "
    "Arabic-first business system modules such as analytics dashboards, workflow automation, reporting, "
    "customer management, operations tracking, and decision-support panels. Keep the interface clean, "
    "premium, and believable. Avoid WhatsApp, messaging problems, chat bubbles, or consumer-app aesthetics. "
    "The mood is executive, calm, high-end, Saudi, and modern. Begin with a macro view of his fingertip "
    "touching the screen, then slowly pull back to reveal him operating the system. Use subtle cyan-blue "
    "holographic light, warm background bokeh, shallow depth of field, and controlled camera motion. End "
    "by transforming the interface into a refined Ziyada System logo impression with a modern Arabic "
    "technology brand feel. Opening and closing composition should feel close enough to support a seamless loop."
)

NEGATIVE_PROMPT = (
    "No WhatsApp references, no phone chat interface, no exaggerated cyberpunk clutter, no distorted hands, "
    "no extra people, no English headline text, no messy typography, no gaming HUD, no neon overload, "
    "no comedy tone, no aggressive action, no facial changes, no broken anatomy."
)

KIE_API_BASE = "https://api.kie.ai"
KIE_UPLOAD_BASE = "https://kieai.redpandaai.co"
VEO_API_ENDPOINT = f"{KIE_API_BASE}/api/v1/veo/generate"


def load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def get_api_key() -> str:
    for name in ("KIE_AI_API_KEY", "KIE_API_KEY", "SEEDANCE_API_KEY"):
        value = os.getenv(name)
        if value:
            return value
    raise SystemExit(
        "Missing KIE API key. Add KIE_AI_API_KEY or KIE_API_KEY to .env, then run again."
    )


def upload_image(api_key: str, image_path: Path) -> str:
    with image_path.open("rb") as fh:
        response = requests.post(
            f"{KIE_UPLOAD_BASE}/api/file-stream-upload",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (image_path.name, fh, "image/png")},
            data={"uploadPath": "images/user-uploads", "fileName": image_path.name},
            timeout=120,
        )
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data", {})
    file_url = data.get("fileUrl") or data.get("downloadUrl")
    if not file_url:
        raise RuntimeError(f"Upload succeeded but no fileUrl returned: {payload}")
    return file_url



def create_video_task(api_key: str, image_url: str) -> dict:
    if MODEL_NAME == "veo3_fast":
        # Veo 3.1 Fast: Image-to-Video mode
        payload = {
            "prompt": PROMPT,
            "imageUrls": [image_url],
            "model": "veo3_fast",
            "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO",
            "aspect_ratio": "16:9",
            "enableTranslation": True
        }
        response = requests.post(
            VEO_API_ENDPOINT,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
    elif MODEL_NAME == "wan-2-7-video":
        # Wan 2.7 Video: Image-to-Video mode
        payload = {
            "model": "wan-2-7-video",
            "input": {
                "mode": "image-to-video",
                "prompt": PROMPT,
                "negative_prompt": NEGATIVE_PROMPT,
                "image_url": image_url,
                "aspect_ratio": "16:9",
                "resolution": "720p",
                "duration": 10,
                "generate_audio": False,
                "return_last_frame": True,
            },
        }
        response = requests.post(
            f"{KIE_API_BASE}/api/v1/jobs/createTask",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
    elif MODEL_NAME == "kling-3-motion-control":
        # Kling 3.0 Motion Control: Image-to-Video (basic)
        payload = {
            "model": "kling-3-motion-control",
            "input": {
                "mode": "image-to-video",
                "prompt": PROMPT,
                "negative_prompt": NEGATIVE_PROMPT,
                "image_url": image_url,
                "aspect_ratio": "16:9",
                "resolution": "720p",
                "duration": 10,
                "generate_audio": False,
                "return_last_frame": True,
            },
        }
        response = requests.post(
            f"{KIE_API_BASE}/api/v1/jobs/createTask",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
    else:
        raise ValueError(f"Unsupported model: {MODEL_NAME}")
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Task creation failed: {json.dumps(data, ensure_ascii=False)}")
    return {"request": payload, "response": data}


def try_poll_task(api_key: str, task_id: str) -> dict | None:
    candidates = [
        (f"{KIE_API_BASE}/api/v1/jobs/recordInfo", {"taskId": task_id}),
        (f"{KIE_API_BASE}/api/v1/jobs/getTask", {"taskId": task_id}),
        (f"{KIE_API_BASE}/api/v1/jobs/queryTask", {"taskId": task_id}),
    ]
    headers = {"Authorization": f"Bearer {api_key}"}
    for url, params in candidates:
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=60)
            if resp.ok:
                payload = resp.json()
                if isinstance(payload, dict) and payload.get("code") == 200:
                    return {"url": url, "payload": payload}
        except requests.RequestException:
            continue
    return None


def main() -> None:
    load_dotenv_file(ROOT / ".env")

    if not REFERENCE_IMAGE.exists():
        raise SystemExit(f"Reference image not found: {REFERENCE_IMAGE}")

    api_key = get_api_key()
    image_url = upload_image(api_key, REFERENCE_IMAGE)
    created = create_video_task(api_key, image_url)
    task_id = created["response"].get("data", {}).get("taskId", "")

    record = {
        "reference_image": str(REFERENCE_IMAGE),
        "uploaded_image_url": image_url,
        "task_id": task_id,
        "created": created,
        "model": MODEL_NAME,
    }

    time.sleep(3)
    poll = try_poll_task(api_key, task_id) if task_id else None
    if poll:
        record["initial_poll"] = poll

    output_file = OUTPUT_DIR / f"ziyada_{MODEL_NAME}_task.json"
    output_file.write_text(json.dumps(record, ensure_ascii=False, indent=2))
    print(output_file)
    print(task_id)


if __name__ == "__main__":
    main()
