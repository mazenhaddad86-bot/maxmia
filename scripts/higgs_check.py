from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    # Open higgsfield in new tab
    page = ctx.new_page()
    page.goto("https://higgsfield.ai/feed", wait_until="domcontentloaded", timeout=20000)
    time.sleep(6)
    page.screenshot(path="scripts/higgs_state.png", full_page=False)
    info = page.evaluate("""() => {
        const t = document.body.innerText.slice(0,400);
        const hasLogin = t.includes('Log in') || t.includes('Sign in');
        const hasClerk = !!window.Clerk;
        const clerkSession = window.Clerk?.session ? 'yes' : 'no';
        return {url: location.href, hasLogin, hasClerk, clerkSession, text: t};
    }""")
    print(info, flush=True)
