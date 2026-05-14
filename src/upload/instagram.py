"""Instagram Reels Upload via Graph API v21.0.

Voraussetzung: IG-Business-Account verknüpft mit FB-Page.
2-Step:
  1. POST /{ig_user_id}/media (media_type=REELS, video_url=public URL)
  2. POST /{ig_user_id}/media_publish (creation_id)

Wichtig: video_url muss ÖFFENTLICH erreichbar sein. In dieser Pipeline
laden wir den fertigen Clip vorher zu einem Public-URL-Host (z.B. eigene
S3/Cloudflare R2). Für lokale Entwicklung: ngrok oder eigener Server.
"""
from __future__ import annotations
import time
from pathlib import Path
import httpx
from .. import config_loader

GRAPH = "https://graph.facebook.com/v21.0"

def upload(video_path: Path, public_video_url: str, caption: str) -> str:
    ig_id = config_loader.env("INSTAGRAM_USER_ID")
    token = config_loader.env("INSTAGRAM_ACCESS_TOKEN")
    if not (ig_id and token):
        raise RuntimeError("INSTAGRAM_USER_ID oder INSTAGRAM_ACCESS_TOKEN fehlt.")

    with httpx.Client(timeout=60.0) as c:
        # 1. Container erzeugen
        r = c.post(
            f"{GRAPH}/{ig_id}/media",
            params={
                "media_type": "REELS",
                "video_url": public_video_url,
                "caption": caption[:2200],
                "access_token": token,
            },
        )
        r.raise_for_status()
        creation_id = r.json()["id"]

        # 2. Auf 'FINISHED' warten
        deadline = time.time() + 300
        while time.time() < deadline:
            s = c.get(
                f"{GRAPH}/{creation_id}",
                params={"fields": "status_code,status", "access_token": token},
            )
            s.raise_for_status()
            sd = s.json()
            if sd.get("status_code") == "FINISHED":
                break
            if sd.get("status_code") == "ERROR":
                raise RuntimeError(f"IG container error: {sd}")
            time.sleep(5)

        # 3. Publish
        p = c.post(
            f"{GRAPH}/{ig_id}/media_publish",
            params={"creation_id": creation_id, "access_token": token},
        )
        p.raise_for_status()
        media_id = p.json()["id"]
        return f"https://www.instagram.com/reel/{media_id}"
