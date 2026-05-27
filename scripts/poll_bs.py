# -*- coding: utf-8 -*-
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request
SONGS = ["26b56666-c34e-4b27-8445-5f79f525dea1", "93eec1c5-00f8-497c-99ea-da69496b4542"]
DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\babyshark")
DEST.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    done = {}
    for i in range(20):
        print(f"[{time.strftime('%H:%M:%S')}] {i+1}/20 BS", flush=True)
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
                    out = DEST / f"bs_{sid[:8]}.mp3"
                    urllib.request.urlretrieve(url, str(out))
                    sz = out.stat().st_size
                    if sz > 100000: print(f"  ✅ {sid[:8]}: {sz}", flush=True); done[sid] = sz
            except: pass
        if len(done) == len(SONGS): break
        time.sleep(25)
    print("DONE:", done, flush=True)
