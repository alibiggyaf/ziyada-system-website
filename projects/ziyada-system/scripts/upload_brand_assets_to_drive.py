#!/usr/bin/env python3
"""
رفع أصول العلامة التجارية لزيادة سيستم إلى Google Drive
Upload Ziyada System Brand Assets to Google Drive

يقوم هذا السكريبت بإنشاء هيكل مجلدات منظم ورفع جميع الأصول البصرية.

الاستخدام:
  python scripts/upload_brand_assets_to_drive.py

المتطلبات:
  pip install google-auth google-auth-oauthlib google-api-python-client
"""

from __future__ import annotations

import json
import mimetypes
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Paths ──
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Auth
TOKEN_PATH = PROJECT_DIR / "token_docs.json"
CREDS_PATH = PROJECT_DIR / "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# ── Drive Folder Structure ──
FOLDER_STRUCTURE = {
    "Ziyada_Brand_Assets": {
        "01_Logos": {
            "_files": [
                ASSETS_DIR / "ziyada_logo_profile_automation.svg",
                ASSETS_DIR / "ziyada_logo_profile_automation_simple.svg",
                ASSETS_DIR / "logo-monochrome-white.svg",
                ASSETS_DIR / "logo-monochrome-dark.svg",
            ]
        },
        "02_Icons": {
            "ui-icons": {
                "_note": "Exported from BrandIcons.jsx — 20 stroke-based SVG icons"
            },
            "corporate-icons": {
                "_dir": ASSETS_DIR / "corporate-design-kit" / "icons"
            }
        },
        "03_Patterns": {
            "brain-element": {
                "_dir": ASSETS_DIR / "brain-element-pattern",
                "_extensions": [".svg", ".png"]
            },
            "minimal-patterns": {
                "_dir": ASSETS_DIR / "corporate-design-kit" / "patterns-minimal"
            }
        },
        "04_Backgrounds": {
            "_dir": ASSETS_DIR / "corporate-design-kit" / "backgrounds"
        },
        "05_Frames": {
            "_dir": ASSETS_DIR / "corporate-design-kit" / "frames"
        },
        "06_Cards": {
            "_dir": ASSETS_DIR / "corporate-design-kit" / "cards"
        },
        "07_Templates": {
            "_dir": ASSETS_DIR / "templates"
        },
        "08_Brand_Guideline": {
            "_files": [
                PROJECT_DIR / "BRAND_IDENTITY_GUIDELINE_V2.md",
            ]
        },
    }
}


def get_credentials():
    """Get or refresh Google OAuth credentials."""
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("  Refreshing expired token...")
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
            print("  Token refreshed successfully.")
        elif creds and creds.refresh_token:
            print("  Refreshing token...")
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        else:
            if not CREDS_PATH.exists():
                print(f"ERROR: {CREDS_PATH} not found. Download from Google Cloud Console.")
                exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=8080)
            TOKEN_PATH.write_text(creds.to_json())
    return creds


def create_folder(service, name: str, parent_id: str = None) -> str:
    """Create a folder in Google Drive and return its ID."""
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    # Check if folder exists
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    existing = results.get("files", [])
    if existing:
        print(f"  📁 Folder exists: {name}")
        return existing[0]["id"]

    folder = service.files().create(body=metadata, fields="id").execute()
    print(f"  📁 Created folder: {name}")
    return folder["id"]


def upload_file(service, file_path: Path, parent_id: str) -> dict:
    """Upload a file to Google Drive and return its metadata."""
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    metadata = {
        "name": file_path.name,
        "parents": [parent_id],
    }

    # Check if file exists
    query = f"name='{file_path.name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    existing = results.get("files", [])

    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)

    if existing:
        # Update existing file
        file = service.files().update(
            fileId=existing[0]["id"],
            media_body=media,
            fields="id, name, webViewLink"
        ).execute()
        print(f"    ↻ Updated: {file_path.name}")
    else:
        file = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, name, webViewLink"
        ).execute()
        print(f"    ✓ Uploaded: {file_path.name}")

    return file


def upload_directory(service, dir_path: Path, parent_id: str, extensions: list = None) -> list:
    """Upload all files in a directory to a Drive folder."""
    results = []
    if not dir_path.exists():
        print(f"    ⚠ Directory not found: {dir_path}")
        return results

    for f in sorted(dir_path.iterdir()):
        if f.is_file() and not f.name.startswith("."):
            if extensions and f.suffix.lower() not in extensions:
                continue
            if f.suffix.lower() in [".md", ".txt", ".svg", ".png", ".jpg", ".jpeg", ".pdf", ".html", ".css"]:
                result = upload_file(service, f, parent_id)
                results.append({"local": str(f), "drive_id": result["id"], "link": result.get("webViewLink", "")})
    return results


def process_structure(service, structure: dict, parent_id: str = None) -> list:
    """Recursively create folders and upload files based on the structure definition."""
    manifest = []

    for name, config in structure.items():
        if name.startswith("_"):
            continue

        folder_id = create_folder(service, name, parent_id)

        if isinstance(config, dict):
            # Upload specific files
            if "_files" in config:
                for file_path in config["_files"]:
                    if file_path.exists():
                        result = upload_file(service, file_path, folder_id)
                        manifest.append({
                            "local": str(file_path),
                            "folder": name,
                            "drive_id": result["id"],
                            "link": result.get("webViewLink", "")
                        })
                    else:
                        print(f"    ⚠ File not found: {file_path}")

            # Upload entire directory
            if "_dir" in config:
                extensions = config.get("_extensions")
                results = upload_directory(service, config["_dir"], folder_id, extensions)
                manifest.extend(results)

            # Recurse into subfolders
            sub_items = {k: v for k, v in config.items() if not k.startswith("_")}
            if sub_items:
                sub_manifest = process_structure(service, sub_items, folder_id)
                manifest.extend(sub_manifest)

    return manifest


def make_folder_shareable(service, folder_id: str) -> str:
    """Make the root folder shareable via link and return the URL."""
    permission = {
        "type": "anyone",
        "role": "reader",
    }
    service.permissions().create(fileId=folder_id, body=permission).execute()
    file = service.files().get(fileId=folder_id, fields="webViewLink").execute()
    return file["webViewLink"]


def main():
    print("=" * 60)
    print("  Ziyada System — Brand Asset Upload to Google Drive")
    print("  رفع أصول العلامة التجارية إلى جوجل درايف")
    print("=" * 60)
    print()

    # Authenticate
    print("🔐 Authenticating with Google...")
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
    print("✓ Authenticated successfully\n")

    # Create structure and upload
    print("📤 Creating folder structure and uploading assets...\n")
    manifest = process_structure(service, FOLDER_STRUCTURE)

    # Make root folder shareable
    root_name = list(FOLDER_STRUCTURE.keys())[0]
    query = f"name='{root_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    root_folders = results.get("files", [])

    share_link = ""
    if root_folders:
        share_link = make_folder_shareable(service, root_folders[0]["id"])
        print(f"\n🔗 Shareable link: {share_link}")

    # Save manifest
    manifest_path = OUTPUT_DIR / "brand_assets_manifest.json"
    manifest_data = {
        "root_folder": root_name,
        "share_link": share_link,
        "total_files": len(manifest),
        "assets": manifest,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False))
    print(f"\n📋 Manifest saved: {manifest_path}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  ✅ Upload complete!")
    print(f"  📁 Total files uploaded: {len(manifest)}")
    print(f"  🔗 Share this link with your team:")
    print(f"     {share_link}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
