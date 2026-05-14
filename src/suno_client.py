"""Suno via Drittanbieter (sunoapi.org schema).

Hinweis: Suno hat keine offizielle Public API. sunoapi.org ist der
populärste Wrapper. Endpoints/Felder können sich ändern — bei Fehler
im README den aktuellen Provider-Doc-Stand prüfen.
"""
from __future__ import annotations
import time
from pathlib import Path
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from . import config_loader

POLL_INTERVAL = 5
POLL_TIMEOUT = 480

def _client() -> httpx.Client:
    base = config_loader.env("SUNO_API_BASE", "https://api.sunoapi.org")
    key = config_loader.env("SUNO_API_KEY")
    if not key:
        raise RuntimeError("SUNO_API_KEY fehlt in .env")
    return httpx.Client(
        base_url=base,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        timeout=60.0,
    )

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
def generate_audio(
    prompt: str,
    lyrics: str | None = None,
    style: str = "children's nursery rhyme, playful, fun, sing along, upbeat",
    title: str = "Kids Song",
    instrumental: bool = False,
    duration_target: int = 180,
) -> str:
    """→ audio_url (mp3).

    Für Kinderlieder: instrumental=False + lyrics übergeben.
    Suno generiert dann kompletten Song mit Vocals.
    """
    # customMode=True: eigene Lyrics + Style + Title steuern das Ergebnis
    payload = {
        "customMode": True,
        "instrumental": instrumental,
        "model": "V4",
        "style": style[:200],   # API-Limit: 200 Zeichen
        "title": title[:80],    # API-Limit: 80 Zeichen
        "prompt": (lyrics or prompt)[:3000],   # API-Limit: 3000 Zeichen (customMode)
        "callBackUrl": "https://api.example.com/callback",  # Required by API, wir nutzen polling
    }
    with _client() as c:
        r = c.post("/api/v1/generate", json=payload)
        r.raise_for_status()
        data = r.json()
        task_id = (data.get("data") or {}).get("taskId") or data.get("taskId")
        if not task_id:
            raise RuntimeError(f"Suno: keine taskId im Response: {data}")
        return _poll(task_id)

def _poll(task_id: str) -> str:
    deadline = time.time() + POLL_TIMEOUT
    FAILED = {"CREATE_TASK_FAILED", "GENERATE_AUDIO_FAILED", "CALLBACK_EXCEPTION", "SENSITIVE_WORD_ERROR"}
    with _client() as c:
        while time.time() < deadline:
            r = c.get("/api/v1/generate/record-info", params={"taskId": task_id})
            r.raise_for_status()
            d = r.json()
            inner = (d.get("data") or {})
            status = inner.get("status") or d.get("status", "")
            if status == "SUCCESS":
                suno_data = inner.get("response", {}).get("sunoData") or []
                if suno_data and suno_data[0].get("audioUrl"):
                    return suno_data[0]["audioUrl"]
            if status in FAILED:
                raise RuntimeError(f"Suno generation failed ({status}): {d}")
            time.sleep(POLL_INTERVAL)
    raise TimeoutError("Suno timeout after 8 minutes")

def get_credits() -> float:
    """Gibt verbleibende Credits zurück."""
    with _client() as c:
        r = c.get("/api/v1/generate/credit")
        r.raise_for_status()
        return float((r.json().get("data") or 0))


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=120.0, follow_redirects=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=1 << 16):
                f.write(chunk)
    return dest
