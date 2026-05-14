"""Facebook Reels auf Page via Graph API.

3-Step (chunked upload):
  1. POST /{page_id}/video_reels?upload_phase=start  → video_id, upload_url
  2. POST upload_url   (Datei senden)
  3. POST /{page_id}/video_reels?upload_phase=finish → publish
"""
from __future__ import annotations
from pathlib import Path
import httpx
from .. import config_loader

GRAPH = "https://graph.facebook.com/v21.0"
RUPLOAD = "https://rupload.facebook.com/video-upload/v21.0"

def upload(video_path: Path, description: str) -> str:
    page_id = config_loader.env("FACEBOOK_PAGE_ID")
    token = config_loader.env("FACEBOOK_PAGE_ACCESS_TOKEN")
    if not (page_id and token):
        raise RuntimeError("FACEBOOK_PAGE_ID oder FACEBOOK_PAGE_ACCESS_TOKEN fehlt.")

    file_size = video_path.stat().st_size

    with httpx.Client(timeout=300.0) as c:
        # 1. Start
        s = c.post(
            f"{GRAPH}/{page_id}/video_reels",
            params={"upload_phase": "start", "access_token": token},
        )
        s.raise_for_status()
        sd = s.json()
        video_id = sd["video_id"]

        # 2. Upload via rupload
        with open(video_path, "rb") as f:
            data = f.read()
        u = c.post(
            f"{RUPLOAD}/{video_id}",
            headers={
                "Authorization": f"OAuth {token}",
                "offset": "0",
                "file_size": str(file_size),
            },
            content=data,
        )
        u.raise_for_status()

        # 3. Finish/publish
        p = c.post(
            f"{GRAPH}/{page_id}/video_reels",
            params={
                "upload_phase": "finish",
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description[:2200],
                "access_token": token,
            },
        )
        p.raise_for_status()
        return f"https://www.facebook.com/reel/{video_id}"
