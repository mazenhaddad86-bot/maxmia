# -*- coding: utf-8 -*-
"""Upload via maxmiayt2 Cloud-Projekt (eigene Quota)"""
import os, sys, json, pickle, time
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

BASE = Path(__file__).parent
CREDENTIALS = BASE / "client_secrets_v2.json"
TOKEN_FILE  = BASE / "token_v2.pickle"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube"]

def auth():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE,"rb") as f: creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try: creds.refresh(Request())
            except Exception: creds=None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open(TOKEN_FILE,"wb") as f: pickle.dump(creds,f)
    return build("youtube","v3",credentials=creds)

def upload_video(video_path, title, desc, tags, category_id="1", privacy="public", thumbnail_path=None):
    print(f"\n[v2] Lade hoch: {Path(video_path).name}")
    print(f"   Titel: {title}")
    yt = auth()
    body = {"snippet":{"title":title,"description":desc,"tags":tags,"categoryId":category_id,"defaultLanguage":"en"},
            "status":{"privacyStatus":privacy,"selfDeclaredMadeForKids":True}}
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp=None; last=-1
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            p = int(status.progress()*100)
            if p != last: print(f"   {p}%"); last=p
    vid = resp["id"]
    print(f"✅ https://youtube.com/watch?v={vid}")
    if thumbnail_path and Path(thumbnail_path).exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumbnail_path, mimetype="image/png")).execute()
            print("   Thumbnail gesetzt")
        except Exception as e: print(f"   Thumb-Fehler: {e}")
    return vid

if __name__ == "__main__":
    # Test: zeig den Kanal an
    yt = auth()
    r = yt.channels().list(part="snippet", mine=True).execute()
    for ch in r.get("items",[]):
        print("Verbunden mit Kanal:", ch["snippet"]["title"])
