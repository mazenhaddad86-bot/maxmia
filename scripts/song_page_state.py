from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/song/bad6e924-e381-4dc4-aa4b-70e606ae467a", wait_until="domcontentloaded", timeout=15000)
    time.sleep(4)
    page.screenshot(path="scripts/twinkle_state.png", full_page=False)
    info = page.evaluate("""() => {
        const t = document.body.innerText;
        // Look for status indicators
        return {
            hasGenerating: t.includes('Generating') || t.includes('generating'),
            hasFailed: t.includes('Failed') || t.includes('failed') || t.includes('Error'),
            hasQueue: t.includes('queue') || t.includes('Queue'),
            hasCopyright: t.includes('copyrighted'),
            hasProcessing: t.includes('Processing') || t.includes('processing'),
            textSnippet: t.slice(0,500)
        };
    }""")
    print(info, flush=True)
