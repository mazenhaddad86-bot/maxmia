# -*- coding: utf-8 -*-
import time, json
from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request

SONGS = ["2c2583e7-5d41-45ca-9659-021f7c92d671", "259b2472-45eb-405f-88a3-8311f5f48972"]
DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\wheels\suno")
DEST.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    done = {}
    for attempt in range(20):  # max 20 * 30s = 10 Min
        print(f"\n[{time.strftime('%H:%M:%S')}] Attempt {attempt+1}/20", flush=True)
        for sid in SONGS:
            if sid in done: continue
            # Hole audio URL aus Song-Page
            page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=20000)
            time.sleep(3)
            url = page.evaluate("""() => {
                const a = document.querySelector('audio');
                if (a && a.src && !a.src.includes('None.mp3') && !a.src.includes('sil-')) return a.src;
                // Check for explicit URLs in scripts
                const html = document.documentElement.outerHTML;
                const matches = html.match(/https:\/\/cdn1\.suno\.ai\/[a-f0-9-]+\.mp3/g);
                if (matches) {
                    return matches.find(u => !u.includes('None') && !u.includes('sil')) || null;
                }
                return null;
            }""")
            if url:
                try:
                    out = DEST / f"final_{sid[:8]}.mp3"
                    urllib.request.urlretrieve(url, str(out))
                    sz = out.stat().st_size
                    if sz > 100000:
                        print(f"  ✅ {sid[:8]}: {sz} bytes → {out.name}", flush=True)
                        done[sid] = sz
                    else:
                        print(f"  ⏳ {sid[:8]}: only {sz} bytes, retry", flush=True)
                except Exception as e:
                    print(f"  ❌ {sid[:8]}: dl fail {e}", flush=True)
            else:
                print(f"  ⏳ {sid[:8]}: noch keine URL", flush=True)
        if len(done) == len(SONGS):
            print("\n🎉 BEIDE FERTIG!", flush=True)
            break
        time.sleep(30)

# Final
for sid in SONGS:
    if sid in done:
        f = DEST / f"final_{sid[:8]}.mp3"
        print(f"\n{sid}: {done[sid]} bytes", flush=True)
