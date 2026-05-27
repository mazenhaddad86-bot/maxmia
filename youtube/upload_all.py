# -*- coding: utf-8 -*-
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from upload import upload_video, TOKEN_FILE

OUT = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output")

# Alten widerrufenen Token loeschen -> erzwingt frischen Login
if TOKEN_FILE.exists():
    TOKEN_FILE.unlink()
    print("Alter Token geloescht - frischer Login noetig")

def tags_base(extra):
    return extra + ["nursery rhymes","kids songs","children songs","baby songs","toddler songs",
        "songs for kids","kids videos","max and mia","preschool songs","sing along",
        "kids learning","educational videos for kids","animation for kids","3d nursery rhymes","bedtime songs"]

# ---- HAUPTVIDEOS ----
MAIN = [
  {"file": OUT/"baa-baa-black-sheep/baa_baa_final_v3.mp4",
   "title": "Baa Baa Black Sheep \U0001F411 | Nursery Rhymes & Kids Songs | Max & Mia World",
   "desc": "Baa Baa Black Sheep, have you any wool? \U0001F411 Sing along with Max & Mia in this fun 3D animated nursery rhyme!\n\n#BaaBaaBlackSheep #NurseryRhymes #KidsSongs #MaxAndMia #ForKids",
   "tags": tags_base(["baa baa black sheep","sheep song"]), "thumb": r"C:/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/thumbnails/baa_thumb.png"},
  {"file": OUT/"humpty-dumpty/humpty_dumpty_v3_FINAL.mp4",
   "title": "Humpty Dumpty \U0001F95A | Nursery Rhymes & Kids Songs | Max & Mia World",
   "desc": "Humpty Dumpty sat on a wall! \U0001F95A Sing along with Max & Mia in this fun 3D animated nursery rhyme!\n\n#HumptyDumpty #NurseryRhymes #KidsSongs #MaxAndMia #ForKids",
   "tags": tags_base(["humpty dumpty","humpty dumpty song"]), "thumb": r"C:/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/thumbnails/humpty_thumb.png"},
  {"file": OUT/"twinkle/twinkle_final.mp4",
   "title": "Twinkle Twinkle Little Star ⭐ | Nursery Rhymes & Kids Songs | Max & Mia World",
   "desc": "Twinkle Twinkle Little Star, how I wonder what you are! ⭐ Sing along with Max & Mia in this fun 3D animated nursery rhyme!\n\n#TwinkleTwinkle #NurseryRhymes #KidsSongs #MaxAndMia #ForKids",
   "tags": tags_base(["twinkle twinkle little star","star song","lullaby"]), "thumb": r"C:/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/thumbnails/twinkle_thumb.png"},
  {"file": OUT/"nature-discovery/final_v2_16x9.mp4",
   "title": "Nature Discovery \U0001F33F | Learning for Kids | Max & Mia World",
   "desc": "Explore the wonders of nature with Max & Mia! \U0001F33F A fun 3D animated learning adventure for kids.\n\n#NatureForKids #LearningVideos #KidsEducation #MaxAndMia #ForKids",
   "tags": tags_base(["nature for kids","learning videos","educational"]), "thumb": r"C:/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/thumbnails/nature_thumb.png"},
]

# ---- SHORTS ----
SHORTS = []
short_map = {
  "baa-baa-black-sheep": ("Baa Baa Black Sheep","#BaaBaaBlackSheep"),
  "humpty-dumpty": ("Humpty Dumpty","#HumptyDumpty"),
  "twinkle": ("Twinkle Twinkle Little Star","#TwinkleTwinkle"),
  "nature-discovery": ("Nature Discovery","#Nature"),
}
import glob
for folder,(name,htag) in short_map.items():
    for sf in sorted(glob.glob(str(OUT/folder/"shorts"/"*.mp4"))) + sorted(glob.glob(str(OUT/folder/"*SHORT*.mp4"))) + sorted(glob.glob(str(OUT/folder/"*short*.mp4"))):
        SHORTS.append({"file": Path(sf),
            "title": f"{name} {htag} #Shorts | Kids Songs | Max & Mia",
            "desc": f"{name} - fun nursery rhyme short for kids! {htag} #Shorts #NurseryRhymes #KidsSongs #ForKids",
            "tags": tags_base([name.lower(),"shorts","kids shorts"])})

print(f"\n=== UPLOAD PLAN: {len(MAIN)} Hauptvideos + {len(SHORTS)} Shorts ===\n")

results = []
# Erst Hauptvideos (loest beim ersten Mal den Login aus)
for v in MAIN:
    if not v["file"].exists():
        print("FEHLT:", v["file"]); continue
    try:
        vid = upload_video(str(v["file"]), v["title"], v["desc"], v["tags"], category_id="1", privacy="public", thumbnail_path=v.get("thumb"))
        results.append((v["title"], vid)); time.sleep(2)
    except Exception as e:
        print("FEHLER bei", v["file"].name, ":", e)

for v in SHORTS:
    if not v["file"].exists(): continue
    try:
        vid = upload_video(str(v["file"]), v["title"], v["desc"], v["tags"], category_id="1", privacy="public")
        results.append((v["title"], vid)); time.sleep(2)
    except Exception as e:
        print("FEHLER bei", v["file"].name, ":", e)

print("\n=== FERTIG ===")
for t,vid in results:
    print(f"https://youtube.com/watch?v={vid}  -  {t}")
