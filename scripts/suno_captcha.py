# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.screenshot(path="scripts/captcha_check.png", full_page=True)
    # Find iframes (captchas often use iframes)
    info = page.evaluate("""() => {
        const r = {};
        r.iframes = Array.from(document.querySelectorAll('iframe')).map(f => ({src: (f.src||'').slice(0,100), id: f.id, name: f.name, hidden: f.hidden}));
        r.cloudflare = !!document.querySelector('[class*="cf-" i], [id*="cf-" i]');
        r.captcha = !!document.querySelector('[class*="captcha" i], [id*="captcha" i]');
        r.recaptcha = !!document.querySelector('[class*="recaptcha"], [id*="recaptcha"]');
        r.turnstile = !!document.querySelector('[class*="turnstile"], [id*="turnstile"]');
        // Body text die Hinweise enthalten
        const t = document.body.innerText;
        r.checkText = t.includes('Verify') || t.includes('captcha') || t.includes('robot') || t.includes('challenge');
        return r;
    }""")
    print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
