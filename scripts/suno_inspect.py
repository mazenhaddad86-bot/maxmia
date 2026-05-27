# -*- coding: utf-8 -*-
"""Inspiziere Suno-Create-UI"""
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    if "create" not in page.url:
        page.goto("https://suno.com/create", wait_until="networkidle", timeout=60000)
        time.sleep(4)
    print(f"URL: {page.url}", flush=True)
    page.screenshot(path="scripts/suno_create_logged_in.png", full_page=True)
    print("FullPage Screenshot: scripts/suno_create_logged_in.png", flush=True)
    
    # Inspiziere UI-Elemente
    elements_info = page.evaluate("""() => {
        const results = {};
        // Custom-Mode toggle
        const customToggle = document.querySelector('[data-testid="custom-mode-switch"]') 
            || Array.from(document.querySelectorAll('button,label,div')).find(el => el.textContent && el.textContent.trim() === 'Custom');
        results.customToggle = customToggle ? 'found: ' + customToggle.tagName : 'NOT FOUND';
        
        // Lyrics textarea
        const lyricsTA = document.querySelector('textarea[placeholder*="lyric" i]') 
            || document.querySelector('textarea[placeholder*="Lyric" i]')
            || document.querySelector('[data-testid="lyrics-input"]');
        results.lyricsTA = lyricsTA ? 'found: ' + (lyricsTA.placeholder || 'no placeholder') : 'NOT FOUND';
        
        // Style/Genre input
        const styleInput = document.querySelector('textarea[placeholder*="style" i]')
            || document.querySelector('input[placeholder*="style" i]')
            || document.querySelector('textarea[placeholder*="genre" i]');
        results.styleInput = styleInput ? 'found: ' + (styleInput.placeholder || 'no placeholder') : 'NOT FOUND';
        
        // Model select
        const modelBtns = Array.from(document.querySelectorAll('button')).filter(b => /v[0-9]/i.test(b.textContent||''));
        results.modelBtns = modelBtns.length ? modelBtns.map(b=>b.textContent.trim().slice(0,30)) : 'NO MODEL BUTTONS';
        
        // Create button
        const createBtn = Array.from(document.querySelectorAll('button')).find(b => /^Create$/i.test((b.textContent||'').trim()));
        results.createBtn = createBtn ? 'found' : 'NOT FOUND';
        
        // Show all textareas
        const tas = Array.from(document.querySelectorAll('textarea')).map(t => ({ph: t.placeholder, id: t.id, name: t.name}));
        results.allTextareas = tas;
        return results;
    }""")
    print("\n=== UI Inspection ===", flush=True)
    print(json.dumps(elements_info, indent=2, ensure_ascii=False), flush=True)
