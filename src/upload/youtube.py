"""YouTube Shorts Upload via Data API v3 (resumable upload)."""
from __future__ import annotations
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from .. import config_loader

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def _service():
    token_file = config_loader.ROOT / config_loader.env("YOUTUBE_TOKEN_FILE", "scripts/youtube_token.json")
    if not token_file.exists():
        raise RuntimeError(
            f"YouTube-Token fehlt ({token_file}). "
            "Einmalig laufen: python scripts/setup_youtube_oauth.py"
        )
    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)

def upload(video_path: Path, title: str, description: str, tags: list[str]) -> str:
    yt = _service()
    privacy = config_loader.env("YOUTUBE_PRIVACY", "public")
    category = config_loader.env("YOUTUBE_CATEGORY_ID", "22")
    made_for_kids = config_loader.env_bool("YOUTUBE_MADE_FOR_KIDS", False)

    # YouTube erkennt Shorts automatisch an: vertikales Format + #Shorts in Titel/Desc + ≤60s
    title_with_tag = title if "#shorts" in title.lower() else f"{title} #Shorts"

    body = {
        "snippet": {
            "title": title_with_tag[:95],
            "description": description[:4900],
            "tags": tags[:30],
            "categoryId": category,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
    return f"https://youtube.com/shorts/{resp['id']}"
