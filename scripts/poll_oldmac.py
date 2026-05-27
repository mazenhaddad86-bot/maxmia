# -*- coding: utf-8 -*-
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request
SONGS = ["e7c021e9-093d-4ea7-b1f4-4d6fc1e85a81", "2c1ea1ba-1b41-4cc0-b593-f724f28c049d"]
DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\oldmacdonald")
DEST.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    done = {}
    for i in range(20):
        print(f"[{time.strftime('%H:%M:%S')}] {i+1}/20 OldMac", flush=True)
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
                    out = DEST / f"oldmac_{sid[:8]}.mp3"
                    urllib.request.urlretrieve(url, str(out))
                    sz = out.stat().st_size
                    if sz > 100000:
                        print(f"  ✅ {sid[:8]}: {sz}", flush=True)
                        done[sid] = sz
            except Exception as e: print(f"  ❌ {str(e)[:60]}", flush=True)
        if len(done) == len(SONGS): break
        time.sleep(25)
    print("DONE:", done, flush=True)
