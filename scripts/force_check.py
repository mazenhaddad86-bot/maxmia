from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/song/bad6e924-e381-4dc4-aa4b-70e606ae467a", wait_until="networkidle", timeout=20000)
    time.sleep(5)
    info = page.evaluate("""() => {
        const a = document.querySelector('audio');
        const r = {audioElements: document.querySelectorAll('audio').length};
        if (a) {
            r.src = a.src || a.currentSrc || '';
            r.readyState = a.readyState;
            r.duration = a.duration;
        }
        // Check for "Done" or "Ready" UI
        const allText = document.body.innerText;
        const html = document.documentElement.outerHTML;
        // Look for clip data
        const playInfo = html.match(/"id":"bad6e924[^"]*","clip_id":"([^"]+)"|"audio_url":"([^"]+)"/g);
        r.playInfo = playInfo ? playInfo.slice(0,3) : null;
        return r;
    }""")
    print(info, flush=True)
