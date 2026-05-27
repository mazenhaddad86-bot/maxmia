# -*- coding: utf-8 -*-
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request

SONGS = ["d1a1c1d7-6f4f-4c29-ac1e-d400fa767f8b", "16b83b57-3791-4485-aad4-f29ec1aa32d0"]
DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\wheels\suno")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    done = {}
    for i in range(20):
        print(f"[{time.strftime('%H:%M:%S')}] {i+1}/20", flush=True)
        for sid in SONGS:
            if sid in done: continue
            try:
                page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=15000)
                time.sleep(2.5)
                url = page.evaluate("""() => {
                    const a = document.querySelector('audio');
                    if (a && a.src && !a.src.includes('None.mp3') && !a.src.includes('sil-')) return a.src;
                    const m = document.documentElement.outerHTML.match(/https:\/\/cdn1\.suno\.ai\/[a-f0-9-]+\.mp3/g);
                    if (m) return m.find(u=>!u.includes('None')&&!u.includes('sil')) || null;
                    return null;
                }""")
                if url:
                    out = DEST / f"wheels_pep_{sid[:8]}.mp3"
                    urllib.request.urlretrieve(url, str(out))
                    sz = out.stat().st_size
                    if sz > 100000:
                        print(f"  ✅ {sid[:8]}: {sz}", flush=True)
                        done[sid] = sz
                    else:
                        print(f"  ⏳ small: {sz}", flush=True)
                else:
                    print(f"  ⏳ {sid[:8]} keine URL", flush=True)
            except Exception as e: print(f"  ❌ {str(e)[:60]}", flush=True)
        if len(done) == len(SONGS): break
        time.sleep(25)
    print("FINAL:", done, flush=True)
