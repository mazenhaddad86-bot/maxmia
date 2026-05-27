# -*- coding: utf-8 -*-
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request
SONGS = ["bad6e924-e381-4dc4-aa4b-70e606ae467a", "36df5251-cd66-4cd5-9f29-bdff061940ed"]
DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\twinkle")
DEST.mkdir(parents=True, exist_ok=True)
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
                time.sleep(3)
                url = page.evaluate("""() => {
                    const a = document.querySelector('audio');
                    if (a && a.src && !a.src.includes('None.mp3') && !a.src.includes('sil-')) return a.src;
                    const m = document.documentElement.outerHTML.match(/https:\/\/cdn1\.suno\.ai\/[a-f0-9-]+\.mp3/g);
                    if (m) return m.find(u=>!u.includes('None')&&!u.includes('sil')) || null;
                    return null;
                }""")
                if url:
                    out = DEST / f"twinkle_v55_{sid[:8]}.mp3"
                    urllib.request.urlretrieve(url, str(out))
                    sz = out.stat().st_size
                    if sz > 100000: print(f"  ✅ {sid[:8]}: {sz}", flush=True); done[sid] = sz
            except: pass
        if len(done) == len(SONGS): break
        time.sleep(30)
    print("DONE:", done, flush=True)
