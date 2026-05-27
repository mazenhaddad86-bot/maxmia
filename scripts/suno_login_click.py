# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print(f"URL: {page.url}", flush=True)
    # Click Log In
    try:
        page.get_by_role("button", name="Log In", exact=False).first.click(timeout=5000)
        print("Klick Log In done", flush=True)
    except Exception as e:
        # Try link
        try:
            page.locator("a:has-text('Log In')").first.click(timeout=5000)
            print("Klick Log In (link) done", flush=True)
        except Exception as e2:
            print(f"Konnte Log In nicht klicken: {e2}", flush=True)
    time.sleep(4)
    print(f"Jetzt URL: {page.url}", flush=True)
    page.screenshot(path="scripts/suno_login_dialog.png")
    print("Screenshot: scripts/suno_login_dialog.png", flush=True)
