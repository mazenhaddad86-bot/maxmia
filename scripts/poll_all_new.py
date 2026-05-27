# -*- coding: utf-8 -*-
import time
from pathlib import Path
import urllib.request

JOBS = [
    ("twinkle", "9b867004-ea8d-44ab-a387-0698c013d8b7"),
    ("twinkle", "8518f8c4-dd1f-4b69-8658-2fa3d6fc294c"),
    ("incy", "9a7dedbc-41b7-4bd2-943f-7aa9f10f3a36"),
    ("incy", "64c6a37d-af93-4b1a-8fbd-9581d923d895"),
    ("row", "136d4cff-51fe-4ca0-8177-b989077b7457"),
    ("row", "897c5839-a3a7-4408-b83d-dda2fb1e7fdf"),
]
BASE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output")

done = set()
for i in range(25):
    print(f"\n[{time.strftime('%H:%M:%S')}] Round {i+1}/25", flush=True)
    for theme, sid in JOBS:
        if sid in done: continue
        url = f"https://cdn1.suno.ai/{sid}.mp3"
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
            if len(data) > 100000:
                dest = BASE / theme
                dest.mkdir(parents=True, exist_ok=True)
                out = dest / f"{theme}_v55_{sid[:8]}.mp3"
                out.write_bytes(data)
                print(f"  ✅ {theme}/{sid[:8]}: {len(data)} bytes", flush=True)
                done.add(sid)
        except: pass
    if len(done) == len(JOBS): print("ALLE FERTIG!", flush=True); break
    time.sleep(30)
print(f"\n=== {len(done)}/{len(JOBS)} fertig ===", flush=True)
