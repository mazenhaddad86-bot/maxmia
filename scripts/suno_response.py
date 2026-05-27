# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    
    # Capture all relevant network
    responses = []
    def on_resp(r):
        if "suno.com/api" in r.url or "studio-api" in r.url:
            try:
                body = r.text() if r.status == 200 else None
            except:
                body = None
            responses.append({"status": r.status, "url": r.url[:140], "body_len": len(body) if body else 0, "body_preview": body[:200] if body else None})
    page.on("response", on_resp)
    
    # Fill
    page.locator("textarea").nth(0).fill("[Verse]\nThe wheels go round")
    page.locator("textarea").nth(1).fill("kids nursery rhyme")
    time.sleep(1)
    
    print("→ Klick Create", flush=True)
    page.locator("button:has-text('Create')").last.click()
    time.sleep(8)
    
    print("\n=== API Responses ===", flush=True)
    for r in responses[:15]:
        print(f"{r['status']} {r['url']} len={r['body_len']}", flush=True)
        if r['body_preview']:
            print(f"   body: {r['body_preview']}", flush=True)
