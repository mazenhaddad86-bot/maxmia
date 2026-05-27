"""
Upload fertige Kling-Videos zu YouTube: OldMac, Twinkle, Wheels
"""
import os, sys, pickle, time
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

BASE_DIR    = Path(__file__).parent
CREDENTIALS = BASE_DIR / "client_secrets.json"
TOKEN_FILE  = BASE_DIR / "token.pickle"
PROJECT     = BASE_DIR.parent

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

VIDEOS = [
    {
        "file": PROJECT / "output/oldmacdonald/oldmac_kling_final.mp4",
        "title": "Old MacDonald Had a Farm 🐄 | Max and Mia World | Farm Animals Song for Kids",
        "description": (
            "EE-I-EE-I-O! 🐄🐷🐔🐑\n\n"
            "Join Max and Mia on Old MacDonald's farm! Meet cows, pigs, ducks, "
            "sheep, horses and more in this fun animated nursery rhyme for kids!\n\n"
            "Perfect for toddlers and preschoolers who love animals and singalong songs!\n\n"
            "Subscribe for more Max and Mia adventures every week! 🌟\n\n"
            "#OldMacDonald #FarmAnimals #KidsSongs #NurseryRhymes #MaxAndMia "
            "#ToddlerSongs #AnimatedKidsSongs #PreschoolSongs"
        ),
        "tags": ["Old MacDonald", "farm animals", "kids songs", "nursery rhymes",
                 "Max and Mia", "toddler songs", "animated kids", "animal sounds",
                 "preschool", "cow song", "pig song", "kids animation", "Pixar style"],
    },
    {
        "file": PROJECT / "output/twinkle/twinkle_kling_final.mp4",
        "title": "Shiny Shiny Tiny Gem ✨ | Max and Mia World | Twinkle Twinkle Lullaby",
        "description": (
            "Twinkle twinkle little star... ✨🌙\n\n"
            "Watch Max and Mia drift through a magical starry sky in this beautiful "
            "lullaby. Perfect for bedtime, nap time, and quiet play!\n\n"
            "Soft and soothing for babies, toddlers, and little ones who love stars.\n\n"
            "Subscribe for more Max and Mia World! 🌟\n\n"
            "#TwinkleTwinkle #Lullaby #BedtimeSong #KidsSongs #MaxAndMia "
            "#BabySongs #SleepMusic #ToddlerSongs"
        ),
        "tags": ["Twinkle Twinkle", "lullaby", "bedtime song", "kids songs",
                 "Max and Mia", "star song", "sleep music babies", "nursery rhymes",
                 "animated kids", "toddler songs", "Pixar style", "preschool"],
    },
    {
        "file": PROJECT / "output/wheels/wheels_kling_final.mp4",
        "title": "The Wheels on the Bus 🚌 | Max and Mia World | Bus Song for Kids",
        "description": (
            "The wheels on the bus go round and round! 🚌\n\n"
            "Hop on the bus with Max and Mia for a fun adventure through town! "
            "Wipers, doors, babies, driver — everyone's on board!\n\n"
            "Perfect bouncy song for toddlers and preschoolers!\n\n"
            "Subscribe for more Max and Mia adventures! 🌟\n\n"
            "#WheelsOnTheBus #KidsSongs #BusSong #NurseryRhymes #MaxAndMia "
            "#ToddlerSongs #AnimatedKids #PreschoolSongs"
        ),
        "tags": ["Wheels on the Bus", "bus song", "kids songs", "nursery rhymes",
                 "Max and Mia", "toddler songs", "animated kids", "preschool",
                 "round and round", "kids animation", "Pixar style"],
    },
]


def get_service():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def upload_video(youtube, v):
    path = str(v["file"])
    size_mb = round(v["file"].stat().st_size / 1024 / 1024, 1)
    print(f"\n{'='*60}")
    print(f"Uploading: {v['file'].name} ({size_mb} MB)")
    print(f"Title: {v['title'][:70]}")

    body = {
        "snippet": {
            "title": v["title"],
            "description": v["description"],
            "tags": v["tags"],
            "categoryId": "27",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True,
        },
    }
    media = MediaFileUpload(path, mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    last = -1
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            if pct != last:
                print(f"  {pct}%", end="\r", flush=True)
                last = pct

    vid_id = response["id"]
    print(f"\n✅ Done! https://www.youtube.com/watch?v={vid_id}")
    return vid_id


if __name__ == "__main__":
    youtube = get_service()
    uploaded = []
    for i, v in enumerate(VIDEOS):
        if not v["file"].exists():
            print(f"SKIP (not found): {v['file']}")
            continue
        try:
            vid_id = upload_video(youtube, v)
            uploaded.append({"title": v["title"][:60], "id": vid_id})
            if i < len(VIDEOS) - 1:
                print("Waiting 30s between uploads...")
                time.sleep(30)
        except HttpError as e:
            print(f"ERROR: {e}")
            break

    print(f"\n{'='*60}")
    print(f"Uploaded {len(uploaded)}/{len(VIDEOS)} videos:")
    for u in uploaded:
        print(f"  {u['title']} → https://youtube.com/watch?v={u['id']}")
