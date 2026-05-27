# -*- coding: utf-8 -*-
import time, urllib.request, ssl
from pathlib import Path

SONGS = ["af25bc4b-16f8-4ec1-8a98-d5f162cb3543", "a1ce9e4c-a8e3-4886-af50-9469cb55675a"]
DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\wheels\suno")
DEST.mkdir(parents=True, exist_ok=True)

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def try_download(sid):
    """Versuche CDN-Download; gibt Größe zurück falls erfolgreich"""
    url = f"https://cdn1.suno.ai/{sid}.mp3"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            data = r.read()
        if len(data) < 50000:  # zu klein = noch nicht fertig
            return 0
        out = DEST / f"new_{sid[:8]}.mp3"
        out.write_bytes(data)
        return len(data)
    except Exception as e:
        return 0

done = {}
for attempt in range(15):  # max 15 * 30s = 7.5 Min
    print(f"\n[{time.strftime('%H:%M:%S')}] Attempt {attempt+1}", flush=True)
    for sid in SONGS:
        if sid in done: continue
        size = try_download(sid)
        if size > 0:
            print(f"  ✅ {sid[:8]}: {size} bytes saved", flush=True)
            done[sid] = size
        else:
            print(f"  ⏳ {sid[:8]}: nicht fertig", flush=True)
    if len(done) == len(SONGS):
        print("\n🎉 Beide Songs heruntergeladen!", flush=True)
        break
    time.sleep(30)

print("\n=== Final Status ===")
for sid in SONGS:
    if sid in done:
        print(f"  ✅ {sid[:8]}: {done[sid]} bytes")
    else:
        print(f"  ❌ {sid[:8]}: NOCH NICHT FERTIG")
