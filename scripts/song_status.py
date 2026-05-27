# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="networkidle", timeout=30000)
    time.sleep(5)
    info = page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('a[href*="/song/"]')).slice(0,4);
        return items.map(a => {
            const parent = a.closest('[class*="row"], [class*="tile"], li, div');
            const text = parent ? parent.textContent.trim().replace(/\s+/g,' ').slice(0,200) : '';
            return {
                href: a.getAttribute('href'),
                title: a.textContent.trim().slice(0,40),
                fullContext: text
            };
        });
    }""")
    print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
    # Suno API check via fetch
    statuses = page.evaluate("""async () => {
        try {
            const r = await fetch('/api/billing/info/');
            return {status: r.status};
        } catch(e) { return {err: e.message}; }
    }""")
    print("Billing-API:", statuses, flush=True)
