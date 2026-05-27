from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pages = browser.contexts[0].pages
    sp = next((pg for pg in pages if "suno.com" in pg.url), pages[0])
    sp.goto(f"https://suno.com/song/41f6064a-c8fa-4676-9a45-30201f771081", wait_until="domcontentloaded", timeout=15000)
    time.sleep(4)
    info = sp.evaluate("""() => {
        const a = document.querySelector('audio');
        const html = document.documentElement.outerHTML;
        const audio_urls = html.match(/cdn1\.suno\.ai\/[a-f0-9-]+\.mp3/g);
        return {
            audSrc: a ? (a.src||a.currentSrc||'') : 'no audio',
            urls: audio_urls ? [...new Set(audio_urls)].slice(0,3) : null,
            text: document.body.innerText.slice(0,200)
        };
    }""")
    print(info, flush=True)
