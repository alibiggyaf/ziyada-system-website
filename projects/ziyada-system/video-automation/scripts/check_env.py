from __future__ import annotations

import os
from pathlib import Path


REQUIRED_VARS = [
    "AIRTABLE_API_KEY",
    "AIRTABLE_BASE_ID",
    "AIRTABLE_PROJECTS_TABLE",
    "AIRTABLE_SCENES_TABLE",
    "AIRTABLE_FINAL_TABLE",
    "KIE_API_KEY",
    "KIE_BASE_URL",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
    "SUNO_API_KEY",
    "SUNO_BASE_URL",
    "STORAGE_OUTPUT_DIR",
    "TEMP_ASSETS_DIR",
    "N8N_WEBHOOK_BASE_URL",
]


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    missing = [key for key in REQUIRED_VARS if not os.getenv(key)]
    if missing:
        print("Missing required environment variables:")
        for key in missing:
            print(f"- {key}")
        raise SystemExit(1)

    print("Environment looks complete for local testing.")
    print(f"Storage output dir: {os.environ['STORAGE_OUTPUT_DIR']}")
    print(f"Temp assets dir: {os.environ['TEMP_ASSETS_DIR']}")


if __name__ == "__main__":
    main()
