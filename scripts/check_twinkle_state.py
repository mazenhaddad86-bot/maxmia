from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    for sid in ["bad6e924-e381-4dc4-aa4b-70e606ae467a", "36df5251-cd66-4cd5-9f29-bdff061940ed"]:
        page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=15000)
        time.sleep(4)
        info = page.evaluate("""() => {
            const a = document.querySelector('audio');
            const audSrc = a ? (a.src || '') : 'no audio el';
            const html = document.documentElement.outerHTML;
            const m = html.match(/https:\/\/cdn1\.suno\.ai\/[a-f0-9-]+\.mp3/g);
            return {audSrc: audSrc.slice(0,80), mp3Urls: [...new Set(m||[])].slice(0,3)};
        }""")
        print(f"\n=== {sid[:8]} ===")
        print(info)
