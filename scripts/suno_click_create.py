# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print(f"URL: {page.url}", flush=True)
    
    # Click Create button
    print("→ Klick Create", flush=True)
    try:
        # Try main create button at bottom
        page.get_by_role("button", name="Create", exact=True).click(timeout=8000)
        print("✓ Create geklickt", flush=True)
    except Exception as e:
        print(f"Create-Klick fail: {e}", flush=True)
        # Fallback
        try:
            page.locator("button:has-text('Create')").last.click(timeout=5000)
            print("✓ Create geklickt (fallback)", flush=True)
        except Exception as e2:
            print(f"Fallback fail: {e2}", flush=True)
    
    time.sleep(4)
    page.screenshot(path="scripts/suno_after_create.png")
    print("Screenshot: scripts/suno_after_create.png", flush=True)
    print(f"URL nach Klick: {page.url}", flush=True)
