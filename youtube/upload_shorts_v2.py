# -*- coding: utf-8 -*-
import sys, glob, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from upload_v2 import upload_video
OUT = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output")
def tags(extra): return extra+["nursery rhymes","kids songs","shorts","children songs","baby songs","toddler songs","songs for kids","kids videos","max and mia","preschool songs","sing along","kids learning"]
short_map = {
  "humpty-dumpty": ("Humpty Dumpty","#HumptyDumpty"),
  "twinkle": ("Twinkle Twinkle Little Star","#TwinkleTwinkle"),
  "nature-discovery": ("Nature Discovery","#Nature"),
}
SHORTS=[]
for folder,(name,htag) in short_map.items():
  for sf in sorted(glob.glob(str(OUT/folder/"shorts"/"*.mp4")))+sorted(glob.glob(str(OUT/folder/"*SHORT*.mp4")))+sorted(glob.glob(str(OUT/folder/"*short*.mp4"))):
    SHORTS.append({"file":Path(sf),"title":f"{name} {htag} #Shorts | Kids Songs | Max & Mia","desc":f"{name} - fun nursery rhyme short for kids! {htag} #Shorts #NurseryRhymes #KidsSongs #ForKids","tags":tags([name.lower(),"shorts","kids shorts"])})
print(f"=== {len(SHORTS)} Shorts zum Hochladen ===")
results=[]
for v in SHORTS:
  if not v["file"].exists(): print("FEHLT:",v["file"]); continue
  try:
    vid = upload_video(str(v["file"]), v["title"], v["desc"], v["tags"], category_id="1", privacy="public")
    results.append((v["title"][:60],vid)); time.sleep(2)
  except Exception as e:
    print("FEHLER:",str(e)[:200])
print("\n=== FERTIG ===")
for t,vid in results: print(f"https://youtube.com/watch?v={vid}  -  {t}")
