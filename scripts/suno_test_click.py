# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Console listener
    msgs = []
    page.on("console", lambda m: msgs.append(f"{m.type}: {m.text[:150]}"))
    
    # Credits info
    credits = page.evaluate("""() => {
        // Suche nach Credit-Anzeige
        const all = document.body.innerText;
        const m = all.match(/(\d[\d,.]*)\s*K?\s*credit/i);
        return m ? m[0] : 'kein credit-text gefunden';
    }""")
    print("Credits info:", credits, flush=True)
    
    # Click Create - mit Playwright locator (echter Click + Event-Trigger)
    print("→ Click Create via Playwright locator", flush=True)
    btn = page.locator("button:has-text('Create')").last
    btn.click()
    
    # SOFORT direkt nach click check für API-Calls
    time.sleep(1)
    page.screenshot(path="scripts/suno_immediate.png")
    
    # Check für neue Songs in Sidebar (suche nach "wheels")
    immediate = page.evaluate("""() => {
        const r = {};
        r.allText = document.body.innerText.toLowerCase();
        r.hasWheelsTitle = r.allText.includes('the wheels');
        r.allText = r.allText.length;
        // Schau in Workspace nach
        const ws = document.querySelectorAll('[class*="workspace" i] *');
        r.wsItems = Array.from(ws).slice(0,30).map(e=>e.textContent.trim().slice(0,30)).filter(t=>t.length>3).slice(0,10);
        return r;
    }""")
    print("Immediate state:", json.dumps(immediate, ensure_ascii=False), flush=True)
    
    time.sleep(4)
    print("\nConsole-Messages:", msgs[-10:], flush=True)
