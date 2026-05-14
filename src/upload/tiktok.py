"""TikTok Direct Post via Content Posting API.

Voraussetzung: App im TikTok Developer Portal mit 'video.publish' Scope.
Vor App-Audit sind Posts nur PRIVAT (SELF_ONLY) sichtbar.

Flow:
1. POST /v2/post/publish/video/init/        → upload_url + publish_id
2. PUT  upload_url   (chunked file upload)
3. GET  /v2/post/publish/status/fetch/?publish_id  (poll)
"""
from __future__ import annotations
import os
import time
from pathlib import Path
import httpx
from .. import config_loader

API_BASE = "https://open.tiktokapis.com"

def _headers() -> dict:
    token = config_loader.env("TIKTOK_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("TIKTOK_ACCESS_TOKEN fehlt. Siehe README → TikTok-Setup.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def upload(video_path: Path, title: str, description: str, tags: list[str]) -> str:
    privacy = config_loader.env("TIKTOK_PRIVACY", "PUBLIC_TO_EVERYONE")
    file_size = video_path.stat().st_size
    chunk_size = min(file_size, 64 * 1024 * 1024)
    total_chunks = max(1, (file_size + chunk_size - 1) // chunk_size)

    # Caption mit Hashtags
    caption = description
    if tags:
        caption = f"{caption}\n\n" + " ".join(t if t.startswith("#") else f"#{t}" for t in tags)
    caption = caption[:2200]

    init_body = {
        "post_info": {
            "title": caption,
            "privacy_level": privacy,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunks,
        },
    }
    with httpx.Client(timeout=120.0) as c:
        r = c.post(f"{API_BASE}/v2/post/publish/video/init/", headers=_headers(), json=init_body)
        r.raise_for_status()
        data = r.json()["data"]
        upload_url = data["upload_url"]
        publish_id = data["publish_id"]

        # Chunked upload
        with open(video_path, "rb") as f:
            for i in range(total_chunks):
                start = i * chunk_size
                end = min(start + chunk_size, file_size) - 1
                chunk = f.read(end - start + 1)
                put = c.put(
                    upload_url,
                    headers={
                        "Content-Range": f"bytes {start}-{end}/{file_size}",
                        "Content-Type": "video/mp4",
                        "Content-Length": str(len(chunk)),
                    },
                    content=chunk,
                )
                put.raise_for_status()

        # Poll status
        deadline = time.time() + 300
        while time.time() < deadline:
            sr = c.post(
                f"{API_BASE}/v2/post/publish/status/fetch/",
                headers=_headers(),
                json={"publish_id": publish_id},
            )
            sr.raise_for_status()
            sd = sr.json()["data"]
            status = sd.get("status")
            if status == "PUBLISH_COMPLETE":
                return f"tiktok://publish_id/{publish_id}"
            if status in ("FAILED", "PUBLISH_FAILED"):
                raise RuntimeError(f"TikTok publish failed: {sd}")
            time.sleep(5)
    raise TimeoutError("TikTok publish status timeout")
