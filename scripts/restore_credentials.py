"""Stellt YouTube Credentials aus GitHub Secrets wieder her."""
import base64, json, os, pickle
from google.oauth2.credentials import Credentials
from pathlib import Path

Path("youtube").mkdir(exist_ok=True)

# YouTube Token
raw = os.environ["YOUTUBE_TOKEN_JSON"]
try:
    data = json.loads(base64.b64decode(raw + "=="))
except Exception:
    data = json.loads(raw)

creds = Credentials(
    token=data["token"],
    refresh_token=data["refresh_token"],
    token_uri=data["token_uri"],
    client_id=data["client_id"],
    client_secret=data["client_secret"],
    scopes=data["scopes"],
)
with open("youtube/token.pickle", "wb") as f:
    pickle.dump(creds, f)

# Client Secrets
raw_cs = os.environ["YOUTUBE_CLIENT_SECRETS"]
try:
    cs = json.loads(base64.b64decode(raw_cs + "=="))
except Exception:
    cs = json.loads(raw_cs)
with open("youtube/client_secrets.json", "w") as f:
    json.dump(cs, f)

print("YouTube credentials restored successfully")
