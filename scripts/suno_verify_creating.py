# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    time.sleep(8)
    page.screenshot(path="scripts/suno_creating.png", full_page=False)
    # Check für "Creating" or new entries
    info = page.evaluate("""() => {
        const result = {};
        result.url = location.href;
        // Look for queue/creating indicators
        result.creating = !!document.querySelector('[data-testid*="creating"], [data-testid*="queue"]');
        // Workspace songs
        const songs = document.querySelectorAll('[data-testid="song-tile"], [class*="song-tile" i]');
        result.songs = songs.length;
        // Look at first few items in workspace
        const items = Array.from(document.querySelectorAll('aside a, aside li')).slice(0,5).map(e=>e.textContent.trim().slice(0,40));
        result.firstWorkspaceItems = items;
        return result;
    }""")
    print("Status:", info, flush=True)
