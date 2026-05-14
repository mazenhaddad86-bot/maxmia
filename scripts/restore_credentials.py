"""Stellt YouTube Credentials aus GitHub Secrets wieder her."""
import base64, json, os, pickle
from google.oauth2.credentials import Credentials
from pathlib import Path

Path("youtube").mkdir(exist_ok=True)

def decode_secret(raw: str) -> dict:
    """Dekodiert Secret — entfernt BOM und versucht base64 oder plain JSON."""
    # BOM und Whitespace entfernen
    raw = raw.strip().lstrip('﻿').lstrip('\xef\xbb\xbf').strip()
    # Nur ASCII behalten
    raw = raw.encode('ascii', errors='ignore').decode('ascii').strip()
    try:
        return json.loads(base64.b64decode(raw + "=="))
    except Exception:
        return json.loads(raw)

# YouTube Token
raw = os.environ["YOUTUBE_TOKEN_JSON"]
data = decode_secret(raw)

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
cs = decode_secret(raw_cs)
with open("youtube/client_secrets.json", "w") as f:
    json.dump(cs, f)

print("YouTube credentials restored successfully")
