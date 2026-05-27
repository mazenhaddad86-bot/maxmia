# -*- coding: utf-8 -*-
import sys, pickle
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
HERE = Path(__file__).parent
creds = pickle.load(open(HERE/"token.pickle","rb"))
yt = build("youtube","v3",credentials=creds)
T = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\thumbnails")
mapping = {
  "N5LwCvfbtbI": T/"twinkle_thumb.png",   # Twinkle (neues Bild)
  "tKbgMtKkaZo": T/"baa_thumb.png",
  "I8P6n8K2tUA": T/"humpty_thumb.png",
  "BE2JEtae0Yg": T/"nature_thumb.png",
}
for vid, thumb in mapping.items():
    if not thumb.exists():
        print("FEHLT:", thumb); continue
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/png")).execute()
        print("OK Thumbnail gesetzt:", vid, "->", thumb.name)
    except Exception as e:
        print("FEHLER", vid, ":", str(e)[:200])
