from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
    time.sleep(7)
    info = page.evaluate("""() => {
        const t = document.body.innerText;
        const m1 = t.match(/(\d[\d,.]*)\s*[Kk]?\s*credit/);
        const m2 = t.match(/(\d+)\s*credits/);
        return {
            creditsM1: m1 ? m1[0] : null,
            creditsM2: m2 ? m2[0] : null,
            url: location.href
        };
    }""")
    print(info, flush=True)
