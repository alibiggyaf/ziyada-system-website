#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Dict

import imageio_ffmpeg
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects" / "ziyada-system"
OUTPUTS = PROJECT / "outputs"
TOKEN_PATH = PROJECT / "token_docs.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

MODEL = "sora-2"
SIZE = "1280x720"  # 16:9
SECONDS_PER_SCENE = "8"
POLL_INTERVAL_SECONDS = 5
POLL_MAX_ATTEMPTS = 120

SCENE_1_PROMPT = (
    "16:9 cinematic awareness intro video, Saudi business environment, "
    "no on-screen text, no captions, no numbers. "
    "Start with abstract geometric blue network animation and soft light motion, "
    "then reveal a Saudi operations team collaborating in a calm modern workspace. "
    "Mood: trustworthy, human, practical, non-sales. "
    "Visual direction: deep blue and purple gradient accents inspired by enterprise tech identity. "
    "Smooth camera movement, polished transitions, clean composition."
)

SCENE_2_PROMPT = (
    "16:9 cinematic awareness outro video that visually continues from previous scene, "
    "Saudi business operations in control, unified communication flow, "
    "no on-screen text, no captions, no numbers. "
    "Show elegant geometric 3D light lines in background and a confident team workflow. "
    "End with a minimal brand-feel closing shot on deep blue geometric background. "
    "Mood: calm confidence, future-ready, non-promotional, premium corporate style."
)

VOICEOVER_AR = (
    "في يوم الشغل، التفاصيل كثيرة، والمتابعة ما توقف. "
    "ومع وضوح النظام، كل فريق يقدر يشتغل بهدوء أكثر. "
    "تنسيق أفضل، تواصل أسهل، وخطوات أوضح من البداية للنهاية. "
    "هذا هو الفرق لما التقنية تخدم الناس فعلاً."
)


def read_openai_api_key() -> str:
    env_path = ROOT / ".env"
    if not env_path.exists():
        raise RuntimeError(".env file is missing")

    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("OPENAI_API_KEY="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            if value:
                return value
    raise RuntimeError("OPENAI_API_KEY not found in .env")


def openai_post(api_key: str, path: str, payload: Dict) -> Dict:
    resp = requests.post(
        f"https://api.openai.com{path}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=180,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"OpenAI POST {path} failed: {resp.status_code} {resp.text[:800]}")
    return resp.json()


def openai_get(api_key: str, path: str) -> Dict:
    resp = requests.get(
        f"https://api.openai.com{path}",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=180,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"OpenAI GET {path} failed: {resp.status_code} {resp.text[:800]}")
    return resp.json()


def create_video_job(api_key: str, prompt: str) -> str:
    payload = {
        "model": MODEL,
        "seconds": SECONDS_PER_SCENE,
        "size": SIZE,
        "prompt": prompt,
    }
    data = openai_post(api_key, "/v1/videos", payload)
    return data["id"]


def wait_for_video(api_key: str, video_id: str) -> Dict:
    last = {}
    for _ in range(POLL_MAX_ATTEMPTS):
        data = openai_get(api_key, f"/v1/videos/{video_id}")
        last = data
        status = data.get("status")
        if status == "completed":
            return data
        if status == "failed":
            err = data.get("error") or {}
            raise RuntimeError(f"Video failed for {video_id}: {err}")
        time.sleep(POLL_INTERVAL_SECONDS)
    raise RuntimeError(f"Video polling timed out for {video_id}. Last status: {last.get('status')}")


def download_video_content(api_key: str, video_id: str, target: Path) -> None:
    resp = requests.get(
        f"https://api.openai.com/v1/videos/{video_id}/content",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=240,
    )
    if resp.status_code >= 300:
        raise RuntimeError(
            f"Video download failed for {video_id}: {resp.status_code} {resp.text[:500]}"
        )
    target.write_bytes(resp.content)


def generate_voiceover(api_key: str, target: Path) -> None:
    resp = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini-tts",
            "voice": "alloy",
            "format": "mp3",
            "input": VOICEOVER_AR,
            "instructions": (
                "Arabic Saudi white dialect, calm and warm, awareness style, "
                "professional, medium pace, short pauses between sentences."
            ),
        },
        timeout=240,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"TTS failed: {resp.status_code} {resp.text[:800]}")
    target.write_bytes(resp.content)


def run_ffmpeg(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:1400])


def stitch_scenes_with_transition(scene1: Path, scene2: Path, out_no_audio: Path) -> None:
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    # Crossfade starts at 7s: 8 + 8 - 1 = 15s total.
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        str(scene1),
        "-i",
        str(scene2),
        "-filter_complex",
        "[0:v][1:v]xfade=transition=fade:duration=1:offset=7,format=yuv420p[v]",
        "-map",
        "[v]",
        "-an",
        "-t",
        "15",
        str(out_no_audio),
    ]
    run_ffmpeg(cmd)


def mux_voiceover(video_no_audio: Path, voiceover: Path, out_video: Path) -> None:
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        str(video_no_audio),
        "-i",
        str(voiceover),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(out_video),
    ]
    run_ffmpeg(cmd)


def upload_to_drive(video_path: Path) -> Dict:
    if not TOKEN_PATH.exists():
        raise RuntimeError("token_docs.json missing for Google Drive upload")

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    drive = build("drive", "v3", credentials=creds)
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=False)
    created = drive.files().create(
        body={"name": video_path.name},
        media_body=media,
        fields="id,name,webViewLink,webContentLink",
    ).execute()

    try:
        drive.permissions().create(
            fileId=created["id"],
            body={"role": "reader", "type": "anyone"},
            fields="id",
        ).execute()
    except Exception:
        pass

    return drive.files().get(
        fileId=created["id"],
        fields="id,name,webViewLink,webContentLink",
    ).execute()


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    api_key = read_openai_api_key()

    scene1_path = OUTPUTS / "ziyada_awareness_scene_01.mp4"
    scene2_path = OUTPUTS / "ziyada_awareness_scene_02.mp4"
    stitched_path = OUTPUTS / "ziyada_awareness_ad_15s_no_audio.mp4"
    voice_path = OUTPUTS / "ziyada_awareness_ad_15s_ar_vo.mp3"
    final_path = OUTPUTS / "ziyada_awareness_ad_15s_final.mp4"

    video1_id = create_video_job(api_key, SCENE_1_PROMPT)
    wait_for_video(api_key, video1_id)
    download_video_content(api_key, video1_id, scene1_path)

    video2_id = create_video_job(api_key, SCENE_2_PROMPT)
    wait_for_video(api_key, video2_id)
    download_video_content(api_key, video2_id, scene2_path)

    stitch_scenes_with_transition(scene1_path, scene2_path, stitched_path)
    generate_voiceover(api_key, voice_path)
    mux_voiceover(stitched_path, voice_path, final_path)

    drive_links = upload_to_drive(final_path)

    print(
        json.dumps(
            {
                "scene_1_video_id": video1_id,
                "scene_2_video_id": video2_id,
                "scene_1_local": str(scene1_path),
                "scene_2_local": str(scene2_path),
                "stitched_local": str(stitched_path),
                "voice_local": str(voice_path),
                "final_local": str(final_path),
                "drive_file_id": drive_links.get("id"),
                "drive_web_view": drive_links.get("webViewLink"),
                "drive_web_content": drive_links.get("webContentLink"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
