"""
upload_to_social.py — Lädt das fertige Video auf Instagram (Reels) + Facebook hoch.

Pipeline:
  1. Video auf Cloudinary hochladen → öffentliche URL
  2. Instagram Reels via Graph API posten
  3. Facebook Reels via Graph API posten (optional)

Usage:
    python scripts/upload_to_social.py
    python scripts/upload_to_social.py --video output/nature-discovery/final_9x16.mp4
    python scripts/upload_to_social.py --dry-run   (nur Cloudinary-Upload, kein Posting)
"""
from __future__ import annotations
import argparse
import os
import sys
import time
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
VIDEO_9X16  = Path("output/nature-discovery/final_9x16.mp4")
VIDEO_16X9  = Path("output/nature-discovery/final_16x9.mp4")
GRAPH_BASE  = "https://graph.facebook.com/v21.0"

CAPTION = """🌿 Max & Mia entdecken die Natur! 🦋🍄🐛

Komm mit Max und Mia auf ein Abenteuer durch den Wald!
Schmetterlinge, bunte Pilze und süße Tiere warten auf euch! 🐞🐸

🎵 Singt mit und entdeckt die Natur!

#MaxAndMia #KidsMusic #NurseryRhymes #KinderLieder #NatureForKids #Kinder #ChildrensSongs #KidsYouTube #NaturAbenteuer #MaxUndMia"""


# ── Cloudinary ────────────────────────────────────────────────────────────────
def upload_to_cloudinary(video_path: Path) -> str:
    """Lädt Video auf Cloudinary hoch und gibt öffentliche URL zurück."""
    try:
        import cloudinary
        import cloudinary.uploader
    except ImportError:
        print("  Installiere cloudinary...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cloudinary", "-q"])
        import cloudinary
        import cloudinary.uploader

    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True,
    )

    print(f"  Lade hoch: {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.1f} MB)...")
    result = cloudinary.uploader.upload_large(
        str(video_path),
        resource_type="video",
        folder="maxmia",
        public_id=f"nature-discovery-{int(time.time())}",
        overwrite=True,
    )
    url = result["secure_url"]
    print(f"  ✅ Cloudinary URL: {url}")
    return url


# ── Instagram ─────────────────────────────────────────────────────────────────
def post_instagram_reel(public_video_url: str, caption: str) -> str:
    """Postet ein Reel auf Instagram via Graph API. Gibt Post-URL zurück."""
    try:
        import httpx
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "-q"])
        import httpx

    ig_id = os.environ.get("INSTAGRAM_USER_ID", "")
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    if not (ig_id and token):
        raise RuntimeError("INSTAGRAM_USER_ID oder INSTAGRAM_ACCESS_TOKEN fehlt in .env")

    with httpx.Client(timeout=60.0) as c:
        print("  Erstelle Instagram-Container...")
        r = c.post(
            f"{GRAPH_BASE}/{ig_id}/media",
            params={
                "media_type": "REELS",
                "video_url": public_video_url,
                "caption": caption[:2200],
                "access_token": token,
            },
        )
        if r.status_code != 200:
            raise RuntimeError(f"Container-Fehler: {r.status_code} — {r.text}")
        creation_id = r.json()["id"]
        print(f"  Container ID: {creation_id}")

        # Auf FINISHED warten
        print("  Warte auf Video-Verarbeitung (bis 5 Min)...")
        deadline = time.time() + 300
        while time.time() < deadline:
            s = c.get(
                f"{GRAPH_BASE}/{creation_id}",
                params={"fields": "status_code,status", "access_token": token},
            )
            s.raise_for_status()
            sd = s.json()
            status = sd.get("status_code", "?")
            print(f"    Status: {status}", end="\r")
            if status == "FINISHED":
                print(f"    Status: FINISHED ✅")
                break
            if status in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"IG Container Error: {sd}")
            time.sleep(8)
        else:
            raise TimeoutError("Instagram Container Processing Timeout (5 Min)")

        # Publish
        print("  Veröffentliche Reel...")
        p = c.post(
            f"{GRAPH_BASE}/{ig_id}/media_publish",
            params={"creation_id": creation_id, "access_token": token},
        )
        p.raise_for_status()
        media_id = p.json()["id"]
        url = f"https://www.instagram.com/reel/{media_id}"
        print(f"  ✅ Instagram Reel live: {url}")
        return url


