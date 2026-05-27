from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pages = browser.contexts[0].pages
    sp = next((pg for pg in pages if "suno.com" in pg.url), pages[0])
    sp.goto("https://suno.com/song/8dce0014-64ea-4140-93a5-8cae0e3c6b11", wait_until="domcontentloaded", timeout=15000)
    time.sleep(4)
    info = sp.evaluate("""() => {
        const html = document.documentElement.outerHTML;
        const m = html.match(/cdn1\.suno\.ai\/[a-f0-9-]+\.mp3/g);
        const t = document.body.innerText.slice(0,300);
        return {urls: m ? [...new Set(m)].slice(0,3) : [], text: t};
    }""")
    print(info, flush=True)
