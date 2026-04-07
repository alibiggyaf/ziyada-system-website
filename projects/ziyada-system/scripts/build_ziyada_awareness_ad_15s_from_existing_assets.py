#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects" / "ziyada-system"
OUTPUTS = PROJECT / "outputs"
TOKEN_PATH = PROJECT / "token_docs.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

SCENE_1 = OUTPUTS / "ziyada_awareness_scene_01.mp4"
SCENE_2 = OUTPUTS / "ziyada_sora_ad_16x9_v1.mp4"
VOICE = OUTPUTS / "ziyada_sora_ad_16x9_v1_ar_vo.mp3"

STITCHED = OUTPUTS / "ziyada_awareness_ad_15s_fallback_no_audio.mp4"
FINAL = OUTPUTS / "ziyada_awareness_ad_15s_fallback_final.mp4"


def run_ffmpeg(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:1400])


def stitch() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    # 8s + 8s with 1s xfade = 15s final.
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(SCENE_1),
        "-i",
        str(SCENE_2),
        "-filter_complex",
        "[0:v][1:v]xfade=transition=fade:duration=1:offset=7,format=yuv420p[v]",
        "-map",
        "[v]",
        "-an",
        "-t",
        "15",
        str(STITCHED),
    ]
    run_ffmpeg(cmd)


def mux_voice() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(STITCHED),
        "-i",
        str(VOICE),
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
        str(FINAL),
    ]
    run_ffmpeg(cmd)


def upload_to_drive() -> dict:
    if not TOKEN_PATH.exists():
        raise RuntimeError("token_docs.json missing for Drive upload")

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    drive = build("drive", "v3", credentials=creds)
    media = MediaFileUpload(str(FINAL), mimetype="video/mp4", resumable=False)
    created = drive.files().create(
        body={"name": FINAL.name},
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
    missing = [p for p in [SCENE_1, SCENE_2, VOICE] if not p.exists()]
    if missing:
        raise RuntimeError(f"Missing required assets: {missing}")

    stitch()
    mux_voice()
    links = upload_to_drive()

    print(
        json.dumps(
            {
                "scene_1": str(SCENE_1),
                "scene_2": str(SCENE_2),
                "voice": str(VOICE),
                "stitched": str(STITCHED),
                "final": str(FINAL),
                "drive_file_id": links.get("id"),
                "drive_web_view": links.get("webViewLink"),
                "drive_web_content": links.get("webContentLink"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
