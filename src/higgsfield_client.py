"""Higgsfield CLI-Wrapper: Bilder (Nano Banana Pro — FREE UNLIMITED) + Videos (VEO 3).

Bilder:  nano_banana_2 → kostenlos, unbegrenzt (Standard Queue)
Videos:  veo3          → kostenpflichtig (Credits), beste Qualität

Authentifizierung: Higgsfield CLI (`higgsfield auth login` einmalig im Browser).
Kein API-Key nötig — der CLI-Token wird lokal gespeichert.
"""
from __future__ import annotations
import json
import subprocess
import time
from pathlib import Path
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from . import config_loader

POLL_INTERVAL = 4
POLL_TIMEOUT = 600  # 10 Min
IMAGE_MODEL = "nano_banana_2"  # FREE UNLIMITED — Standard Queue


def _client() -> httpx.Client:
    """REST-Client für Higgsfield API (Videogenerierung)."""
    base = config_loader.env("HIGGSFIELD_API_BASE", "https://api.higgsfield.ai")
    key = config_loader.env("HIGGSFIELD_API_KEY")
    if not key:
        raise RuntimeError("HIGGSFIELD_API_KEY fehlt in .env")
    return httpx.Client(
        base_url=base,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        timeout=60.0,
    )


def _cli(args: list[str]) -> str:
    """Führt einen Higgsfield-CLI-Befehl aus und gibt stdout zurück."""
    result = subprocess.run(
        ["higgsfield"] + args,
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"Higgsfield CLI error: {result.stderr.strip()}")
    return result.stdout.strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
def generate_image(prompt: str, style: str = "", aspect_ratio: str = "16:9") -> str:
    """→ image_url via Nano Banana Pro (FREE UNLIMITED, Standard Queue)."""
    full_prompt = f"{prompt}" + (f" {style}" if style else "")
    job_id = _cli([
        "generate", "create", IMAGE_MODEL,
        "--prompt", full_prompt,
        "--aspect_ratio", aspect_ratio,
    ])
    return _wait_image(job_id)


def _wait_image(job_id: str) -> str:
    """Wartet via `higgsfield generate wait` und gibt image_url zurück."""
    url = _cli(["generate", "wait", job_id])
    if url.startswith("http"):
        return url
    raise RuntimeError(f"Unerwartete Higgsfield-Ausgabe: {url}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
def generate_video(
    image_url: str,
    motion_prompt: str,
    duration_sec: int = 8,
    model: str | None = None,
    aspect_ratio: str = "16:9",
) -> str:
    """Image-to-Video via VEO 3.1 (Standard) oder DOP (Fallback). → video_url"""
    video_model = model or config_loader.env("HIGGSFIELD_VIDEO_MODEL", "veo3")
    payload = {
        "image_url": image_url,
        "prompt": motion_prompt,
        "duration": duration_sec,
        "resolution": config_loader.env("HIGGSFIELD_RESOLUTION", "720p"),
        "aspect_ratio": aspect_ratio,
        "model": video_model,
    }
    with _client() as c:
        r = c.post("/v1/videos", json=payload)
        r.raise_for_status()
        d = r.json()
        if d.get("video_url"):
            return d["video_url"]
        job_id = d.get("generation_id") or d.get("id")
        return _poll_video(job_id)

def _poll_video(job_id: str) -> str:
    deadline = time.time() + POLL_TIMEOUT
    with _client() as c:
        while time.time() < deadline:
            r = c.get(f"/v1/jobs/{job_id}")
            r.raise_for_status()
            d = r.json()
            if d.get("status") == "completed":
                return d["result"]["video_url"]
            if d.get("status") in ("failed", "error"):
                raise RuntimeError(f"Higgsfield video failed: {d}")
            time.sleep(POLL_INTERVAL)
    raise TimeoutError("Higgsfield video generation timeout")

def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=120.0, follow_redirects=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=1 << 16):
                f.write(chunk)
    return dest
