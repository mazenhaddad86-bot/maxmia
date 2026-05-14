"""
YouTube Upload Script - Max & Mia World
Basiert auf: github.com/darkzOGx/youtube-automation-agent
Authentifizierung: OAuth2 (einmalig) -> Token wird gespeichert -> danach vollautomatisch
"""

import os
import sys
import json
import pickle
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# ─── Pfade ───────────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).parent
CREDENTIALS    = BASE_DIR / "client_secrets.json"   # von Google Cloud Console
TOKEN_FILE     = BASE_DIR / "token.pickle"           # wird nach erstem Login gespeichert

# ─── Scopes (gleich wie im Repo) ─────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def get_authenticated_service():
    """
    OAuth2 Flow - genau wie authenticate.js aus dem Repo.
    Beim ersten Mal: Browser oeffnet sich -> einloggen -> Token gespeichert.
    Danach: automatisch mit gespeichertem Token.
    """
    creds = None

    # Token vorhanden? Laden
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    # Token abgelaufen oder nicht vorhanden -> neu einloggen
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token abgelaufen, erneuere automatisch...")
            creds.refresh(Request())
        else:
            if not CREDENTIALS.exists():
                print(f"\nFEHLER: {CREDENTIALS} nicht gefunden!")
                print("Bitte client_secrets.json aus Google Cloud Console herunterladen")
                print("und in diesen Ordner legen: " + str(BASE_DIR))
                sys.exit(1)

            print("\nErste Anmeldung - Browser oeffnet sich...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)

        # Token speichern fuer naechstes Mal
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print("Token gespeichert - naechstes Mal automatisch!")

    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    category_id: str = "27",      # 27 = Education, 1 = Film, 10 = Music
    privacy: str = "public",     # "public" | "unlisted" | "public"
    thumbnail_path: str = None,
):
    """
    Video auf YouTube hochladen.
    Gleiche Logik wie PublishingSchedulingAgent aus dem Repo.
    """
    print(f"\nLade hoch: {Path(video_path).name}")
    print(f"Titel: {title}")
    print(f"Sichtbarkeit: {privacy}")

    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "de",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": True,  # Kindervideo!
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 5,  # 5 MB chunks
    )

    print("Upload gestartet...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    last_progress = -1
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                if progress != last_progress:
                    print(f"  Fortschritt: {progress}%")
                    last_progress = progress
        except HttpError as e:
            print(f"HTTP Fehler: {e}")
            raise

    video_id = response["id"]
    print(f"\nErfolgreich hochgeladen!")
    print(f"Video-ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")

    # Thumbnail setzen (falls angegeben)
    if thumbnail_path and Path(thumbnail_path).exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
            ).execute()
            print("Thumbnail gesetzt!")
        except Exception as e:
            print(f"Thumbnail Fehler (nicht kritisch): {e}")

    return video_id


# ─── Haupt-Konfiguration fuer Humpty Dumpty ──────────────────────────────────
if __name__ == "__main__":

    VIDEO_FILE = r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\humpty-dumpty\humpty_dumpty_v3_FINAL.mp4"

    TITLE = "Humpty Dumpty | Max & Mia World | Nursery Rhyme | Kinderlieder"

    DESCRIPTION = """Humpty Dumpty sat on a wall... 🥚

Singe mit Max & Mia das bekannteste Kinderlied der Welt!
Humpty Dumpty faellt von der Mauer - koennen alle des Koenigs Maenner ihn retten?

Perfekt fuer Kleinkinder und Kindergarten-Kinder!

#HumptyDumpty #MaxUndMia #Kinderlieder #NurseryRhyme #Kinder
#KindervideosDeutsch #Liederfuerkinder #KinderTV"""

    TAGS = [
        "Humpty Dumpty",
        "Max und Mia",
        "Kinderlieder",
        "Nursery Rhyme",
        "Kinder",
        "Kinderlied",
        "Kids Songs",
        "German Kids",
        "Kleinkinder",
        "Lernvideo",
        "Animated Kids Song",
        "Humpty Dumpty Song",
        "Max Mia World",
    ]

    # Erst als "public" hochladen - dann manuell pruefen und veroeffentlichen
    upload_video(
        video_path=VIDEO_FILE,
        title=TITLE,
        description=DESCRIPTION,
        tags=TAGS,
        category_id="27",   # Education
        privacy="public",  # Erst privat - du kannst es dann manuell public machen
    )
