# -*- coding: utf-8 -*-
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request

SONGS = ["cdc15bc4-0025-48ec-91d1-49f543f02c6b", "8da03158-242e-423a-9dc7-906541f10c80"]
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
                    out = DEST / f"wheels_hype_{sid[:8]}.mp3"
                    urllib.request.urlretrieve(url, str(out))
                    sz = out.stat().st_size
                    if sz > 100000:
                        print(f"  ✅ {sid[:8]}: {sz}", flush=True)
                        done[sid] = sz
                    else:
                        print(f"  ⏳ {sid[:8]}: {sz}b", flush=True)
                else:
                    print(f"  ⏳ {sid[:8]}: keine URL", flush=True)
            except Exception as e: print(f"  ❌ {str(e)[:60]}", flush=True)
        if len(done) == len(SONGS): break
        time.sleep(25)
    print("FINAL:", done, flush=True)
