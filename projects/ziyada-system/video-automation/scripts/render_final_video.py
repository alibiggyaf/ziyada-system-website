from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def fetch_to_path(url: str, dest: Path) -> Path:
    if url.startswith(("http://", "https://")):
        urllib.request.urlretrieve(url, dest)
        return dest

    source = Path(url)
    if not source.exists():
        raise FileNotFoundError(f"Asset not found: {url}")
    shutil.copy2(source, dest)
    return dest


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def build_concat_file(video_paths: list[Path], concat_path: Path) -> None:
    lines = [f"file '{path.as_posix()}'" for path in video_paths]
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render(manifest: dict, output_path: Path) -> dict:
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg is required and was not found in PATH")

    with tempfile.TemporaryDirectory(prefix="video-render-") as tmp:
        tmp_dir = Path(tmp)
        working_videos: list[Path] = []
        working_voices: list[Path] = []
        working_music: list[Path] = []

        sorted_scenes = sorted(
            manifest["scenes"],
            key=lambda scene: int(scene["scene_order"]),
        )

        for idx, scene in enumerate(sorted_scenes, start=1):
            video_path = fetch_to_path(
                scene["scene_video_url"],
                tmp_dir / f"scene_{idx:02d}.mp4",
            )
            voice_path = fetch_to_path(
                scene["voiceover_url"],
                tmp_dir / f"scene_{idx:02d}_voice.mp3",
            )
            working_videos.append(video_path)
            working_voices.append(voice_path)

            music_url = scene.get("music_url_1") or scene.get("music_url_2")
            if music_url:
                working_music.append(
                    fetch_to_path(music_url, tmp_dir / f"scene_{idx:02d}_music.mp3")
                )

        concat_file = tmp_dir / "concat.txt"
        build_concat_file(working_videos, concat_file)

        concat_out = tmp_dir / "concat_video.mp4"
        run(
            [
                ffmpeg_bin,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                str(concat_out),
            ]
        )

        voice_concat_file = tmp_dir / "voice_concat.txt"
        build_concat_file(working_voices, voice_concat_file)
        voice_mix_out = tmp_dir / "voice_track.mp3"
        run(
            [
                ffmpeg_bin,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(voice_concat_file),
                "-c",
                "copy",
                str(voice_mix_out),
            ]
        )

        music_mix_out = None
        if working_music:
            music_concat_file = tmp_dir / "music_concat.txt"
            build_concat_file(working_music, music_concat_file)
            music_mix_out = tmp_dir / "music_track.mp3"
            run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(music_concat_file),
                    "-c",
                    "copy",
                    str(music_mix_out),
                ]
            )

        ensure_dir(output_path.parent)

        if music_mix_out:
            run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-i",
                    str(concat_out),
                    "-i",
                    str(voice_mix_out),
                    "-i",
                    str(music_mix_out),
                    "-filter_complex",
                    "[1:a]volume=1.2[voice];[2:a]volume=0.18[music];[voice][music]amix=inputs=2:duration=longest[aout]",
                    "-map",
                    "0:v:0",
                    "-map",
                    "[aout]",
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                    "-shortest",
                    str(output_path),
                ]
            )
        else:
            run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-i",
                    str(concat_out),
                    "-i",
                    str(voice_mix_out),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                    "-shortest",
                    str(output_path),
                ]
            )

        return {
            "project_id": manifest.get("project_id"),
            "output_path": str(output_path.resolve()),
            "scene_count": len(sorted_scenes),
            "music_used": bool(working_music),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to JSON manifest file")
    parser.add_argument("--output", required=True, help="Final video output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    manifest_path = Path(args.manifest)
    output_path = Path(args.output)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = render(manifest, output_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
