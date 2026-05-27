from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
    time.sleep(8)
    page.screenshot(path="scripts/peek.png", full_page=False)
    print(f"URL: {page.url}")
    info = page.evaluate("""() => {
        const tas = document.querySelectorAll('textarea');
        return {
            taCount: tas.length,
            taInfo: Array.from(tas).slice(0,3).map(t=>({ph:t.placeholder?.slice(0,40), visible:t.offsetParent!==null}))
        };
    }""")
    print(info)
