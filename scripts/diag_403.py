from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    sid = "bad6e924-e381-4dc4-aa4b-70e606ae467a"  # Twinkle 1
    page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=15000)
    time.sleep(5)
    # Schauen ob Song überhaupt fertig generiert
    info = page.evaluate("""() => {
        const a = document.querySelector('audio');
        const r = {
            audioSrc: a ? a.src : 'kein audio element',
            audioReady: a ? a.readyState : 'N/A',
            audioDuration: a ? a.duration : 'N/A',
        };
        // Suche im HTML nach allen audio URLs
        const html = document.documentElement.outerHTML;
        const urls = html.match(/https?:[^"'\s]+\.(mp3|m4a|wav|ogg)[^"'\s]*/g);
        r.allAudioUrls = urls ? [...new Set(urls)].slice(0,5) : null;
        // Check JSON-LD oder window state
        const scripts = document.querySelectorAll('script');
        for (const s of scripts) {
            const t = s.textContent;
            if (t && t.includes('audio_url')) {
                const m = t.match(/"audio_url":"([^"]+)"/);
                if (m) { r.found_audio_url = m[1]; break; }
            }
        }
        // Status indicator
        const bodyText = document.body.innerText.slice(0,500);
        r.bodyHint = bodyText;
        return r;
    }""")
    for k,v in info.items(): print(f"  {k}: {str(v)[:200]}", flush=True)
