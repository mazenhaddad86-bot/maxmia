"""YouTube Upload - Baa Baa Black Sheep"""
import os, sys, pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

BASE_DIR    = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\youtube")
CREDENTIALS = BASE_DIR / "client_secrets.json"
TOKEN_FILE  = BASE_DIR / "token.pickle"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

def get_service():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Erneuere Token...")
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)

VIDEO     = r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\baa-baa-black-sheep\baa_baa_final_v3.mp4"
THUMBNAIL = r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\baa-baa-black-sheep\thumbnail_final.jpg"

TITLE = "Baa Baa Black Sheep \U0001f411 | Nursery Rhyme for Kids | Max & Mia"

DESCRIPTION = """Baa Baa Black Sheep - the classic nursery rhyme with Max & Mia! \U0001f411

Join Max and Mia as they meet a fluffy black sheep on an English farm and help deliver three big bags of wool to the farmer, grandma, and a little boy!

\U0001f411 Perfect for toddlers and preschoolers!
\U0001f3b5 Original music by Suno AI v5.5

► Subscribe for more Max & Mia nursery rhymes!

#BaaBaaBlackSheep #NurseryRhyme #KidsSongs #MaxAndMia #ToddlerSongs #KidsCartoon #ChildrensSong #PreschoolSongs"""

TAGS = [
    "baa baa black sheep", "nursery rhyme", "kids songs", "children song",
    "toddler songs", "max and mia", "animated nursery rhyme", "preschool",
    "black sheep song", "farm song for kids", "kids cartoon", "baby songs",
    "3D kids animation", "nursery rhymes for babies"
]

yt = get_service()
body = {
    "snippet": {
        "title": TITLE,
        "description": DESCRIPTION,
        "tags": TAGS,
        "categoryId": "27",
        "defaultLanguage": "en",
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": True,
    },
}
media = MediaFileUpload(VIDEO, mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)
req = yt.videos().insert(part="snippet,status", body=body, media_body=media)

response = None
last = -1
while response is None:
    status, response = req.next_chunk()
    if status:
        p = int(status.progress() * 100)
        if p != last:
            print(f"  {p}%")
            last = p

video_id = response["id"]
print(f"\nHochgeladen! ID: {video_id}")
print(f"URL: https://www.youtube.com/watch?v={video_id}")

# Thumbnail setzen
try:
    yt.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(THUMBNAIL, mimetype="image/jpeg")
    ).execute()
    print("Thumbnail gesetzt!")
except Exception as e:
    print(f"Thumbnail Fehler: {e}")
