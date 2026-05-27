# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Console-Listener
    logs = []
    page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text[:200]}"))
    page.on("requestfailed", lambda req: logs.append(f"[FAIL] {req.url} -> {req.failure}"))
    page.on("response", lambda r: logs.append(f"[{r.status}] {r.url[:120]}") if r.status >= 400 else None)
    
    # Inspect button state
    print("=== Aktueller URL ===", page.url, flush=True)
    btn_state = page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => /^Create$/i.test((b.textContent||'').trim()));
        if (!btns.length) return null;
        const b = btns[0];
        return {disabled:b.disabled, ariaDisabled:b.getAttribute('aria-disabled'), text:b.textContent, cls:b.className.slice(0,150)};
    }""")
    print("Create-Button State:", btn_state, flush=True)
    
    # Check für irgendeinen Title-Eingabe (vllt. ist es Pflicht)
    fields = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('input,textarea')).map(e => ({
            type: e.tagName + (e.type ? ':'+e.type : ''),
            name: e.name || e.id,
            ph: e.placeholder || '',
            val: e.value?.slice(0,40),
            required: e.required
        }));
    }""")
    print("All fields:", json.dumps(fields, indent=2, ensure_ascii=False), flush=True)
