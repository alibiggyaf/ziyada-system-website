import os, sys
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
sys.path.insert(0, ".")
from google_auth_oauthlib.flow import Flow
flow = Flow.from_client_secrets_file(
    "projects/ziyada-system/client_secret_724758724688-3l2nvclnr94u15l1fm0i79c1id5ncm6k.apps.googleusercontent.com.json",
    scopes=["https://www.googleapis.com/auth/documents","https://www.googleapis.com/auth/drive.file"],
    redirect_uri="http://localhost:8080/"
)
url, _ = flow.authorization_url(prompt="consent", access_type="offline")
with open("auth_url.txt", "w") as f:
    f.write(url + "\n")
print("SAVED:", url[:80] + "...")
