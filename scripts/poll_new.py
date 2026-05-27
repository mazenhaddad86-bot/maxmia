# -*- coding: utf-8 -*-
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request

SONGS = ["47b8a02f-99eb-4f6d-a275-1b84315fc2b9", "8ba030b2-f75b-4fab-b26f-f46ee4328637"]
DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\wheels\suno")
DEST.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    done = {}
    for i in range(20):
        print(f"\n[{time.strftime('%H:%M:%S')}] {i+1}/20", flush=True)
        for sid in SONGS:
            if sid in done: continue
            try:
                page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=20000)
                time.sleep(2.5)
                url = page.evaluate("""() => {
                    const a = document.querySelector('audio');
                    if (a && a.src && !a.src.includes('None.mp3') && !a.src.includes('sil-')) return a.src;
                    const m = document.documentElement.outerHTML.match(/https:\/\/cdn1\.suno\.ai\/[a-f0-9-]+\.mp3/g);
                    if (m) return m.find(u=>!u.includes('None')&&!u.includes('sil')) || null;
                    return null;
                }""")
                if url:
                    out = DEST / f"wheels_v5_{sid[:8]}.mp3"
                    urllib.request.urlretrieve(url, str(out))
                    sz = out.stat().st_size
                    if sz > 100000:
                        dur = "?"
                        print(f"  ✅ {sid[:8]}: {sz} bytes → {out.name}", flush=True)
                        done[sid] = sz
                    else:
                        print(f"  ⏳ {sid[:8]}: only {sz}b", flush=True)
                else:
                    print(f"  ⏳ {sid[:8]}: no URL", flush=True)
            except Exception as e:
                print(f"  ❌ {sid[:8]}: {str(e)[:80]}", flush=True)
        if len(done) >= 1:
            print(f"\n>= 1 Song fertig", flush=True)
            if len(done) == len(SONGS):
                print("ALLE FERTIG!", flush=True)
                break
        time.sleep(30)
    print("\n=== Final ===", flush=True)
    for sid in SONGS: print(f"  {sid}: {'✅ '+str(done[sid]) if sid in done else '❌ NICHT FERTIG'}", flush=True)
