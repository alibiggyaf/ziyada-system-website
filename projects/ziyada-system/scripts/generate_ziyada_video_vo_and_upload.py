#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess

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

VIDEO_IN = OUTPUTS / "ziyada_sora_ad_16x9_v1.mp4"
AUDIO_OUT = OUTPUTS / "ziyada_sora_ad_16x9_v1_ar_vo.mp3"
VIDEO_OUT = OUTPUTS / "ziyada_sora_ad_16x9_v1_with_ar_vo.mp4"

VOICE_SCRIPT = (
    "كل يوم يبدأ برسائل كثيرة ومتابعات ما تخلص. "
    "تتأخر الردود وتضيع فرص بين القنوات. "
    "هنا يجي دور زيادة سيستم. "
    "نوحد القنوات وننظم المتابعة ونخلي التشغيل أوضح لفريقك. "
    "النتيجة ضغط أقل واستجابة أسرع وفرص أكثر تتحول لمبيعات. "
    "إذا ودك شغل أذكى وأسهل حنا جاهزين."
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


def generate_arabic_voiceover(openai_api_key: str) -> None:
    resp = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini-tts",
            "voice": "alloy",
            "format": "mp3",
            "input": VOICE_SCRIPT,
            "instructions": (
                "Arabic Saudi white dialect, warm and professional, clear pacing, "
                "no hype, brief pauses between ideas."
            ),
        },
        timeout=240,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"TTS failed: {resp.status_code} {resp.text[:500]}")
    AUDIO_OUT.write_bytes(resp.content)


def mux_video_and_audio() -> None:
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        str(VIDEO_IN),
        "-i",
        str(AUDIO_OUT),
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
        str(VIDEO_OUT),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Mux failed: {proc.stderr[:1200]}")


def upload_to_drive() -> dict:
    if not TOKEN_PATH.exists():
        raise RuntimeError("token_docs.json missing for Google Drive upload")

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    drive = build("drive", "v3", credentials=creds)
    metadata = {"name": VIDEO_OUT.name}
    media = MediaFileUpload(str(VIDEO_OUT), mimetype="video/mp4", resumable=False)
    created = drive.files().create(
        body=metadata,
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
    if not VIDEO_IN.exists():
        raise RuntimeError(f"Input video not found: {VIDEO_IN}")

    key = read_openai_api_key()
    generate_arabic_voiceover(key)
    mux_video_and_audio()
    links = upload_to_drive()

    print(
        json.dumps(
            {
                "video_local": str(VIDEO_OUT),
                "audio_local": str(AUDIO_OUT),
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
