#!/usr/bin/env python3
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DOC_ID = "1wshq883UJYvSqqjqv1JE_nv9uFucAzrgHGhMiIAbjVM"
OLD_TEXT = "# الملحق العربي لدليل هيكلة مساحة العمل (Arabic Addendum)"
NEW_TEXT = "=== الملحق العربي (Arabic Section) ===\n\n# الملحق العربي لدليل هيكلة مساحة العمل (Arabic Addendum)"

project_root = Path(__file__).resolve().parent.parent
token_path = project_root / "token_docs.json"

creds = Credentials.from_authorized_user_file(
    str(token_path),
    [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive.file",
    ],
)

docs = build("docs", "v1", credentials=creds)
result = docs.documents().batchUpdate(
    documentId=DOC_ID,
    body={
        "requests": [
            {
                "replaceAllText": {
                    "containsText": {"text": OLD_TEXT, "matchCase": True},
                    "replaceText": NEW_TEXT,
                }
            }
        ]
    },
).execute()

changed = result.get("replies", [{}])[0].get("replaceAllText", {}).get("occurrencesChanged", 0)
print(f"occurrences_changed={changed}")
print(f"url=https://docs.google.com/document/d/{DOC_ID}/edit")
