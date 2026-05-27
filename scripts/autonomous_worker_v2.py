"""V2 Worker - aktualisierte Pending Liste"""
import time, os
from pathlib import Path
import urllib.request

BASE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output")
LOG = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\scripts\autonomous.log")

PENDING = [
    ("incy", "8dce0014-64ea-4140-93a5-8cae0e3c6b11"),    # NEU
    ("incy", "17fbe105-082e-466c-b316-c65b9d780fed"),    # NEU
    # Alte IDs sind tot - lasse weg
]

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] V2: {msg}\n")

log("=== V2 Worker startet (Incy neu) ===")
done = set()
interval = 60
iteration = 0
while True:
    iteration += 1
    for theme, sid in PENDING:
        if sid in done: continue
        try:
            req = urllib.request.Request(f"https://cdn1.suno.ai/{sid}.mp3", headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r: data = r.read()
            if len(data) > 100000:
                dest = BASE / theme; dest.mkdir(parents=True, exist_ok=True)
                out = dest / f"{theme}_v55_new_{sid[:8]}.mp3"
                out.write_bytes(data)
                done.add(sid)
                log(f"✅ {theme}/{sid[:8]}: {len(data)} bytes")
        except: pass
    log(f"Iter {iteration} — {len(done)}/{len(PENDING)} fertig")
    if len(done) == len(PENDING): 
        log("ALLE NEUEN FERTIG!"); break
    time.sleep(interval)
