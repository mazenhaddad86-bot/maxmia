import time
from pathlib import Path
import urllib.request

JOBS = [
    ("twinkle", "9b867004-ea8d-44ab-a387-0698c013d8b7"),
    ("twinkle", "8518f8c4-dd1f-4b69-8658-2fa3d6fc294c"),
    ("incy", "9a7dedbc-41b7-4bd2-943f-7aa9f10f3a36"),
    ("incy", "64c6a37d-af93-4b1a-8fbd-9581d923d895"),
    ("monkeys", "876957b6-3d51-4086-b49e-82c4e566ced0"),
    ("monkeys", "981fd9df-b091-4a13-93f2-5d56dc610ccc"),
    ("happy", "13e28373-091f-4a83-b3a3-80c0e704e211"),
    ("happy", "c50ca40c-e3c2-4cee-9be5-740ad0129ccf"),
    ("patcake", "774a6c2a-9a84-402c-91ac-0eb71b16ebcd"),
    ("patcake", "165e31c0-e903-4544-b815-42543c030dca"),
]
BASE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output")
done = set()
for i in range(25):
    print(f"[{time.strftime('%H:%M:%S')}] {i+1}/25", flush=True)
    for theme, sid in JOBS:
        if sid in done: continue
        try:
            req = urllib.request.Request(f"https://cdn1.suno.ai/{sid}.mp3", headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r: data = r.read()
            if len(data) > 100000:
                dest = BASE / theme; dest.mkdir(parents=True, exist_ok=True)
                out = dest / f"{theme}_v55_{sid[:8]}.mp3"
                out.write_bytes(data)
                print(f"  ✅ {theme}/{sid[:8]}: {len(data)}", flush=True)
                done.add(sid)
        except: pass
    if len(done) == len(JOBS): break
    time.sleep(25)
print(f"\n{len(done)}/{len(JOBS)} fertig", flush=True)