# ── Facebook ──────────────────────────────────────────────────────────────────
def post_facebook_reel(video_path: Path, description: str) -> str:
    """Postet ein Reel auf einer Facebook-Page. Gibt Post-URL zurück."""
    try:
        import httpx
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "-q"])
        import httpx

    page_id = os.environ.get("FACEBOOK_PAGE_ID", "")
    token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    if not (page_id and token):
        raise RuntimeError("FACEBOOK_PAGE_ID oder FACEBOOK_PAGE_ACCESS_TOKEN fehlt in .env")

    file_size = video_path.stat().st_size
    rupload = "https://rupload.facebook.com/video-upload/v21.0"

    with httpx.Client(timeout=300.0) as c:
        # 1. Start
        print("  Starte Facebook Upload...")
        s = c.post(
            f"{GRAPH_BASE}/{page_id}/video_reels",
            params={"upload_phase": "start", "access_token": token},
        )
        s.raise_for_status()
        video_id = s.json()["video_id"]

        # 2. Upload
        print(f"  Lade Video hoch ({file_size / 1024 / 1024:.1f} MB)...")
        with open(video_path, "rb") as f:
            data = f.read()
        u = c.post(
            f"{rupload}/{video_id}",
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
            f"{GRAPH_BASE}/{page_id}/video_reels",
            params={
                "upload_phase": "finish",
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description[:2200],
                "access_token": token,
            },
        )
        p.raise_for_status()
        url = f"https://www.facebook.com/reel/{video_id}"
        print(f"  ✅ Facebook Reel live: {url}")
        return url


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Upload Max & Mia Video zu Social Media")
    parser.add_argument("--video", type=Path, default=VIDEO_9X16, help="Pfad zum 9:16 Video")
    parser.add_argument("--dry-run", action="store_true", help="Nur Cloudinary-Upload, kein Social-Posting")
    parser.add_argument("--ig-only", action="store_true", help="Nur Instagram (kein Facebook)")
    args = parser.parse_args()

    video = args.video
    if not video.exists():
        sys.exit(f"Video nicht gefunden: {video}")

    print(f"\n{'='*55}")
    print("  Max & Mia — Social Media Upload")
    print(f"  Video: {video} ({video.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"{'='*55}\n")

    # Step 1: Cloudinary
    print("📤 Schritt 1: Cloudinary Upload...")
    public_url = upload_to_cloudinary(video)

    if args.dry_run:
        print(f"\n✅ Dry-Run fertig. URL: {public_url}")
        return

    # Step 2: Instagram
    if os.environ.get("INSTAGRAM_ENABLED", "false").lower() == "true":
        print("\n📱 Schritt 2: Instagram Reel...")
        try:
            ig_url = post_instagram_reel(public_url, CAPTION)
        except Exception as e:
            print(f"  ❌ Instagram Fehler: {e}")
            ig_url = None
    else:
        print("\n  ⚠️  Instagram deaktiviert (INSTAGRAM_ENABLED=false)")
        ig_url = None

    # Step 3: Facebook
    if not args.ig_only and os.environ.get("FACEBOOK_ENABLED", "false").lower() == "true":
        print("\n📘 Schritt 3: Facebook Reel...")
        try:
            fb_url = post_facebook_reel(video, CAPTION)
        except Exception as e:
            print(f"  ❌ Facebook Fehler: {e}")
            fb_url = None
    else:
        if not args.ig_only:
            print("\n  ⚠️  Facebook deaktiviert (FACEBOOK_ENABLED=false)")
        fb_url = None

    print(f"\n{'='*55}")
    print("  FERTIG!")
    if ig_url:
        print(f"  Instagram: {ig_url}")
    if fb_url:
        print(f"  Facebook:  {fb_url}")
    print(f"  Cloudinary: {public_url}")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()
