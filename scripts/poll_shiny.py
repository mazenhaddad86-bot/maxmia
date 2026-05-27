import time
from pathlib import Path
import urllib.request
SONGS = ["41f6064a-c8fa-4676-9a45-30201f771081", "c2a09676-efed-4039-aaca-603f3fccfd4a"]
DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\twinkle")
DEST.mkdir(parents=True, exist_ok=True)
done = set()
for i in range(25):
    print(f"[{time.strftime('%H:%M:%S')}] {i+1}/25", flush=True)
    for sid in SONGS:
        if sid in done: continue
        try:
            req = urllib.request.Request(f"https://cdn1.suno.ai/{sid}.mp3", headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r: data = r.read()
            if len(data) > 100000:
                out = DEST / f"twinkle_v55_{sid[:8]}.mp3"
                out.write_bytes(data)
                print(f"  ✅ {sid[:8]}: {len(data)}", flush=True)
                done.add(sid)
        except: pass
    if len(done) == len(SONGS): break
    time.sleep(25)
