"""Autonomer Worker — läuft ENDLOS, prüft + lädt alle Suno-Songs automatisch"""
import time, json, os
from pathlib import Path
import urllib.request

BASE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output")
LOG = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\scripts\autonomous.log")

# Alle bekannten pending Songs
PENDING = [
    ("twinkle", "ac051e17-46bc-44c1-8309-26cde3c5f39d"),
    ("twinkle", "71053e6a-b8c5-4b03-a06a-5ec5bfd7290a"),
    ("incy", "9a7dedbc-41b7-4bd2-943f-7aa9f10f3a36"),
    ("incy", "64c6a37d-af93-4b1a-8fbd-9581d923d895"),
    ("monkeys", "876957b6-3d51-4086-b49e-82c4e566ced0"),
    ("monkeys", "981fd9df-b091-4a13-93f2-5d56dc610ccc"),
    ("happy", "13e28373-091f-4a83-b3a3-80c0e704e211"),
    ("happy", "c50ca40c-e3c2-4cee-9be5-740ad0129ccf"),
    ("patcake", "774a6c2a-9a84-402c-91ac-0eb71b16ebcd"),
    ("patcake", "165e31c0-e903-4544-b815-42543c030dca"),
]

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

log("=== Autonomer Worker startet ===")
done = set()
# Initial: check what's already downloaded
for theme, sid in PENDING:
    out = BASE / theme / f"{theme}_v55_{sid[:8]}.mp3"
    if out.exists() and out.stat().st_size > 100000:
        done.add(sid)
        log(f"  Already done: {theme}/{sid[:8]}")

# Endlos-Schleife mit zunehmenden Intervals
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
                out = dest / f"{theme}_v55_{sid[:8]}.mp3"
                out.write_bytes(data)
                done.add(sid)
                log(f"✅ {theme}/{sid[:8]}: {len(data)} bytes")
        except Exception as e: pass
    log(f"Iteration {iteration} — {len(done)}/{len(PENDING)} fertig — warte {interval}s")
    if len(done) == len(PENDING):
        log("ALLE FERTIG! Worker bleibt aktiv für neue Songs.")
    time.sleep(interval)
    # Backoff
    if iteration % 5 == 0 and interval < 300:
        interval += 30
