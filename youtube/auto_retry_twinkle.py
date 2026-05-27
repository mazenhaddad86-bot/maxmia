# -*- coding: utf-8 -*-
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from upload import upload_video

V = r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\twinkle\twinkle_final_fixed.mp4"
THUMB = r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\thumbnails\twinkle_thumb.png"
TITLE = "Twinkle Twinkle Little Star ⭐ | Nursery Rhymes & Kids Songs | Max & Mia World"
DESC = "Twinkle Twinkle Little Star, how I wonder what you are! ⭐ Sing along with Max & Mia in this fun 3D animated nursery rhyme!\n\n#TwinkleTwinkle #NurseryRhymes #KidsSongs #MaxAndMia #ForKids"
TAGS = ["twinkle twinkle little star","star song","lullaby","nursery rhymes","kids songs",
        "children songs","baby songs","toddler songs","songs for kids","kids videos",
        "max and mia","preschool songs","sing along","kids learning","bedtime songs"]

attempt = 0
while True:
    attempt += 1
    print(f"\n[{time.strftime('%H:%M:%S')}] Versuch {attempt}...")
    try:
        vid = upload_video(V, TITLE, DESC, TAGS, category_id="1", privacy="public", thumbnail_path=THUMB)
        print(f"\nERFOLG: https://youtube.com/watch?v={vid}")
        with open("youtube/twinkle_uploaded.txt","w") as f:
            f.write(f"https://youtube.com/watch?v={vid}\n")
        break
    except Exception as e:
        msg = str(e)[:200]
        print(f"FEHLER: {msg}")
        if "uploadLimitExceeded" in msg or "exceeded" in msg:
            print(f"  -> Tageslimit, warte 30 Min ...")
            time.sleep(1800)
        else:
            print(f"  -> Anderer Fehler, warte 5 Min ...")
            time.sleep(300)
