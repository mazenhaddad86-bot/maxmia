from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print(f"URL: {page.url}", flush=True)
    print(f"Title: {page.title()}", flush=True)
    page.screenshot(path="scripts/where.png")
