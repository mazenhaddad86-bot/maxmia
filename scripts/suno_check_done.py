# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.screenshot(path="scripts/suno_check_done.png", full_page=False)
    
    # Inspiziere die obersten Songs in der Workspace
    info = page.evaluate("""() => {
        const result = {};
        // Try to find the song list items (looking at sidebar)
        const links = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        result.songLinks = links.slice(0,4).map(a => ({
            href: a.getAttribute('href'),
            title: (a.textContent || '').trim().slice(0,40)
        }));
        // Loading indicators
        const loading = document.querySelectorAll('[class*="loading" i], [class*="spinner" i], [aria-busy="true"]').length;
        result.loadingCount = loading;
        return result;
    }""")
    print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
